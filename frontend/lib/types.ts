export type ThreatLevelStr = "low" | "medium" | "high" | "critical";

export interface Country {
  id: string;
  name: string;
  iso2?: string | null;
  iso3?: string | null;
  region?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  risk_score: number;
}

export interface Company {
  id: string;
  name: string;
  description?: string | null;
  sector?: string | null;
}

export interface Threat {
  level: ThreatLevelStr;
  score: number;
  factors?: Record<string, boolean> | null;
}

export interface Investment {
  amount_usd?: number | null;
  currency_raw?: string | null;
  description?: string | null;
}

export interface ArticleListItem {
  id: string;
  title: string;
  source?: string | null;
  image_url?: string | null;
  published_at?: string | null;
  infra_category?: string | null;
  summary?: string | null;
  threat?: Threat | null;
  countries: Country[];
  companies: Company[];
  matched_keywords: string[];
}

export interface ArticleDetail extends ArticleListItem {
  url: string;
  clean_text?: string | null;
  geopolitical_topics?: string[] | null;
  investment?: Investment | null;
}

export interface Infrastructure {
  id: string;
  name: string;
  category: string;
  latitude?: number | null;
  longitude?: number | null;
  description?: string | null;
  country?: Country | null;
}

export interface ChartPoint {
  label: string;
  value: number;
}

export interface DashboardKPIs {
  articles_today: number;
  threat_events_today: number;
  countries_tracked: number;
  companies_tracked: number;
  total_investment_usd: number;
  average_threat_score: number;
}

export interface DashboardResponse {
  kpis: DashboardKPIs;
  articles_per_day: ChartPoint[];
  threat_distribution: ChartPoint[];
  top_countries: ChartPoint[];
  top_companies: ChartPoint[];
  infrastructure_categories: ChartPoint[];
}

export interface SearchResult {
  article_id: string;
  title?: string | null;
  source?: string | null;
  infra_category?: string | null;
  relevance?: number | null;
  snippet?: string | null;
}

export interface ChatResponse {
  answer: string;
  sources: { article_id: string; title?: string | null; source?: string | null }[];
}
