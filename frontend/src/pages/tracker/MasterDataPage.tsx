// Concept by MrHan (08974747477)
import { useSearchParams } from 'react-router-dom';
import { usePageTitle } from '@/hooks/usePageTitle';
import { PageHeader } from '@/components/layout/PageHeader';
import { NamedResourceManager } from '@/features/masterdata/NamedResourceManager';
import type { NamedResourceKind } from '@/api/masterdataAdmin';

const TABS: { key: NamedResourceKind; label: string; singular: string }[] = [
  { key: 'categories', label: 'Categories', singular: 'Category' },
  { key: 'responsible-parties', label: 'Responsible parties', singular: 'Responsible party' },
  { key: 'meetings', label: 'Meeting types', singular: 'Meeting type' },
];

function isKind(value: string): value is NamedResourceKind {
  return TABS.some((t) => t.key === value);
}

export function MasterDataPage() {
  usePageTitle('Master Data');
  const [params, setParams] = useSearchParams();
  const raw = params.get('tab') ?? '';
  const active = isKind(raw) ? raw : 'categories';
  const activeTab = TABS.find((t) => t.key === active)!;

  function selectTab(key: NamedResourceKind) {
    const next = new URLSearchParams(params);
    next.set('tab', key);
    setParams(next);
  }

  return (
    <section>
      <PageHeader
        title="Master Data"
        description="Manage categories, responsible parties, and meeting types."
      />

      <div className="mb-4 flex flex-wrap gap-1 border-b border-border" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            type="button"
            role="tab"
            aria-selected={tab.key === active}
            onClick={() => selectTab(tab.key)}
            className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium ${
              tab.key === active
                ? 'border-primary text-primary'
                : 'border-transparent text-muted hover:text-text'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Remount per tab so filter/search state does not leak between resources. */}
      <NamedResourceManager key={active} kind={active} singular={activeTab.singular} />
    </section>
  );
}
