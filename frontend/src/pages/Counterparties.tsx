import { PageHeader } from "../components/PageHeader";
import { PhaseNotice } from "../components/PhaseNotice";
import { CounterpartyCard, type CounterpartyProfileData } from "../components/CounterpartyCard";

const MOCK: CounterpartyProfileData[] = [
  {
    name: "Schmidt Industrial GmbH",
    country: "Germany",
    corridor: "Germany → India",
    currencies: ["EUR", "USD"],
    contributingSmeCount: 6,
    transactionCount: 94,
    onTimeCount: 88,
    moderatelyLateCount: 4,
    significantlyLateCount: 2,
    onTimePct: 93.6,
    medianDelayDays: 3,
    delayVariance: "low",
    trend: "stable",
    score: 94,
    tier: "A",
    thinData: false,
  },
  {
    name: "Northwind Traders",
    country: "United Kingdom",
    corridor: "UK → India",
    currencies: ["GBP"],
    contributingSmeCount: 2,
    transactionCount: 6,
    onTimeCount: 1,
    moderatelyLateCount: 3,
    significantlyLateCount: 2,
    onTimePct: 16.7,
    medianDelayDays: 12,
    delayVariance: "high",
    trend: "declining",
    score: 46,
    tier: "D",
    thinData: true,
  },
];

export function Counterparties() {
  return (
    <div>
      <PageHeader
        title="Counterparties"
        subtitle="Pooled buyer intelligence — the moat made visible. No single lender relationship sees this much history."
      />
      <PhaseNotice
        phase="Phase 4 (Core SME Experience)"
        note="These are illustrative profile cards. Live pooled data (already computed correctly in the backend since Phase 2) gets wired into a real list + detail route in Phase 4."
      />
      <div style={{ display: "grid", gap: 16 }}>
        {MOCK.map((c) => (
          <CounterpartyCard key={c.name} data={c} />
        ))}
      </div>
    </div>
  );
}
