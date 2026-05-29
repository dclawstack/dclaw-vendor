"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  CheckCircle2,
  FileCheck,
  ListChecks,
  Send,
  Sparkles,
  Upload,
} from "lucide-react";

import {
  DkBadge,
  DkButton,
  DkCard,
  DkCardContent,
  DkInput,
  DkLabel,
} from "@/components/dk";
import {
  activateOnboardingCase,
  decideApprovalStep,
  generateChecklist,
  getOnboardingCase,
  getVendor,
  submitOnboardingCase,
  uploadOnboardingDocument,
  validateDocument,
  type OnboardingCase,
} from "@/lib/api";
import {
  approvalStatusTone,
  docStatusTone,
  formatDate,
  onboardingStatusTone,
} from "@/lib/format";

export default function OnboardingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [oc, setOc] = useState<OnboardingCase | null>(null);
  const [vendorName, setVendorName] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);

  const [docType, setDocType] = useState("w9");
  const fileRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const c = await getOnboardingCase(id);
      setOc(c);
      const v = await getVendor(c.vendor_id);
      setVendorName(v.name);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function run(key: string, fn: () => Promise<unknown>) {
    setBusy(key);
    try {
      await fn();
      await load();
    } finally {
      setBusy(null);
    }
  }

  async function upload() {
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    await run("upload", async () => {
      await uploadOnboardingDocument(id, docType, file);
      if (fileRef.current) fileRef.current.value = "";
    });
  }

  if (loading) return <p className="text-sm text-[var(--dk-fg-2)]">Loading…</p>;
  if (!oc)
    return (
      <div className="flex flex-col gap-4">
        <p className="text-sm text-[var(--dk-fg-2)]">Onboarding case not found.</p>
        <Link href="/onboarding" className="text-brand hover:underline">
          ← Back to onboarding
        </Link>
      </div>
    );

  const currentStep = [...oc.steps]
    .sort((a, b) => a.step_order - b.step_order)
    .find((s) => s.status === "pending");
  const canSubmit = oc.status === "draft" || oc.status === "collecting";
  const canActivate = oc.status === "approved";

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/onboarding"
        className="inline-flex items-center gap-1 text-sm text-[var(--dk-fg-2)] hover:text-brand"
      >
        <ArrowLeft className="h-4 w-4" /> Onboarding
      </Link>

      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h1 className="font-display text-2xl font-bold text-ink">{vendorName}</h1>
          <div>
            <DkBadge tone={onboardingStatusTone[oc.status]}>
              {oc.status.replace("_", " ")}
            </DkBadge>
          </div>
        </div>
        <div className="flex flex-wrap justify-end gap-2">
          <DkButton
            variant="secondary"
            loading={busy === "checklist"}
            onClick={() => run("checklist", () => generateChecklist(id))}
          >
            <Sparkles className="h-4 w-4" /> Generate checklist
          </DkButton>
          {canSubmit && (
            <DkButton
              loading={busy === "submit"}
              onClick={() => run("submit", () => submitOnboardingCase(id))}
            >
              <Send className="h-4 w-4" /> Submit for approval
            </DkButton>
          )}
          {canActivate && (
            <DkButton
              loading={busy === "activate"}
              onClick={() => run("activate", () => activateOnboardingCase(id))}
            >
              <CheckCircle2 className="h-4 w-4" /> Activate vendor
            </DkButton>
          )}
        </div>
      </div>

      {/* Checklist */}
      <DkCard>
        <DkCardContent className="flex flex-col gap-3 py-5">
          <div className="flex items-center gap-2">
            <ListChecks className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Document checklist</span>
          </div>
          {oc.checklist && oc.checklist.length > 0 ? (
            <ul className="flex flex-col gap-2">
              {oc.checklist.map((c, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-ink">
                  <DkBadge tone="neutral">{c.doc_type}</DkBadge>
                  <span>{c.item}</span>
                  {c.required && (
                    <span className="text-xs text-[var(--dk-danger)]">required</span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-[var(--dk-fg-2)]">
              No checklist yet — generate one with AI based on this vendor&apos;s profile.
            </p>
          )}
        </DkCardContent>
      </DkCard>

      {/* Documents */}
      <DkCard>
        <DkCardContent className="flex flex-col gap-4 py-5">
          <div className="flex items-center gap-2">
            <Upload className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Documents</span>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex flex-col gap-1.5 sm:w-40">
              <DkLabel>Document type</DkLabel>
              <DkInput value={docType} onChange={(e) => setDocType(e.target.value)} />
            </div>
            <div className="flex flex-col gap-1.5 flex-1">
              <DkLabel>File</DkLabel>
              <input
                ref={fileRef}
                type="file"
                className="text-sm text-ink file:mr-3 file:rounded-pill file:border-0 file:bg-[var(--dk-purple-100)] file:px-3 file:py-1.5 file:text-brand"
              />
            </div>
            <DkButton loading={busy === "upload"} onClick={upload}>
              <Upload className="h-4 w-4" /> Upload
            </DkButton>
          </div>

          {oc.documents.length > 0 && (
            <ul className="flex flex-col divide-y divide-[var(--dk-border)]">
              {oc.documents.map((d) => (
                <li key={d.id} className="flex items-center justify-between gap-3 py-2">
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-ink">{d.filename}</span>
                    <span className="text-xs text-[var(--dk-fg-muted)]">
                      {d.doc_type} · {formatDate(d.uploaded_at)}
                      {d.validation?.issues?.length
                        ? ` · ${d.validation.issues.join("; ")}`
                        : ""}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <DkBadge tone={docStatusTone[d.status]}>{d.status}</DkBadge>
                    <DkButton
                      variant="ghost"
                      loading={busy === `val-${d.id}`}
                      onClick={() => run(`val-${d.id}`, () => validateDocument(d.id))}
                    >
                      <FileCheck className="h-4 w-4" /> Validate
                    </DkButton>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </DkCardContent>
      </DkCard>

      {/* Approval chain */}
      <DkCard>
        <DkCardContent className="flex flex-col gap-3 py-5">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Approval chain</span>
          </div>
          <ul className="flex flex-col gap-2">
            {[...oc.steps]
              .sort((a, b) => a.step_order - b.step_order)
              .map((s) => (
                <li
                  key={s.id}
                  className="flex items-center justify-between gap-3 rounded-xl border border-[var(--dk-border)] px-3 py-2"
                >
                  <div className="flex flex-col">
                    <span className="text-sm font-medium text-ink">
                      {s.step_order + 1}. {s.name}
                    </span>
                    <span className="text-xs text-[var(--dk-fg-muted)]">
                      {s.approver_role || "—"}
                      {s.decided_by ? ` · by ${s.decided_by}` : ""}
                      {s.comment ? ` · ${s.comment}` : ""}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <DkBadge tone={approvalStatusTone[s.status]}>{s.status}</DkBadge>
                    {oc.status === "pending_approval" && currentStep?.id === s.id && (
                      <>
                        <DkButton
                          variant="secondary"
                          loading={busy === `approve-${s.id}`}
                          onClick={() =>
                            run(`approve-${s.id}`, () =>
                              decideApprovalStep(s.id, { decision: "approve" }),
                            )
                          }
                        >
                          Approve
                        </DkButton>
                        <DkButton
                          variant="danger"
                          loading={busy === `reject-${s.id}`}
                          onClick={() =>
                            run(`reject-${s.id}`, () =>
                              decideApprovalStep(s.id, { decision: "reject" }),
                            )
                          }
                        >
                          Reject
                        </DkButton>
                      </>
                    )}
                  </div>
                </li>
              ))}
          </ul>
        </DkCardContent>
      </DkCard>
    </div>
  );
}
