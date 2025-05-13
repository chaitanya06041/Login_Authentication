import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getToken, removeToken } from '../utils/auth';

const Home = () => {
  const navigate = useNavigate();

  useEffect(() => {
    if (!getToken()) navigate('/login');
    // Listen to storage changes (cross-tab logout)
    window.addEventListener('storage', () => {
      if (!getToken()) navigate('/login');
    });
  }, []);

  const handleLogout = () => {
    removeToken();
    navigate('/login');
  };

  return (
    <div>
      <h2>Welcome to Home!</h2>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
};

export default Home;
