// Simple wrapper around localStorage for auth

export function setToken(token) {
    localStorage.setItem('token', token);
    // Broadcast login event to other tabs
    localStorage.setItem('auth-event', Date.now());
  }
  
  export function getToken() {
    return localStorage.getItem('token');
  }
  
  export function removeToken() {
    localStorage.removeItem('token');
    localStorage.setItem('auth-event', Date.now());
  }
  