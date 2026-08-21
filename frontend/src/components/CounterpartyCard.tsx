import { RiskBadge } from "./RiskBadge";
import styles from "./CounterpartyCard.module.css";

export interface CounterpartyProfileData {
  name: string;
  country: string;
  corridor: string;
  currencies: string[];
  contributingSmeCount: number;
  transactionCount: number;
  onTimeCount: number;
  moderatelyLateCount: number;
  significantlyLateCount: number;
  onTimePct: number;
  medianDelayDays: number;
  delayVariance: "low" | "moderate" | "high";
  trend: "improving" | "stable" | "declining";
  score: number;
  tier: string;
  thinData: boolean;
}

const TREND_ARROW: Record<CounterpartyProfileData["trend"], string> = {
  improving: "▲",
  stable: "–",
  declining: "▼",
};

export function CounterpartyCard({ data, compact = false }: { data: CounterpartyProfileData; compact?: boolean }) {
  const d = data;
  const total = d.onTimeCount + d.moderatelyLateCount + d.significantlyLateCount || 1;

  return (
    <div className={`${styles.card} ${compact ? styles.compact : ""}`}>
      <div className={styles.header}>
        <div>
          <div className={styles.name}>{d.name}</div>
          <div className={styles.corridor}>
            {d.corridor} · {d.currencies.join(" / ")}
          </div>
        </div>
        <RiskBadge tier={d.tier} score={d.score} />
      </div>

      {d.thinData && (
        <div className={styles.thinDataFlag}>
          Limited data — fewer than 10 observed transactions. Conservative pricing applied.
        </div>
      )}

      <div className={styles.statRow}>
        <div>
          <span className={styles.statValue}>{d.transactionCount}</span>
          <span className={styles.statLabel}>observed transactions</span>
        </div>
        <div>
          <span className={styles.statValue}>{d.onTimePct.toFixed(1)}%</span>
          <span className={styles.statLabel}>on-time</span>
        </div>
        <div>
          <span className={styles.statValue}>{d.medianDelayDays}d</span>
          <span className={styles.statLabel}>median delay</span>
        </div>
        <div>
          <span className={styles.statValue}>
            {TREND_ARROW[d.trend]} {d.trend}
          </span>
          <span className={styles.statLabel}>trend</span>
        </div>
      </div>

      <div className={styles.bucketBar}>
        <div
          className={styles.bucketOnTime}
          style={{ width: `${(d.onTimeCount / total) * 100}%` }}
          title={`${d.onTimeCount} on-time`}
        />
        <div
          className={styles.bucketModerate}
          style={{ width: `${(d.moderatelyLateCount / total) * 100}%` }}
          title={`${d.moderatelyLateCount} moderately delayed`}
        />
        <div
          className={styles.bucketSignificant}
          style={{ width: `${(d.significantlyLateCount / total) * 100}%` }}
          title={`${d.significantlyLateCount} significantly delayed`}
        />
      </div>
      <div className={styles.bucketLegend}>
        <span><i className={styles.dotOnTime} /> On-time ({d.onTimeCount})</span>
        <span><i className={styles.dotModerate} /> Moderate ({d.moderatelyLateCount})</span>
        <span><i className={styles.dotSignificant} /> Significant ({d.significantlyLateCount})</span>
      </div>

      <div className={styles.footer}>
        Data contributed by <strong>{d.contributingSmeCount} SMEs</strong> on the platform — no single
        lender relationship could see this much history.
      </div>
    </div>
  );
}
