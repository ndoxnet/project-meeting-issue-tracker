// Concept by MrHan (08974747477)
import { Link } from 'react-router-dom';

/** Clickable KPI tile. `to` (optional) links to a filtered view. */
export function StatCard({
  label,
  value,
  to,
  tone = 'default',
}: {
  label: string;
  value: number;
  to?: string;
  tone?: 'default' | 'danger' | 'warning';
}) {
  const valueColor =
    tone === 'danger' ? 'text-danger' : tone === 'warning' ? 'text-warning' : 'text-text';
  const body = (
    <div className="rounded-lg border border-border bg-surface p-4">
      <div className="text-sm text-muted">{label}</div>
      <div className={`mt-1 text-2xl font-semibold ${valueColor}`}>{value}</div>
    </div>
  );
  return to ? (
    <Link to={to} className="block transition hover:border-primary/40" aria-label={`${label}: ${value}`}>
      {body}
    </Link>
  ) : (
    body
  );
}
