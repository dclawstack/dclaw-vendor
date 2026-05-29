"use client";

import { useCallback, useEffect, useState } from "react";
import { Leaf } from "lucide-react";

import { DkBadge, DkButton, DkCard, DkCardContent, DkProgress } from "@/components/dk";
import {
  getLatestSustainability,
  scoreVendorSustainability,
  type SustainabilityScore,
} from "@/lib/api";

function tone(v: number): "success" | "warning" | "danger" {
  if (v >= 75) return "success";
  if (v >= 50) return "warning";
  return "danger";
}

export function SustainabilityPanel({ vendorId }: { vendorId: string }) {
  const [score, setScore] = useState<SustainabilityScore | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setScore(await getLatestSustainability(vendorId));
  }, [vendorId]);

  useEffect(() => {
    load();
  }, [load]);

  async function run() {
    setBusy(true);
    try {
      setScore(await scoreVendorSustainability(vendorId));
    } finally {
      setBusy(false);
    }
  }

  const dims: [keyof SustainabilityScore, string][] = [
    ["environmental_score", "Environmental"],
    ["social_score", "Social"],
    ["governance_score", "Governance"],
  ];

  return (
    <DkCard>
      <DkCardContent className="flex flex-col gap-3 py-5">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Leaf className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Sustainability (ESG)</span>
            {score && (
              <DkBadge tone={tone(score.overall_score)}>
                {score.overall_score.toFixed(0)} ESG · {score.carbon_footprint.toFixed(0)}t CO₂e
              </DkBadge>
            )}
          </div>
          <DkButton variant="secondary" loading={busy} onClick={run}>
            <Leaf className="h-4 w-4" /> Score (AI)
          </DkButton>
        </div>

        {!score ? (
          <p className="text-sm text-[var(--dk-fg-2)]">
            No ESG score yet — estimate environmental/social/governance scores and carbon footprint.
          </p>
        ) : (
          <>
            {score.summary && <p className="text-sm text-ink">{score.summary}</p>}
            <div className="flex flex-col gap-2.5">
              {dims.map(([key, label]) => {
                const v = score[key] as number;
                return (
                  <div key={key} className="flex items-center gap-3">
                    <span className="w-28 text-sm text-[var(--dk-fg-2)]">{label}</span>
                    <DkProgress value={v} tone={tone(v)} showLabel className="flex-1" />
                  </div>
                );
              })}
            </div>
            {score.targets && score.targets.length > 0 && (
              <div className="flex flex-col gap-1">
                <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
                  Targets
                </span>
                {score.targets.map((t, i) => (
                  <p key={i} className="text-sm text-[var(--dk-fg-2)]">
                    {t.target} <span className="text-[var(--dk-fg-muted)]">· {t.by}</span>
                  </p>
                ))}
              </div>
            )}
          </>
        )}
      </DkCardContent>
    </DkCard>
  );
}
