import styles from "./Button.module.css";

type Variant = "primary" | "secondary";

export function Button({
  variant = "secondary",
  children,
  ...rest
}: {
  variant?: Variant;
  children: React.ReactNode;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button className={`${styles.btn} ${styles[variant]}`} {...rest}>
      {children}
    </button>
  );
}
