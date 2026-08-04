"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutGrid, Newspaper, Globe2, Building2, MapPinned, Search, MessagesSquare } from "lucide-react";
import clsx from "clsx";

const NAV = [
  { href: "/", label: "Overview", icon: LayoutGrid },
  { href: "/articles", label: "Intelligence Feed", icon: Newspaper },
  { href: "/countries", label: "Countries", icon: Globe2 },
  { href: "/companies", label: "Companies", icon: Building2 },
  { href: "/map", label: "Asset Map", icon: MapPinned },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex w-64 shrink-0 flex-col border-r border-border bg-surface/60 backdrop-blur-md">
      <div className="flex items-center gap-3 px-6 h-16 border-b border-border">
        <div className="relative w-8 h-8 shrink-0">
          <div className="absolute inset-0 rounded-full border border-signal/40" />
          <div className="absolute inset-1 rounded-full border border-signal/25" />
          <div className="absolute inset-0 origin-center animate-sweep">
            <div className="absolute top-1/2 left-1/2 w-1/2 h-px bg-gradient-to-r from-signal to-transparent" />
          </div>
          <div className="absolute inset-[13px] rounded-full bg-signal shadow-[0_0_8px_2px_rgba(47,214,192,0.6)]" />
        </div>
        <div className="leading-tight">
          <div className="font-display font-semibold text-sm tracking-wide text-ink">GCIIP</div>
          <div className="text-[10px] uppercase tracking-[0.14em] text-ink-faint">Infra Intelligence</div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm transition-colors",
                active
                  ? "bg-surface-3 text-ink border border-border-strong"
                  : "text-ink-muted hover:text-ink hover:bg-surface-2 border border-transparent"
              )}
            >
              <Icon size={16} strokeWidth={1.75} />
              <span>{label}</span>
              {active && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-signal" />}
            </Link>
          );
        })}
      </nav>

      <div className="px-6 py-4 border-t border-border text-[11px] text-ink-faint font-mono">
        SOURCES: RSS / GDELT
        <br />
        FREE-TIER ONLY
      </div>
    </aside>
  );
}
