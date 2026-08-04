import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import ArticleCard from "@/components/ArticleCard";

export const dynamic = "force-dynamic";

export default async function CountryDetailPage({ params }: { params: { id: string } }) {
  const country = await api.country(params.id).catch(() => null);
  if (!country) notFound();

  const [articles, infra] = await Promise.all([
    api.countryArticles(params.id).catch(() => []),
    api.infrastructure().catch(() => []),
  ]);
  const countryInfra = infra.filter((i) => i.country?.id === params.id);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-semibold text-ink">{country.name}</h1>
          <p className="text-sm text-ink-muted mt-1">{country.region || "Region unknown"}</p>
        </div>
        <div className="glass-panel rounded-lg px-5 py-3 text-right">
          <div className="text-[11px] uppercase tracking-wide text-ink-faint font-mono">Risk Score</div>
          <div className="font-display text-2xl text-amber">{country.risk_score.toFixed(0)}</div>
        </div>
      </div>

      <div>
        <h2 className="font-display text-base font-medium text-ink mb-3">Infrastructure Assets ({countryInfra.length})</h2>
        <div className="grid md:grid-cols-2 gap-3">
          {countryInfra.map((i) => (
            <div key={i.id} className="glass-panel rounded-lg p-4">
              <div className="text-sm text-ink font-medium">{i.name}</div>
              <div className="text-xs text-ink-muted mt-1">{i.category.replace("_", " ")}</div>
            </div>
          ))}
          {countryInfra.length === 0 && (
            <div className="text-sm text-ink-muted col-span-full">No tracked infrastructure assets for this country yet.</div>
          )}
        </div>
      </div>

      <div>
        <h2 className="font-display text-base font-medium text-ink mb-3">Recent Coverage</h2>
        <div className="grid md:grid-cols-2 gap-4">
          {articles.map((a) => (
            <ArticleCard key={a.id} article={a} />
          ))}
          {articles.length === 0 && <div className="text-sm text-ink-muted">No articles yet.</div>}
        </div>
      </div>
    </div>
  );
}
