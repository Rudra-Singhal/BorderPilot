"""Server-rendered, print-friendly HTML view of a BankPacket -- the "PDF-style"
minimal deliverable format called for in place of a real bank API integration.
Self-contained (no external assets) so it can be saved or printed offline.
"""

from app.models import BankPacket

_STYLE = """
  * { box-sizing: border-box; }
  body {
    font-family: "IBM Plex Sans", "Segoe UI", -apple-system, sans-serif;
    color: #14181B;
    background: #F3F5F1;
    margin: 0;
    padding: 40px 24px 80px;
    line-height: 1.5;
  }
  .sheet { max-width: 880px; margin: 0 auto; background: #FBFCFA; border: 1px solid #D9E0DA;
           border-radius: 10px; padding: 40px 44px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  .meta { color: #5B655F; font-size: 13px; margin-bottom: 28px; font-family: ui-monospace, monospace; }
  h2 { font-size: 14px; text-transform: uppercase; letter-spacing: 0.06em; color: #5B655F;
       border-bottom: 1px solid #D9E0DA; padding-bottom: 8px; margin: 32px 0 14px; }
  table { width: 100%; border-collapse: collapse; font-size: 13.5px; margin-bottom: 6px; }
  th, td { text-align: left; padding: 7px 10px 7px 0; border-bottom: 1px solid #E4E9E5; }
  th { color: #5B655F; font-weight: 600; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.03em; }
  td.num, th.num { font-variant-numeric: tabular-nums; text-align: right; }
  .summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #D9E0DA;
                  border: 1px solid #D9E0DA; border-radius: 8px; overflow: hidden; }
  .summary-cell { background: #FBFCFA; padding: 14px 16px; }
  .summary-cell .val { font-size: 19px; font-weight: 600; font-variant-numeric: tabular-nums; }
  .summary-cell .lbl { font-size: 11px; color: #5B655F; text-transform: uppercase; letter-spacing: 0.05em; }
  .pill { display: inline-block; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 999px; }
  .pill-auto { background: #DCEAE4; color: #165545; }
  .pill-review { background: #F1E3CE; color: #A9701F; }
  .justification { color: #5B655F; font-size: 12.5px; margin-top: 2px; }
  .flagged-section { background: #F1E3CE22; border: 1px solid #E7D3AC; border-radius: 8px; padding: 4px 16px; }
  @media print { body { background: #fff; } .sheet { border: none; padding: 0; } }
"""


def render_packet_html(packet: BankPacket) -> str:
    body = packet.body
    summary = body["summary"]
    matches = body["matches"]
    flagged = body["flagged_for_review"]

    def match_row(m: dict) -> str:
        pill_cls = "pill-auto" if m["eligibility_flag"] != "needs_review" else "pill-review"
        pill_label = "Auto-eligible" if m["eligibility_flag"] != "needs_review" else "Needs review"
        return f"""
        <tr>
          <td>{m['payable_sme_name']} &rarr; {m['counterparty_name']} &rarr; {m['receivable_sme_name']}
            <div class="justification">{m['justification_text']}</div>
          </td>
          <td class="num">{m['matched_amount_usd']:,.2f}</td>
          <td>{m['confidence_tier']}</td>
          <td><span class="pill {pill_cls}">{pill_label}</span></td>
        </tr>"""

    def residual_row(r: dict) -> str:
        return f"""
        <tr>
          <td>{r['sme_name']} &middot; {r['counterparty_name']} ({r['direction']})</td>
          <td class="num">{r['amount']:,.2f} {r['currency']}</td>
          <td class="num">{r['residual_usd']:,.2f}</td>
          <td>{r['reason'].replace('_', ' ')}</td>
        </tr>"""

    matches_html = "".join(match_row(m) for m in matches) or "<tr><td colspan='4'>No matches in this run.</td></tr>"
    residuals_html = "".join(residual_row(r) for r in flagged["residual_obligations"]) or (
        "<tr><td colspan='4'>No residual obligations.</td></tr>"
    )

    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>BorderPilot Netting Packet</title>
<style>{_STYLE}</style></head>
<body>
<div class="sheet">
  <h1>BorderPilot &mdash; Netting Packet</h1>
  <div class="meta">Netting run {body['netting_run_id']} &middot; executed {body['executed_at']} &middot; generated {packet.generated_at}</div>

  <div class="summary-grid">
    <div class="summary-cell"><div class="val">${summary['gross_obligations_usd']:,.2f}</div><div class="lbl">Gross obligations</div></div>
    <div class="summary-cell"><div class="val">${summary['total_matched_usd']:,.2f}</div><div class="lbl">Total matched</div></div>
    <div class="summary-cell"><div class="val">${summary['net_settlement_usd']:,.2f}</div><div class="lbl">Net settlement required</div></div>
    <div class="summary-cell"><div class="val">${summary['fx_friction_savings_usd']:,.2f}</div><div class="lbl">Est. FX/friction saved</div></div>
  </div>

  <h2>Proposed matches ({summary['matches_count']})</h2>
  <table>
    <thead><tr><th>Route</th><th class="num">Amount (USD)</th><th>Tier</th><th>Eligibility</th></tr></thead>
    <tbody>{matches_html}</tbody>
  </table>

  <h2>Flagged for manual review</h2>
  <div class="flagged-section">
    <p style="font-size:13px;color:#5B655F;">
      {summary['needs_review_count']} match(es) below tier B, plus {summary['flagged_residual_count']} obligation(s)
      with unmatched or partial residual amounts.
    </p>
    <table>
      <thead><tr><th>Obligation</th><th class="num">Original amount</th><th class="num">Residual (USD)</th><th>Reason</th></tr></thead>
      <tbody>{residuals_html}</tbody>
    </table>
  </div>
</div>
</body></html>"""
