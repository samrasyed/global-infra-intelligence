import { Newspaper, ShieldAlert, Globe2, Building2, DollarSign, Gauge } from "lucide-react";
import { api } from "@/lib/api";
import KpiCard from "@/components/KpiCard";
import { ArticlesPerDayChart, ThreatDistributionChart, TopEntitiesChart } from "@/components/Charts";
import { formatUSD, formatInfraCategory } from "@/lib/format";
import ArticleCard from "@/components/ArticleCard";

export const dynamic = "force-dynamic";

export default async function OverviewPage() {
  const [dashboard, latest] = await Promise.all([
    api.dashboard().catch(() => null),
    api.articles({ page_size: 6 }).catch(() => []),
  ]);

  if (!dashboard) {
    return (
      <div className="glass-panel rounded-lg p-8 text-center text-ink-muted">
        Could not reach the GCIIP API. Confirm the backend is running at{" "}
        <code className="font-mono text-ink">NEXT_PUBLIC_API_BASE_URL</code>.
      </div>
    );
  }

  const { kpis, articles_per_day, threat_distribution, top_countries, top_companies, infrastructure_categories } =
    dashboard;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-display text-xl font-semibold text-ink">Executive Overview</h1>
        <p className="text-sm text-ink-muted mt-1">Real-time synthesis of global critical-infrastructure signal.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard label="Articles Today" value={String(kpis.articles_today)} icon={Newspaper} accent="signal" />
        <KpiCard label="Threat Events" value={String(kpis.threat_events_today)} icon={ShieldAlert} accent="crimson" />
        <KpiCard label="Countries" value={String(kpis.countries_tracked)} icon={Globe2} accent="cobalt" />
        <KpiCard label="Companies" value={String(kpis.companies_tracked)} icon={Building2} accent="cobalt" />
        <KpiCard label="Investment Tracked" value={formatUSD(kpis.total_investment_usd)} icon={DollarSign} accent="amber" />
        <KpiCard label="Avg Threat Score" value={kpis.average_threat_score.toFixed(0)} icon={Gauge} accent="amber" />
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="glass-panel rounded-lg p-5 lg:col-span-2">
          <div className="text-xs uppercase tracking-wide text-ink-faint font-mono mb-3">Articles / Day (14d)</div>
          <ArticlesPerDayChart data={articles_per_day} />
        </div>
        <div className="glass-panel rounded-lg p-5">
          <div className="text-xs uppercase tracking-wide text-ink-faint font-mono mb-3">Threat Distribution</div>
          <ThreatDistributionChart data={threat_distribution} />
          <div className="flex flex-wrap gap-3 mt-2 justify-center text-[11px] font-mono">
            {threat_distribution.map((d) => (
              <span key={d.label} className="text-ink-muted">
                {d.label}: {d.value}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-4">
        <div className="glass-panel rounded-lg p-5">
          <div className="text-xs uppercase tracking-wide text-ink-faint font-mono mb-3">Top Countries</div>
          <TopEntitiesChart data={top_countries} color="#4C8DFF" />
        </div>
        <div className="glass-panel rounded-lg p-5">
          <div className="text-xs uppercase tracking-wide text-ink-faint font-mono mb-3">Top Companies</div>
          <TopEntitiesChart data={top_companies} color="#2FD6C0" />
        </div>
        <div className="glass-panel rounded-lg p-5">
          <div className="text-xs uppercase tracking-wide text-ink-faint font-mono mb-3">Infrastructure Mix</div>
          <TopEntitiesChart
            data={infrastructure_categories.map((c) => ({ ...c, label: formatInfraCategory(c.label) }))}
            color="#F0A83C"
          />
        </div>
      </div>

      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-display text-base font-medium text-ink">Latest Intelligence</h2>
          <a href="/articles" className="text-xs text-signal hover:underline font-mono">
            VIEW ALL →
          </a>
        </div>
        <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
          {latest.map((a) => (
            <ArticleCard key={a.id} article={a} />
          ))}
          {latest.length === 0 && (
            <div className="col-span-full text-sm text-ink-muted glass-panel rounded-lg p-6">
              No articles ingested yet. Trigger a manual ingestion cycle from the admin API
              (<code className="font-mono">POST /api/admin/ingest/run</code>) or run the seed script.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
