import type { ReactNode } from "react";
import styles from "./FinancialMetric.module.css";

type Trend = "up" | "down" | "flat";
type IconTone = "gold" | "good" | "warning" | "critical" | "info";

export function FinancialMetric({
  label,
  value,
  hint,
  trend,
  trendLabel,
  size = "default",
  icon,
  iconTone = "gold",
}: {
  label: string;
  value: string;
  hint?: string;
  trend?: Trend;
  trendLabel?: string;
  size?: "display" | "default";
  icon?: ReactNode;
  iconTone?: IconTone;
}) {
  return (
    <div className={styles.card}>
      {icon && <span className={`${styles.iconBadge} ${styles[iconTone]}`}>{icon}</span>}
      <div className={`${styles.value} ${size === "display" ? styles.display : ""}`}>{value}</div>
      <div className={styles.labelRow}>
        <span className={styles.label}>{label}</span>
        {trend && (
          <span className={`${styles.trend} ${styles[trend]}`}>
            {trend === "up" ? "▲" : trend === "down" ? "▼" : "–"} {trendLabel}
          </span>
        )}
      </div>
      {hint && <div className={styles.hint}>{hint}</div>}
    </div>
  );
}
