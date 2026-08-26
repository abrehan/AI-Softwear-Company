import React, { createContext, useContext, useEffect, useState } from "react";

export interface User {
  id: number;
  username: string;
  email: string;
  role: "admin" | "user";
  disabled: boolean;
  created_at: string;
}

interface AuthContextValue {
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const TOKEN_KEY = "ai_software_company_access_token";

async function getMe(token: string): Promise<User> {
  const response = await fetch("/api/users/me/", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw new Error("Session expired or unauthorized.");
  return response.json();
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    if (!token) {
      setUser(null);
      return;
    }
    try {
      setUser(await getMe(token));
    } catch {
      logout();
    }
  };

  const login = async (username: string, password: string) => {
    const body = new URLSearchParams({ username, password });
    const response = await fetch("/api/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || "Login failed.");
    if (!data.access_token) throw new Error("Login response did not contain an access token.");
    localStorage.setItem(TOKEN_KEY, data.access_token);
    setToken(data.access_token);
    setUser(await getMe(data.access_token));
  };

  useEffect(() => {
    const initialize = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        setUser(await getMe(token));
      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    };
    void initialize();
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
