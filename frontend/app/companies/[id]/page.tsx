import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import ArticleCard from "@/components/ArticleCard";
import { formatUSD } from "@/lib/format";

export const dynamic = "force-dynamic";

export default async function CompanyDetailPage({ params }: { params: { id: string } }) {
  const company = await api.company(params.id).catch(() => null);
  if (!company) notFound();

  const [articles, investments] = await Promise.all([
    api.companyArticles(params.id).catch(() => []),
    fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"}/api/companies/${params.id}/investments`, {
      cache: "no-store",
    })
      .then((r) => (r.ok ? r.json() : []))
      .catch(() => []),
  ]);

  const totalInvestment = investments.reduce((sum: number, i: { amount_usd?: number }) => sum + (i.amount_usd || 0), 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink">{company.name}</h1>
        <p className="text-sm text-ink-muted mt-1">{company.sector || "Sector unknown"}</p>
      </div>

      {company.description && (
        <div className="glass-panel rounded-lg p-5">
          <p className="text-sm text-ink-muted leading-relaxed">{company.description}</p>
        </div>
      )}

      <div className="grid grid-cols-2 gap-4">
        <div className="glass-panel rounded-lg p-5">
          <div className="text-[11px] uppercase tracking-wide text-ink-faint font-mono mb-2">Tracked Investment</div>
          <div className="font-display text-xl text-amber">{formatUSD(totalInvestment)}</div>
        </div>
        <div className="glass-panel rounded-lg p-5">
          <div className="text-[11px] uppercase tracking-wide text-ink-faint font-mono mb-2">Articles</div>
          <div className="font-display text-xl text-ink">{articles.length}</div>
        </div>
      </div>

      <div>
        <h2 className="font-display text-base font-medium text-ink mb-3">Coverage</h2>
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
