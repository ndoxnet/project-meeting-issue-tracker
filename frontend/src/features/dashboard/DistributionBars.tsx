// Concept by MrHan (08974747477)
// Dependency-free horizontal bar list. Each row shows the label and the numeric
// value as TEXT; the bar is decorative (aria-hidden). Information never depends
// on bar length or color alone.
import type { CountByLabel } from '@/api/types';

export function DistributionBars({ data }: { data: CountByLabel[] }) {
  const max = data.reduce((m, d) => Math.max(m, d.count), 0) || 1;
  return (
    <ul className="space-y-2">
      {data.map((row) => (
        <li key={row.label}>
          <div className="flex items-baseline justify-between gap-2 text-sm">
            <span className="truncate text-text">{row.label}</span>
            <span className="shrink-0 font-medium text-text tabular-nums">{row.count}</span>
          </div>
          <div className="mt-1 h-2 w-full overflow-hidden rounded bg-background" aria-hidden="true">
            <div
              className="h-full rounded bg-primary"
              style={{ width: `${Math.round((row.count / max) * 100)}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}
