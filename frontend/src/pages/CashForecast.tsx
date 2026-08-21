import { useMemo, useState } from "react";
import { PageHeader } from "../components/PageHeader";
import { Card } from "../components/Card";
import { PhaseNotice } from "../components/PhaseNotice";
import { FanChart, type FanChartPoint } from "../components/FanChart";
import { ScenarioSlider } from "../components/ScenarioSlider";
import { FinancialMetric } from "../components/FinancialMetric";

function buildMockForecast(delayDays: number): FanChartPoint[] {
  const days = [0, 15, 30, 45, 60, 75, 90];
  const base = 6240000;
  const dailyBurn = 42000;
  const delayDrag = delayDays * 1800;
  return days.map((d) => {
    const projected = base - dailyBurn * d - delayDrag * (d / 30);
    const spread80 = 180000 + d * 900;
    const spread95 = 320000 + d * 1600;
    return {
      date: d === 0 ? "Today" : `+${d}d`,
      base: Math.round(projected),
      low80: Math.round(projected - spread80),
      high80: Math.round(projected + spread80),
      low95: Math.round(projected - spread95),
      high95: Math.round(projected + spread95),
    };
  });
}

export function CashForecast() {
  const [delayDays, setDelayDays] = useState(15);
  const data = useMemo(() => buildMockForecast(delayDays), [delayDays]);
  const day60 = data.find((d) => d.date === "+60d")!;
  const gapDay = data.find((d) => d.base < 0);

  return (
    <div>
      <PageHeader
        title="Cash & forecast"
        subtitle="What happens to my cash next — base case plus uncertainty from payment delay and FX."
      />
      <PhaseNotice
        phase="Phase 7 (Digital Twin)"
        note="Chart and slider are wired to illustrative mock data. Live Monte Carlo simulation and real liquidity-gap detection land in Phase 7."
      />

      <Card>
        <FanChart data={data} />
      </Card>

      <div style={{ height: 16 }} />

      <Card title="What-if: buyer payment delay">
        <ScenarioSlider
          label="Buyer pays this many days late"
          min={0}
          max={45}
          value={delayDays}
          onChange={setDelayDays}
          formatValue={(v) => `${v}d`}
        />
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 20 }}>
          <FinancialMetric
            label="60-day projected cash (80% confidence)"
            value={`₹${(day60.low80 / 100000).toFixed(1)}L–₹${(day60.high80 / 100000).toFixed(1)}L`}
          />
          <FinancialMetric
            label="Liquidity gap"
            value={gapDay ? gapDay.date : "None projected"}
            trend={gapDay ? "down" : "flat"}
            trendLabel={gapDay ? "within 90 days" : undefined}
          />
        </div>
      </Card>
    </div>
  );
}
