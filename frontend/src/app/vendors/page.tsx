"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Building2, Plus, Search } from "lucide-react";

import {
  DkBadge,
  DkButton,
  DkDialog,
  DkDialogContent,
  DkDialogFooter,
  DkDialogHeader,
  DkEmptyState,
  DkInput,
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
  createVendor,
  listVendors,
  type Vendor,
  type VendorCreate,
  type VendorStatus,
} from "@/lib/api";
import { VENDOR_STATUSES, vendorStatusTone } from "@/lib/format";

const emptyForm: VendorCreate = {
  name: "",
  contact_name: "",
  email: "",
  phone: "",
  payment_terms: "",
  status: "active",
};

export default function VendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<VendorStatus | "">("");

  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<VendorCreate>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listVendors({ search, status: statusFilter });
      setVendors(res.items);
      setTotal(res.total);
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter]);

  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  async function submit() {
    if (!form.name.trim()) {
      setError("Name is required");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await createVendor(form);
      setOpen(false);
      setForm(emptyForm);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create vendor");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <DkPageHeader
        eyebrow="Procurement"
        title="Vendors"
        description="Your supplier directory."
        actions={
          <DkButton onClick={() => setOpen(true)}>
            <Plus className="h-4 w-4" /> Add Vendor
          </DkButton>
        }
      />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--dk-fg-muted)]" />
          <DkInput
            className="pl-9"
            placeholder="Search by name or email…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="sm:w-48">
          <DkSelect
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as VendorStatus | "")}
          >
            <option value="">All statuses</option>
            {VENDOR_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </DkSelect>
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-[var(--dk-fg-2)]">Loading…</p>
      ) : vendors.length === 0 ? (
        <DkEmptyState
          icon={<Building2 className="h-6 w-6" />}
          title="No vendors yet"
          description="Add your first supplier to start tracking purchase orders."
          actions={
            <DkButton onClick={() => setOpen(true)}>
              <Plus className="h-4 w-4" /> Add Vendor
            </DkButton>
          }
        />
      ) : (
        <div className="rounded-2xl border border-[var(--dk-border)] bg-white">
          <DkTable>
            <DkTableHeader>
              <DkTableRow>
                <DkTableHead>Name</DkTableHead>
                <DkTableHead>Email</DkTableHead>
                <DkTableHead>Payment terms</DkTableHead>
                <DkTableHead>Status</DkTableHead>
              </DkTableRow>
            </DkTableHeader>
            <DkTableBody>
              {vendors.map((v) => (
                <DkTableRow key={v.id}>
                  <DkTableCell>
                    <Link
                      href={`/vendors/${v.id}`}
                      className="font-medium text-brand hover:underline"
                    >
                      {v.name}
                    </Link>
                  </DkTableCell>
                  <DkTableCell>{v.email || "—"}</DkTableCell>
                  <DkTableCell>{v.payment_terms || "—"}</DkTableCell>
                  <DkTableCell>
                    <DkBadge tone={vendorStatusTone[v.status]}>{v.status}</DkBadge>
                  </DkTableCell>
                </DkTableRow>
              ))}
            </DkTableBody>
          </DkTable>
        </div>
      )}
      <p className="text-xs text-[var(--dk-fg-muted)]">{total} vendor(s)</p>

      <DkDialog open={open} onClose={() => setOpen(false)}>
        <DkDialogHeader
          title="Add Vendor"
          description="Create a new supplier record."
          onClose={() => setOpen(false)}
        />
        <DkDialogContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <DkLabel>Name *</DkLabel>
            <DkInput
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Acme Corp"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <DkLabel>Contact name</DkLabel>
              <DkInput
                value={form.contact_name ?? ""}
                onChange={(e) => setForm({ ...form, contact_name: e.target.value })}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Email</DkLabel>
              <DkInput
                value={form.email ?? ""}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Phone</DkLabel>
              <DkInput
                value={form.phone ?? ""}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Payment terms</DkLabel>
              <DkInput
                value={form.payment_terms ?? ""}
                onChange={(e) => setForm({ ...form, payment_terms: e.target.value })}
                placeholder="Net 30"
              />
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <DkLabel>Status</DkLabel>
            <DkSelect
              value={form.status}
              onChange={(e) =>
                setForm({ ...form, status: e.target.value as VendorStatus })
              }
            >
              {VENDOR_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
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
