import { LucideIcon } from "lucide-react";

export default function KpiCard({
  label,
  value,
  icon: Icon,
  accent = "signal",
}: {
  label: string;
  value: string;
  icon: LucideIcon;
  accent?: "signal" | "amber" | "crimson" | "cobalt";
}) {
  const accentClass = {
    signal: "text-signal",
    amber: "text-amber",
    crimson: "text-crimson",
    cobalt: "text-cobalt",
  }[accent];

  return (
    <div className="glass-panel rounded-lg p-5 relative overflow-hidden">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-[11px] uppercase tracking-[0.12em] text-ink-faint font-mono mb-2">{label}</div>
          <div className="font-display text-2xl font-semibold text-ink">{value}</div>
        </div>
        <Icon size={18} strokeWidth={1.5} className={accentClass} />
      </div>
    </div>
  );
}
