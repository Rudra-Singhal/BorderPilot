import { PageHeader } from "../components/PageHeader";
import { Card } from "../components/Card";
import { PhaseNotice } from "../components/PhaseNotice";
import { ComplianceItem, type ComplianceItemData } from "../components/ComplianceItem";

const ITEMS: ComplianceItemData[] = [
  { label: "Commercial invoice on file", status: "verified" },
  { label: "Shipping documentation on file", status: "verified" },
  {
    label: "Form A2 declaration (outward remittance)",
    status: "pending",
    detail: "Required before disbursement can be marked complete.",
  },
  {
    label: "Netting eligibility — same-category current-account transaction",
    status: "illustrative",
    detail: "Actual eligibility depends on transaction type, counterparties, and applicable RBI/FEMA requirements.",
  },
  {
    label: "Export realization timeline within RBI guidance",
    status: "illustrative",
  },
];

export function Compliance() {
  return (
    <div>
      <PageHeader
        title="Compliance"
        subtitle="What do I need to complete this transaction — verified requirements kept clearly separate from illustrative demo logic."
      />
      <PhaseNotice
        phase="Phase 8 (AI + Compliance)"
        note="Per-transaction requirement tracking (ComplianceRequirement) lands in Phase 8. This preview fixes the verified/illustrative labeling discipline the real screen must follow."
      />
      <Card>
        {ITEMS.map((item) => (
          <ComplianceItem key={item.label} item={item} />
        ))}
      </Card>
    </div>
  );
}
