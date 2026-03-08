import type { Metadata } from "next";
import { Outfit, Montserrat } from "next/font/google";
import "./globals.css";
import AppShell from "@/components/AppShell";
import { ToastProvider } from "@/components/ui/Toast";
import { FounderAuthProvider, FounderSessionStatus } from "@/lib/founder-auth";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  weight: ["400", "600", "700", "800"],
});

const montserrat = Montserrat({
  variable: "--font-montserrat",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Adhi Compliance | AI Governance Platform",
  description:
    "Enterprise AI compliance monitoring, risk assessment, and regulatory tracking powered by RootedAI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${outfit.variable} ${montserrat.variable} antialiased bg-[rgb(5,5,5)] text-white min-h-screen`}
      >
        <FounderAuthProvider>
          <ToastProvider>
            <AppShell>{children}</AppShell>
            <FounderSessionStatus />
          </ToastProvider>
        </FounderAuthProvider>
      </body>
    </html>
  );
}
