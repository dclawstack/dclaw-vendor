"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Pencil, Plus, Trash2 } from "lucide-react";

import {
  DkBadge,
  DkButton,
  DkCard,
  DkCardContent,
  DkDialog,
  DkDialogContent,
  DkDialogFooter,
  DkDialogHeader,
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
  createPurchaseOrder,
  deleteVendor,
  getVendor,
  listPurchaseOrders,
  updateVendor,
  type PurchaseOrder,
  type Vendor,
  type VendorStatus,
} from "@/lib/api";
import {
  currency,
  formatDate,
  poStatusTone,
  VENDOR_STATUSES,
  vendorStatusTone,
} from "@/lib/format";

export default function VendorDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = params.id;

  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [pos, setPos] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<Vendor | null>(null);
  const [saving, setSaving] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [v, poRes] = await Promise.all([
        getVendor(id),
        listPurchaseOrders({ vendor_id: id }),
      ]);
      setVendor(v);
      setPos(poRes.items);
    } catch {
      setNotFound(true);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function saveEdit() {
    if (!form) return;
    setSaving(true);
    try {
      await updateVendor(id, {
        name: form.name,
        contact_name: form.contact_name,
        email: form.email,
        phone: form.phone,
        address: form.address,
        payment_terms: form.payment_terms,
        status: form.status,
      });
      setEditing(false);
      await load();
    } finally {
      setSaving(false);
    }
  }

  async function remove() {
    await deleteVendor(id);
    router.push("/vendors");
  }

  async function addPo() {
    const po = await createPurchaseOrder({ vendor_id: id });
    router.push(`/purchase-orders/${po.id}`);
  }

  if (loading) return <p className="text-sm text-[var(--dk-fg-2)]">Loading…</p>;
  if (notFound || !vendor)
    return (
      <div className="flex flex-col gap-4">
        <p className="text-sm text-[var(--dk-fg-2)]">Vendor not found.</p>
        <Link href="/vendors" className="text-brand hover:underline">
          ← Back to vendors
        </Link>
      </div>
    );

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/vendors"
        className="inline-flex items-center gap-1 text-sm text-[var(--dk-fg-2)] hover:text-brand"
      >
        <ArrowLeft className="h-4 w-4" /> Vendors
      </Link>

      <DkPageHeader
        title={vendor.name}
        description={vendor.email ?? undefined}
        actions={
          <>
            <DkButton
              variant="secondary"
              onClick={() => {
                setForm(vendor);
                setEditing(true);
              }}
            >
              <Pencil className="h-4 w-4" /> Edit
            </DkButton>
            <DkButton variant="danger" onClick={() => setConfirmDelete(true)}>
              <Trash2 className="h-4 w-4" /> Delete
            </DkButton>
          </>
        }
      />

      <DkCard>
        <DkCardContent className="grid grid-cols-2 gap-x-8 gap-y-4 py-6 md:grid-cols-3">
          <Field label="Status">
            <DkBadge tone={vendorStatusTone[vendor.status]}>{vendor.status}</DkBadge>
          </Field>
          <Field label="Contact">{vendor.contact_name || "—"}</Field>
          <Field label="Phone">{vendor.phone || "—"}</Field>
          <Field label="Payment terms">{vendor.payment_terms || "—"}</Field>
          <Field label="Address">{vendor.address || "—"}</Field>
          <Field label="Added">{formatDate(vendor.created_at)}</Field>
        </DkCardContent>
      </DkCard>

      <div className="flex items-center justify-between">
        <h2 className="font-display text-xl font-semibold text-ink">Purchase orders</h2>
        <DkButton variant="secondary" onClick={addPo}>
          <Plus className="h-4 w-4" /> Add PO
        </DkButton>
      </div>

      {pos.length === 0 ? (
        <p className="text-sm text-[var(--dk-fg-2)]">No purchase orders for this vendor.</p>
      ) : (
        <div className="rounded-2xl border border-[var(--dk-border)] bg-white">
          <DkTable>
            <DkTableHeader>
              <DkTableRow>
                <DkTableHead>PO</DkTableHead>
                <DkTableHead>Status</DkTableHead>
                <DkTableHead>Total</DkTableHead>
                <DkTableHead>Expected</DkTableHead>
              </DkTableRow>
            </DkTableHeader>
            <DkTableBody>
              {pos.map((po) => (
                <DkTableRow key={po.id}>
                  <DkTableCell>
                    <Link
                      href={`/purchase-orders/${po.id}`}
                      className="font-medium text-brand hover:underline"
                    >
                      {po.id.slice(0, 8)}
                    </Link>
                  </DkTableCell>
                  <DkTableCell>
                    <DkBadge tone={poStatusTone[po.status]}>{po.status}</DkBadge>
                  </DkTableCell>
                  <DkTableCell>{currency(po.total)}</DkTableCell>
                  <DkTableCell>{formatDate(po.expected_delivery)}</DkTableCell>
                </DkTableRow>
              ))}
            </DkTableBody>
          </DkTable>
        </div>
      )}

      {/* Edit modal */}
      <DkDialog open={editing} onClose={() => setEditing(false)}>
        <DkDialogHeader title="Edit Vendor" onClose={() => setEditing(false)} />
        {form && (
          <DkDialogContent className="flex flex-col gap-4">
            <div className="flex flex-col gap-1.5">
              <DkLabel>Name</DkLabel>
              <DkInput
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
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
                />
              </div>
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Address</DkLabel>
              <DkInput
                value={form.address ?? ""}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
              />
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
          </DkDialogContent>
        )}
        <DkDialogFooter>
          <DkButton variant="secondary" onClick={() => setEditing(false)}>
            Cancel
          </DkButton>
          <DkButton onClick={saveEdit} loading={saving}>
            Save
          </DkButton>
        </DkDialogFooter>
      </DkDialog>

      {/* Delete confirm */}
      <DkDialog open={confirmDelete} onClose={() => setConfirmDelete(false)} size="sm">
        <DkDialogHeader
          title="Delete vendor?"
          description="Purchase orders are kept but unlinked from this vendor."
          onClose={() => setConfirmDelete(false)}
        />
        <DkDialogFooter>
          <DkButton variant="secondary" onClick={() => setConfirmDelete(false)}>
            Cancel
          </DkButton>
          <DkButton variant="danger" onClick={remove}>
            Delete
          </DkButton>
        </DkDialogFooter>
      </DkDialog>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
        {label}
      </span>
      <span className="text-sm text-ink">{children}</span>
    </div>
  );
}
