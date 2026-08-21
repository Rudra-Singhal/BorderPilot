import { PageHeader } from "../components/PageHeader";
import { Card } from "../components/Card";
import { PhaseNotice } from "../components/PhaseNotice";
import { FinancialMetric } from "../components/FinancialMetric";
import { LiquidityOpportunityCard, type LiquidityOpportunity } from "../components/LiquidityOpportunityCard";

const MOCK: LiquidityOpportunity[] = [
  {
    id: "1",
    buyerName: "Schmidt Industrial GmbH",
    invoiceAmount: 50000,
    currency: "EUR",
    tier: "A",
    score: 94,
    advancePct: 90,
    feePct: 1.8,
    advanceAmountUsd: 45000,
    daysToMaturity: 45,
  },
  {
    id: "2",
    buyerName: "Coastal Foods Inc",
    invoiceAmount: 18500,
    currency: "USD",
    tier: "B",
    score: 82,
    advancePct: 80,
    feePct: 3.1,
    advanceAmountUsd: 14800,
    daysToMaturity: 28,
  },
];

export function Liquidity() {
  const total = MOCK.reduce((s, o) => s + o.advanceAmountUsd, 0);

  return (
    <div>
      <PageHeader
        title="Liquidity unlock"
        subtitle="How much money can I unlock today — the minimum recommended set to close the projected gap, not every eligible invoice."
      />
      <PhaseNotice
        phase="Phase 5 (Financing Orchestration)"
        note="Recommendation logic, the mock lender call, and live cash-forecast updates land in Phase 5. This preview shows the intended card shape and copy tone."
      />

      <Card>
        <FinancialMetric
          size="display"
          label="Recommended unlock (minimum set to close the gap)"
          value={`$${total.toLocaleString()}`}
          hint="From 2 of 9 eligible receivables — not everything, just enough."
        />
      </Card>

      <div style={{ height: 16 }} />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {MOCK.map((o) => (
          <LiquidityOpportunityCard key={o.id} opportunity={o} />
        ))}
      </div>
    </div>
  );
}
