import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../api/client';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchCurrentUser = async () => {
    const token = localStorage.getItem('skillswap_token');
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const resp = await api.get('/auth/me');
      setUser(resp.data);
      localStorage.setItem('skillswap_user', JSON.stringify(resp.data));
    } catch (err) {
      console.error('Failed to fetch current user profile:', err);
      localStorage.removeItem('skillswap_token');
      localStorage.removeItem('skillswap_user');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const login = async (roll_no, password) => {
    const resp = await api.post('/auth/login', { roll_no, password });
    const { access_token } = resp.data;
    localStorage.setItem('skillswap_token', access_token);
    await fetchCurrentUser();
    return resp.data;
  };

  const logout = () => {
    localStorage.removeItem('skillswap_token');
    localStorage.removeItem('skillswap_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser: fetchCurrentUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
