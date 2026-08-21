import { formatUsd } from "../lib/format";
import styles from "./ExposureBar.module.css";

export function ExposureBar({
  currency,
  usdValue,
  maxUsdValue,
}: {
  currency: string;
  usdValue: number;
  maxUsdValue: number;
}) {
  const pct = maxUsdValue > 0 ? Math.max(4, (usdValue / maxUsdValue) * 100) : 0;
  return (
    <div className={styles.row}>
      <span className={styles.currency}>{currency}</span>
      <div className={styles.track}>
        <div className={styles.fill} style={{ width: `${pct}%` }} />
      </div>
      <span className={styles.value}>{formatUsd(usdValue)}</span>
    </div>
  );
}
