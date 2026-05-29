"use client";

import { useCallback, useEffect, useState } from "react";
import { MessageSquare, Plus, Star } from "lucide-react";

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
  DkTextarea,
} from "@/components/dk";
import {
  addSurveyResponse,
  createSurvey,
  getSurvey,
  getVendorSentiment,
  listSurveys,
  listVendors,
  type Survey,
  type Vendor,
  type VendorSentiment,
} from "@/lib/api";
import { formatDate, sentimentTone } from "@/lib/format";

export default function FeedbackPage() {
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [selected, setSelected] = useState<Survey | null>(null);
  const [sentiment, setSentiment] = useState<VendorSentiment | null>(null);

  const [createOpen, setCreateOpen] = useState(false);
  const [cForm, setCForm] = useState({ vendor_id: "", title: "" });
  const [resp, setResp] = useState({ respondent: "", rating: 5, comment: "" });
  const [busy, setBusy] = useState(false);

  const vendorName = (id: string) => vendors.find((v) => v.id === id)?.name ?? "—";

  const load = useCallback(async () => {
    const [s, v] = await Promise.all([listSurveys(), listVendors({ limit: 100 })]);
    setSurveys(s.items);
    setVendors(v.items);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const openSurvey = useCallback(async (s: Survey) => {
    const full = await getSurvey(s.id);
    setSelected(full);
    setSentiment(await getVendorSentiment(full.vendor_id));
  }, []);

  async function create() {
    if (!cForm.vendor_id || !cForm.title.trim()) return;
    setBusy(true);
    try {
      const s = await createSurvey(cForm);
      setCreateOpen(false);
      setCForm({ vendor_id: "", title: "" });
      await load();
      await openSurvey(s);
    } finally {
      setBusy(false);
    }
  }

  async function submitResponse() {
    if (!selected) return;
    setBusy(true);
    try {
      await addSurveyResponse(selected.id, {
        respondent: resp.respondent || undefined,
        rating: resp.rating,
        comment: resp.comment || undefined,
      });
      setResp({ respondent: "", rating: 5, comment: "" });
      await openSurvey(selected);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <DkPageHeader
        eyebrow="Procurement"
        title="Stakeholder Feedback"
        description="Run vendor surveys and track AI sentiment over time."
        actions={
          <DkButton onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4" /> New survey
          </DkButton>
        }
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_1.4fr]">
        <DkCard>
          <DkCardContent className="flex flex-col gap-2 py-4">
            <span className="font-display font-semibold text-ink">Surveys</span>
            {surveys.length === 0 ? (
              <p className="text-sm text-[var(--dk-fg-2)]">No surveys yet.</p>
            ) : (
              surveys.map((s) => (
                <button
                  key={s.id}
                  onClick={() => openSurvey(s)}
                  className={`flex flex-col rounded-xl border px-3 py-2 text-left ${
                    selected?.id === s.id
                      ? "border-brand bg-[var(--dk-purple-100)]"
                      : "border-[var(--dk-border)]"
                  }`}
                >
                  <span className="text-sm font-medium text-ink">{s.title}</span>
                  <span className="text-xs text-[var(--dk-fg-muted)]">
                    {vendorName(s.vendor_id)} · {s.responses.length} responses
                  </span>
                </button>
              ))
            )}
          </DkCardContent>
        </DkCard>

        {selected ? (
          <div className="flex flex-col gap-4">
            {sentiment && sentiment.response_count > 0 && (
              <DkCard>
                <DkCardContent className="flex flex-wrap items-center gap-3 py-4">
                  <span className="font-display font-semibold text-ink">
                    {vendorName(selected.vendor_id)} sentiment
                  </span>
                  <DkBadge tone="neutral">
                    <Star className="h-3 w-3" /> {sentiment.average_rating?.toFixed(1)} avg
                  </DkBadge>
                  <DkBadge tone="success">{sentiment.positive} positive</DkBadge>
                  <DkBadge tone="neutral">{sentiment.neutral} neutral</DkBadge>
                  <DkBadge tone="danger">{sentiment.negative} negative</DkBadge>
                  {sentiment.average_sentiment != null && (
                    <span className="text-sm text-[var(--dk-fg-2)]">
                      score {sentiment.average_sentiment.toFixed(2)}
                    </span>
                  )}
                </DkCardContent>
              </DkCard>
            )}

            <DkCard>
              <DkCardContent className="flex flex-col gap-3 py-4">
                <span className="font-display font-semibold text-ink">{selected.title}</span>
                {selected.responses.length === 0 ? (
                  <p className="text-sm text-[var(--dk-fg-2)]">No responses yet.</p>
                ) : (
                  <ul className="flex flex-col divide-y divide-[var(--dk-border)]">
                    {selected.responses.map((r) => (
                      <li key={r.id} className="flex flex-col gap-1 py-2">
                        <div className="flex items-center gap-2">
                          <DkBadge tone="neutral">
                            <Star className="h-3 w-3" /> {r.rating}
                          </DkBadge>
                          {r.sentiment && (
                            <DkBadge tone={sentimentTone[r.sentiment]}>{r.sentiment}</DkBadge>
                          )}
                          <span className="text-xs text-[var(--dk-fg-muted)]">
                            {r.respondent || "anon"} · {formatDate(r.created_at)}
                          </span>
                        </div>
                        {r.comment && <p className="text-sm text-ink">{r.comment}</p>}
                      </li>
                    ))}
                  </ul>
                )}

                <div className="flex flex-col gap-2 rounded-xl bg-[var(--dk-bg)] p-3">
                  <div className="flex gap-2">
                    <DkInput
                      placeholder="Respondent"
                      value={resp.respondent}
                      onChange={(e) => setResp({ ...resp, respondent: e.target.value })}
                    />
                    <DkSelect
                      className="w-24"
                      value={String(resp.rating)}
                      onChange={(e) => setResp({ ...resp, rating: Number(e.target.value) })}
                    >
                      {[5, 4, 3, 2, 1].map((n) => (
                        <option key={n} value={n}>
                          {n} ★
                        </option>
                      ))}
                    </DkSelect>
                  </div>
                  <DkTextarea
                    rows={2}
                    placeholder="Comment (AI sentiment analysed)…"
                    value={resp.comment}
                    onChange={(e) => setResp({ ...resp, comment: e.target.value })}
                  />
                  <div>
                    <DkButton onClick={submitResponse} loading={busy}>
                      Submit response
                    </DkButton>
                  </div>
                </div>
              </DkCardContent>
            </DkCard>
          </div>
        ) : (
          <DkCard>
            <DkCardContent className="flex items-center gap-2 py-10 text-sm text-[var(--dk-fg-2)]">
              <MessageSquare className="h-5 w-5" /> Select a survey to view responses.
            </DkCardContent>
          </DkCard>
        )}
      </div>

      <DkDialog open={createOpen} onClose={() => setCreateOpen(false)}>
        <DkDialogHeader title="New survey" onClose={() => setCreateOpen(false)} />
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
              placeholder="Q2 stakeholder survey"
            />
          </div>
        </DkDialogContent>
        <DkDialogFooter>
          <DkButton variant="secondary" onClick={() => setCreateOpen(false)}>
            Cancel
          </DkButton>
          <DkButton onClick={create} loading={busy}>
            Create
          </DkButton>
        </DkDialogFooter>
      </DkDialog>
    </div>
  );
}
