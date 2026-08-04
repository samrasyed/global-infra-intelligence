import type {
  ArticleListItem,
  ArticleDetail,
  Country,
  Company,
  Infrastructure,
  DashboardResponse,
  SearchResult,
  ChatResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  dashboard: () => apiFetch<DashboardResponse>("/api/dashboard"),

  articles: (params: Record<string, string | number | undefined> = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined) as [string, string][]
    ).toString();
    return apiFetch<ArticleListItem[]>(`/api/articles${qs ? `?${qs}` : ""}`);
  },

  article: (id: string) => apiFetch<ArticleDetail>(`/api/articles/${id}`),

  relatedArticles: (id: string) => apiFetch<ArticleListItem[]>(`/api/articles/${id}/related`),

  countries: () => apiFetch<Country[]>("/api/countries"),

  country: (id: string) => apiFetch<Country>(`/api/countries/${id}`),

  countryArticles: (id: string) => apiFetch<ArticleListItem[]>(`/api/countries/${id}/articles`),

  companies: () => apiFetch<Company[]>("/api/companies"),

  company: (id: string) => apiFetch<Company>(`/api/companies/${id}`),

  companyArticles: (id: string) => apiFetch<ArticleListItem[]>(`/api/companies/${id}/articles`),

  infrastructure: (category?: string) =>
    apiFetch<Infrastructure[]>(`/api/infrastructure${category ? `?category=${category}` : ""}`),

  search: (q: string) => apiFetch<{ query: string; results: SearchResult[] }>(`/api/search?q=${encodeURIComponent(q)}`),

  chat: (message: string) =>
    apiFetch<ChatResponse>("/api/chat", { method: "POST", body: JSON.stringify({ message }) }),

  triggerIngestion: () => apiFetch<Record<string, unknown>>("/api/admin/ingest/run", { method: "POST" }),
};
