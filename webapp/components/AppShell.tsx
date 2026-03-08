"use client";

import { useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Menu } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Sidebar from "@/components/Sidebar";
import AuthGuard from "@/components/AuthGuard";
import { PageTransition } from "@/components/PageTransition";

const PUBLIC_ROUTES = ["/login"];
const ORG_KEY = "adhi_selected_org";


export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const isPublic = PUBLIC_ROUTES.includes(pathname);

  useEffect(() => {
    if (isPublic) return;
    const org = localStorage.getItem(ORG_KEY);
    if (!org) {
      router.replace("/login");
    }
  }, [pathname, isPublic, router]);

  if (isPublic) {
    return <>{children}</>;
  }


  return (
    <AuthGuard>
      <div className="flex h-screen overflow-hidden">
        {/* ── Desktop sidebar ── */}
        <div className="hidden md:block flex-shrink-0">
          <Sidebar onNavigate={() => setMobileOpen(false)} />
        </div>

        {/* ── Mobile overlay sidebar ── */}
        <AnimatePresence>
          {mobileOpen && (
            <>
              {/* Backdrop */}
              <motion.div
                key="backdrop"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm md:hidden"
                onClick={() => setMobileOpen(false)}
                aria-hidden="true"
              />
              {/* Drawer */}
              <motion.div
                key="drawer"
                initial={{ x: -280 }}
                animate={{ x: 0 }}
                exit={{ x: -280 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="fixed inset-y-0 left-0 z-50 md:hidden"
                role="dialog"
                aria-modal="true"
                aria-label="Navigation menu"
              >
                <Sidebar onNavigate={() => setMobileOpen(false)} />
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* ── Main content ── */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Mobile top bar */}
          <div className="md:hidden flex-shrink-0 h-14 glass-sidebar border-b border-white/[0.06] flex items-center gap-3 px-4">
            <button
              onClick={() => setMobileOpen(true)}
              aria-label="Open navigation menu"
              className="p-2 rounded-lg hover:bg-white/[0.05] transition-colors"
            >
              <Menu className="w-5 h-5 text-white" />
            </button>
            <p className="font-heading font-black text-white tracking-[0.25em] text-xs uppercase">
              ROOTEDAI
            </p>
          </div>

          {/* Skip to main content for a11y */}
          <a
            href="#main-content"
            className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-500 focus:text-white focus:rounded-lg focus:text-sm focus:font-medium"
          >
            Skip to main content
          </a>

          <main
            id="main-content"
            className="flex-1 overflow-y-auto dot-grid bg-radial-dark"
          >
            <AnimatePresence mode="wait">
              <PageTransition key={pathname} className="min-h-full">
                {children}
              </PageTransition>
            </AnimatePresence>
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
