import { PageHeader } from "../components/PageHeader";
import { Card } from "../components/Card";
import { PhaseNotice } from "../components/PhaseNotice";
import { InsightCard } from "../components/InsightCard";

const EXAMPLE_QA = [
  {
    q: "Why is Schmidt rated Tier A?",
    a: "Schmidt Industrial GmbH has 94 observed transactions pooled across 6 SMEs on the platform, with a 93.6% on-time payment rate and a median delay of 3 days — this supports a Tier A reliability rating.",
  },
  {
    q: "How much can I unlock this week?",
    a: "₹41.2L of receivables currently appear eligible. The strongest opportunity is Schmidt Industrial GmbH, with an estimated ₹35.8L advance at 90% and a 1.8% fee.",
  },
  {
    q: "What happens if the buyer pays 15 days late?",
    a: "Your 60-day projected cash position shifts from ₹24L–₹31L to ₹18L–₹27L (80% confidence band), and the liquidity gap moves 9 days earlier.",
  },
];

export function Assistant() {
  return (
    <div>
      <PageHeader
        title="Assistant"
        subtitle="Contextual AI copilot, grounded in real application state — never a generic chatbot."
      />
      <PhaseNotice
        phase="Phase 8 (AI + Compliance)"
        note="Reuses the constrained-prompt Bedrock pattern from services/explain.py. Below are illustrative example exchanges showing the required answer shape: result, numbers, reasoning, source link."
      />
      <Card title="Example exchanges">
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {EXAMPLE_QA.map((qa) => (
            <div key={qa.q}>
              <div style={{ fontWeight: 700, fontSize: 13.5, marginBottom: 8 }}>{qa.q}</div>
              <InsightCard text={qa.a} sourceLabel="source" sourceHref="#" />
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
