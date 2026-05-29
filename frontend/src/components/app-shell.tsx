"use client";

import Link from "next/link";
import {
  Building2,
  FileText,
  LayoutDashboard,
  Package,
  Settings,
} from "lucide-react";

import { DkSidebar } from "@/components/dk";

const groups = [
  {
    items: [
      { label: "Dashboard", href: "/", icon: <LayoutDashboard className="h-4 w-4" /> },
      { label: "Vendors", href: "/vendors", icon: <Building2 className="h-4 w-4" /> },
      {
        label: "Purchase Orders",
        href: "/purchase-orders",
        icon: <FileText className="h-4 w-4" />,
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
  return (
    <div className="flex min-h-screen">
      <div className="flex w-60 shrink-0 flex-col border-r border-[var(--dk-border)] bg-white">
        <Link
          href="/"
          className="flex items-center gap-2 px-5 py-5 font-display text-lg font-bold text-ink"
        >
          <Package className="h-5 w-5 text-brand" />
          DClaw Vendor
        </Link>
        <DkSidebar groups={groups} className="border-r-0" />
      </div>
      <main className="flex-1 overflow-x-hidden bg-[var(--dk-bg)]">
        <div className="mx-auto max-w-6xl px-8 py-10">{children}</div>
      </main>
    </div>
  );
}
