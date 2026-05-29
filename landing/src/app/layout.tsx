import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: "DClaw Vendor — AI-native vendor & purchase order management",
  description:
    "Evaluate, onboard, and manage vendors end-to-end with an AI Vendor Copilot. Supplier directory, purchase orders, onboarding, and performance tracking.",
  icons: { icon: [{ url: "/favicon.svg", type: "image/svg+xml" }] },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={poppins.variable}>
      <body
        className="min-h-screen bg-background font-sans text-foreground antialiased"
        style={{ fontFamily: "var(--font-poppins), var(--dk-font-sans)" }}
      >
        {children}
      </body>
    </html>
  );
}
