"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Check, Plus, Trash2 } from "lucide-react";

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
  createLineItem,
  deleteLineItem,
  deletePurchaseOrder,
  getPurchaseOrder,
  getVendor,
  updateLineItem,
  updatePurchaseOrder,
  type POLineItem,
  type POStatus,
  type PurchaseOrder,
} from "@/lib/api";
import { currency, formatDate, PO_STATUSES, poStatusTone } from "@/lib/format";

export default function PurchaseOrderDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const id = params.id;

  const [po, setPo] = useState<PurchaseOrder | null>(null);
  const [vendorName, setVendorName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);

  const [addOpen, setAddOpen] = useState(false);
  const [newLine, setNewLine] = useState({ product_name: "", quantity: 1, unit_price: 0 });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getPurchaseOrder(id);
      setPo(data);
      if (data.vendor_id) {
        try {
          setVendorName((await getVendor(data.vendor_id)).name);
        } catch {
          setVendorName(null);
        }
      } else {
        setVendorName(null);
      }
    } catch {
      setNotFound(true);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function changeStatus(status: POStatus) {
    await updatePurchaseOrder(id, { status });
    await load();
  }

  async function addLine() {
    if (!newLine.product_name.trim()) return;
    setSaving(true);
    try {
      await createLineItem({ po_id: id, ...newLine });
      setAddOpen(false);
      setNewLine({ product_name: "", quantity: 1, unit_price: 0 });
      await load();
    } finally {
      setSaving(false);
    }
  }

  async function removePo() {
    await deletePurchaseOrder(id);
    router.push("/purchase-orders");
  }

  if (loading) return <p className="text-sm text-[var(--dk-fg-2)]">Loading…</p>;
  if (notFound || !po)
    return (
      <div className="flex flex-col gap-4">
        <p className="text-sm text-[var(--dk-fg-2)]">Purchase order not found.</p>
        <Link href="/purchase-orders" className="text-brand hover:underline">
          ← Back to purchase orders
        </Link>
      </div>
    );

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/purchase-orders"
        className="inline-flex items-center gap-1 text-sm text-[var(--dk-fg-2)] hover:text-brand"
      >
        <ArrowLeft className="h-4 w-4" /> Purchase Orders
      </Link>

      <DkPageHeader
        title={`PO ${po.id.slice(0, 8)}`}
        actions={
          <DkButton variant="danger" onClick={() => setConfirmDelete(true)}>
            <Trash2 className="h-4 w-4" /> Delete
          </DkButton>
        }
      />

      <DkCard>
        <DkCardContent className="grid grid-cols-2 items-start gap-x-8 gap-y-4 py-6 md:grid-cols-4">
          <div className="flex flex-col gap-1">
            <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
              Vendor
            </span>
            <span className="text-sm text-ink">
              {po.vendor_id ? (
                <Link href={`/vendors/${po.vendor_id}`} className="text-brand hover:underline">
                  {vendorName ?? po.vendor_id.slice(0, 8)}
                </Link>
              ) : (
                "—"
              )}
            </span>
          </div>
          <div className="flex flex-col gap-1.5">
            <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
              Status
            </span>
            <DkSelect
              className="h-9"
              value={po.status}
              onChange={(e) => changeStatus(e.target.value as POStatus)}
            >
              {PO_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </DkSelect>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
              Expected
            </span>
            <span className="text-sm text-ink">{formatDate(po.expected_delivery)}</span>
          </div>
          <div className="flex flex-col gap-1">
            <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
              Total
            </span>
            <span className="font-display text-lg font-semibold text-ink">
              {currency(po.total)}
            </span>
          </div>
          {po.notes && (
            <div className="col-span-2 flex flex-col gap-1 md:col-span-4">
              <span className="text-xs font-semibold uppercase tracking-wide text-[var(--dk-fg-muted)]">
                Notes
              </span>
              <span className="text-sm text-ink">{po.notes}</span>
            </div>
          )}
        </DkCardContent>
      </DkCard>

      <div className="flex items-center justify-between">
        <h2 className="font-display text-xl font-semibold text-ink">
          Line items
          <DkBadge tone="neutral" className="ml-2 align-middle">
            {po.line_items.length}
          </DkBadge>
        </h2>
        <DkButton variant="secondary" onClick={() => setAddOpen(true)}>
          <Plus className="h-4 w-4" /> Add line item
        </DkButton>
      </div>

      {po.line_items.length === 0 ? (
        <p className="text-sm text-[var(--dk-fg-2)]">No line items.</p>
      ) : (
        <div className="rounded-2xl border border-[var(--dk-border)] bg-white">
          <DkTable>
            <DkTableHeader>
              <DkTableRow>
                <DkTableHead>Product</DkTableHead>
                <DkTableHead>Qty</DkTableHead>
                <DkTableHead>Unit price</DkTableHead>
                <DkTableHead>Line total</DkTableHead>
                <DkTableHead>Received</DkTableHead>
                <DkTableHead className="text-right">Actions</DkTableHead>
              </DkTableRow>
            </DkTableHeader>
            <DkTableBody>
              {po.line_items.map((li) => (
                <LineRow key={li.id} item={li} onChange={load} />
              ))}
            </DkTableBody>
          </DkTable>
        </div>
      )}

      {/* Add line item */}
      <DkDialog open={addOpen} onClose={() => setAddOpen(false)}>
        <DkDialogHeader title="Add line item" onClose={() => setAddOpen(false)} />
        <DkDialogContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <DkLabel>Product name</DkLabel>
            <DkInput
              value={newLine.product_name}
              onChange={(e) => setNewLine({ ...newLine, product_name: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <DkLabel>Quantity</DkLabel>
              <DkInput
                type="number"
                min={0}
                value={newLine.quantity}
                onChange={(e) =>
                  setNewLine({ ...newLine, quantity: Number(e.target.value) })
                }
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Unit price</DkLabel>
              <DkInput
                type="number"
                min={0}
                step="0.01"
                value={newLine.unit_price}
                onChange={(e) =>
                  setNewLine({ ...newLine, unit_price: Number(e.target.value) })
                }
              />
            </div>
          </div>
        </DkDialogContent>
        <DkDialogFooter>
          <DkButton variant="secondary" onClick={() => setAddOpen(false)}>
            Cancel
          </DkButton>
          <DkButton onClick={addLine} loading={saving}>
            Add
          </DkButton>
        </DkDialogFooter>
      </DkDialog>

      {/* Delete confirm */}
      <DkDialog open={confirmDelete} onClose={() => setConfirmDelete(false)} size="sm">
        <DkDialogHeader
          title="Delete purchase order?"
          description="This removes the PO and all its line items."
          onClose={() => setConfirmDelete(false)}
        />
        <DkDialogFooter>
          <DkButton variant="secondary" onClick={() => setConfirmDelete(false)}>
            Cancel
          </DkButton>
          <DkButton variant="danger" onClick={removePo}>
            Delete
          </DkButton>
        </DkDialogFooter>
      </DkDialog>
    </div>
  );
}

function LineRow({ item, onChange }: { item: POLineItem; onChange: () => void }) {
  const [received, setReceived] = useState(item.received_qty);
  const [busy, setBusy] = useState(false);
  const dirty = received !== item.received_qty;

  async function saveReceived() {
    setBusy(true);
    try {
      await updateLineItem(item.id, { received_qty: received });
      await onChange();
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    setBusy(true);
    try {
      await deleteLineItem(item.id);
      await onChange();
    } finally {
      setBusy(false);
    }
  }

  return (
    <DkTableRow>
      <DkTableCell className="font-medium text-ink">{item.product_name}</DkTableCell>
      <DkTableCell>{item.quantity}</DkTableCell>
      <DkTableCell>{currency(item.unit_price)}</DkTableCell>
      <DkTableCell>{currency(item.quantity * item.unit_price)}</DkTableCell>
      <DkTableCell>
        <div className="flex items-center gap-2">
          <DkInput
            type="number"
            min={0}
            className="h-9 w-20"
            value={received}
            onChange={(e) => setReceived(Number(e.target.value))}
          />
          <span className="text-xs text-[var(--dk-fg-muted)]">/ {item.quantity}</span>
          {dirty && (
            <DkButton
              variant="secondary"
              size="icon"
              aria-label="Save received quantity"
              loading={busy}
              onClick={saveReceived}
            >
              <Check className="h-4 w-4" />
            </DkButton>
          )}
        </div>
      </DkTableCell>
      <DkTableCell className="text-right">
        <DkButton
          variant="ghost"
          size="icon"
          aria-label="Delete line item"
          loading={busy}
          onClick={remove}
        >
          <Trash2 className="h-4 w-4" />
        </DkButton>
      </DkTableCell>
    </DkTableRow>
  );
}
