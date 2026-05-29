"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Sparkles, X } from "lucide-react";

import { DkButton, DkInput } from "@/components/dk";
import { chatCopilot, type ChatMessage } from "@/lib/api";

const GREETING: ChatMessage = {
  role: "assistant",
  content:
    "Hi! I'm your Vendor Copilot. Ask me about your vendors, purchase orders, spend, or who looks risky.",
};

export function CopilotWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([GREETING]);
  const [suggestions, setSuggestions] = useState<string[]>([
    "How many vendors do I have?",
    "Which vendors look risky?",
    "What's my total spend?",
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, loading]);

  async function send(text: string) {
    const content = text.trim();
    if (!content || loading) return;
    const next = [...messages, { role: "user" as const, content }];
    setMessages(next);
    setInput("");
    setSuggestions([]);
    setLoading(true);
    try {
      const reply = await chatCopilot(next.filter((m) => m !== GREETING));
      setMessages([...next, { role: "assistant", content: reply.reply }]);
      setSuggestions(reply.suggested_actions ?? []);
    } catch {
      setMessages([
        ...next,
        {
          role: "assistant",
          content:
            "I couldn't reach the AI provider. Check the LLM settings (Ollama running / OpenRouter key) and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        aria-label="Open Vendor Copilot"
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-pill bg-brand text-white shadow-brand transition-all duration-base ease-out-quart hover:bg-[var(--dk-purple-800)] hover:scale-105"
      >
        <Sparkles className="h-6 w-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex h-[560px] w-[calc(100vw-3rem)] max-w-sm flex-col overflow-hidden rounded-2xl border border-[var(--dk-border)] bg-white shadow-lg">
      {/* header */}
      <div className="flex items-center justify-between bg-brand px-4 py-3 text-white">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          <span className="font-display font-semibold">Vendor Copilot</span>
        </div>
        <button onClick={() => setOpen(false)} aria-label="Close" className="rounded-pill p-1 hover:bg-white/15">
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* messages */}
      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={m.role === "user" ? "flex justify-end" : "flex justify-start"}
          >
            <div
              className={
                m.role === "user"
                  ? "max-w-[85%] rounded-2xl rounded-br-sm bg-brand px-3.5 py-2 text-sm text-white"
                  : "max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-bl-sm bg-[var(--dk-gray-100)] px-3.5 py-2 text-sm text-ink"
              }
            >
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm bg-[var(--dk-gray-100)] px-3.5 py-2 text-sm text-[var(--dk-fg-muted)]">
              Thinking…
            </div>
          </div>
        )}
      </div>

      {/* suggestions */}
      {suggestions.length > 0 && !loading && (
        <div className="flex flex-wrap gap-2 px-4 pb-2">
          {suggestions.slice(0, 3).map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="rounded-pill border border-[var(--dk-border-strong)] bg-white px-3 py-1 text-xs font-medium text-brand transition-colors hover:bg-[var(--dk-purple-50)]"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* input */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex items-center gap-2 border-t border-[var(--dk-border)] p-3"
      >
        <DkInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the copilot…"
          className="h-10"
        />
        <DkButton type="submit" size="icon" loading={loading} aria-label="Send">
          <Send className="h-4 w-4" />
        </DkButton>
      </form>
    </div>
  );
}
