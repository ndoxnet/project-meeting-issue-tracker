// Concept by MrHan (08974747477)
import { useEffect } from 'react';
import { env } from '@/config/env';

/** Set document.title per route for accessibility/orientation. */
export function usePageTitle(title: string): void {
  useEffect(() => {
    document.title = `${title} · ${env.appName}`;
  }, [title]);
}
