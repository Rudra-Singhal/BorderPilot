import { useCallback, useState } from "react";

// Lightweight demo session auth -- fixed credentials, no backend user table.
// Per product spec: "do not build full KYC/auth infrastructure," but a login
// screen is still expected since judges/users expect one.
const DEMO_EMAIL = "raj@borderpilot.demo";
const DEMO_PASSWORD = "demo1234";
const SESSION_KEY = "borderpilot-session";

export function isAuthenticated(): boolean {
  return localStorage.getItem(SESSION_KEY) === "active";
}

export function useAuth() {
  const [authenticated, setAuthenticated] = useState(isAuthenticated());

  const login = useCallback((email: string, password: string): boolean => {
    if (email.trim().toLowerCase() === DEMO_EMAIL && password === DEMO_PASSWORD) {
      localStorage.setItem(SESSION_KEY, "active");
      setAuthenticated(true);
      return true;
    }
    return false;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(SESSION_KEY);
    setAuthenticated(false);
  }, []);

  return { authenticated, login, logout, demoEmail: DEMO_EMAIL, demoPassword: DEMO_PASSWORD };
}
