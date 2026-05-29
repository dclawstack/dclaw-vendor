"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ClipboardCheck, Plus } from "lucide-react";

import {
  DkBadge,
  DkButton,
  DkDialog,
  DkDialogContent,
  DkDialogFooter,
  DkDialogHeader,
  DkEmptyState,
  DkLabel,
  DkPageHeader,
  DkSelect,
  DkTable,
  DkTableBody,
  DkTableCell,
  DkTableHead,
  DkTableHeader,
  DkTableRow,
} from "@/components/dk";
import {
  createOnboardingCase,
  listOnboardingCases,
  listVendors,
  type OnboardingCase,
  type Vendor,
} from "@/lib/api";
import { formatDate, onboardingStatusTone } from "@/lib/format";

export default function OnboardingPage() {
  const router = useRouter();
  const [cases, setCases] = useState<OnboardingCase[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);

  const [open, setOpen] = useState(false);
  const [vendorId, setVendorId] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [c, v] = await Promise.all([
        listOnboardingCases({ limit: 100 }),
        listVendors({ limit: 100 }),
      ]);
      setCases(c.items);
      setVendors(v.items);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const vendorName = (id: string) => vendors.find((v) => v.id === id)?.name ?? "—";

  async function submit() {
    if (!vendorId) {
      setError("Pick a vendor");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const c = await createOnboardingCase({ vendor_id: vendorId });
      setOpen(false);
      setVendorId("");
      router.push(`/onboarding/${c.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create case");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <DkPageHeader
        eyebrow="Procurement"
        title="Vendor Onboarding"
        description="Collect documents, validate with AI, and route for multi-step approval."
        actions={
          <DkButton onClick={() => setOpen(true)}>
            <Plus className="h-4 w-4" /> New Onboarding
          </DkButton>
        }
      />

      {loading ? (
        <p className="text-sm text-[var(--dk-fg-2)]">Loading…</p>
      ) : cases.length === 0 ? (
        <DkEmptyState
          icon={<ClipboardCheck className="h-6 w-6" />}
          title="No onboarding cases"
          description="Start onboarding a vendor: collect documents, validate, route for approval."
          actions={
            <DkButton onClick={() => setOpen(true)}>
              <Plus className="h-4 w-4" /> New Onboarding
            </DkButton>
          }
        />
      ) : (
        <div className="rounded-2xl border border-[var(--dk-border)] bg-white">
          <DkTable>
            <DkTableHeader>
              <DkTableRow>
                <DkTableHead>Vendor</DkTableHead>
                <DkTableHead>Status</DkTableHead>
                <DkTableHead>Documents</DkTableHead>
                <DkTableHead>Created</DkTableHead>
              </DkTableRow>
            </DkTableHeader>
            <DkTableBody>
              {cases.map((c) => (
                <DkTableRow key={c.id}>
                  <DkTableCell>
                    <Link
                      href={`/onboarding/${c.id}`}
                      className="font-medium text-brand hover:underline"
                    >
                      {vendorName(c.vendor_id)}
                    </Link>
                  </DkTableCell>
                  <DkTableCell>
                    <DkBadge tone={onboardingStatusTone[c.status]}>
                      {c.status.replace("_", " ")}
                    </DkBadge>
                  </DkTableCell>
                  <DkTableCell>{c.documents.length}</DkTableCell>
                  <DkTableCell>{formatDate(c.created_at)}</DkTableCell>
                </DkTableRow>
              ))}
            </DkTableBody>
          </DkTable>
        </div>
      )}

      <DkDialog open={open} onClose={() => setOpen(false)}>
        <DkDialogHeader
          title="New Onboarding Case"
          description="Pick a vendor to onboard."
          onClose={() => setOpen(false)}
        />
        <DkDialogContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <DkLabel>Vendor *</DkLabel>
            <DkSelect value={vendorId} onChange={(e) => setVendorId(e.target.value)}>
              <option value="">Select a vendor…</option>
              {vendors.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name}
                </option>
              ))}
            </DkSelect>
          </div>
          {error && <p className="text-sm text-[var(--dk-danger)]">{error}</p>}
        </DkDialogContent>
        <DkDialogFooter>
          <DkButton variant="secondary" onClick={() => setOpen(false)}>
            Cancel
          </DkButton>
          <DkButton onClick={submit} loading={saving}>
            Create
          </DkButton>
        </DkDialogFooter>
      </DkDialog>
    </div>
  );
}
