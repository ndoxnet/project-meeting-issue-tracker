// Concept by MrHan (08974747477)
import { usePageTitle } from '@/hooks/usePageTitle';

/**
 * Placeholder for a module not yet implemented. Uses the final shell layout and
 * shows NO fake data / KPIs — only a clear "coming in Phase 2C.x" message.
 */
export function PlaceholderPage({
  title,
  phase,
  description,
}: {
  title: string;
  phase: string;
  description?: string;
}) {
  usePageTitle(title);
  return (
    <section>
      <h1 className="text-xl font-semibold text-text">{title}</h1>
      {description && <p className="mt-2 text-sm text-muted">{description}</p>}
      <div className="mt-6 rounded-lg border border-dashed border-border bg-surface p-8 text-center text-muted">
        This module will be implemented in <span className="font-medium text-text">{phase}</span>.
      </div>
    </section>
  );
}
