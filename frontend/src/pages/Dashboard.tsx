import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { toUsd } from "../lib/fx";
import { formatDateTime, formatUsd } from "../lib/format";
import { PageHeader } from "../components/PageHeader";
import { StatTile } from "../components/StatTile";
import { Card } from "../components/Card";
import { ExposureBar } from "../components/ExposureBar";
import { LoadingState, ErrorState } from "../components/AsyncState";
import { IconArrowRight } from "../components/icons";
import styles from "./Dashboard.module.css";

export function Dashboard() {
  const { data, loading, error } = useAsync(() =>
    Promise.all([api.smes(), api.counterparties(), api.obligations(), api.nettingRuns()])
  );

  if (loading) return <LoadingState label="Loading dashboard..." />;
  if (error || !data) return <ErrorState message={error ?? "unknown error"} />;

  const [smes, counterparties, obligations, nettingRuns] = data;

  const grossUsd = obligations.reduce((sum, o) => sum + toUsd(o.amount, o.currency), 0);
  const openCount = obligations.filter((o) => o.status === "open").length;
  const nettedCount = obligations.filter((o) => o.status === "netted").length;

  const byCurrency = new Map<string, number>();
  for (const o of obligations) {
    byCurrency.set(o.currency, (byCurrency.get(o.currency) ?? 0) + toUsd(o.amount, o.currency));
  }
  const exposure = [...byCurrency.entries()].sort((a, b) => b[1] - a[1]);
  const maxExposure = exposure[0]?.[1] ?? 0;

  const latestRun = nettingRuns[0];

  return (
    <div>
      <PageHeader
        title="Executive dashboard"
        subtitle="Pooled cash position, receivables and payables, and FX exposure across every linked SME."
      />

      <div className={styles.statGrid}>
        <StatTile label="SMEs onboarded" value={String(smes.length)} />
        <StatTile label="Pooled counterparties" value={String(counterparties.length)} />
        <StatTile label="Gross obligations" value={formatUsd(grossUsd)} hint="USD-equivalent, static FX table" />
        <StatTile label="Open / netted" value={`${openCount} / ${nettedCount}`} hint="obligation status" />
      </div>

      <div className={styles.twoCol}>
        <Card title="FX exposure by currency">
          <div>
            {exposure.map(([currency, value]) => (
              <ExposureBar key={currency} currency={currency} usdValue={value} maxUsdValue={maxExposure} />
            ))}
          </div>
        </Card>

        <Card
          title="Recent netting runs"
          action={
            <Link to="/netting-runs" className={styles.viewAll}>
              View all <IconArrowRight />
            </Link>
          }
        >
          {nettingRuns.length === 0 ? (
            <p className={styles.empty}>No netting runs yet.</p>
          ) : (
            <ul className={styles.runList}>
              {nettingRuns.slice(0, 5).map((run) => (
                <li key={run.id}>
                  <Link to={`/netting-runs/${run.id}`} className={styles.runRow}>
                    <span className={styles.runDate}>{formatDateTime(run.executed_at)}</span>
                    <span className={styles.runMeta}>
                      {run.matches_created} match{run.matches_created === 1 ? "" : "es"} ·{" "}
                      {run.obligations_considered} obligations considered
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}
          {latestRun && (
            <Link to={`/netting-runs/${latestRun.id}/packet`} className={styles.packetLink}>
              View latest bank packet <IconArrowRight />
            </Link>
          )}
        </Card>
      </div>
    </div>
  );
}
