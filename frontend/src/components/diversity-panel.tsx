"use client";

import { useState } from "react";
import { Users } from "lucide-react";

import {
  DkBadge,
  DkButton,
  DkCard,
  DkCardContent,
  DkCheckbox,
  DkInput,
  DkLabel,
  DkSwitch,
} from "@/components/dk";
import { DIVERSITY_CATEGORIES, updateVendor, type Vendor } from "@/lib/api";

export function DiversityPanel({
  vendor,
  onSaved,
}: {
  vendor: Vendor;
  onSaved: () => void;
}) {
  const [editing, setEditing] = useState(false);
  const [diverse, setDiverse] = useState(vendor.diverse_owned);
  const [certified, setCertified] = useState(vendor.diversity_certified);
  const [cats, setCats] = useState<string[]>(vendor.diversity_categories ?? []);
  const [body, setBody] = useState(vendor.certification_body ?? "");
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await updateVendor(vendor.id, {
        diverse_owned: diverse,
        diversity_certified: certified,
        diversity_categories: cats,
        certification_body: body || null,
      });
      setEditing(false);
      onSaved();
    } finally {
      setSaving(false);
    }
  }

  function toggleCat(c: string) {
    setCats((prev) => (prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]));
  }

  return (
    <DkCard>
      <DkCardContent className="flex flex-col gap-3 py-5">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-brand" />
            <span className="font-display font-semibold text-ink">Diversity</span>
            {vendor.diverse_owned && <DkBadge tone="brand">diverse-owned</DkBadge>}
            {vendor.diversity_certified && <DkBadge tone="success">certified</DkBadge>}
          </div>
          <DkButton variant="secondary" onClick={() => setEditing((v) => !v)}>
            {editing ? "Cancel" : "Edit"}
          </DkButton>
        </div>

        {!editing ? (
          vendor.diverse_owned ? (
            <div className="flex flex-wrap items-center gap-2 text-sm text-ink">
              {(vendor.diversity_categories ?? []).map((c) => (
                <DkBadge key={c} tone="neutral">
                  {c.replace(/_/g, " ")}
                </DkBadge>
              ))}
              {vendor.certification_body && (
                <span className="text-[var(--dk-fg-2)]">· {vendor.certification_body}</span>
              )}
            </div>
          ) : (
            <p className="text-sm text-[var(--dk-fg-2)]">Not marked as diverse-owned.</p>
          )
        ) : (
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-6">
              <label className="flex items-center gap-2 text-sm">
                <DkSwitch
                  checked={diverse}
                  onChange={(e) => setDiverse(e.target.checked)}
                />{" "}
                Diverse-owned
              </label>
              <label className="flex items-center gap-2 text-sm">
                <DkSwitch
                  checked={certified}
                  onChange={(e) => setCertified(e.target.checked)}
                />{" "}
                Certified
              </label>
            </div>
            <div className="flex flex-wrap gap-3">
              {DIVERSITY_CATEGORIES.map((c) => (
                <label key={c} className="flex items-center gap-2 text-sm">
                  <DkCheckbox checked={cats.includes(c)} onChange={() => toggleCat(c)} />
                  {c.replace(/_/g, " ")}
                </label>
              ))}
            </div>
            <div className="flex flex-col gap-1.5 sm:w-72">
              <DkLabel>Certification body</DkLabel>
              <DkInput value={body} onChange={(e) => setBody(e.target.value)} placeholder="NMSDC, WBENC…" />
            </div>
            <div>
              <DkButton onClick={save} loading={saving}>
                Save
              </DkButton>
            </div>
          </div>
        )}
      </DkCardContent>
    </DkCard>
  );
}
