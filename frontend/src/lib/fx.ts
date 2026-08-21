// Mirrors the static FX table in backend/app/services/netting.py (FX_TO_USD).
// Used only for dashboard-level display aggregates -- the backend is the source
// of truth for anything netting-related.
export const FX_TO_USD: Record<string, number> = {
  USD: 1.0,
  EUR: 1.08,
  GBP: 1.27,
  INR: 0.012,
  SEK: 0.095,
  SGD: 0.74,
  COP: 0.00025,
};

export function toUsd(amount: number, currency: string): number {
  return amount * (FX_TO_USD[currency] ?? 0);
}
