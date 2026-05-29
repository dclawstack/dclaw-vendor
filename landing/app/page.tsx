import {
  ArrowRight,
  ChevronRight,
  Sparkles,
  Building2,
  FileText,
  PackageCheck,
  LayoutDashboard,
  Bot,
  Tags,
  ClipboardCheck,
  Gauge,
  Search,
  Server,
  Database,
  Activity,
  CheckCircle2,
  Mail,
  ShieldCheck,
  Boxes,
} from "lucide-react";

function Github({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden className={className}>
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.27-1.68-1.27-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.76 2.69 1.25 3.35.96.1-.75.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.69 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.46.11-3.04 0 0 .97-.31 3.18 1.18.92-.26 1.91-.39 2.89-.39.98 0 1.97.13 2.89.39 2.21-1.49 3.18-1.18 3.18-1.18.62 1.58.23 2.75.11 3.04.73.81 1.18 1.84 1.18 3.1 0 4.42-2.7 5.39-5.27 5.68.42.36.78 1.06.78 2.14v3.17c0 .31.21.68.8.56C20.21 21.39 23.5 17.08 23.5 12 23.5 5.65 18.35.5 12 .5z" />
    </svg>
  );
}

function Linkedin({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden className={className}>
      <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.86-3.04-1.86 0-2.14 1.45-2.14 2.95v5.66H9.35V9h3.41v1.56h.05c.48-.9 1.64-1.86 3.38-1.86 3.61 0 4.27 2.38 4.27 5.48v6.27zM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .78 0 1.73v20.54C0 23.22.79 24 1.77 24h20.45c.99 0 1.78-.78 1.78-1.73V1.73C24 .78 23.21 0 22.22 0z" />
    </svg>
  );
}

/* Live app URL — overridable per environment, defaults to local dev (:3019). */
const APP_URL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3060";
const REPO_URL = "https://github.com/dclawstack/dclaw-vendor";

/* ------------------------------------------------------------------ */
/* Section components                                                 */
/* ------------------------------------------------------------------ */

