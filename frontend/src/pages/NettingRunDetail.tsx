import { Link, useParams } from "react-router-dom";
import { api } from "../lib/api";
import { useAsync } from "../lib/useAsync";
import { formatDateTime } from "../lib/format";
import { PageHeader } from "../components/PageHeader";
import { StatTile } from "../components/StatTile";
import { Card } from "../components/Card";
import { Button } from "../components/Button";
import { MatchCard } from "../components/MatchCard";
import { LoadingState, ErrorState } from "../components/AsyncState";
import { IconArrowRight } from "../components/icons";
import styles from "./NettingRunDetail.module.css";

export function NettingRunDetail() {
  const { runId } = useParams<{ runId: string }>();
  const { data, loading, error } = useAsync(
    () => Promise.all([api.nettingRun(runId!), api.packet(runId!)]),
    [runId]
  );

  if (loading) return <LoadingState label="Loading netting run..." />;
  if (error || !data) return <ErrorState message={error ?? "unknown error"} />;

  const [run, packet] = data;
  const autoEligible = packet.body.matches.filter((m) => m.eligibility_flag !== "needs_review");
  const needsReview = packet.body.flagged_for_review.needs_review_matches;

  return (
    <div>
      <PageHeader
        title="Netting run"
        subtitle={`Executed ${formatDateTime(run.executed_at)} · settlement window ${run.window_days} days`}
        action={
          <Link to={`/netting-runs/${run.id}/packet`}>
            <Button variant="primary">
              View bank packet <IconArrowRight />
            </Button>
          </Link>
        }
      />

      <div className={styles.statGrid}>
        <StatTile label="Obligations considered" value={String(run.obligations_considered)} />
        <StatTile label="Matches created" value={String(run.matches_created)} />
        <StatTile label="Auto-eligible" value={String(autoEligible.length)} />
        <StatTile label="Needs review" value={String(needsReview.length)} />
      </div>

      <div className={styles.sections}>
        <Card title={`Auto-eligible matches (${autoEligible.length})`}>
          {autoEligible.length === 0 ? (
            <p className={styles.empty}>No tier A/B matches in this run.</p>
          ) : (
            autoEligible.map((m) => <MatchCard key={m.match_id} match={m} />)
          )}
        </Card>

        <Card title={`Needs review (${needsReview.length})`}>
          {needsReview.length === 0 ? (
            <p className={styles.empty}>No flagged matches in this run.</p>
          ) : (
            needsReview.map((m) => <MatchCard key={m.match_id} match={m} />)
          )}
        </Card>
      </div>
    </div>
  );
}
