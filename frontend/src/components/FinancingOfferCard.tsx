import { useState } from "react";
import { MoneyValue } from "./MoneyValue";
import { RiskBadge } from "./RiskBadge";
import styles from "./FinancingOfferCard.module.css";

export interface ScoreBucket {
  label: string;
  weightPct: number;
  score: number;
}

export interface FinancingOfferData {
  buyerName: string;
  invoiceAmount: number;
  currency: string;
  advancePct: number;
  feePct: number;
  advanceAmountUsd: number;
  feeAmountUsd: number;
  netProceedsUsd: number;
  maturityDate: string;
  tier: string;
  score: number;
  buckets: ScoreBucket[];
}

export function FinancingOfferCard({ offer }: { offer: FinancingOfferData }) {
  const [expanded, setExpanded] = useState(false);
  const o = offer;

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div>
          <div className={styles.title}>Financing offer — {o.buyerName}</div>
          <div className={styles.sub}>
            <MoneyValue value={o.invoiceAmount} currency={o.currency} /> invoice
          </div>
        </div>
        <RiskBadge tier={o.tier} score={o.score} />
      </div>

      <div className={styles.grid}>
        <div>
          <span className={styles.gridLabel}>Advance</span>
          <span className={styles.gridValue}>{o.advancePct}%</span>
        </div>
        <div>
          <span className={styles.gridLabel}>Fee</span>
          <span className={styles.gridValue}>
            {o.feePct}% (<MoneyValue value={o.feeAmountUsd} currency="USD" />)
          </span>
        </div>
        <div>
          <span className={styles.gridLabel}>Net proceeds</span>
          <span className={styles.gridValueHero}>
            <MoneyValue value={o.netProceedsUsd} currency="USD" />
          </span>
        </div>
        <div>
          <span className={styles.gridLabel}>Maturity</span>
          <span className={styles.gridValue}>{o.maturityDate}</span>
        </div>
      </div>

      <button className={styles.whyToggle} onClick={() => setExpanded((v) => !v)}>
        {expanded ? "Hide" : "Why this rate?"} {expanded ? "▲" : "▼"}
      </button>

      {expanded && (
        <div className={styles.buckets}>
          {o.buckets.map((b) => (
            <div key={b.label} className={styles.bucketRow}>
              <span className={styles.bucketLabel}>
                {b.label} <span className={styles.bucketWeight}>{b.weightPct}%</span>
              </span>
              <div className={styles.bucketTrack}>
                <div className={styles.bucketFill} style={{ width: `${b.score}%` }} />
              </div>
              <span className={styles.bucketScore}>{Math.round(b.score)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
