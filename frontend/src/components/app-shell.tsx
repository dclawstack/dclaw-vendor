"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Building2,
  ClipboardCheck,
  FileText,
  LayoutDashboard,
  MessageSquare,
  Settings,
  ShieldCheck,
} from "lucide-react";

import { DkSidebar } from "@/components/dk";
import { CopilotWidget } from "@/components/copilot-widget";

const groups = [
  {
    items: [
      { label: "Dashboard", href: "/dashboard", icon: <LayoutDashboard className="h-4 w-4" /> },
      { label: "Vendors", href: "/vendors", icon: <Building2 className="h-4 w-4" /> },
      {
        label: "Purchase Orders",
        href: "/purchase-orders",
        icon: <FileText className="h-4 w-4" />,
      },
      {
        label: "Onboarding",
        href: "/onboarding",
        icon: <ClipboardCheck className="h-4 w-4" />,
      },
      {
        label: "Analytics",
        href: "/analytics",
        icon: <BarChart3 className="h-4 w-4" />,
      },
      {
        label: "Feedback",
        href: "/feedback",
        icon: <MessageSquare className="h-4 w-4" />,
      },
      {
        label: "Audits",
        href: "/audits",
        icon: <ShieldCheck className="h-4 w-4" />,
      },
    ],
  },
  {
    label: "Configure",
    items: [
      { label: "Settings", href: "/settings", icon: <Settings className="h-4 w-4" /> },
    ],
  },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  // Root "/" is the bare welcome splash — no sidebar chrome.
  if (pathname === "/") return <>{children}</>;
  return (
    <div className="flex min-h-screen">
      <div className="flex w-60 shrink-0 flex-col border-r border-[var(--dk-border)] bg-white">
        <Link
          href="/dashboard"
          className="flex items-center gap-2 px-5 py-5 font-display text-lg font-bold text-ink"
        >
          <img src="/brand/logos/dclaw-icon-purple.svg" alt="" className="h-6 w-6" />
          DClaw Vendor
        </Link>
        <DkSidebar groups={groups} className="border-r-0" />
      </div>
      <main className="flex-1 overflow-x-hidden bg-[var(--dk-bg)]">
        <div className="mx-auto max-w-6xl px-8 py-10">{children}</div>
      </main>
      <CopilotWidget />
    </div>
  );
}
