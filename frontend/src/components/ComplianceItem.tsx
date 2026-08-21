import styles from "./ComplianceItem.module.css";

export interface ComplianceItemData {
  label: string;
  status: "verified" | "pending" | "illustrative";
  detail?: string;
}

const STATUS_LABEL: Record<ComplianceItemData["status"], string> = {
  verified: "Verified",
  pending: "Pending",
  illustrative: "Illustrative",
};

export function ComplianceItem({ item }: { item: ComplianceItemData }) {
  return (
    <div className={styles.row}>
      <div className={styles.main}>
        <span className={`${styles.dot} ${styles[item.status]}`} />
        <span className={styles.label}>{item.label}</span>
        <span className={`${styles.status} ${styles[item.status]}`}>{STATUS_LABEL[item.status]}</span>
      </div>
      {item.status === "illustrative" && (
        <p className={styles.caveat}>
          Illustrative demo rule — not verified regulatory guidance.
          {item.detail ? ` ${item.detail}` : ""}
        </p>
      )}
      {item.status !== "illustrative" && item.detail && <p className={styles.detail}>{item.detail}</p>}
    </div>
  );
}
