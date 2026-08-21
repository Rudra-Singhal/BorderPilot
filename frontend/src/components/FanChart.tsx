import { useMemo } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export interface FanChartPoint {
  date: string;
  base: number;
  low95: number;
  high95: number;
  low80: number;
  high80: number;
}

/** Renders the 95% band, then the 80% band on top, then the base-case line --
 * the uncertainty-visualization primitive for the Digital Twin (30/60/90 forecast).
 * Uses the standard Recharts stacked-area technique: a transparent "floor" area up to
 * the band's low value, then a visible area for (high - low) stacked on top of it. */
export function FanChart({ data, height = 260 }: { data: FanChartPoint[]; height?: number }) {
  const chartData = useMemo(
    () =>
      data.map((d) => ({
        ...d,
        band95: d.high95 - d.low95,
        band80: d.high80 - d.low80,
      })),
    [data]
  );

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={chartData} margin={{ top: 8, right: 12, bottom: 0, left: 0 }}>
        <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
        <XAxis
          dataKey="date"
          tick={{ fill: "var(--chart-axis)", fontSize: 11, fontFamily: "var(--font-mono)" }}
          axisLine={{ stroke: "var(--border)" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "var(--chart-axis)", fontSize: 11, fontFamily: "var(--font-mono)" }}
          axisLine={false}
          tickLine={false}
          width={56}
        />
        <ReferenceLine y={0} stroke="var(--critical)" strokeDasharray="3 3" />
        <Tooltip
          contentStyle={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
            fontFamily: "var(--font-mono)",
          }}
        />
        <Area dataKey="low95" stackId="95" stroke="none" fill="transparent" isAnimationActive={false} />
        <Area
          dataKey="band95"
          stackId="95"
          stroke="none"
          fill="var(--chart-band-95)"
          isAnimationActive={false}
        />
        <Area dataKey="low80" stackId="80" stroke="none" fill="transparent" isAnimationActive={false} />
        <Area
          dataKey="band80"
          stackId="80"
          stroke="none"
          fill="var(--chart-band-80)"
          isAnimationActive={false}
        />
        <Line type="monotone" dataKey="base" stroke="var(--chart-line)" strokeWidth={2.5} dot={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
