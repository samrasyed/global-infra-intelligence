"use client";

import { useEffect, useState } from "react";

export default function TopBar() {
  const [time, setTime] = useState<string>("");

  useEffect(() => {
    const update = () =>
      setTime(
        new Date().toLocaleString("en-GB", {
          timeZone: "UTC",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }) + " UTC"
      );
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="h-16 border-b border-border flex items-center justify-between px-6 md:px-8 bg-base/70 backdrop-blur-md sticky top-0 z-20">
      <div className="flex items-center gap-2 text-xs font-mono text-ink-faint">
        <span className="w-1.5 h-1.5 rounded-full bg-signal animate-pulse" />
        <span className="text-ink-muted">LIVE INGESTION</span>
        <span className="mx-2 text-border-strong">|</span>
        <span>{time}</span>
      </div>
      <div className="text-xs font-mono text-ink-faint hidden md:block">
        SESSION: ANALYST-01 · CLEARANCE: OPEN-SOURCE
      </div>
    </header>
  );
}
