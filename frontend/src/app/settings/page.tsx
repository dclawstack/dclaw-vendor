"use client";

import { useEffect, useState } from "react";
import { Check, KeyRound, Server, Sparkles } from "lucide-react";

import {
  DkBadge,
  DkButton,
  DkCard,
  DkCardContent,
  DkInput,
  DkLabel,
  DkPageHeader,
  DkSelect,
} from "@/components/dk";
import {
  getLLMSettings,
  updateLLMSettings,
  type LLMProvider,
  type LLMSettings,
} from "@/lib/api";

const PROVIDERS: { value: LLMProvider; label: string; hint: string }[] = [
  { value: "auto", label: "Auto", hint: "Try Ollama first, fall back to OpenRouter" },
  { value: "ollama", label: "Ollama (local)", hint: "Use the local Ollama server only" },
  { value: "openrouter", label: "OpenRouter (cloud)", hint: "Use OpenRouter only" },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<LLMSettings | null>(null);
  const [provider, setProvider] = useState<LLMProvider>("auto");
  const [ollamaUrl, setOllamaUrl] = useState("");
  const [ollamaModel, setOllamaModel] = useState("");
  const [orKey, setOrKey] = useState("");
  const [orModel, setOrModel] = useState("");
  const [orUrl, setOrUrl] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function hydrate(s: LLMSettings) {
    setSettings(s);
    setProvider(s.llm_provider);
    setOllamaUrl(s.ollama_base_url);
    setOllamaModel(s.ollama_model);
    setOrModel(s.openrouter_model);
    setOrUrl(s.openrouter_base_url);
    setOrKey(""); // never prefill the secret
  }

  useEffect(() => {
    getLLMSettings()
      .then(hydrate)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load settings"))
      .finally(() => setLoading(false));
  }, []);

  async function save() {
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const updated = await updateLLMSettings({
        llm_provider: provider,
        ollama_base_url: ollamaUrl,
        ollama_model: ollamaModel,
        openrouter_model: orModel,
        openrouter_base_url: orUrl,
        // only send the key if the user typed a new one
        ...(orKey.trim() ? { openrouter_api_key: orKey.trim() } : {}),
      });
      hydrate(updated);
      setSaved(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save settings");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <p className="text-sm text-[var(--dk-fg-2)]">Loading…</p>;

  return (
    <div className="flex flex-col gap-6">
      <DkPageHeader
        eyebrow="Configure"
        title="Settings"
        description="Configure the LLM providers that power the AI Vendor Copilot."
        actions={
          <DkButton onClick={save} loading={saving}>
            {saved ? <Check className="h-4 w-4" /> : null}
            {saved ? "Saved" : "Save changes"}
          </DkButton>
        }
      />

      {error && <p className="text-sm text-[var(--dk-danger)]">{error}</p>}

      {/* Provider selection */}
      <DkCard>
        <DkCardContent className="flex flex-col gap-4 py-6">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-brand" />
            <h2 className="font-display text-lg font-semibold text-ink">Provider</h2>
          </div>
          <div className="flex flex-col gap-1.5 sm:max-w-sm">
            <DkLabel>Active provider</DkLabel>
            <DkSelect
              value={provider}
              onChange={(e) => setProvider(e.target.value as LLMProvider)}
            >
              {PROVIDERS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </DkSelect>
            <p className="text-xs text-[var(--dk-fg-muted)]">
              {PROVIDERS.find((p) => p.value === provider)?.hint}
            </p>
          </div>
        </DkCardContent>
      </DkCard>

      {/* Ollama */}
      <DkCard>
        <DkCardContent className="flex flex-col gap-4 py-6">
          <div className="flex items-center gap-2">
            <Server className="h-5 w-5 text-brand" />
            <h2 className="font-display text-lg font-semibold text-ink">
              Ollama (local primary)
            </h2>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <DkLabel>Endpoint</DkLabel>
              <DkInput
                value={ollamaUrl}
                placeholder="http://localhost:11434"
                onChange={(e) => setOllamaUrl(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Model</DkLabel>
              <DkInput
                value={ollamaModel}
                placeholder="llama3.1"
                onChange={(e) => setOllamaModel(e.target.value)}
              />
            </div>
          </div>
        </DkCardContent>
      </DkCard>

      {/* OpenRouter */}
      <DkCard>
        <DkCardContent className="flex flex-col gap-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <KeyRound className="h-5 w-5 text-brand" />
              <h2 className="font-display text-lg font-semibold text-ink">
                OpenRouter (cloud fallback)
              </h2>
            </div>
            {settings?.openrouter_api_key_set ? (
              <DkBadge tone="success">Key set · {settings.openrouter_api_key_preview}</DkBadge>
            ) : (
              <DkBadge tone="warning">No key</DkBadge>
            )}
          </div>
          <div className="flex flex-col gap-1.5">
            <DkLabel>API token</DkLabel>
            <DkInput
              type="password"
              value={orKey}
              placeholder={
                settings?.openrouter_api_key_set
                  ? "•••••••• (leave blank to keep current)"
                  : "sk-or-v1-…"
              }
              onChange={(e) => setOrKey(e.target.value)}
            />
            <p className="text-xs text-[var(--dk-fg-muted)]">
              Stored server-side; never displayed in full after saving.
            </p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-1.5">
              <DkLabel>Model</DkLabel>
              <DkInput
                value={orModel}
                placeholder="moonshotai/kimi-k2"
                onChange={(e) => setOrModel(e.target.value)}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <DkLabel>Base URL</DkLabel>
              <DkInput
                value={orUrl}
                placeholder="https://openrouter.ai/api/v1"
                onChange={(e) => setOrUrl(e.target.value)}
              />
            </div>
          </div>
        </DkCardContent>
      </DkCard>
    </div>
  );
}
