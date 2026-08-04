import Link from "next/link";
import type { ArticleListItem } from "@/lib/types";
import ThreatBadge from "./ThreatBadge";
import { formatInfraCategory, timeAgo } from "@/lib/format";

export default function ArticleCard({ article }: { article: ArticleListItem }) {
  return (
    <Link
      href={`/articles/${article.id}`}
      className="glass-panel rounded-lg p-5 flex flex-col gap-3 hover:border-border-strong transition-colors group"
    >
      <div className="flex items-center justify-between gap-2 text-[11px] font-mono text-ink-faint uppercase tracking-wide">
        <span>{article.source || "Unknown source"}</span>
        <span>{timeAgo(article.published_at)}</span>
      </div>

      <h3 className="font-display text-base font-medium text-ink leading-snug group-hover:text-signal transition-colors">
        {article.title}
      </h3>

      {article.summary && <p className="text-sm text-ink-muted leading-relaxed line-clamp-2">{article.summary}</p>}

      <div className="flex items-center flex-wrap gap-2 mt-1">
        {article.threat && <ThreatBadge level={article.threat.level} score={article.threat.score} />}
        <span className="px-2 py-0.5 rounded border border-border text-[11px] text-ink-muted">
          {formatInfraCategory(article.infra_category)}
        </span>
        {article.countries.slice(0, 3).map((c) => (
          <span key={c.id} className="px-2 py-0.5 rounded border border-border text-[11px] text-ink-muted">
            {c.name}
          </span>
        ))}
        {article.matched_keywords && article.matched_keywords.length > 0 && (
          <div className="flex items-center flex-wrap gap-1.5 mt-2 border-t border-border/10 pt-2 w-full">
            <span className="text-[10px] uppercase font-mono text-ink-faint mr-1">Matches:</span>
            {article.matched_keywords.slice(0, 4).map((kw) => (
              <span key={kw} className="px-1.5 py-0.5 rounded bg-surface-3 border border-border text-[10px] text-signal font-mono">
                #{kw}
              </span>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
}
