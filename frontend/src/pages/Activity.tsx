import { PageHeader } from "../components/PageHeader";
import { Card } from "../components/Card";
import { PhaseNotice } from "../components/PhaseNotice";
import { ActivityRow, type ActivityEvent } from "../components/ActivityRow";

const EVENTS: ActivityEvent[] = [
  { id: "1", timestamp: "2026-08-22 09:14", actor: "system", eventType: "score_computed", description: "Reliability score recomputed for Schmidt Industrial GmbH — 94/100, Tier A" },
  { id: "2", timestamp: "2026-08-22 09:15", actor: "system", eventType: "netting_match", description: "Matched Kestrel Electronics payable against Nordic Gears + Baltic Steel receivables via Northwind Traders" },
  { id: "3", timestamp: "2026-08-22 09:20", actor: "user", eventType: "financing_offer", description: "Offer generated for Acme Textiles — 90% advance, 1.8% fee" },
  { id: "4", timestamp: "2026-08-22 09:21", actor: "user", eventType: "lender_request", description: "Risk packet submitted to mock NBFC service" },
];

export function Activity() {
  return (
    <div>
      <PageHeader
        title="Activity"
        subtitle="Append-only audit trail — every score, match, offer, and lender decision, for trust and technical credibility."
      />
      <PhaseNotice
        phase="Phase 8 (AI + Compliance)"
        note="AuditEvent table and a real event feed land in Phase 8. Underlying data already exists (versioned ReliabilityScore, timestamped NettingRun/OffsetMatch) — this screen just needs to present it."
      />
      <Card>
        {EVENTS.map((e) => (
          <ActivityRow key={e.id} event={e} />
        ))}
      </Card>
    </div>
  );
}
