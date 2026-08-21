import { PageHeader } from "../components/PageHeader";
import { Card } from "../components/Card";
import { PhaseNotice } from "../components/PhaseNotice";
import { ExposureBar } from "../components/ExposureBar";
import { RiskBadge } from "../components/RiskBadge";
import tableStyles from "../components/Table.module.css";

const EXPOSURE = [
  { currency: "USD", usd: 68851 },
  { currency: "EUR", usd: 59457 },
  { currency: "GBP", usd: 45794 },
  { currency: "INR", usd: 324 },
];

const CORRIDORS = [
  { corridor: "Germany → India", tier: "A", score: 91, volatilityBand: "Low" },
  { corridor: "USA → India", tier: "B", score: 78, volatilityBand: "Low" },
  { corridor: "UK → India", tier: "C", score: 64, volatilityBand: "Moderate" },
  { corridor: "Vietnam → India", tier: "D", score: 52, volatilityBand: "Moderate" },
];

export function FxExposure() {
  const max = Math.max(...EXPOSURE.map((e) => e.usd));

  return (
    <div>
      <PageHeader
        title="FX & exposure"
        subtitle="Currency and corridor risk at a glance."
      />
      <PhaseNotice
        phase="Phase 3 (Core Financial Engines)"
        note="Currency exposure reuses the real Dashboard calculation. Corridor risk tiers below are illustrative until CurrencyExposure lands in Phase 2/3."
      />

      <Card title="Exposure by currency">
        {EXPOSURE.map((e) => (
          <ExposureBar key={e.currency} currency={e.currency} usdValue={e.usd} maxUsdValue={max} />
        ))}
      </Card>

      <div style={{ height: 16 }} />

      <Card title="Corridor risk">
        <table className={tableStyles.table}>
          <thead>
            <tr>
              <th>Corridor</th>
              <th>Illustrative tier</th>
              <th>FX volatility band</th>
            </tr>
          </thead>
          <tbody>
            {CORRIDORS.map((c) => (
              <tr key={c.corridor}>
                <td>{c.corridor}</td>
                <td>
                  <RiskBadge tier={c.tier} score={c.score} />
                </td>
                <td className={tableStyles.muted}>{c.volatilityBand}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
