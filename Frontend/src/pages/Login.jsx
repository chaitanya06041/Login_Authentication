import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { setToken, getToken } from '../utils/auth';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (getToken()) navigate('/');
    // Listen to storage event (cross-tab sync)
    window.addEventListener('storage', () => {
      if (getToken()) navigate('/');
    });
  }, []);

  const handleSignup = () => {
    navigate('/signup')
  }
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:8000/login', { email, password });
      setToken(res.data.token);
      navigate('/');
    } catch (err) {
      alert('Login failed');
    }
  };

  const handleGoogleLogin = () => {
    window.location.href = 'http://localhost:8000/auth/google';
  };

  const handleGithubLogin = () => {
    window.location.href = 'http://localhost:8000/auth/github';
  };

  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Login</button>
      </form>

      <button onClick={handleGoogleLogin}>Login with Google</button>
      <button onClick={handleGithubLogin}>Login with GitHub</button>
      <button onClick={handleSignup}>SIGNUP</button>

    </div>
  );
};

export default Login;
