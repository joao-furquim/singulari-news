import React, { createContext, useContext, useState, useCallback } from 'react';
import { User } from '../types';

interface AuthContextType {
  token: string | null;
  user: User | null;
  preferences: string[];
  isAuthenticated: boolean;
  login: (token: string, user: User, preferences: string[]) => void;
  logout: () => void;
  updateUser: (user: User) => void;
  updatePreferences: (preferences: string[]) => void;
  pendingAction: (() => void) | null;
  setPendingAction: (action: (() => void) | null) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(
    () => localStorage.getItem('token'),
  );
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('user');
    return stored ? (JSON.parse(stored) as User) : null;
  });
  const [preferences, setPreferences] = useState<string[]>(() => {
    const stored = localStorage.getItem('preferences');
    return stored ? (JSON.parse(stored) as string[]) : [];
  });
  const [pendingAction, setPendingAction] = useState<(() => void) | null>(null);

  const login = useCallback(
    (newToken: string, newUser: User, newPreferences: string[]) => {
      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(newUser));
      localStorage.setItem('preferences', JSON.stringify(newPreferences));
      setToken(newToken);
      setUser(newUser);
      setPreferences(newPreferences);
    },
    [],
  );

  const logout = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('preferences');
    setToken(null);
    setUser(null);
    setPreferences([]);
  }, []);

  const updateUser = useCallback((updated: User) => {
    localStorage.setItem('user', JSON.stringify(updated));
    setUser(updated);
  }, []);

  const updatePreferences = useCallback((updated: string[]) => {
    localStorage.setItem('preferences', JSON.stringify(updated));
    setPreferences(updated);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        preferences,
        isAuthenticated: !!token,
        login,
        logout,
        updateUser,
        updatePreferences,
        pendingAction,
        setPendingAction,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
