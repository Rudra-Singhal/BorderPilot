const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${init?.method ?? "GET"} ${path} failed: ${res.status} ${body}`);
  }
  return res.json() as Promise<T>;
}

export interface SME {
  id: string;
  name: string;
  country: string;
  base_currency: string;
  created_at: string;
}

export interface Counterparty {
  id: string;
  name: string;
  country: string;
  created_at: string;
}

export interface Obligation {
  id: string;
  sme_id: string;
  counterparty_id: string;
  direction: "receivable" | "payable";
  amount: number;
  currency: string;
  expected_settlement_date: string;
  status: "open" | "settled" | "netted";
  created_at: string;
}

export interface ReliabilityScore {
  id: string;
  counterparty_id: string;
  obligation_id: string | null;
  score: number;
  tier: string;
  version: number;
  factors: Record<string, unknown>;
  computed_at: string;
}

export interface OffsetMatch {
  id: string;
  netting_run_id: string;
  counterparty_id: string;
  payable_obligation_id: string;
  receivable_obligation_id: string;
  settlement_bucket_start: string;
  settlement_bucket_end: string;
  matched_amount_usd: number;
  confidence_tier: string | null;
  eligibility_flag: "auto_eligible" | "needs_review" | null;
  justification_text: string | null;
  ai_generated: boolean | null;
  created_at: string;
}

export interface NettingRun {
  id: string;
  executed_at: string;
  window_days: number;
  obligations_considered: number;
  matches_created: number;
  fx_snapshot: Record<string, number>;
}

export interface NettingRunDetail extends NettingRun {
  matches: OffsetMatch[];
}

export interface BankPacketMatchEntry {
  match_id: string;
  counterparty_name: string;
  payable_sme_name: string;
  payable_obligation_currency: string;
  payable_obligation_amount: number;
  receivable_sme_name: string;
  receivable_obligation_currency: string;
  receivable_obligation_amount: number;
  matched_amount_usd: number;
  confidence_tier: string | null;
  eligibility_flag: string | null;
  justification_text: string | null;
  ai_generated: boolean | null;
  settlement_window: [string, string];
}

export interface BankPacketResidualEntry {
  obligation_id: string;
  sme_name: string;
  counterparty_name: string;
  direction: string;
  currency: string;
  amount: number;
  total_usd: number;
  matched_usd: number;
  residual_usd: number;
  reason: "unmatched" | "partially_matched";
}

export interface BankPacket {
  id: string;
  netting_run_id: string;
  generated_at: string;
  gross_obligations_usd: number;
  total_matched_usd: number;
  net_settlement_usd: number;
  fx_friction_savings_usd: number;
  matches_count: number;
  auto_eligible_count: number;
  needs_review_count: number;
  body: {
    netting_run_id: string;
    executed_at: string;
    summary: Record<string, number>;
    matches: BankPacketMatchEntry[];
    flagged_for_review: {
      needs_review_matches: BankPacketMatchEntry[];
      residual_obligations: BankPacketResidualEntry[];
    };
  };
}

export const api = {
  smes: () => request<SME[]>("/smes"),
  counterparties: () => request<Counterparty[]>("/counterparties"),
  obligations: () => request<Obligation[]>("/obligations"),
  counterpartyScore: (id: string) => request<ReliabilityScore>(`/reliability-scores/counterparty/${id}`),
  nettingRuns: () => request<NettingRun[]>("/netting-runs"),
  nettingRun: (id: string) => request<NettingRunDetail>(`/netting-runs/${id}`),
  triggerNettingRun: () => request<NettingRunDetail>("/netting-runs", { method: "POST" }),
  packet: (runId: string) => request<BankPacket>(`/netting-runs/${runId}/packet`),
  apiBase: API_BASE,
};
