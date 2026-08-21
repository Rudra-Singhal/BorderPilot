import { FINANCING_STAGES, type FinancingStage } from "../lib/financingStages";
import styles from "./StatusTimeline.module.css";

export function StatusTimeline({ currentStage }: { currentStage: FinancingStage }) {
  const currentIndex = FINANCING_STAGES.indexOf(currentStage);

  return (
    <div className={styles.timeline}>
      {FINANCING_STAGES.map((stage, i) => {
        const state = i < currentIndex ? "done" : i === currentIndex ? "current" : "pending";
        return (
          <div key={stage} className={styles.step}>
            <div className={`${styles.dot} ${styles[state]}`}>{state === "done" ? "✓" : i + 1}</div>
            <span className={`${styles.label} ${state === "current" ? styles.currentLabel : ""}`}>
              {stage}
            </span>
            {i < FINANCING_STAGES.length - 1 && (
              <div className={`${styles.connector} ${i < currentIndex ? styles.connectorDone : ""}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
