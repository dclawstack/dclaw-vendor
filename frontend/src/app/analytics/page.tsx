"use client";

import { useCallback, useEffect, useState } from "react";
import { Cable, Lightbulb, RefreshCw, TrendingDown, Users } from "lucide-react";

import {
  DkBadge,
  DkButton,
  DkCard,
  DkCardContent,
  DkPageHeader,
  DkProgress,
  DkTable,
  DkTableBody,
  DkTableCell,
  DkTableHead,
  DkTableHeader,
  DkTableRow,
} from "@/components/dk";
import {
  getDiversityReport,
  getIntegrationStatus,
  getReconciliation,
  getSpendInsights,
  getSpendSummary,
  syncErp,
  type DiversityReport,
  type IntegrationStatus,
  type ReconciliationResult,
  type SpendInsights,
  type SpendSummary,
} from "@/lib/api";
import { currency } from "@/lib/format";

const reconTone = {
  matched: "success",
  over_billed: "danger",
  under_billed: "warning",
  unmatched: "neutral",
} as const;

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<SpendSummary | null>(null);
  const [insights, setInsights] = useState<SpendInsights | null>(null);
  const [insightBusy, setInsightBusy] = useState(false);

  const [status, setStatus] = useState<IntegrationStatus | null>(null);
  const [recon, setRecon] = useState<ReconciliationResult | null>(null);
  const [syncBusy, setSyncBusy] = useState(false);
  const [diversity, setDiversity] = useState<DiversityReport | null>(null);

  const load = useCallback(async () => {
    const [s, st, rc, dv] = await Promise.all([
      getSpendSummary(),
      getIntegrationStatus(),
      getReconciliation(),
      getDiversityReport(),
    ]);
    setSummary(s);
    setStatus(st);
    setRecon(rc);
    setDiversity(dv);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function runInsights() {
    setInsightBusy(true);
    try {
      setInsights(await getSpendInsights());
    } finally {
      setInsightBusy(false);
    }
  }

  async function runSync() {
    setSyncBusy(true);
    try {
      await syncErp();
      await load();
    } finally {
      setSyncBusy(false);
    }
  }

  const maxCat = Math.max(1, ...(summary?.by_category.map((b) => b.spend) ?? []));

  return (
    <div className="flex flex-col gap-6">
      <DkPageHeader
        eyebrow="Procurement"
        title="Spend Analytics & Integration"
        description="Where the money goes, AI-found savings, and ERP sync / invoice reconciliation."
      />

      {/* Spend summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Stat label="Total spend" value={summary ? currency(summary.total_spend) : "—"} />
        <Stat label="Purchase orders" value={summary ? String(summary.po_count) : "—"} />
        <Stat
          label="Categories"
          value={summary ? String(summary.by_category.length) : "—"}
        />
      </div>

      <DkCard>
        <DkCardContent className="flex flex-col gap-3 py-5">
          <span className="font-display font-semibold text-ink">Spend by category</span>
          {summary && summary.by_category.length > 0 ? (
            <div className="flex flex-col gap-2.5">
              {summary.by_category.map((b) => (
                <div key={b.key} className="flex items-center gap-3">
                  <span className="w-32 truncate text-sm text-[var(--dk-fg-2)]">{b.key}</span>
                  <DkProgress value={(b.spend / maxCat) * 100} className="flex-1" />
                  <span className="w-24 text-right text-sm tabular-nums text-ink">
                    {currency(b.spend)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[var(--dk-fg-2)]">No spend recorded yet.</p>
          )}
        </DkCardContent>
      </DkCard>

      {/* Diversity report */}
      {diversity && (
        <DkCard>
          <DkCardContent className="flex flex-col gap-3 py-5">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-brand" />
              <span className="font-display font-semibold text-ink">Supplier diversity</span>
              <DkBadge tone="brand">{diversity.diverse_spend_pct.toFixed(0)}% diverse spend</DkBadge>
            </div>
            <p className="text-sm text-[var(--dk-fg-2)]">
              {currency(diversity.diverse_spend)} of {currency(diversity.total_spend)} ·{" "}
              {diversity.diverse_vendor_count}/{diversity.vendor_count} vendors diverse-owned ·{" "}
              {diversity.certified_count} certified
            </p>
            {diversity.by_category.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {diversity.by_category.map((c) => (
                  <DkBadge key={c.category} tone="neutral">
                    {c.category.replace(/_/g, " ")}: {currency(c.spend)} ({c.vendor_count})
                  </DkBadge>
                ))}
              </div>
            )}
          </DkCardContent>
        </DkCard>
      )}

      {/* AI savings */}
      <DkCard>
        <DkCardContent className="flex flex-col gap-3 py-5">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4 text-brand" />
              <span className="font-display font-semibold text-ink">AI savings opportunities</span>
              {insights && (
                <DkBadge tone="success">
                  target {currency(insights.target_savings)}
                </DkBadge>
              )}
            </div>
            <DkButton variant="secondary" loading={insightBusy} onClick={runInsights}>
              <TrendingDown className="h-4 w-4" /> Find savings
            </DkButton>
          </div>
          {!insights ? (
            <p className="text-sm text-[var(--dk-fg-2)]">
              Run AI analysis to surface ~10% savings and vendor-consolidation plays.
            </p>
          ) : (
            <>
              <p className="text-sm text-ink">{insights.summary}</p>
              <ul className="flex flex-col gap-2">
                {insights.opportunities.map((o, i) => (
                  <li key={i} className="flex items-center justify-between gap-3 text-sm">
                    <span className="text-ink">
                      <span className="font-medium">{o.title}</span>
                      {o.category ? ` · ${o.category}` : ""} — {o.rationale}
                    </span>
                    <DkBadge tone="success">{currency(o.estimated_savings)}</DkBadge>
                  </li>
                ))}
              </ul>
              {insights.consolidation.length > 0 && (
                <div className="flex flex-col gap-1.5">
                  <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
                    Consolidation
                  </span>
                  {insights.consolidation.map((c, i) => (
                    <p key={i} className="text-sm text-[var(--dk-fg-2)]">
                      <span className="font-medium text-ink">{c.category}:</span>{" "}
                      {c.vendors.join(", ")} — {c.rationale}
                    </p>
                  ))}
                </div>
              )}
            </>
          )}
        </DkCardContent>
      </DkCard>

      {/* ERP integration */}
      <DkCard>
        <DkCardContent className="flex flex-col gap-3 py-5">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Cable className="h-4 w-4 text-brand" />
              <span className="font-display font-semibold text-ink">
                Procurement integration
              </span>
              {status && (
                <DkBadge tone={status.connected ? "success" : "neutral"}>
                  {status.backend}
                  {status.connected ? " · connected" : ""}
                </DkBadge>
              )}
            </div>
            <DkButton variant="secondary" loading={syncBusy} onClick={runSync}>
              <RefreshCw className="h-4 w-4" /> Sync ERP
            </DkButton>
          </div>

          {recon && recon.rows.length > 0 ? (
            <>
              <div className="flex gap-2">
                <DkBadge tone="success">{recon.matched} matched</DkBadge>
                <DkBadge tone="danger">{recon.discrepancies} discrepancies</DkBadge>
                <DkBadge tone="neutral">{recon.unmatched} unmatched</DkBadge>
              </div>
              <div className="rounded-2xl border border-[var(--dk-border)]">
                <DkTable>
                  <DkTableHeader>
                    <DkTableRow>
                      <DkTableHead>PO ref</DkTableHead>
                      <DkTableHead>Invoice</DkTableHead>
                      <DkTableHead>Invoice amt</DkTableHead>
                      <DkTableHead>PO total</DkTableHead>
                      <DkTableHead>Variance</DkTableHead>
                      <DkTableHead>Status</DkTableHead>
                    </DkTableRow>
                  </DkTableHeader>
                  <DkTableBody>
                    {recon.rows.map((r) => (
                      <DkTableRow key={r.invoice_number}>
                        <DkTableCell>{r.external_ref}</DkTableCell>
                        <DkTableCell>{r.invoice_number}</DkTableCell>
                        <DkTableCell>{currency(r.invoice_amount)}</DkTableCell>
                        <DkTableCell>{r.po_total != null ? currency(r.po_total) : "—"}</DkTableCell>
                        <DkTableCell>{r.variance != null ? currency(r.variance) : "—"}</DkTableCell>
                        <DkTableCell>
                          <DkBadge tone={reconTone[r.status]}>{r.status.replace("_", " ")}</DkBadge>
                        </DkTableCell>
                      </DkTableRow>
                    ))}
                  </DkTableBody>
                </DkTable>
              </div>
            </>
          ) : (
            <p className="text-sm text-[var(--dk-fg-2)]">
              Sync the ERP to pull purchase orders and reconcile invoices against them.
            </p>
          )}
        </DkCardContent>
      </DkCard>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <DkCard>
      <DkCardContent className="flex flex-col gap-1 py-5">
        <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
          {label}
        </span>
        <span className="font-display text-2xl font-bold text-ink">{value}</span>
      </DkCardContent>
    </DkCard>
  );
}
