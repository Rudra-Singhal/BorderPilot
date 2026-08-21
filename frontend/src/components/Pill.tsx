import styles from "./Pill.module.css";

type Tone = "good" | "warning" | "critical" | "neutral";

export function Pill({ tone, children }: { tone: Tone; children: React.ReactNode }) {
  return <span className={`${styles.pill} ${styles[tone]}`}>{children}</span>;
}
