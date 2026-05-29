"use client";

import { useCallback, useEffect, useState } from "react";
import { Plus, ShieldCheck } from "lucide-react";

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
} from "@/components/dk";
import {
  addAuditFinding,
  closeAudit,
  createAudit,
  getAudit,
  listAudits,
  listVendors,
  updateAuditFinding,
  type Audit,
  type FindingSeverity,
  type Vendor,
} from "@/lib/api";
import {
  auditStatusTone,
  findingSeverityTone,
  findingStatusTone,
  formatDate,
} from "@/lib/format";

const SEVERITIES: FindingSeverity[] = ["low", "medium", "high", "critical"];

export default function AuditsPage() {
  const [audits, setAudits] = useState<Audit[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [selected, setSelected] = useState<Audit | null>(null);

  const [createOpen, setCreateOpen] = useState(false);
  const [cForm, setCForm] = useState({ vendor_id: "", title: "", scheduled_date: "", auditor: "" });
  const [finding, setFinding] = useState<{ description: string; severity: FindingSeverity }>({
    description: "",
    severity: "medium",
  });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const vendorName = (id: string) => vendors.find((v) => v.id === id)?.name ?? "—";

  const load = useCallback(async () => {
    const [a, v] = await Promise.all([listAudits(), listVendors({ limit: 100 })]);
    setAudits(a.items);
    setVendors(v.items);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openAudit = useCallback(async (a: Audit) => {
    setErr(null);
    setSelected(await getAudit(a.id));
  }, []);

  async function create() {
    if (!cForm.vendor_id || !cForm.title.trim()) return;
    setBusy(true);
    try {
      const a = await createAudit({
        vendor_id: cForm.vendor_id,
        title: cForm.title,
        scheduled_date: cForm.scheduled_date || null,
        auditor: cForm.auditor || null,
      });
      setCreateOpen(false);
      setCForm({ vendor_id: "", title: "", scheduled_date: "", auditor: "" });
      await load();
      await openAudit(a);
    } finally {
      setBusy(false);
    }
  }

  async function addFinding() {
    if (!selected || !finding.description.trim()) return;
    setBusy(true);
    try {
      await addAuditFinding(selected.id, finding);
      setFinding({ description: "", severity: "medium" });
      await openAudit(selected);
    } finally {
      setBusy(false);
    }
  }

  async function closeFinding(id: string) {
    if (!selected) return;
    await updateAuditFinding(id, { status: "closed" });
    await openAudit(selected);
  }

  async function close() {
    if (!selected) return;
    setErr(null);
    try {
      await closeAudit(selected.id);
      await openAudit(selected);
      await load();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Cannot close audit");
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <DkPageHeader
        eyebrow="Procurement"
        title="Audits & Compliance"
        description="Schedule vendor audits, track findings, and validate closure."
        actions={
          <DkButton onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" /> Schedule audit
          </DkButton>
        }
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_1.4fr]">
        <DkCard>
          <DkCardContent className="flex flex-col gap-2 py-4">
            <span className="font-display font-semibold text-ink">Audits</span>
            {audits.length === 0 ? (
              <p className="text-sm text-[var(--dk-fg-2)]">No audits scheduled.</p>
            ) : (
              audits.map((a) => (
                <button
                  key={a.id}
                  onClick={() => openAudit(a)}
                  className={`flex flex-col rounded-xl border px-3 py-2 text-left ${
                    selected?.id === a.id
                      ? "border-brand bg-[var(--dk-purple-100)]"
                      : "border-[var(--dk-border)]"
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-ink">{a.title}</span>
                    <DkBadge tone={auditStatusTone[a.status]}>{a.status.replace("_", " ")}</DkBadge>
                  </div>
                  <span className="text-xs text-[var(--dk-fg-muted)]">
                    {vendorName(a.vendor_id)} · {a.findings.length} findings
                  </span>
                </button>
              ))
            )}
          </DkCardContent>
        </DkCard>

        {selected ? (
          <DkCard>
            <DkCardContent className="flex flex-col gap-3 py-4">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-display font-semibold text-ink">{selected.title}</span>
                  <DkBadge tone={auditStatusTone[selected.status]}>
                    {selected.status.replace("_", " ")}
                  </DkBadge>
                </div>
                {selected.status !== "closed" && (
                  <DkButton variant="secondary" onClick={close}>
                    <ShieldCheck className="h-4 w-4" /> Close audit
                  </DkButton>
                )}
              </div>
              {err && <p className="text-sm text-[var(--dk-danger)]">{err}</p>}
              <p className="text-xs text-[var(--dk-fg-muted)]">
                {vendorName(selected.vendor_id)}
                {selected.auditor ? ` · ${selected.auditor}` : ""}
                {selected.scheduled_date ? ` · ${formatDate(selected.scheduled_date)}` : ""}
              </p>

              {selected.findings.length === 0 ? (
                <p className="text-sm text-[var(--dk-fg-2)]">No findings recorded.</p>
              ) : (
                <ul className="flex flex-col divide-y divide-[var(--dk-border)]">
                  {selected.findings.map((f) => (
                    <li key={f.id} className="flex items-center justify-between gap-3 py-2">
                      <div className="flex flex-col">
                        <span className="text-sm text-ink">{f.description}</span>
                        {f.remediation && (
                          <span className="text-xs text-[var(--dk-fg-muted)]">{f.remediation}</span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <DkBadge tone={findingSeverityTone[f.severity]}>{f.severity}</DkBadge>
                        <DkBadge tone={findingStatusTone[f.status]}>{f.status}</DkBadge>
                        {f.status !== "closed" && (
                          <DkButton variant="ghost" onClick={() => closeFinding(f.id)}>
                            Close
                          </DkButton>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              )}

              {selected.status !== "closed" && (
                <div className="flex gap-2 rounded-xl bg-[var(--dk-bg)] p-3">
                  <DkInput
                    placeholder="New finding…"
                    value={finding.description}
                    onChange={(e) => setFinding({ ...finding, description: e.target.value })}
                  />
                  <DkSelect
                    className="w-32"
                    value={finding.severity}
                    onChange={(e) =>
                      setFinding({ ...finding, severity: e.target.value as FindingSeverity })
                    }
                  >
                    {SEVERITIES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </DkSelect>
                  <DkButton onClick={addFinding} loading={busy}>
                    Add
                  </DkButton>
                </div>
              )}
            </DkCardContent>
          </DkCard>
        ) : (
          <DkCard>
            <DkCardContent className="flex items-center gap-2 py-10 text-sm text-[var(--dk-fg-2)]">
              <ShieldCheck className="h-5 w-5" /> Select an audit to view findings.
            </DkCardContent>
          </DkCard>
        )}
      </div>

      <DkDialog open={createOpen} onClose={() => setCreateOpen(false)}>
        <DkDialogHeader title="Schedule audit" onClose={() => setCreateOpen(false)} />
        <DkDialogContent className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <DkLabel>Vendor *</DkLabel>
            <DkSelect
              value={cForm.vendor_id}
              onChange={(e) => setCForm({ ...cForm, vendor_id: e.target.value })}
            >
              <option value="">Select a vendor…</option>
              {vendors.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.name}
                </option>
              ))}
            </DkSelect>
          </div>
          <div className="flex flex-col gap-1.5">
            <DkLabel>Title *</DkLabel>
            <DkInput
              value={cForm.title}
              onChange={(e) => setCForm({ ...cForm, title: e.target.value })}
              placeholder="Annual SOC 2 audit"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <DkLabel>Scheduled date</DkLabel>
              <DkInput
                type="date"
                value={cForm.scheduled_date}
                onChange={(e) => setCForm({ ...cForm, scheduled_date: e.target.value })}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Auditor</DkLabel>
              <DkInput
                value={cForm.auditor}
                onChange={(e) => setCForm({ ...cForm, auditor: e.target.value })}
              />
            </div>
          </div>
        </DkDialogContent>
        <DkDialogFooter>
          <DkButton variant="secondary" onClick={() => setCreateOpen(false)}>
            Cancel
          </DkButton>
          <DkButton onClick={create} loading={busy}>
            Schedule
          </DkButton>
        </DkDialogFooter>
      </DkDialog>
    </div>
  );
}
