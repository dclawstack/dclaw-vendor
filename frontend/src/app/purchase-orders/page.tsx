"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { FileText, Plus, Trash2 } from "lucide-react";

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
  createPurchaseOrder,
  listPurchaseOrders,
  listVendors,
  type POLineItemNestedCreate,
  type POStatus,
  type PurchaseOrder,
  type Vendor,
} from "@/lib/api";
import { currency, formatDate, PO_STATUSES, poStatusTone } from "@/lib/format";

interface DraftLine extends POLineItemNestedCreate {
  key: number;
}

export default function PurchaseOrdersPage() {
  const [pos, setPos] = useState<PurchaseOrder[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [vendorFilter, setVendorFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState<POStatus | "">("");

  const [open, setOpen] = useState(false);
  const [vendorId, setVendorId] = useState("");
  const [expected, setExpected] = useState("");
  const [notes, setNotes] = useState("");
  const [lines, setLines] = useState<DraftLine[]>([]);
  const [saving, setSaving] = useState(false);

  const vendorName = useCallback(
    (vid: string | null) => vendors.find((v) => v.id === vid)?.name ?? "—",
    [vendors],
  );

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listPurchaseOrders({
        vendor_id: vendorFilter || undefined,
        status: statusFilter,
      });
      setPos(res.items);
      setTotal(res.total);
    } finally {
      setLoading(false);
    }
  }, [vendorFilter, statusFilter]);

  useEffect(() => {
    listVendors({ limit: 100 }).then((r) => setVendors(r.items));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  function resetForm() {
    setVendorId("");
    setExpected("");
    setNotes("");
    setLines([]);
  }

  async function submit() {
    setSaving(true);
    try {
      await createPurchaseOrder({
        vendor_id: vendorId || null,
        expected_delivery: expected || null,
        notes: notes || null,
        line_items: lines.map(({ key: _key, ...li }) => li),
      });
      setOpen(false);
      resetForm();
      await load();
    } finally {
      setSaving(false);
    }
  }

  const draftTotal = lines.reduce(
    (sum, l) => sum + (l.quantity ?? 0) * (l.unit_price ?? 0),
    0,
  );

  return (
    <div className="flex flex-col gap-6">
      <DkPageHeader
        eyebrow="Procurement"
        title="Purchase Orders"
        description="Orders raised against your vendors."
        actions={
          <DkButton onClick={() => setOpen(true)}>
            <Plus className="h-4 w-4" /> Add PO
          </DkButton>
        }
      />

      <div className="flex flex-col gap-3 sm:flex-row">
        <div className="sm:w-64">
          <DkSelect value={vendorFilter} onChange={(e) => setVendorFilter(e.target.value)}>
            <option value="">All vendors</option>
            {vendors.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name}
              </option>
            ))}
          </DkSelect>
        </div>
        <div className="sm:w-48">
          <DkSelect
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as POStatus | "")}
          >
            <option value="">All statuses</option>
            {PO_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </DkSelect>
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-[var(--dk-fg-2)]">Loading…</p>
      ) : pos.length === 0 ? (
        <DkEmptyState
          icon={<FileText className="h-6 w-6" />}
          title="No purchase orders"
          description="Create a PO to start tracking line items and deliveries."
          actions={
            <DkButton onClick={() => setOpen(true)}>
              <Plus className="h-4 w-4" /> Add PO
            </DkButton>
          }
        />
      ) : (
        <div className="rounded-2xl border border-[var(--dk-border)] bg-white">
          <DkTable>
            <DkTableHeader>
              <DkTableRow>
                <DkTableHead>PO</DkTableHead>
                <DkTableHead>Vendor</DkTableHead>
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
                  <DkTableCell>{vendorName(po.vendor_id)}</DkTableCell>
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
      <p className="text-xs text-[var(--dk-fg-muted)]">{total} purchase order(s)</p>

      <DkDialog open={open} onClose={() => setOpen(false)} size="lg">
        <DkDialogHeader
          title="Add Purchase Order"
          description="Pick a vendor and add line items."
          onClose={() => setOpen(false)}
        />
        <DkDialogContent className="flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <DkLabel>Vendor</DkLabel>
              <DkSelect value={vendorId} onChange={(e) => setVendorId(e.target.value)}>
                <option value="">— None —</option>
                {vendors.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name}
                  </option>
                ))}
              </DkSelect>
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Expected delivery</DkLabel>
              <DkInput
                type="date"
                value={expected}
                onChange={(e) => setExpected(e.target.value)}
              />
            </div>
          </div>
          <div className="flex flex-col gap-1.5">
            <DkLabel>Notes</DkLabel>
            <DkInput value={notes} onChange={(e) => setNotes(e.target.value)} />
          </div>

          <div className="flex items-center justify-between pt-2">
            <DkLabel>Line items</DkLabel>
            <DkButton
              variant="secondary"
              size="sm"
              onClick={() =>
                setLines([
                  ...lines,
                  { key: Date.now(), product_name: "", quantity: 1, unit_price: 0 },
                ])
              }
            >
              <Plus className="h-4 w-4" /> Add line
            </DkButton>
          </div>
          {lines.length === 0 && (
            <p className="text-sm text-[var(--dk-fg-muted)]">No line items yet.</p>
          )}
          {lines.map((line, i) => (
            <div key={line.key} className="flex items-end gap-2">
              <div className="flex flex-1 flex-col gap-1.5">
                {i === 0 && <DkLabel>Product</DkLabel>}
                <DkInput
                  value={line.product_name}
                  placeholder="Product name"
                  onChange={(e) =>
                    setLines(
                      lines.map((l) =>
                        l.key === line.key ? { ...l, product_name: e.target.value } : l,
                      ),
                    )
                  }
                />
              </div>
              <div className="flex w-20 flex-col gap-1.5">
                {i === 0 && <DkLabel>Qty</DkLabel>}
                <DkInput
                  type="number"
                  min={0}
                  value={line.quantity}
                  onChange={(e) =>
                    setLines(
                      lines.map((l) =>
                        l.key === line.key
                          ? { ...l, quantity: Number(e.target.value) }
                          : l,
                      ),
                    )
                  }
                />
              </div>
              <div className="flex w-28 flex-col gap-1.5">
                {i === 0 && <DkLabel>Unit price</DkLabel>}
                <DkInput
                  type="number"
                  min={0}
                  step="0.01"
                  value={line.unit_price}
                  onChange={(e) =>
                    setLines(
                      lines.map((l) =>
                        l.key === line.key
                          ? { ...l, unit_price: Number(e.target.value) }
                          : l,
                      ),
                    )
                  }
                />
              </div>
              <DkButton
                variant="ghost"
                size="icon"
                aria-label="Remove line"
                onClick={() => setLines(lines.filter((l) => l.key !== line.key))}
              >
                <Trash2 className="h-4 w-4" />
              </DkButton>
            </div>
          ))}
          {lines.length > 0 && (
            <p className="text-right text-sm font-semibold text-ink">
              Total: {currency(draftTotal)}
            </p>
          )}
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
