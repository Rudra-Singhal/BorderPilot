import styles from "./ActivityRow.module.css";

export interface ActivityEvent {
  id: string;
  timestamp: string;
  actor: "system" | "user";
  eventType: string;
  description: string;
}

export function ActivityRow({ event }: { event: ActivityEvent }) {
  return (
    <div className={styles.row}>
      <span className={styles.timestamp}>{event.timestamp}</span>
      <span className={`${styles.actor} ${styles[event.actor]}`}>{event.actor}</span>
      <span className={styles.eventType}>{event.eventType}</span>
      <span className={styles.description}>{event.description}</span>
    </div>
  );
}
