"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { api } from "@/lib/api";
import type { Infrastructure, Country } from "@/lib/types";

const InfraMap = dynamic(() => import("@/components/InfraMap"), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-full text-ink-muted text-sm">Loading map…</div>,
});

export default function MapPage() {
  const [assets, setAssets] = useState<Infrastructure[]>([]);
  const [countries, setCountries] = useState<Country[]>([]);

  useEffect(() => {
    Promise.all([
      api.infrastructure().catch(() => []),
      api.countries().catch(() => []),
    ]).then(([assetsData, countriesData]) => {
      setAssets(assetsData);
      setCountries(countriesData);
    });
  }, []);

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div>
        <h1 className="font-display text-xl font-semibold text-ink">Asset Map</h1>
        <p className="text-sm text-ink-muted mt-1">{assets.length} assets and {countries.filter(c => c.risk_score > 0).length} risk zones plotted globally.</p>
      </div>
      <div className="glass-panel rounded-lg overflow-hidden flex-1" style={{ minHeight: 560 }}>
        <InfraMap assets={assets} countries={countries} />
      </div>
    </div>
  );
}
