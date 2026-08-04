import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function CountriesPage() {
  const countries = await api.countries().catch(() => []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-ink">Countries</h1>
        <p className="text-sm text-ink-muted mt-1">Ranked by derived risk score across tracked coverage.</p>
      </div>

      <div className="glass-panel rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-wide text-ink-faint font-mono border-b border-border">
              <th className="px-5 py-3 font-normal">Country</th>
              <th className="px-5 py-3 font-normal">Region</th>
              <th className="px-5 py-3 font-normal">Risk Score</th>
            </tr>
          </thead>
          <tbody>
            {countries.map((c) => (
              <tr key={c.id} className="border-b border-border last:border-0 hover:bg-surface-2/60">
                <td className="px-5 py-3">
                  <a href={`/countries/${c.id}`} className="text-ink hover:text-signal font-medium">
                    {c.name}
                  </a>
                </td>
                <td className="px-5 py-3 text-ink-muted">{c.region || "—"}</td>
                <td className="px-5 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 rounded-full bg-surface-3 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-signal to-amber"
                        style={{ width: `${Math.min(c.risk_score, 100)}%` }}
                      />
                    </div>
                    <span className="font-mono text-xs text-ink-muted">{c.risk_score.toFixed(0)}</span>
                  </div>
                </td>
              </tr>
            ))}
            {countries.length === 0 && (
              <tr>
                <td colSpan={3} className="px-5 py-8 text-center text-ink-muted">
                  No countries in the database yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
