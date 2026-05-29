"use client";

import { useCallback, useEffect, useState } from "react";
import { ShieldAlert } from "lucide-react";

import { DkBadge, DkButton, DkCard, DkCardContent } from "@/components/dk";
import {
  assessVendorRisk,
  getLatestRisk,
  type RiskAssessment,
  type RiskChange,
} from "@/lib/api";
import { riskLevelTone } from "@/lib/format";

const sevTone = { low: "success", medium: "warning", high: "danger" } as const;
const changeTone = {
  new: "danger",
  increased: "danger",
  decreased: "info",
  resolved: "success",
} as const;

export function RiskPanel({ vendorId }: { vendorId: string }) {
  const [risk, setRisk] = useState<RiskAssessment | null>(null);
  const [changes, setChanges] = useState<RiskChange[]>([]);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setRisk(await getLatestRisk(vendorId));
  }, [vendorId]);

  useEffect(() => {
    load();
  }, [load]);

  async function assess() {
    setBusy(true);
    try {
      const res = await assessVendorRisk(vendorId);
      setRisk(res.assessment);
      setChanges(res.changes);
    } finally {
      setBusy(false);
    }
  }

  return (
    <DkCard>
      <DkCardContent className="flex flex-col gap-3 py-5">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Risk assessment</span>
            {risk && (
              <DkBadge tone={riskLevelTone[risk.overall_level]}>
                {risk.overall_level} · {risk.overall_score.toFixed(0)}/100
              </DkBadge>
            )}
          </div>
          <DkButton variant="secondary" loading={busy} onClick={assess}>
            <ShieldAlert className="h-4 w-4" /> Assess (AI)
          </DkButton>
        </div>

        {changes.length > 0 && (
          <div className="flex flex-wrap gap-2 rounded-xl bg-[var(--dk-warning-bg)] px-3 py-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-warning)]">
              Changes since last check:
            </span>
            {changes.map((c) => (
              <DkBadge key={c.type} tone={changeTone[c.change]}>
                {c.type} {c.change}
              </DkBadge>
            ))}
          </div>
        )}

        {!risk ? (
          <p className="text-sm text-[var(--dk-fg-2)]">
            No risk assessment yet — run an AI assessment across 20 risk types.
          </p>
        ) : (
          <>
            {risk.summary && <p className="text-sm text-ink">{risk.summary}</p>}
            {risk.factors.length > 0 ? (
              <ul className="flex flex-col gap-2">
                {risk.factors.map((f, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-ink">
                    <DkBadge tone={sevTone[f.severity]}>{f.severity}</DkBadge>
                    <span>
                      <span className="font-medium">{f.type}:</span> {f.note}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-[var(--dk-fg-2)]">No material risks identified.</p>
            )}
          </>
        )}
      </DkCardContent>
    </DkCard>
  );
}
