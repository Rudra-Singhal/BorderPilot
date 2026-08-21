import type { BankPacketMatchEntry } from "../lib/api";
import { formatUsd, tierBucket } from "../lib/format";
import { Pill } from "./Pill";
import styles from "./MatchCard.module.css";

export function MatchCard({ match }: { match: BankPacketMatchEntry }) {
  const isAutoEligible = match.eligibility_flag !== "needs_review";
  return (
    <div className={styles.card}>
      <div className={styles.route}>
        <span className={styles.party}>{match.payable_sme_name}</span>
        <span className={styles.arrow}>owes</span>
        <span className={styles.counterparty}>{match.counterparty_name}</span>
        <span className={styles.arrow}>owes</span>
        <span className={styles.party}>{match.receivable_sme_name}</span>
      </div>

      {match.justification_text && <p className={styles.justification}>{match.justification_text}</p>}

      <div className={styles.footer}>
        <span className={styles.amount}>{formatUsd(match.matched_amount_usd)}</span>
        {match.confidence_tier && <Pill tone={tierBucket(match.confidence_tier)}>Tier {match.confidence_tier}</Pill>}
        <Pill tone={isAutoEligible ? "good" : "warning"}>
          {isAutoEligible ? "Auto-eligible" : "Needs review"}
        </Pill>
        {match.ai_generated === false && <span className={styles.fallbackNote}>fallback template</span>}
      </div>
    </div>
  );
}
