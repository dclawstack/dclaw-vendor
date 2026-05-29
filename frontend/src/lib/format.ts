import type { POStatus, VendorStatus, VendorTier } from "@/lib/api";

type Tone = "brand" | "neutral" | "success" | "warning" | "danger" | "info" | "outline";

export function currency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

export function formatDate(value: string | null): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export const vendorStatusTone: Record<VendorStatus, Tone> = {
  active: "success",
  inactive: "neutral",
  blacklisted: "danger",
};

export const poStatusTone: Record<POStatus, Tone> = {
  draft: "neutral",
  sent: "info",
  partial: "warning",
  received: "success",
  cancelled: "danger",
};

export const tierTone: Record<VendorTier, Tone> = {
  strategic: "brand",
  preferred: "info",
  approved: "success",
  transactional: "neutral",
};

export const VENDOR_TIERS: VendorTier[] = [
  "strategic",
  "preferred",
  "approved",
  "transactional",
];

export const VENDOR_STATUSES: VendorStatus[] = ["active", "inactive", "blacklisted"];
export const PO_STATUSES: POStatus[] = [
  "draft",
  "sent",
  "partial",
  "received",
  "cancelled",
];
