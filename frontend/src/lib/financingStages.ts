export const FINANCING_STAGES = [
  "Opportunity",
  "Offer",
  "Submitted",
  "Under review",
  "Approved",
  "Disbursed",
  "Settled",
] as const;

export type FinancingStage = (typeof FINANCING_STAGES)[number];
