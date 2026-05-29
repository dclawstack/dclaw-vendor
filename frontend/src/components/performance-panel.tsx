"use client";

import { useCallback, useEffect, useState } from "react";
import { Gauge, TrendingUp } from "lucide-react";

import { DkBadge, DkButton, DkCard, DkCardContent, DkProgress } from "@/components/dk";
import {
  getBenchmark,
  getLatestScore,
  getScoreTrend,
  scoreVendorPerformance,
  type BenchmarkResult,
  type PerformanceScore,
  type TrendPoint,
} from "@/lib/api";

function tone(v: number): "success" | "warning" | "danger" {
  if (v >= 75) return "success";
  if (v >= 50) return "warning";
  return "danger";
}

const DIMENSIONS: [keyof PerformanceScore, string][] = [
  ["quality_score", "Quality"],
  ["delivery_score", "Delivery"],
  ["cost_score", "Cost"],
  ["compliance_score", "Compliance"],
];

export function PerformancePanel({ vendorId }: { vendorId: string }) {
  const [latest, setLatest] = useState<PerformanceScore | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [benchmark, setBenchmark] = useState<BenchmarkResult | null>(null);
  const [scoring, setScoring] = useState(false);

  const load = useCallback(async () => {
    const [l, t, b] = await Promise.all([
      getLatestScore(vendorId),
      getScoreTrend(vendorId),
      getBenchmark(vendorId),
    ]);
    setLatest(l);
    setTrend(t);
    setBenchmark(b);
  }, [vendorId]);

  useEffect(() => {
    load();
  }, [load]);

  async function score() {
    setScoring(true);
    try {
      await scoreVendorPerformance(vendorId);
      await load();
    } finally {
      setScoring(false);
    }
  }

  const maxTrend = Math.max(1, ...trend.map((p) => p.overall_score));

  return (
    <DkCard>
      <DkCardContent className="flex flex-col gap-4 py-5">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Gauge className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Performance</span>
            {latest && (
              <DkBadge tone={tone(latest.overall_score)}>
                {latest.overall_score.toFixed(0)} overall · {latest.period}
              </DkBadge>
            )}
          </div>
          <DkButton variant="secondary" loading={scoring} onClick={score}>
            <Gauge className="h-4 w-4" /> Score (AI)
          </DkButton>
        </div>

        {!latest ? (
          <p className="text-sm text-[var(--dk-fg-2)]">
            No performance score yet — generate one with AI from this vendor&apos;s order history.
          </p>
        ) : (
          <>
            {latest.summary && <p className="text-sm text-ink">{latest.summary}</p>}
            <div className="flex flex-col gap-2.5">
              {DIMENSIONS.map(([key, label]) => {
                const v = latest[key] as number;
                return (
                  <div key={key} className="flex items-center gap-3">
                    <span className="w-24 text-sm text-[var(--dk-fg-2)]">{label}</span>
                    <DkProgress value={v} tone={tone(v)} showLabel className="flex-1" />
                  </div>
                );
              })}
            </div>

            {benchmark && benchmark.peer_count > 0 && (
              <p className="text-sm text-[var(--dk-fg-2)]">
                <span className="font-medium text-ink">Benchmark:</span>{" "}
                {benchmark.vendor_overall?.toFixed(0)} vs peer avg{" "}
                {benchmark.peer_average?.toFixed(0)} ({benchmark.peer_group}) ·{" "}
                {benchmark.percentile?.toFixed(0)}th percentile of {benchmark.peer_count} peer(s)
              </p>
            )}

            {trend.length > 1 && (
              <div className="flex flex-col gap-2">
                <div className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
                  <TrendingUp className="h-3.5 w-3.5" /> Overall trend
                </div>
                <div className="flex items-end gap-2 h-24">
                  {trend.map((p) => (
                    <div key={p.period} className="flex flex-1 flex-col items-center gap-1">
                      <div
                        className="w-full rounded-t bg-brand/80"
                        style={{ height: `${(p.overall_score / maxTrend) * 100}%` }}
                        title={`${p.period}: ${p.overall_score}`}
                      />
                      <span className="text-[10px] text-[var(--dk-fg-muted)]">{p.period}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </DkCardContent>
    </DkCard>
  );
}
