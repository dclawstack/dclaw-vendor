"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, CreditCard, Lock } from "lucide-react";

import { DkBadge, DkButton, DkCard, DkCardContent } from "@/components/dk";
import {
  createCheckout,
  getAuthConfig,
  getBillingPlans,
  getSubscription,
  type AuthConfig,
  type Plan,
  type Subscription,
} from "@/lib/api";

export function BillingPanel() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [sub, setSub] = useState<Subscription | null>(null);
  const [auth, setAuth] = useState<AuthConfig | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    const [p, s, a] = await Promise.all([
      getBillingPlans(),
      getSubscription(),
      getAuthConfig(),
    ]);
    setPlans(p);
    setSub(s);
    setAuth(a);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function upgrade(planId: string) {
    setBusy(planId);
    try {
      const { url } = await createCheckout(planId, sub?.seats || 1);
      if (url) window.location.href = url;
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Auth status */}
      <DkCard>
        <DkCardContent className="flex items-center justify-between gap-2 py-4">
          <div className="flex items-center gap-2">
            <Lock className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Authentication</span>
            <DkBadge tone={auth?.enabled ? "success" : "neutral"}>
              {auth?.enabled ? "Logto enabled" : "open (dev mode)"}
            </DkBadge>
          </div>
          {auth?.enabled && auth.endpoint && (
            <a
              href={auth.endpoint}
              target="_blank"
              rel="noreferrer"
              className="text-sm text-brand hover:underline"
            >
              Manage in Logto →
            </a>
          )}
        </DkCardContent>
      </DkCard>

      {/* Billing */}
      <DkCard>
        <DkCardContent className="flex flex-col gap-4 py-5">
          <div className="flex items-center gap-2">
            <CreditCard className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Billing &amp; plan</span>
            {sub && (
              <DkBadge tone="brand">
                {sub.plan_name} · {sub.seats} seats · {sub.status}
              </DkBadge>
            )}
            {sub && <span className="text-xs text-[var(--dk-fg-muted)]">{sub.backend}</span>}
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            {plans.map((p) => {
              const current = sub?.plan_id === p.id || sub?.plan_name === p.name;
              return (
                <div
                  key={p.id}
                  className={`flex flex-col gap-3 rounded-2xl border p-4 ${
                    current ? "border-brand" : "border-[var(--dk-border)]"
                  }`}
                >
                  <div className="flex flex-col">
                    <span className="font-display font-semibold text-ink">{p.name}</span>
                    <span className="text-sm text-[var(--dk-fg-2)]">
                      ${p.price_per_seat.toFixed(0)}/seat/mo
                    </span>
                  </div>
                  <ul className="flex flex-col gap-1 text-sm text-[var(--dk-fg-2)]">
                    {p.features.map((f) => (
                      <li key={f} className="flex items-center gap-1.5">
                        <Check className="h-3.5 w-3.5 text-brand" /> {f}
                      </li>
                    ))}
                  </ul>
                  <DkButton
                    variant={current ? "secondary" : "primary"}
                    disabled={current}
                    loading={busy === p.id}
                    onClick={() => upgrade(p.id)}
                  >
                    {current ? "Current plan" : "Choose plan"}
                  </DkButton>
                </div>
              );
            })}
          </div>
        </DkCardContent>
      </DkCard>
    </div>
  );
}
