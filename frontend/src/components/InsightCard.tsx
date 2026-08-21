import styles from "./InsightCard.module.css";

export function InsightCard({
  text,
  sourceLabel,
  sourceHref,
}: {
  text: string;
  sourceLabel?: string;
  sourceHref?: string;
}) {
  return (
    <div className={styles.card}>
      <div className={styles.badge}>AI-generated explanation</div>
      <p className={styles.text}>{text}</p>
      {sourceLabel && (
        <a className={styles.source} href={sourceHref}>
          View source data →
        </a>
      )}
    </div>
  );
}
