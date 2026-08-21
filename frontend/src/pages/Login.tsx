import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { Button } from "../components/Button";
import styles from "./Login.module.css";

export function Login() {
  const { login, demoEmail, demoPassword } = useAuth();
  const [email, setEmail] = useState(demoEmail);
  const [password, setPassword] = useState(demoPassword);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (login(email, password)) {
      navigate("/", { replace: true });
    } else {
      setError("Incorrect email or password.");
    }
  }

  return (
    <div className={styles.page}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <div className={styles.brand}>
          <span className={styles.brandMark} />
          <span className={styles.brandName}>BorderPilot</span>
        </div>
        <p className={styles.tagline}>Underwriting orchestration for cross-border trade finance.</p>

        <label className={styles.label}>
          Email
          <input
            className={styles.input}
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="username"
          />
        </label>
        <label className={styles.label}>
          Password
          <input
            className={styles.input}
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </label>

        {error && <div className={styles.error}>{error}</div>}

        <Button variant="primary" type="submit">
          Sign in
        </Button>

        <p className={styles.hint}>Demo credentials are pre-filled.</p>
      </form>
    </div>
  );
}
