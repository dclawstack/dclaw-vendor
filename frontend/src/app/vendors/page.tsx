"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Building2, Plus, Search, Sparkles } from "lucide-react";

import {
  DkBadge,
  DkButton,
  DkChip,
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
  classifyVendorsBatch,
  createVendor,
  getVendorFacets,
  listVendors,
  type Vendor,
  type VendorCreate,
  type VendorFacets,
  type VendorStatus,
  type VendorTier,
} from "@/lib/api";
import {
  VENDOR_STATUSES,
  VENDOR_TIERS,
  tierTone,
  vendorStatusTone,
} from "@/lib/format";

const emptyForm: VendorCreate = {
  name: "",
  contact_name: "",
  email: "",
  phone: "",
  payment_terms: "",
  website: "",
  category: "",
  status: "active",
};

export default function VendorsPage() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [total, setTotal] = useState(0);
  const [facets, setFacets] = useState<VendorFacets | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<VendorStatus | "">("");
  const [tierFilter, setTierFilter] = useState<VendorTier | "">("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [classifying, setClassifying] = useState(false);

  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<VendorCreate>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [res, fc] = await Promise.all([
        listVendors({
          search,
          status: statusFilter,
          tier: tierFilter,
          category: categoryFilter,
        }),
        getVendorFacets(),
      ]);
      setVendors(res.items);
      setTotal(res.total);
      setFacets(fc);
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, tierFilter, categoryFilter]);

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

  async function bulkClassify() {
    setClassifying(true);
    try {
      await classifyVendorsBatch(true);
      await load();
    } catch {
      /* surfaced via empty result; keep the directory usable */
    } finally {
      setClassifying(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <DkPageHeader
        eyebrow="Procurement"
        title="Vendor Directory"
        description="Your classified, enriched supplier directory."
        actions={
          <div className="flex gap-2">
            <DkButton variant="secondary" onClick={bulkClassify} loading={classifying}>
              <Sparkles className="h-4 w-4" /> AI Classify
            </DkButton>
            <DkButton onClick={() => setOpen(true)}>
              <Plus className="h-4 w-4" /> Add Vendor
            </DkButton>
          </div>
        }
      />

      {facets && facets.category.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <DkChip
            tone={categoryFilter === "" ? "brand" : "outline"}
            className="cursor-pointer"
            onClick={() => setCategoryFilter("")}
          >
            All categories
          </DkChip>
          {facets.category.map((c) => (
            <DkChip
              key={c.value}
              tone={categoryFilter === c.value ? "brand" : "outline"}
              className="cursor-pointer"
              onClick={() =>
                setCategoryFilter(categoryFilter === c.value ? "" : c.value)
              }
            >
              {c.value} · {c.count}
            </DkChip>
          ))}
        </div>
      )}

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
        <div className="sm:w-44">
          <DkSelect
            value={tierFilter}
            onChange={(e) => setTierFilter(e.target.value as VendorTier | "")}
          >
            <option value="">All tiers</option>
            {VENDOR_TIERS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </DkSelect>
        </div>
        <div className="sm:w-44">
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
                <DkTableHead>Category</DkTableHead>
                <DkTableHead>Tier</DkTableHead>
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
                    {v.enrichment && (
                      <DkChip tone="info" className="ml-2 align-middle">
                        enriched
                      </DkChip>
                    )}
                  </DkTableCell>
                  <DkTableCell>{v.category || "—"}</DkTableCell>
                  <DkTableCell>
                    {v.tier ? (
                      <DkBadge tone={tierTone[v.tier]}>{v.tier}</DkBadge>
                    ) : (
                      "—"
                    )}
                  </DkTableCell>
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
              <DkLabel>Website</DkLabel>
              <DkInput
                value={form.website ?? ""}
                onChange={(e) => setForm({ ...form, website: e.target.value })}
                placeholder="acme.com"
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Category</DkLabel>
              <DkInput
                value={form.category ?? ""}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                placeholder="IT Services"
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
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <DkLabel>Tier</DkLabel>
              <DkSelect
                value={form.tier ?? ""}
                onChange={(e) =>
                  setForm({ ...form, tier: (e.target.value || null) as VendorTier | null })
                }
              >
                <option value="">Unclassified</option>
                {VENDOR_TIERS.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </DkSelect>
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
