import styles from "./AsyncState.module.css";

export function LoadingState({ label = "Loading..." }: { label?: string }) {
  return <div className={styles.state}>{label}</div>;
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className={`${styles.state} ${styles.error}`}>
      Could not reach the API — {message}
    </div>
  );
}
