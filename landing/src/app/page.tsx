import {
  ArrowRight,
  BarChart3,
  Building2,
  ClipboardCheck,
  FileText,
  Sparkles,
} from "lucide-react";

const APP_URL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3019";

const features = [
  {
    icon: Sparkles,
    title: "AI Vendor Copilot",
    body: "Evaluate, onboard, and manage vendors with an LLM copilot that flags risk and predicts performance.",
  },
  {
    icon: Building2,
    title: "Vendor directory",
    body: "A centralized supplier database with AI classification and web enrichment — built to track thousands of vendors.",
  },
  {
    icon: ClipboardCheck,
    title: "Onboarding workflow",
    body: "Collect documents, validate them automatically, and route approvals to activate vendors faster.",
  },
  {
    icon: FileText,
    title: "Purchase orders",
    body: "Raise POs with line items, track partial receipts, and watch totals recompute in real time.",
  },
  {
    icon: BarChart3,
    title: "Performance tracking",
    body: "Score vendors 0–100 across quality, delivery, cost, and compliance — with trends and benchmarks.",
  },
];

export default function LandingPage() {
  return (
    <div className="flex flex-col">
      {/* Nav */}
      <header className="mx-auto flex w-full max-w-container items-center justify-between px-6 py-6">
        <img
          src="/brand/dclaw-logo-purple-h48.png"
          alt="DClaw"
          className="h-7 w-auto"
        />
        <a
          href={APP_URL}
          className="inline-flex h-10 items-center gap-2 rounded-pill bg-brand px-5 text-sm font-semibold text-white transition-all duration-base ease-out-quart hover:bg-[var(--dk-purple-800)] hover:shadow-brand"
        >
          Open the app <ArrowRight className="h-4 w-4" />
        </a>
      </header>

      {/* Hero */}
      <section className="mx-auto w-full max-w-container px-6 pb-20 pt-16 text-center md:pt-24">
        <p className="mb-4 inline-flex items-center gap-2 rounded-pill bg-[var(--dk-purple-100)] px-4 py-1.5 text-xs font-semibold uppercase tracking-wide text-brand">
          <Sparkles className="h-3.5 w-3.5" /> AI-native procurement
        </p>
        <h1 className="mx-auto max-w-4xl font-display text-4xl font-bold leading-tight tracking-snug text-ink md:text-6xl">
          Vendor &amp; purchase order management, with an AI Copilot built in.
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-fg-2">
          DClaw Vendor helps procurement teams evaluate, onboard, and manage
          suppliers end-to-end — a centralized directory, purchase orders,
          onboarding workflows, and performance scoring, all guided by AI.
        </p>
        <div className="mt-10 flex items-center justify-center gap-4">
          <a
            href={APP_URL}
            className="inline-flex h-12 items-center gap-2 rounded-pill bg-brand px-8 text-md font-semibold text-white transition-all duration-base ease-out-quart hover:bg-[var(--dk-purple-800)] hover:shadow-brand"
          >
            Launch DClaw Vendor <ArrowRight className="h-4 w-4" />
          </a>
          <a
            href="#features"
            className="inline-flex h-12 items-center rounded-pill border border-[var(--dk-border-strong)] bg-white px-8 text-md font-semibold text-ink transition-colors duration-base hover:border-brand hover:text-brand"
          >
            See features
          </a>
        </div>
      </section>

      {/* Features */}
      <section
        id="features"
        className="mx-auto w-full max-w-container px-6 py-16"
      >
        <h2 className="text-center font-display text-3xl font-bold tracking-snug text-ink md:text-4xl">
          Everything procurement needs
        </h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-md leading-relaxed text-fg-2">
          One workspace for suppliers, orders, and performance — with AI doing
          the heavy lifting.
        </p>
        <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {features.map((f) => (
            <div
              key={f.title}
              className="flex flex-col gap-4 rounded-2xl border border-[var(--dk-border)] bg-white p-6 transition-shadow duration-base hover:shadow-md"
            >
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--dk-purple-50)] text-brand">
                <f.icon className="h-5 w-5" />
              </div>
              <h3 className="font-display text-lg font-semibold text-ink">
                {f.title}
              </h3>
              <p className="text-sm leading-relaxed text-fg-2">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Final CTA */}
      <section className="mx-auto w-full max-w-container px-6 py-16">
        <div className="flex flex-col items-center gap-6 rounded-2xl bg-ink px-8 py-16 text-center">
          <h2 className="max-w-2xl font-display text-3xl font-bold tracking-snug text-white md:text-4xl">
            Bring AI to your vendor operations
          </h2>
          <p className="max-w-xl text-md leading-relaxed text-[var(--dk-gray-300)]">
            Open the app and start evaluating, onboarding, and tracking your
            suppliers today.
          </p>
          <a
            href={APP_URL}
            className="inline-flex h-12 items-center gap-2 rounded-pill bg-white px-8 text-md font-semibold text-ink transition-transform duration-base hover:-translate-y-0.5"
          >
            Open DClaw Vendor <ArrowRight className="h-4 w-4" />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="mx-auto w-full max-w-container px-6 py-10">
        <div className="flex flex-col items-center justify-between gap-4 border-t border-[var(--dk-border)] pt-8 text-sm text-fg-muted md:flex-row">
          <div className="flex items-center gap-2">
            <img
              src="/brand/dclaw-logo-purple-h48.png"
              alt="DClaw"
              className="h-5 w-auto"
            />
            <span>© One Convergence</span>
          </div>
          <span>Powered by DKube — the Private AI platform.</span>
        </div>
      </footer>
    </div>
  );
}
