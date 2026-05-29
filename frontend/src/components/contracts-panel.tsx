"use client";

import { useCallback, useEffect, useState } from "react";
import { FileSignature, Plus, Sparkles, Trash2 } from "lucide-react";

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
  DkTextarea,
} from "@/components/dk";
import {
  createContract,
  deleteContract,
  extractContractTerms,
  listContracts,
  type Contract,
} from "@/lib/api";
import { contractStatusTone, currency, formatDate } from "@/lib/format";

export function ContractsPanel({ vendorId }: { vendorId: string }) {
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [addOpen, setAddOpen] = useState(false);
  const [form, setForm] = useState({ title: "", end_date: "", value: "" });
  const [saving, setSaving] = useState(false);

  const [extractFor, setExtractFor] = useState<Contract | null>(null);
  const [extractText, setExtractText] = useState("");
  const [extracting, setExtracting] = useState(false);

  const load = useCallback(async () => {
    const res = await listContracts({ vendor_id: vendorId });
    setContracts(res.items);
  }, [vendorId]);

  useEffect(() => {
    load();
  }, [load]);

  async function add() {
    if (!form.title.trim()) return;
    setSaving(true);
    try {
      await createContract({
        vendor_id: vendorId,
        title: form.title,
        end_date: form.end_date || null,
        value: form.value ? Number(form.value) : null,
      });
      setAddOpen(false);
      setForm({ title: "", end_date: "", value: "" });
      await load();
    } finally {
      setSaving(false);
    }
  }

  async function runExtract() {
    if (!extractFor || !extractText.trim()) return;
    setExtracting(true);
    try {
      await extractContractTerms(extractFor.id, extractText);
      setExtractFor(null);
      setExtractText("");
      await load();
    } finally {
      setExtracting(false);
    }
  }

  return (
    <DkCard>
      <DkCardContent className="flex flex-col gap-4 py-5">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <FileSignature className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Contracts</span>
          </div>
          <DkButton variant="secondary" onClick={() => setAddOpen(true)}>
            <Plus className="h-4 w-4" /> Add contract
          </DkButton>
        </div>

        {contracts.length === 0 ? (
          <p className="text-sm text-[var(--dk-fg-2)]">No contracts on file.</p>
        ) : (
          <ul className="flex flex-col divide-y divide-[var(--dk-border)]">
            {contracts.map((c) => (
              <li key={c.id} className="flex items-center justify-between gap-3 py-2">
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-ink">{c.title}</span>
                  <span className="text-xs text-[var(--dk-fg-muted)]">
                    {c.end_date ? `ends ${formatDate(c.end_date)}` : "no end date"}
                    {c.value != null ? ` · ${currency(c.value)}` : ""}
                    {c.key_terms?.payment_terms ? ` · ${c.key_terms.payment_terms}` : ""}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <DkBadge tone={contractStatusTone[c.status]}>{c.status}</DkBadge>
                  <DkButton variant="ghost" onClick={() => setExtractFor(c)}>
                    <Sparkles className="h-4 w-4" /> Extract
                  </DkButton>
                  <DkButton
                    variant="ghost"
                    onClick={async () => {
                      await deleteContract(c.id);
                      await load();
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </DkButton>
                </div>
              </li>
            ))}
          </ul>
        )}
      </DkCardContent>

      <DkDialog open={addOpen} onClose={() => setAddOpen(false)}>
        <DkDialogHeader title="Add contract" onClose={() => setAddOpen(false)} />
        <DkDialogContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <DkLabel>Title *</DkLabel>
            <DkInput
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Master Services Agreement"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <DkLabel>End date</DkLabel>
              <DkInput
                type="date"
                value={form.end_date}
                onChange={(e) => setForm({ ...form, end_date: e.target.value })}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Value (USD)</DkLabel>
              <DkInput
                type="number"
                value={form.value}
                onChange={(e) => setForm({ ...form, value: e.target.value })}
              />
            </div>
          </div>
        </DkDialogContent>
        <DkDialogFooter>
          <DkButton variant="secondary" onClick={() => setAddOpen(false)}>
            Cancel
          </DkButton>
          <DkButton onClick={add} loading={saving}>
            Create
          </DkButton>
        </DkDialogFooter>
      </DkDialog>

      <DkDialog open={!!extractFor} onClose={() => setExtractFor(null)}>
        <DkDialogHeader
          title="Extract key terms (AI)"
          description="Paste contract text — the AI extracts payment terms, SLA, renewal, etc."
          onClose={() => setExtractFor(null)}
        />
        <DkDialogContent>
          <DkTextarea
            rows={8}
            value={extractText}
            onChange={(e) => setExtractText(e.target.value)}
            placeholder="Paste the contract text here…"
          />
        </DkDialogContent>
        <DkDialogFooter>
          <DkButton variant="secondary" onClick={() => setExtractFor(null)}>
            Cancel
          </DkButton>
          <DkButton onClick={runExtract} loading={extracting}>
            <Sparkles className="h-4 w-4" /> Extract
          </DkButton>
        </DkDialogFooter>
      </DkDialog>
    </DkCard>
  );
}
