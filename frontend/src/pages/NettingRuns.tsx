import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { formatDateTime } from "../lib/format";
import { PageHeader } from "../components/PageHeader";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { LoadingState, ErrorState } from "../components/AsyncState";
import tableStyles from "../components/Table.module.css";

export function NettingRuns() {
  const { data: runs, loading, error, refetch } = useAsync(() => api.nettingRuns());
  const [triggering, setTriggering] = useState(false);
  const navigate = useNavigate();

  async function handleTrigger() {
    setTriggering(true);
    try {
      const run = await api.triggerNettingRun();
      refetch();
      navigate(`/netting-runs/${run.id}`);
    } catch (err) {
      alert(`Netting run failed: ${(err as Error).message}`);
    } finally {
      setTriggering(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Netting runs"
        subtitle="Each run groups open obligations by settlement window and pooled counterparty, then nets what it can."
        action={
          <Button variant="primary" onClick={handleTrigger} disabled={triggering}>
            {triggering ? "Running..." : "Trigger netting run"}
          </Button>
        }
      />

      <Card>
        {loading && <LoadingState label="Loading runs..." />}
        {error && <ErrorState message={error} />}
        {runs && runs.length === 0 && <p>No netting runs yet — trigger the first one above.</p>}
        {runs && runs.length > 0 && (
          <div className="scroll-x">
            <table className={tableStyles.table}>
              <thead>
                <tr>
                  <th>Executed</th>
                  <th className={tableStyles.num}>Obligations considered</th>
                  <th className={tableStyles.num}>Matches created</th>
                  <th className={tableStyles.num}>Window (days)</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr key={run.id}>
                    <td>{formatDateTime(run.executed_at)}</td>
                    <td className={tableStyles.num}>{run.obligations_considered}</td>
                    <td className={tableStyles.num}>{run.matches_created}</td>
                    <td className={tableStyles.num}>{run.window_days}</td>
                    <td>
                      <Link to={`/netting-runs/${run.id}`}>View</Link>
                    </td>
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
