import { api } from "@/lib/api";
import ArticleCard from "@/components/ArticleCard";

export const dynamic = "force-dynamic";

const THREAT_LEVELS = ["low", "medium", "high", "critical"];

export default async function ArticlesPage({
  searchParams,
}: {
  searchParams: { country?: string; infra_category?: string; threat_level?: string };
}) {
  const articles = await api
    .articles({
      page_size: 30,
      country: searchParams.country,
      infra_category: searchParams.infra_category,
      threat_level: searchParams.threat_level,
    })
    .catch(() => []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-ink">Intelligence Feed</h1>
        <p className="text-sm text-ink-muted mt-1">
          {articles.length} processed article{articles.length === 1 ? "" : "s"} matching current filters.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {THREAT_LEVELS.map((lvl) => (
          <a
            key={lvl}
            href={`/articles?threat_level=${lvl}`}
            className="px-3 py-1.5 rounded-md border border-border text-xs font-mono uppercase text-ink-muted hover:text-ink hover:border-border-strong transition-colors"
          >
            {lvl}
          </a>
        ))}
        <a
          href="/articles"
          className="px-3 py-1.5 rounded-md border border-border text-xs font-mono uppercase text-ink-muted hover:text-ink hover:border-border-strong transition-colors"
        >
          clear
        </a>
      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {articles.map((a) => (
          <ArticleCard key={a.id} article={a} />
        ))}
        {articles.length === 0 && (
          <div className="col-span-full text-sm text-ink-muted glass-panel rounded-lg p-6">
            No articles match these filters yet.
          </div>
        )}
      </div>
    </div>
  );
}
