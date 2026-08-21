import styles from "./FinancialMetric.module.css";

type Trend = "up" | "down" | "flat";

export function FinancialMetric({
  label,
  value,
  hint,
  trend,
  trendLabel,
  size = "default",
}: {
  label: string;
  value: string;
  hint?: string;
  trend?: Trend;
  trendLabel?: string;
  size?: "display" | "default";
}) {
  return (
    <div className={styles.metric}>
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
