"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield,
  Building2,
  ArrowRight,
  Loader2,
  Search,
  CheckCircle2,
  Globe,
} from "lucide-react";

interface Organization {
  id: string;
  name: string;
  slug: string;
}

const ORG_KEY = "adhi_selected_org";

export default function OrgSelectorPage() {
  const router = useRouter();
  const [orgs, setOrgs] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem(ORG_KEY);
    if (stored) {
      router.replace("/");
      return;
    }

    const apiBase = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
    fetch(`${apiBase}/organizations`)
      .then((r) => r.json())
      .then((data: Organization[]) => {
        if (Array.isArray(data) && data.length > 0) {
          setOrgs(data);
        } else {
          setOrgs(DEMO_ORGS);
        }
      })
      .catch(() => setOrgs(DEMO_ORGS))
      .finally(() => setLoading(false));
  }, [router]);

  const handleSelect = (org: Organization) => {
    setSelected(org.id);
    localStorage.setItem(ORG_KEY, JSON.stringify(org));
    setTimeout(() => router.replace("/"), 600);
  };

  const filtered = orgs.filter((o) =>
    o.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[rgb(5,5,5)] dot-grid flex items-center justify-center px-4 py-12">
      {/* Glow */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[400px] bg-blue-500/[0.06] rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[400px] h-[300px] bg-purple-500/[0.04] rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="w-full max-w-2xl relative"
      >
        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex flex-col items-center mb-10"
        >
          <div className="w-14 h-14 rounded-2xl bg-blue-500 flex items-center justify-center glow-blue mb-4">
            <Shield className="w-7 h-7 text-white" />
          </div>
          <h1 className="font-heading font-black text-white tracking-[0.3em] text-2xl uppercase">
            ROOTEDAI
          </h1>
          <p className="text-[rgb(163,163,163)] text-sm mt-1 tracking-wide">
            Adhi Compliance Platform
          </p>
        </motion.div>

        {/* Card */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15 }}
          className="glass-card p-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <Building2 className="w-5 h-5 text-blue-400" />
            <h2 className="text-white font-semibold text-lg">Select Organization</h2>
          </div>
          <p className="text-[rgb(115,115,115)] text-sm mb-6">
            Choose which organization&apos;s compliance dashboard to view
          </p>

          {/* Search */}
          {orgs.length > 3 && (
            <div className="relative mb-4">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[rgb(115,115,115)]" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search organizations..."
                className="w-full bg-white/[0.05] border border-white/[0.10] rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-[rgb(115,115,115)] focus:outline-none focus:border-blue-500/60 transition-all"
              />
            </div>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
            </div>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div className="space-y-3">
                {filtered.map((org, i) => (
                  <motion.button
                    key={org.id}
                    initial={{ opacity: 0, x: -16 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.06 }}
                    onClick={() => handleSelect(org)}
                    disabled={!!selected}
                    className={`w-full flex items-center gap-4 p-4 rounded-xl border transition-all text-left group ${selected === org.id
                        ? "border-blue-500/60 bg-blue-500/10"
                        : "border-white/[0.09] bg-white/[0.03] hover:border-blue-500/40 hover:bg-white/[0.06]"
                      }`}
                  >
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-white/[0.08] flex items-center justify-center flex-shrink-0">
                      <Globe className="w-5 h-5 text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-medium text-sm">{org.name}</p>
                      <p className="text-[rgb(115,115,115)] text-xs mt-0.5 truncate">
                        /{org.slug}
                      </p>
                    </div>
                    {selected === org.id ? (
                      <CheckCircle2 className="w-5 h-5 text-blue-400 flex-shrink-0" />
                    ) : (
                      <ArrowRight className="w-4 h-4 text-[rgb(115,115,115)] group-hover:text-white transition-colors flex-shrink-0" />
                    )}
                  </motion.button>
                ))}

                {filtered.length === 0 && (
                  <div className="text-center py-8 text-[rgb(115,115,115)] text-sm">
                    No organizations found
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          )}
        </motion.div>

        <p className="text-center text-[10px] text-[rgb(115,115,115)] mt-6">
          Protected by RootedAI &mdash; Enterprise AI Governance
        </p>
      </motion.div>
    </div>
  );
}

const DEMO_ORGS: Organization[] = [
  { id: "org_1", name: "RootedAI Technologies", slug: "rootedai" },
  { id: "org_2", name: "Acme Corporation", slug: "acme-corp" },
  { id: "org_3", name: "TechScale Ventures", slug: "techscale" },
];
