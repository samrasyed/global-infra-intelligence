import { api } from "@/lib/api";
import { Building2 } from "lucide-react";

export const dynamic = "force-dynamic";

export default async function CompaniesPage() {
  const companies = await api.companies().catch(() => []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-xl font-semibold text-ink">Companies</h1>
        <p className="text-sm text-ink-muted mt-1">Entities detected across tracked infrastructure coverage.</p>
      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {companies.map((c) => (
          <a key={c.id} href={`/companies/${c.id}`} className="glass-panel rounded-lg p-5 hover:border-border-strong transition-colors">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-9 h-9 rounded-md bg-surface-3 flex items-center justify-center text-cobalt">
                <Building2 size={16} />
              </div>
              <div>
                <div className="text-sm font-medium text-ink">{c.name}</div>
                <div className="text-xs text-ink-faint">{c.sector || "Sector unknown"}</div>
              </div>
            </div>
            {c.description && <p className="text-xs text-ink-muted leading-relaxed line-clamp-2">{c.description}</p>}
          </a>
        ))}
        {companies.length === 0 && (
          <div className="col-span-full text-sm text-ink-muted glass-panel rounded-lg p-6">No companies tracked yet.</div>
        )}
      </div>
    </div>
  );
}
