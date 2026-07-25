// Concept by MrHan (08974747477)
// Opened-vs-closed monthly trend. Rendered as a real data TABLE (fully accessible,
// numeric values present) with small decorative bars beside the numbers. No chart
// library — information is available from the table cells alone.
import type { MonthlyTrendPoint } from '@/api/types';

export function TrendTable({ data }: { data: MonthlyTrendPoint[] }) {
  const max = data.reduce((m, d) => Math.max(m, d.opened, d.closed), 0) || 1;
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <caption className="sr-only">Issues opened versus closed, by month</caption>
        <thead>
          <tr className="text-left text-xs text-muted">
            <th scope="col" className="py-1 pr-3 font-medium">
              Month
            </th>
            <th scope="col" className="py-1 pr-3 font-medium">
              Opened
            </th>
            <th scope="col" className="py-1 font-medium">
              Closed
            </th>
          </tr>
        </thead>
        <tbody>
          {data.map((point) => (
            <tr key={point.month} className="border-t border-border">
              <th scope="row" className="whitespace-nowrap py-1.5 pr-3 font-normal text-text">
                {point.month}
              </th>
              <td className="py-1.5 pr-3">
                <TrendCell value={point.opened} max={max} className="bg-blue-400" />
              </td>
              <td className="py-1.5">
                <TrendCell value={point.closed} max={max} className="bg-green-400" />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function TrendCell({ value, max, className }: { value: number; max: number; className: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className="w-6 shrink-0 tabular-nums text-text">{value}</span>
      <span className="h-2 flex-1 overflow-hidden rounded bg-background" aria-hidden="true">
        <span
          className={`block h-full rounded ${className}`}
          style={{ width: `${Math.round((value / max) * 100)}%` }}
        />
      </span>
    </div>
  );
}
