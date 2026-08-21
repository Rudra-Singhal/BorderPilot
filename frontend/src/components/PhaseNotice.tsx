import styles from "./PhaseNotice.module.css";

export function PhaseNotice({ phase, note }: { phase: string; note: string }) {
  return (
    <div className={styles.notice}>
      <span className={styles.tag}>Design preview — {phase}</span>
      <span>{note}</span>
    </div>
  );
}
