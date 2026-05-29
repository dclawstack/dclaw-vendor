import type {
  ApprovalStatus,
  ContractStatus,
  DocumentStatus,
  OnboardingStatus,
  POStatus,
  RiskLevel,
  VendorStatus,
  VendorTier,
} from "@/lib/api";

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

export const onboardingStatusTone: Record<OnboardingStatus, Tone> = {
  draft: "neutral",
  collecting: "info",
  pending_approval: "warning",
  approved: "success",
  rejected: "danger",
  activated: "brand",
};

export const approvalStatusTone: Record<ApprovalStatus, Tone> = {
  pending: "neutral",
  approved: "success",
  rejected: "danger",
};

export const docStatusTone: Record<DocumentStatus, Tone> = {
  uploaded: "neutral",
  validated: "success",
  rejected: "danger",
};

export const riskLevelTone: Record<RiskLevel, Tone> = {
  low: "success",
  medium: "warning",
  high: "danger",
};

export const contractStatusTone: Record<ContractStatus, Tone> = {
  draft: "neutral",
  active: "success",
  expiring: "warning",
  expired: "danger",
  terminated: "neutral",
};

export const VENDOR_STATUSES: VendorStatus[] = ["active", "inactive", "blacklisted"];
export const PO_STATUSES: POStatus[] = [
  "draft",
  "sent",
  "partial",
  "received",
  "cancelled",
];