function NavBar() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-white/70 border-b border-[var(--dk-border)]">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <a href="#top" className="flex items-center gap-2.5">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/brand/logos/dclaw-icon-purple.svg" alt="" aria-hidden="true" className="w-9 h-9" />
          <span className="font-bold text-lg tracking-tight">DClaw</span>
          <span className="hidden sm:inline text-xs text-[var(--dk-fg-3)] font-medium tracking-wider uppercase ml-1 mt-0.5">
            Vendor
          </span>
        </a>
        <nav className="hidden md:flex items-center gap-7 text-sm font-medium text-[var(--dk-fg-2)]">
          <a href="#features" className="hover:text-[var(--dk-purple-800)] transition">Features</a>
          <a href="#lifecycle" className="hover:text-[var(--dk-purple-800)] transition">Lifecycle</a>
          <a href="#analytics" className="hover:text-[var(--dk-purple-800)] transition">Analytics</a>
          <a href="#deploy" className="hover:text-[var(--dk-purple-800)] transition">Deploy</a>
        </nav>
        <div className="flex items-center gap-2.5">
          <a
            href={REPO_URL}
            className="hidden sm:flex items-center gap-1.5 text-sm font-medium text-[var(--dk-fg-2)] hover:text-[var(--dk-purple-800)] transition"
          >
            <Github className="w-4 h-4" /> GitHub
          </a>
          <a
            href={APP_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 text-sm font-semibold rounded-full bg-[var(--dk-purple-700)] text-white px-4 py-2 hover:bg-[var(--dk-purple-800)] transition shadow-sm"
          >
            Launch app <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section
      id="top"
      className="relative overflow-hidden text-white"
      style={{
        background:
          "radial-gradient(circle at 88% 12%, var(--dk-purple-500) 0%, var(--dk-purple-700) 32%, var(--dk-purple-900) 80%)",
      }}
    >
      <div className="dk-grain absolute inset-0 pointer-events-none" />
      <div className="relative max-w-7xl mx-auto px-6 pt-24 pb-32 lg:pt-32 lg:pb-40">
        <div className="dk-fade-in">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/10 border border-white/20 backdrop-blur-sm px-3.5 py-1.5 text-xs font-semibold tracking-wider uppercase mb-7">
            <Sparkles className="w-3.5 h-3.5" /> AI-native procurement
          </div>
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold leading-[1.04] tracking-tight max-w-4xl">
            Your vendor operations, supercharged.
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-white/80 max-w-2xl leading-relaxed">
            A centralized supplier directory, purchase orders with receive tracking,
            onboarding workflows, and performance scoring — all guided by a first-class
            AI Vendor Copilot.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-3">
            <a
              href={APP_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-full bg-white text-[var(--dk-purple-900)] px-6 py-3 font-semibold hover:bg-[var(--dk-purple-50)] transition shadow-lg"
            >
              Launch the app <ArrowRight className="w-4 h-4" />
            </a>
            <a
              href="#features"
              className="inline-flex items-center gap-2 rounded-full bg-white/10 border border-white/30 backdrop-blur-sm text-white px-6 py-3 font-semibold hover:bg-white/20 transition"
            >
              Explore features <ChevronRight className="w-4 h-4" />
            </a>
          </div>

          <div className="mt-14 grid grid-cols-2 sm:grid-cols-4 gap-6 max-w-3xl">
            {[
              { v: "21", l: "API Endpoints" },
              { v: "3", l: "Core Entities" },
              { v: "40", l: "Automated Tests" },
              { v: "100", l: "Test Pass Rate" },
            ].map((s) => (
              <div key={s.l} className="border-l-2 border-white/30 pl-4">
                <div className="text-3xl font-bold tracking-tight">{s.v}</div>
                <div className="text-xs uppercase tracking-wider text-white/60 mt-1">{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      <svg
        className="absolute bottom-0 left-0 right-0 w-full h-12"
        viewBox="0 0 1440 48"
        preserveAspectRatio="none"
        aria-hidden
      >
        <path d="M0 48 L0 24 Q720 -24 1440 24 L1440 48 Z" fill="white" />
      </svg>
    </section>
  );
}

function LogoStrip() {
  const logos = [
    "PostgreSQL", "FastAPI", "SQLAlchemy", "React", "TypeScript",
    "Docker", "Kubernetes", "Tailwind", "Next.js", "Pydantic",
  ];
  return (
    <section className="bg-white border-b border-[var(--dk-border)]">
      <div className="max-w-7xl mx-auto px-6 py-10">
        <p className="text-center text-xs uppercase tracking-[0.2em] text-[var(--dk-fg-3)] mb-6">
          Built on the stack you trust
        </p>
        <div className="flex flex-wrap justify-center items-center gap-x-10 gap-y-4">
          {logos.map((l) => (
            <span
              key={l}
              className="text-[var(--dk-fg-3)] font-semibold text-base tracking-tight grayscale opacity-70 hover:opacity-100 transition"
            >
              {l}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

interface FeatureGroup {
  eyebrow: string;
  title: string;
  description: string;
  features: { icon: React.ComponentType<{ className?: string }>; title: string; body: string }[];
}

const groups: FeatureGroup[] = [
  {
    eyebrow: "Foundation",
    title: "Every supplier, end-to-end.",
    description:
      "Keep your vendor book, purchase orders, and receiving in one continuous flow — no spreadsheets, no context lost between handoffs.",
    features: [
      {
        icon: Building2,
        title: "Vendor Directory",
        body: "A centralized supplier database with search, status filters, and payment terms. Track active, inactive, and blacklisted vendors at a glance.",
      },
      {
        icon: FileText,
        title: "Purchase Orders",
        body: "Raise POs against any vendor with inline line items. Totals recompute in real time as quantities and prices change.",
      },
      {
        icon: PackageCheck,
        title: "Receiving & Line Items",
        body: "Track partial receipts per line item, move POs from draft to received, and always know what's still outstanding.",
      },
      {
        icon: LayoutDashboard,
        title: "Real-Time Dashboard",
        body: "Active vendors, open POs, pending deliveries, and total spend — with a recent-orders feed and vendors-by-status breakdown.",
      },
    ],
  },
  {
    eyebrow: "Intelligence",
    title: "AI that works your vendor book.",
    description:
      "A first-class AI Vendor Copilot threads through every screen — evaluating risk, enriching profiles, and scoring performance so your team moves faster.",
    features: [
      {
        icon: Bot,
        title: "AI Vendor Copilot",
        body: "Evaluate, onboard, and manage vendors with an LLM copilot that flags risk and predicts performance — local Ollama or cloud, your choice.",
      },
      {
        icon: Tags,
        title: "Auto Classification",
        body: "Vendors are automatically categorized by industry and tier on create, with web enrichment to fill in the gaps.",
      },
      {
        icon: ClipboardCheck,
        title: "Onboarding Workflow",
        body: "Collect documents, validate them automatically, and route approvals to activate new vendors faster.",
      },
      {
        icon: Gauge,
        title: "Performance Scoring",
        body: "Score vendors 0–100 across quality, delivery, cost, and compliance, with trends and benchmarks against peers.",
      },
    ],
  },
];

function FeatureGroupBlock({ group }: { group: FeatureGroup }) {
  return (
    <div className="mb-24">
      <div className="max-w-3xl mb-12">
        <div className="inline-block text-xs font-bold uppercase tracking-[0.18em] text-[var(--dk-purple-700)] bg-[var(--dk-purple-100)] px-3 py-1 rounded-full mb-4">
          {group.eyebrow}
        </div>
        <h3 className="text-4xl sm:text-5xl font-bold leading-tight tracking-tight text-[var(--dk-ink)]">
          {group.title}
        </h3>
        <p className="mt-4 text-lg text-[var(--dk-fg-2)] leading-relaxed">
          {group.description}
        </p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {group.features.map((f) => {
          const Icon = f.icon;
          return (
            <div
              key={f.title}
              className="group rounded-2xl border border-[var(--dk-border)] bg-white p-6 hover:border-[var(--dk-purple-300)] hover:shadow-lg hover:shadow-[var(--dk-purple-100)]/50 transition"
            >
              <div className="w-11 h-11 rounded-xl bg-[var(--dk-purple-100)] text-[var(--dk-purple-700)] flex items-center justify-center mb-4 group-hover:bg-[var(--dk-purple-700)] group-hover:text-white transition">
                <Icon className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-[var(--dk-ink)] text-lg tracking-tight">{f.title}</h4>
              <p className="mt-1.5 text-[var(--dk-fg-2)] text-[15px] leading-relaxed">{f.body}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Features() {
  return (
    <section id="features" className="bg-white py-24 sm:py-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-20">
          <div className="inline-block text-xs font-bold uppercase tracking-[0.18em] text-[var(--dk-purple-700)] bg-[var(--dk-purple-100)] px-3 py-1 rounded-full mb-4">
            What it does
          </div>
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight">
            Everything procurement needs to{" "}
            <span className="text-[var(--dk-purple-700)]">manage vendors</span>.
          </h2>
          <p className="mt-5 text-lg text-[var(--dk-fg-2)] leading-relaxed">
            Purpose-built for procurement teams. No bloated suite — just the tools that move
            supplier work forward, with a clean UI and a rock-solid API underneath.
          </p>
        </div>
        {groups.map((g) => (
          <FeatureGroupBlock key={g.title} group={g} />
        ))}
      </div>
    </section>
  );
}

function LifecycleSection() {
  const stages = [
    { name: "Draft", color: "bg-slate-400", desc: "PO created" },
    { name: "Sent", color: "bg-blue-500", desc: "Issued to vendor" },
    { name: "Partial", color: "bg-amber-500", desc: "Some items received" },
    { name: "Received", color: "bg-green-500", desc: "Fully delivered" },
    { name: "Cancelled", color: "bg-red-500", desc: "Voided" },
  ];
  return (
    <section id="lifecycle" className="bg-[var(--dk-bg-tint)] py-24 sm:py-32 border-y border-[var(--dk-border)]">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-block text-xs font-bold uppercase tracking-[0.18em] text-[var(--dk-purple-700)] bg-[var(--dk-purple-100)] px-3 py-1 rounded-full mb-4">
            Lifecycle
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
            Track every PO from draft to delivered.
          </h2>
          <p className="mt-5 text-lg text-[var(--dk-fg-2)] leading-relaxed">
            Move purchase orders through clear stages and watch totals and receipts update in real time.
          </p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {stages.map((stage, i) => (
            <div
              key={i}
              className="relative rounded-xl border border-[var(--dk-border)] bg-white p-4 hover:shadow-md transition"
            >
              <div className={`w-3 h-3 rounded-full ${stage.color} mb-3`} />
              <h4 className="font-semibold text-sm text-[var(--dk-ink)]">{stage.name}</h4>
              <p className="text-xs text-[var(--dk-fg-3)] mt-1">{stage.desc}</p>
              {i < stages.length - 1 && (
                <ChevronRight className="absolute -right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-[var(--dk-border)] hidden lg:block" />
              )}
            </div>
          ))}
        </div>
        <div className="mt-12 p-6 rounded-2xl border border-[var(--dk-border)] bg-white">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[
              { title: "Acme Corp · PO-3F9A", value: "$41.00", recv: "2 / 5 received", stage: "Partial" },
              { title: "Globex Supply · PO-1C7E", value: "$120.00", recv: "0 / 8 received", stage: "Sent" },
              { title: "Initech Parts · PO-9B2D", value: "$35.00", recv: "4 / 4 received", stage: "Received" },
            ].map((po, i) => (
              <div key={i} className="rounded-xl border border-[var(--dk-border)] p-4">
                <p className="font-medium text-sm text-[var(--dk-ink)]">{po.title}</p>
                <p className="text-lg font-bold mt-1">{po.value}</p>
                <div className="flex items-center justify-between mt-3">
                  <span className="text-xs text-[var(--dk-fg-3)]">{po.stage}</span>
                  <span className="text-xs font-medium text-[var(--dk-purple-700)]">{po.recv}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function HowItWorksSection() {
  const steps = [
    {
      icon: Building2,
      title: "Add your vendors",
      desc: "Build a centralized directory — contacts, payment terms, and status. Let AI classify and enrich each profile.",
    },
    {
      icon: FileText,
      title: "Raise purchase orders",
      desc: "Create POs with line items, send them to vendors, and track partial receipts as goods arrive.",
    },
    {
      icon: Gauge,
      title: "Track & score",
      desc: "Monitor spend on the dashboard and score vendor performance across quality, delivery, cost, and compliance.",
    },
  ];
  return (
    <section className="bg-white py-24 sm:py-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-block text-xs font-bold uppercase tracking-[0.18em] text-[var(--dk-purple-700)] bg-[var(--dk-purple-100)] px-3 py-1 rounded-full mb-4">
            How it works
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
            From supplier to spend in 3 steps.
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {steps.map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className="relative text-center">
                <div className="w-16 h-16 mx-auto rounded-2xl bg-[var(--dk-purple-700)] flex items-center justify-center mb-6">
                  <Icon className="w-7 h-7 text-white" />
                </div>
                <span className="text-xs font-bold text-[var(--dk-purple-700)] tracking-wider">0{i + 1}</span>
                <h3 className="text-xl font-semibold text-[var(--dk-ink)] mt-2 mb-3">{item.title}</h3>
                <p className="text-sm text-[var(--dk-fg-2)] leading-relaxed">{item.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function AnalyticsSection() {
  return (
    <section id="analytics" className="bg-[var(--dk-bg-tint)] py-24 sm:py-32 border-y border-[var(--dk-border)]">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <div className="inline-block text-xs font-bold uppercase tracking-[0.18em] text-[var(--dk-purple-700)] bg-[var(--dk-purple-100)] px-3 py-1 rounded-full mb-4">
              Analytics
            </div>
            <h2 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
              Know your spend instantly.
            </h2>
            <p className="mt-5 text-lg text-[var(--dk-fg-2)] leading-relaxed">
              A real-time dashboard with active vendors, open POs, pending deliveries, and total spend.
              Every number updates as your team works — no refresh required.
            </p>
            <div className="mt-7 flex flex-wrap gap-2">
              {["Active vendors", "Open POs", "Pending delivery", "Total spend", "Vendors by status"].map((t) => (
                <span
                  key={t}
                  className="inline-flex items-center gap-1.5 rounded-full bg-[var(--dk-purple-100)] text-[var(--dk-purple-800)] text-xs font-semibold px-3 py-1.5"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" /> {t}
                </span>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Active Vendors", value: "248", sub: "12 onboarding", color: "bg-blue-50 border-blue-100" },
              { label: "Open POs", value: "37", sub: "9 pending delivery", color: "bg-purple-50 border-purple-100" },
              { label: "Total Spend", value: "$1.4M", sub: "this quarter", color: "bg-green-50 border-green-100" },
              { label: "Avg Performance", value: "82", sub: "across 10 KPIs", color: "bg-amber-50 border-amber-100" },
            ].map((card, i) => (
              <div key={i} className={`rounded-xl border p-4 ${card.color}`}>
                <p className="text-xs font-medium text-[var(--dk-fg-3)]">{card.label}</p>
                <p className="text-2xl font-bold mt-1 text-[var(--dk-ink)]">{card.value}</p>
                <p className="text-xs text-[var(--dk-fg-3)] mt-0.5">{card.sub}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function DeploySection() {
  return (
    <section id="deploy" className="bg-white py-24 sm:py-32">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center max-w-3xl mx-auto mb-14">
          <div className="inline-block text-xs font-bold uppercase tracking-[0.18em] text-[var(--dk-purple-700)] bg-[var(--dk-purple-100)] px-3 py-1 rounded-full mb-4">
            Deploy
          </div>
          <h2 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
            Self-hosted. Your data, your perimeter.
          </h2>
          <p className="mt-5 text-lg text-[var(--dk-fg-2)] leading-relaxed">
            Ship the platform as a Helm chart plus container images. Install on any Kubernetes cluster.
            Your supplier data never leaves your infrastructure.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {[
            { icon: Server, t: "Helm + container images", b: "Helm chart at helm/ in the monorepo. GHCR-published images for backend and frontend." },
            { icon: Database, t: "Postgres, schema-isolated", b: "PostgreSQL 16 (Neon or self-hosted). Domain tables live in their own schema, cleanly separated." },
            { icon: Activity, t: "Tested & observable", b: "Async FastAPI with a full pytest suite, health endpoints, and CI on every push out of the box." },
          ].map((b) => {
            const Icon = b.icon;
            return (
              <div key={b.t} className="rounded-2xl bg-[var(--dk-bg-tint)] border border-[var(--dk-border)] p-7">
                <Icon className="w-8 h-8 text-[var(--dk-purple-700)]" />
                <h4 className="mt-4 font-bold text-lg tracking-tight">{b.t}</h4>
                <p className="mt-1.5 text-[var(--dk-fg-2)] text-[15px] leading-relaxed">{b.b}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function CTASection() {
  return (
    <section
      id="cta"
      className="relative overflow-hidden text-white"
      style={{
        background:
          "radial-gradient(circle at 12% 88%, var(--dk-purple-500) 0%, var(--dk-purple-700) 32%, var(--dk-purple-900) 80%)",
      }}
    >
      <div className="dk-grain absolute inset-0 pointer-events-none" />
      <div className="relative max-w-5xl mx-auto px-6 py-24 sm:py-32 text-center">
        <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight max-w-3xl mx-auto">
          Ready to take control of your vendors?
        </h2>
        <p className="mt-6 text-lg sm:text-xl text-white/80 max-w-2xl mx-auto leading-relaxed">
          Open the app and start evaluating, onboarding, and tracking your suppliers —
          all in one self-hosted platform.
        </p>
        <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
          <a
            href={APP_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-full bg-white text-[var(--dk-purple-900)] px-7 py-3.5 font-semibold hover:bg-[var(--dk-purple-50)] transition shadow-xl"
          >
            Launch the app <ArrowRight className="w-4 h-4" />
          </a>
          <a
            href={REPO_URL}
            className="inline-flex items-center gap-2 rounded-full bg-white/10 border border-white/30 backdrop-blur-sm text-white px-7 py-3.5 font-semibold hover:bg-white/20 transition"
          >
            <Github className="w-4 h-4" /> View on GitHub
          </a>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="bg-[var(--dk-purple-900)] text-white/70">
      <div className="max-w-7xl mx-auto px-6 py-14">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2.5">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/brand/logos/dclaw-icon-white.svg" alt="" aria-hidden="true" className="w-9 h-9" />
              <span className="font-bold text-white text-lg tracking-tight">DClaw Vendor</span>
            </div>
            <p className="mt-4 text-sm leading-relaxed max-w-md">
              An AI-native vendor management platform. Supplier directory, purchase orders,
              onboarding, and performance scoring — all self-hosted and under your control.
            </p>
          </div>
          <div>
            <h5 className="text-xs uppercase tracking-wider text-white font-bold mb-3">Product</h5>
            <ul className="space-y-2 text-sm">
              <li><a href="#features" className="hover:text-white transition">Features</a></li>
              <li><a href="#lifecycle" className="hover:text-white transition">Lifecycle</a></li>
              <li><a href="#analytics" className="hover:text-white transition">Analytics</a></li>
              <li><a href="#deploy" className="hover:text-white transition">Deploy</a></li>
            </ul>
          </div>
          <div>
            <h5 className="text-xs uppercase tracking-wider text-white font-bold mb-3">Connect</h5>
            <ul className="space-y-2 text-sm">
              <li>
                <a href={REPO_URL} className="hover:text-white transition inline-flex items-center gap-1.5">
                  <Github className="w-3.5 h-3.5" /> GitHub
                </a>
              </li>
              <li>
                <a href="https://www.linkedin.com/company/oneconvergence" className="hover:text-white transition inline-flex items-center gap-1.5">
                  <Linkedin className="w-3.5 h-3.5" /> LinkedIn
                </a>
              </li>
              <li>
                <a href="mailto:hello@dkube.io" className="hover:text-white transition inline-flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5" /> hello@dkube.io
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-12 pt-6 border-t border-white/10 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 text-xs">
          <div>© 2026 One Convergence — DClaw Vendor.</div>
          <div className="text-white/50 inline-flex items-center gap-2">
            <ShieldCheck className="w-3.5 h-3.5" /> Self-hosted · Powered by DKube
            <Boxes className="w-3.5 h-3.5" />
          </div>
        </div>
      </div>
    </footer>
  );
}

export default function HomePage() {
  return (
    <main className="flex-1">
      <NavBar />
      <Hero />
      <LogoStrip />
      <Features />
      <LifecycleSection />
      <HowItWorksSection />
      <AnalyticsSection />
      <DeploySection />
      <CTASection />
      <Footer />
    </main>
  );
}
