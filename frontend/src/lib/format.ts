export function formatUsd(value: number): string {
  return value.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 });
}

export function formatAmount(value: number, currency: string): string {
  return `${value.toLocaleString("en-US", { maximumFractionDigits: 2 })} ${currency}`;
}

export function formatDate(value: string): string {
  return new Date(value).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

export function formatDateTime(value: string): string {
  return new Date(value).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function tierBucket(tier: string | null | undefined): "good" | "warning" | "critical" | "neutral" {
  if (!tier) return "neutral";
  if (tier === "A" || tier === "B") return "good";
  if (tier === "C") return "warning";
  return "critical";
}
