from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import uvicorn

# Fake DB (use real DB in production)
users_db = {}

# Secret key for JWT
SECRET_KEY = "your_super_secret_key_here"
ALGORITHM = "HS256"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI()

# CORS setup
origins = [
    "http://localhost:5173",  # your frontend URL
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth config
config = Config('.env')  # create a .env file or load manually
oauth = OAuth(config)

# Google OAuth
oauth.register(
    name='google',
    client_id="YOUR_GOOGLE_CLIENT_ID",
    client_secret="YOUR_GOOGLE_CLIENT_SECRET",
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# GitHub OAuth
oauth.register(
    name='github',
    client_id="YOUR_GITHUB_CLIENT_ID",
    client_secret="YOUR_GITHUB_CLIENT_SECRET",
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

# Utility functions
def create_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

# Routes
@app.post("/signup")
async def signup(user: dict):
    email = user.get('email')
    password = user.get('password')
    if email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    users_db[email] = {
        "email": email,
        "password": hash_password(password),
    }
    return {"msg": "User created"}

@app.post("/login")
async def login(user: dict):
    email = user.get('email')
    password = user.get('password')
    db_user = users_db.get(email)
    if not db_user or not verify_password(password, db_user['password']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": email})
    return {"token": token}

@app.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google/callback")
async def google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)
    email = user_info['email']

    # Register user if not exists
    if email not in users_db:
        users_db[email] = {
            "email": email,
            "password": None,  # Social login users have no password
        }

    jwt_token = create_token({"sub": email})
    # Redirect back to frontend with token
    return RedirectResponse(f"http://localhost:5173/?token={jwt_token}")

@app.get("/auth/github")
async def github_login(request: Request):
    redirect_uri = "http://localhost:8000/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@app.get("/auth/github/callback")
async def github_callback(request: Request):
    token = await oauth.github.authorize_access_token(request)
    resp = await oauth.github.get('user', token=token)
    profile = resp.json()
    email = profile['email']

    # If GitHub email is private, fetch emails
    if not email:
        emails_resp = await oauth.github.get('user/emails', token=token)
        emails = emails_resp.json()
        email = emails[0]['email']

    if email not in users_db:
        users_db[email] = {
            "email": email,
            "password": None,
        }

    jwt_token = create_token({"sub": email})
    return RedirectResponse(f"http://localhost:5173/?token={jwt_token}")

# Protected route example
@app.get("/protected")
async def protected(token: str = Depends(lambda request: request.headers.get('Authorization'))):
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    token = token.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email not in users_db:
            raise HTTPException(status_code=401, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"email": user_email}

# Start the server (if running standalone)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
