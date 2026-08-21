import { tierBucket } from "../lib/format";
import styles from "./RiskBadge.module.css";

export function RiskBadge({ tier, score }: { tier: string; score?: number }) {
  const bucket = tierBucket(tier);
  return (
    <span className={`${styles.badge} ${styles[bucket]}`}>
      Tier {tier}
      {score !== undefined && <span className={styles.score}>· {Math.round(score)}</span>}
    </span>
  );
}
