"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  LayoutDashboard,
  BookOpen,
  PenTool,
  Calculator,
  Settings,
  GraduationCap,
  Trophy,
  Target,
  Puzzle,
  BarChart3,
  Clock,
  Lightbulb,
  Sparkles,
  Menu,
  X,
} from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { name: "Home", href: "/", icon: LayoutDashboard },
    { name: "Practice", href: "/practice", icon: Target },
    { name: "Mock Exam", href: "/mock", icon: Clock },
    { name: "Learn", href: "/learn", icon: BookOpen },
    { name: "Strategies", href: "/strategies", icon: Lightbulb },
    { name: "Progress", href: "/progress", icon: BarChart3 },
    { name: "Achievements", href: "/achievements", icon: Trophy },
  ];

  const isActive = (href: string) =>
    pathname === href || (href !== "/" && pathname.startsWith(href));

  return (
    <>
      {/* Top Navigation Bar */}
      <nav className="glass-nav sticky top-0 z-50 w-full">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-3 flex-shrink-0">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/25">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="font-bold text-slate-900 dark:text-white text-lg leading-tight">
                  11+ Tutor
                </h1>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 -mt-0.5 tracking-wider uppercase">
                  Grammar School Prep
                </p>
              </div>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden lg:flex items-center gap-1">
              {navItems.map((item) => {
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                      active
                        ? "bg-white dark:bg-slate-700 text-cyan-600 dark:text-cyan-400 shadow-sm"
                        : "text-slate-600 dark:text-slate-300 hover:bg-white/60 dark:hover:bg-slate-700/60 hover:text-cyan-600 dark:hover:text-cyan-400"
                    }`}
                  >
                    <item.icon className={`w-4 h-4 ${active ? "text-cyan-500" : ""}`} />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>

            {/* Right side: Settings + Mobile Menu */}
            <div className="flex items-center gap-2">
              <Link
                href="/settings"
                className={`p-2.5 rounded-full transition-all ${
                  pathname === "/settings"
                    ? "bg-white dark:bg-slate-700 text-cyan-600 shadow-sm"
                    : "text-slate-500 hover:bg-white/60 dark:hover:bg-slate-700/60 hover:text-cyan-600"
                }`}
              >
                <Settings className="w-5 h-5" />
              </Link>
              <Link
                href="/getting-started"
                className={`hidden sm:flex p-2.5 rounded-full transition-all ${
                  pathname === "/getting-started"
                    ? "bg-white dark:bg-slate-700 text-amber-500 shadow-sm"
                    : "text-slate-500 hover:bg-white/60 dark:hover:bg-slate-700/60 hover:text-amber-500"
                }`}
              >
                <Sparkles className="w-5 h-5" />
              </Link>

              {/* Mobile menu button */}
              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="lg:hidden p-2.5 rounded-full text-slate-600 hover:bg-white/60 dark:hover:bg-slate-700/60 transition-all"
              >
                {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu Dropdown */}
        {mobileOpen && (
          <div className="lg:hidden border-t border-white/30 dark:border-slate-700/50">
            <div className="max-w-7xl mx-auto px-4 py-3 space-y-1">
              {navItems.map((item) => {
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium transition-all ${
                      active
                        ? "bg-white dark:bg-slate-700 text-cyan-600 dark:text-cyan-400 shadow-sm"
                        : "text-slate-600 dark:text-slate-300 hover:bg-white/60"
                    }`}
                  >
                    <item.icon className={`w-5 h-5 ${active ? "text-cyan-500" : "text-slate-400"}`} />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
              <Link
                href="/getting-started"
                onClick={() => setMobileOpen(false)}
                className="flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-white/60 sm:hidden"
              >
                <Sparkles className="w-5 h-5 text-slate-400" />
                <span>Getting Started</span>
              </Link>
            </div>
          </div>
        )}
      </nav>
    </>
  );
}
