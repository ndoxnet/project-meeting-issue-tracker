// Concept by MrHan (08974747477)
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { DataState } from '@/components/feedback/DataState';
import { useSettings } from '@/api/settings';
import { formatDateTime } from '@/lib/dates';

/** Read-only reference view of application settings (Phase 2C.4B). */
export function SettingsPage() {
  usePageTitle('Settings');
  const settings = useSettings();

  return (
    <section>
      <PageHeader
        title="Application Settings"
        description="Reference configuration values (read-only)."
      />

      <div
        role="note"
        className="mb-4 rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800"
      >
        These values are <span className="font-semibold">read-only</span>. Runtime configuration
        currently comes from the server&rsquo;s <span className="font-medium">environment
        configuration</span>, not the <code className="font-mono">app_settings</code> table — so
        editing here would have no effect. Editable settings are deferred to a future backend
        hardening task.
      </div>

      <DataState
        isLoading={settings.isLoading}
        error={settings.error}
        isEmpty={(settings.data?.length ?? 0) === 0}
        loadingLabel="Loading settings…"
        emptyTitle="No settings to show"
      >
        <div className="overflow-x-auto rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-muted">
                <th scope="col" className="p-3 font-medium">
                  Key
                </th>
                <th scope="col" className="p-3 font-medium">
                  Value
                </th>
                <th scope="col" className="p-3 font-medium">
                  Description
                </th>
                <th scope="col" className="p-3 font-medium">
                  Updated
                </th>
              </tr>
            </thead>
            <tbody>
              {settings.data?.map((setting) => (
                <tr key={setting.key} className="border-b border-border last:border-0 align-top">
                  <th scope="row" className="whitespace-nowrap p-3 text-left font-mono font-normal text-text">
                    {setting.key}
                  </th>
                  <td className="p-3">
                    <code className="break-all font-mono text-text">
                      {JSON.stringify(setting.value)}
                    </code>
                  </td>
                  <td className="p-3 text-muted">{setting.description ?? '—'}</td>
                  <td className="whitespace-nowrap p-3 text-muted">
                    {formatDateTime(setting.updated_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DataState>
    </section>
  );
}
