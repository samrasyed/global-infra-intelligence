import clsx from "clsx";
import type { ThreatLevelStr } from "@/lib/types";

const STYLES: Record<ThreatLevelStr, string> = {
  low: "bg-signal/10 text-signal border-signal/30",
  medium: "bg-cobalt/10 text-cobalt border-cobalt/30",
  high: "bg-amber/10 text-amber border-amber/30",
  critical: "bg-crimson/10 text-crimson border-crimson/30",
};

export default function ThreatBadge({ level, score }: { level: ThreatLevelStr; score?: number }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 px-2 py-0.5 rounded border text-[11px] font-mono uppercase tracking-wide",
        STYLES[level]
      )}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {level}
      {typeof score === "number" && <span className="opacity-60">· {Math.round(score)}</span>}
    </span>
  );
}
