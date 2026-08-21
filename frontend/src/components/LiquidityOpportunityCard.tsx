import { MoneyValue } from "./MoneyValue";
import { RiskBadge } from "./RiskBadge";
import { Button } from "./Button";
import styles from "./LiquidityOpportunityCard.module.css";

export interface LiquidityOpportunity {
  id: string;
  buyerName: string;
  invoiceAmount: number;
  currency: string;
  tier: string;
  score: number;
  advancePct: number;
  feePct: number;
  advanceAmountUsd: number;
  daysToMaturity: number;
}

export function LiquidityOpportunityCard({
  opportunity,
  onFinance,
}: {
  opportunity: LiquidityOpportunity;
  onFinance?: (id: string) => void;
}) {
  const o = opportunity;
  return (
    <div className={styles.card}>
      <div className={styles.top}>
        <div>
          <div className={styles.buyer}>{o.buyerName}</div>
          <div className={styles.invoice}>
            <MoneyValue value={o.invoiceAmount} currency={o.currency} /> invoice · due in {o.daysToMaturity}{" "}
            days
          </div>
        </div>
        <RiskBadge tier={o.tier} score={o.score} />
      </div>
      <div className={styles.terms}>
        <div>
          <span className={styles.termLabel}>Advance</span>
          <span className={styles.termValue}>{o.advancePct}%</span>
        </div>
        <div>
          <span className={styles.termLabel}>Fee</span>
          <span className={styles.termValue}>{o.feePct}%</span>
        </div>
        <div>
          <span className={styles.termLabel}>You get today</span>
          <span className={styles.termValueHero}>
            <MoneyValue value={o.advanceAmountUsd} currency="USD" />
          </span>
        </div>
      </div>
      <Button variant="primary" onClick={() => onFinance?.(o.id)}>
        Review &amp; finance
      </Button>
    </div>
  );
}
