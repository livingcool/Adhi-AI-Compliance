"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Cpu,
  FileText,
  MessageSquare,
  ScanSearch,
  AlertTriangle,
  BarChart3,
  Settings,
  Shield,
  LogOut,
  User,
} from "lucide-react";
import { clearToken, getUser } from "@/lib/auth";

const navItems = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/systems", icon: Cpu, label: "AI Systems" },
  { href: "/regulations", icon: FileText, label: "Regulations" },
  { href: "/chat", icon: MessageSquare, label: "Compliance Chat" },
  { href: "/bias", icon: ScanSearch, label: "Bias Auditor" },
  { href: "/incidents", icon: AlertTriangle, label: "Incidents" },
  { href: "/reports", icon: BarChart3, label: "Reports" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

interface SidebarProps {
  onNavigate?: () => void;
}

export default function Sidebar({ onNavigate }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const user = getUser();

  const handleLogout = () => {
    clearToken();
    router.replace("/login");
  };

  return (
    <aside className="glass-sidebar w-60 flex-shrink-0 flex flex-col h-screen" role="navigation" aria-label="Main navigation">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-white/[0.06]">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-blue-500 flex items-center justify-center glow-blue flex-shrink-0">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="font-heading font-black text-white tracking-[0.25em] text-[11px] uppercase">
              ROOTEDAI
            </p>
            <p className="text-[10px] text-[rgb(163,163,163)] tracking-wide mt-0.5">
              Compliance Platform
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto" aria-label="Primary">
        {navItems.map(({ href, icon: Icon, label }) => {
          const isActive =
            pathname === href ||
            (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              onClick={onNavigate}
              aria-current={isActive ? "page" : undefined}
              className={`relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 group ${
                isActive
                  ? "text-blue-400"
                  : "text-[rgb(163,163,163)] hover:text-white hover:bg-white/[0.05]"
              }`}
            >
              {/* Active pill */}
              {isActive && (
                <motion.div
                  layoutId="active-nav-pill"
                  className="absolute inset-0 rounded-xl bg-blue-500/15 border border-blue-500/25"
                  transition={{ type: "spring", stiffness: 380, damping: 34 }}
                />
              )}
              <Icon className="w-4 h-4 flex-shrink-0 relative z-10" />
              <span className="relative z-10">{label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Status footer */}
      <div className="px-3 py-3 border-t border-white/[0.06] space-y-2">
        {/* Platform status */}
        <div className="glass-card p-3 rounded-xl">
          <p className="text-[rgb(115,115,115)] font-medium uppercase tracking-wider text-[10px] mb-1.5">
            Platform Status
          </p>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            <span className="text-white font-medium text-xs">All systems normal</span>
          </div>
        </div>

        {/* User info + logout */}
        <div className="flex items-center gap-2.5 px-2 py-2">
          <div className="w-7 h-7 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
            <User className="w-3.5 h-3.5 text-blue-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-white truncate">
              {user?.name || user?.email || "Admin"}
            </p>
            {user?.email && user.name && (
              <p className="text-[10px] text-[rgb(115,115,115)] truncate">
                {user.email}
              </p>
            )}
          </div>
          <button
            onClick={handleLogout}
            aria-label="Sign out"
            className="p-1.5 rounded-lg text-[rgb(115,115,115)] hover:text-red-400 hover:bg-red-500/10 transition-all"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
