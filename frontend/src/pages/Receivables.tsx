import { useMemo, useState } from "react";
import { api, type Obligation, type ReliabilityScore } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { formatAmount, formatDate, tierBucket } from "../lib/format";
import { PageHeader } from "../components/PageHeader";
import { Card } from "../components/Card";
import { Pill } from "../components/Pill";
import { LoadingState, ErrorState } from "../components/AsyncState";
import tableStyles from "../components/Table.module.css";
import styles from "./Receivables.module.css";

type Direction = "all" | "receivable" | "payable";

export function Receivables() {
  const [filter, setFilter] = useState<Direction>("all");

  const { data, loading, error } = useAsync(async () => {
    const [obligations, counterparties, smes] = await Promise.all([
      api.obligations(),
      api.counterparties(),
      api.smes(),
    ]);
    const scores = await Promise.all(
      counterparties.map((cp) =>
        api.counterpartyScore(cp.id).catch(() => null as ReliabilityScore | null)
      )
    );
    const scoreByCounterparty = new Map(counterparties.map((cp, i) => [cp.id, scores[i]]));
    const counterpartyById = new Map(counterparties.map((cp) => [cp.id, cp]));
    const smeById = new Map(smes.map((s) => [s.id, s]));
    return { obligations, counterpartyById, smeById, scoreByCounterparty };
  });

  const rows = useMemo(() => {
    if (!data) return [];
    return data.obligations
      .filter((o) => filter === "all" || o.direction === filter)
      .sort((a, b) => a.expected_settlement_date.localeCompare(b.expected_settlement_date));
  }, [data, filter]);

  if (loading) return <LoadingState label="Loading obligations..." />;
  if (error || !data) return <ErrorState message={error ?? "unknown error"} />;

  return (
    <div>
      <PageHeader
        title="Receivables & payables"
        subtitle="Every obligation in the pool, with the buyer's pooled reliability tier alongside it."
      />

      <Card
        action={
          <div className={styles.filters}>
            {(["all", "receivable", "payable"] as Direction[]).map((d) => (
              <button
                key={d}
                className={`${styles.filterBtn} ${filter === d ? styles.filterBtnActive : ""}`}
                onClick={() => setFilter(d)}
              >
                {d === "all" ? "All" : d[0].toUpperCase() + d.slice(1) + "s"}
              </button>
            ))}
          </div>
        }
      >
        <div className="scroll-x">
          <table className={tableStyles.table}>
            <thead>
              <tr>
                <th>SME</th>
                <th>Buyer / counterparty</th>
                <th>Country</th>
                <th>Direction</th>
                <th className={tableStyles.num}>Amount</th>
                <th>Due</th>
                <th>Reliability</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((o: Obligation) => {
                const cp = data.counterpartyById.get(o.counterparty_id);
                const sme = data.smeById.get(o.sme_id);
                const score = data.scoreByCounterparty.get(o.counterparty_id);
                return (
                  <tr key={o.id}>
                    <td>{sme?.name ?? "—"}</td>
                    <td>{cp?.name ?? "—"}</td>
                    <td className={tableStyles.muted}>{cp?.country ?? "—"}</td>
                    <td className={tableStyles.muted}>{o.direction}</td>
                    <td className={tableStyles.num}>{formatAmount(o.amount, o.currency)}</td>
                    <td className={tableStyles.muted}>{formatDate(o.expected_settlement_date)}</td>
                    <td>
                      {score ? (
                        <Pill tone={tierBucket(score.tier)}>
                          Tier {score.tier} · {score.score.toFixed(0)}
                        </Pill>
                      ) : (
                        <span className={tableStyles.muted}>not scored</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
