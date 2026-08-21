import { useParams } from "react-router-dom";
import { api } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { formatAmount, formatDateTime, formatUsd } from "../lib/format";
import { PageHeader } from "../components/PageHeader";
import { StatTile } from "../components/StatTile";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { MatchCard } from "../components/MatchCard";
import { LoadingState, ErrorState } from "../components/AsyncState";
import { IconDownload } from "../components/icons";
import tableStyles from "../components/Table.module.css";
import styles from "./PacketView.module.css";

export function PacketView() {
  const { runId } = useParams<{ runId: string }>();
  const { data: packet, loading, error } = useAsync(() => api.packet(runId!), [runId]);

  if (loading) return <LoadingState label="Assembling bank packet..." />;
  if (error || !packet) return <ErrorState message={error ?? "unknown error"} />;

  function downloadJson() {
    const blob = new Blob([JSON.stringify(packet, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `borderpilot-packet-${runId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const residuals = packet.body.flagged_for_review.residual_obligations;

  return (
    <div>
      <PageHeader
        title="Bank packet"
        subtitle={`Netting run ${packet.netting_run_id.slice(0, 8)} · generated ${formatDateTime(packet.generated_at)}`}
        action={
          <div className={styles.actions}>
            <Button onClick={downloadJson}>
              <IconDownload /> Download JSON
            </Button>
            <a href={`${api.apiBase}/netting-runs/${runId}/packet.html`} target="_blank" rel="noreferrer">
              <Button variant="primary">Open print-ready view</Button>
            </a>
          </div>
        }
      />

      <div className={styles.statGrid}>
        <StatTile label="Gross obligations" value={formatUsd(packet.gross_obligations_usd)} />
        <StatTile label="Total matched" value={formatUsd(packet.total_matched_usd)} />
        <StatTile label="Net settlement required" value={formatUsd(packet.net_settlement_usd)} />
        <StatTile label="Est. FX / friction saved" value={formatUsd(packet.fx_friction_savings_usd)} />
      </div>

      <Card title={`Proposed matches (${packet.matches_count})`}>
        {packet.body.matches.map((m) => (
          <MatchCard key={m.match_id} match={m} />
        ))}
      </Card>

      <div style={{ height: 16 }} />

      <Card title={`Flagged for manual review — residual obligations (${residuals.length})`}>
        {residuals.length === 0 ? (
          <p className={styles.empty}>Nothing left over — every obligation in this run was fully matched.</p>
        ) : (
          <div className="scroll-x">
            <table className={tableStyles.table}>
              <thead>
                <tr>
                  <th>SME</th>
                  <th>Counterparty</th>
                  <th>Direction</th>
                  <th className={tableStyles.num}>Original amount</th>
                  <th className={tableStyles.num}>Residual (USD)</th>
                  <th>Reason</th>
                </tr>
              </thead>
              <tbody>
                {residuals.map((r) => (
                  <tr key={r.obligation_id}>
                    <td>{r.sme_name}</td>
                    <td>{r.counterparty_name}</td>
                    <td className={tableStyles.muted}>{r.direction}</td>
                    <td className={tableStyles.num}>{formatAmount(r.amount, r.currency)}</td>
                    <td className={tableStyles.num}>{formatUsd(r.residual_usd)}</td>
                    <td className={tableStyles.muted}>{r.reason.replace("_", " ")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
