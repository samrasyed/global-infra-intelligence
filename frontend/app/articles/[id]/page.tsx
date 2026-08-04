import { notFound } from "next/navigation";
import { api } from "@/lib/api";
import ThreatBadge from "@/components/ThreatBadge";
import ArticleCard from "@/components/ArticleCard";
import { formatInfraCategory, formatUSD, timeAgo } from "@/lib/format";
import { ExternalLink } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function ArticleDetailPage({ params }: { params: { id: string } }) {
  const article = await api.article(params.id).catch(() => null);
  if (!article) notFound();

  const related = await api.relatedArticles(params.id).catch(() => []);

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between text-xs font-mono text-ink-faint uppercase tracking-wide">
        <span>{article.source}</span>
        <span>{timeAgo(article.published_at)}</span>
      </div>

      <h1 className="font-display text-2xl md:text-3xl font-semibold text-ink leading-tight">{article.title}</h1>

      <div className="flex flex-wrap items-center gap-2">
        {article.threat && <ThreatBadge level={article.threat.level} score={article.threat.score} />}
        <span className="px-2 py-0.5 rounded border border-border text-[11px] text-ink-muted">
          {formatInfraCategory(article.infra_category)}
        </span>
        {(article.geopolitical_topics || []).map((t) => (
          <span key={t} className="px-2 py-0.5 rounded border border-border text-[11px] text-ink-muted">
            {t}
          </span>
        ))}
      </div>

      {article.summary && (
        <div className="glass-panel rounded-lg p-5">
          <div className="text-[11px] uppercase tracking-wide text-ink-faint font-mono mb-2">AI Summary</div>
          <p className="text-sm text-ink leading-relaxed">{article.summary}</p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        <div className="glass-panel rounded-lg p-5">
          <div className="text-[11px] uppercase tracking-wide text-ink-faint font-mono mb-3">Countries Involved</div>
          <div className="flex flex-wrap gap-2">
            {article.countries.length
              ? article.countries.map((c) => (
                  <a key={c.id} href={`/countries/${c.id}`} className="px-2 py-1 rounded border border-border text-xs text-ink-muted hover:text-signal hover:border-signal/40">
                    {c.name}
                  </a>
                ))
              : <span className="text-xs text-ink-faint">None detected</span>}
          </div>
        </div>
        <div className="glass-panel rounded-lg p-5">
          <div className="text-[11px] uppercase tracking-wide text-ink-faint font-mono mb-3">Companies</div>
          <div className="flex flex-wrap gap-2">
            {article.companies.length
              ? article.companies.map((c) => (
                  <a key={c.id} href={`/companies/${c.id}`} className="px-2 py-1 rounded border border-border text-xs text-ink-muted hover:text-signal hover:border-signal/40">
                    {c.name}
                  </a>
                ))
              : <span className="text-xs text-ink-faint">None detected</span>}
          </div>
        </div>
      </div>

      {article.investment?.amount_usd && (
        <div className="glass-panel rounded-lg p-5">
          <div className="text-[11px] uppercase tracking-wide text-ink-faint font-mono mb-2">Investment Detected</div>
          <div className="font-display text-xl text-amber">{formatUSD(article.investment.amount_usd)}</div>
        </div>
      )}

      {article.clean_text && (
        <div className="glass-panel rounded-lg p-5">
          <div className="text-[11px] uppercase tracking-wide text-ink-faint font-mono mb-2">Source Text</div>
          <p className="text-sm text-ink-muted leading-relaxed whitespace-pre-line">{article.clean_text}</p>
        </div>
      )}

      <a
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-2 text-sm text-signal hover:underline"
      >
        Read original article <ExternalLink size={14} />
      </a>

      {related.length > 0 && (
        <div>
          <h2 className="font-display text-base font-medium text-ink mb-3">Related Intelligence</h2>
          <div className="grid md:grid-cols-2 gap-4">
            {related.map((a) => (
              <ArticleCard key={a.id} article={a} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
