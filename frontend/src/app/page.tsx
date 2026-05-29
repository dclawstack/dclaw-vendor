"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Building2, FileText, Plus, Truck, Wallet } from "lucide-react";

import {
  DkBadge,
  DkButton,
  DkCard,
  DkCardContent,
  DkPageHeader,
} from "@/components/dk";
import {
  listPurchaseOrders,
  listVendors,
  type PurchaseOrder,
  type Vendor,
  type VendorStatus,
} from "@/lib/api";
import { currency, formatDate, poStatusTone, vendorStatusTone } from "@/lib/format";

const OPEN_STATUSES = new Set(["draft", "sent", "partial"]);
const PENDING_DELIVERY = new Set(["sent", "partial"]);

export default function DashboardPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [pos, setPos] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      listVendors({ limit: 100 }),
      listPurchaseOrders({ limit: 100 }),
    ])
      .then(([v, p]) => {
        setVendors(v.items);
        setPos(p.items);
      })
      .finally(() => setLoading(false));
  }, []);

  const activeVendors = vendors.filter((v) => v.status === "active").length;
  const openPos = pos.filter((p) => OPEN_STATUSES.has(p.status)).length;
  const pendingDelivery = pos.filter((p) => PENDING_DELIVERY.has(p.status)).length;
  const totalSpend = pos.reduce((sum, p) => sum + p.total, 0);

  const byStatus = (["active", "inactive", "blacklisted"] as VendorStatus[]).map(
    (s) => ({ status: s, count: vendors.filter((v) => v.status === s).length }),
  );

  const recentPos = [...pos]
    .sort((a, b) => b.created_at.localeCompare(a.created_at))
    .slice(0, 5);
  const vendorName = (id: string | null) =>
    vendors.find((v) => v.id === id)?.name ?? "—";

  return (
    <div className="flex flex-col gap-6">
      <DkPageHeader
        eyebrow="Overview"
        title="Dashboard"
        description="Vendor and purchase-order activity at a glance."
        actions={
          <>
            <Link href="/vendors">
              <DkButton variant="secondary">
                <Plus className="h-4 w-4" /> Add Vendor
              </DkButton>
            </Link>
            <Link href="/purchase-orders">
              <DkButton>
                <Plus className="h-4 w-4" /> Create PO
              </DkButton>
            </Link>
          </>
        }
      />

      {loading ? (
        <p className="text-sm text-[var(--dk-fg-2)]">Loading…</p>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard
              icon={<Building2 className="h-5 w-5" />}
              label="Active vendors"
              value={String(activeVendors)}
            />
            <StatCard
              icon={<FileText className="h-5 w-5" />}
              label="Open POs"
              value={String(openPos)}
            />
            <StatCard
              icon={<Truck className="h-5 w-5" />}
              label="Pending delivery"
              value={String(pendingDelivery)}
            />
            <StatCard
              icon={<Wallet className="h-5 w-5" />}
              label="Total spend"
              value={currency(totalSpend)}
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <DkCard className="lg:col-span-2">
              <DkCardContent className="py-5">
                <h2 className="mb-4 font-display text-lg font-semibold text-ink">
                  Recent purchase orders
                </h2>
                {recentPos.length === 0 ? (
                  <p className="text-sm text-[var(--dk-fg-2)]">No purchase orders yet.</p>
                ) : (
                  <ul className="flex flex-col divide-y divide-[var(--dk-border)]">
                    {recentPos.map((po) => (
                      <li key={po.id} className="flex items-center justify-between py-3">
                        <div className="flex flex-col">
                          <Link
                            href={`/purchase-orders/${po.id}`}
                            className="font-medium text-brand hover:underline"
                          >
                            PO {po.id.slice(0, 8)}
                          </Link>
                          <span className="text-xs text-[var(--dk-fg-muted)]">
                            {vendorName(po.vendor_id)} · {formatDate(po.created_at)}
                          </span>
                        </div>
                        <div className="flex items-center gap-3">
                          <DkBadge tone={poStatusTone[po.status]}>{po.status}</DkBadge>
                          <span className="text-sm font-medium text-ink">
                            {currency(po.total)}
                          </span>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </DkCardContent>
            </DkCard>

            <DkCard>
              <DkCardContent className="py-5">
                <h2 className="mb-4 font-display text-lg font-semibold text-ink">
                  Vendors by status
                </h2>
                <ul className="flex flex-col gap-3">
                  {byStatus.map((row) => (
                    <li key={row.status} className="flex items-center justify-between">
                      <DkBadge tone={vendorStatusTone[row.status]}>{row.status}</DkBadge>
                      <span className="text-sm font-semibold text-ink">{row.count}</span>
                    </li>
                  ))}
                </ul>
              </DkCardContent>
            </DkCard>
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <DkCard>
      <DkCardContent className="flex flex-col gap-3 py-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--dk-purple-50)] text-brand">
          {icon}
        </div>
        <div className="flex flex-col">
          <span className="font-display text-2xl font-bold text-ink">{value}</span>
          <span className="text-sm text-[var(--dk-fg-2)]">{label}</span>
        </div>
      </DkCardContent>
    </DkCard>
  );
}
