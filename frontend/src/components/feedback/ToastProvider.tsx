// Concept by MrHan (08974747477)
// Accessible toast notifications. Success/info use a polite live region; errors
// use an assertive alert. Toasts SUPPLEMENT inline errors — they are never the
// only presentation of an actionable form/mutation error. Duplicate messages
// (from rerenders or query retries) are de-duplicated while still visible.
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { CheckCircle2, AlertTriangle, Info, X } from 'lucide-react';

type ToastLevel = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  level: ToastLevel;
  message: string;
}

export interface ToastApi {
  push: (level: ToastLevel, message: string) => void;
  success: (message: string) => void;
  error: (message: string) => void;
  info: (message: string) => void;
}

const ToastContext = createContext<ToastApi | null>(null);

/** Access the toast API. Must be used within <ToastProvider>. */
export function useToast(): ToastApi {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within a ToastProvider');
  return ctx;
}

const AUTO_DISMISS_MS = 5000;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(0);

  const remove = useCallback((id: number) => {
    setToasts((current) => current.filter((t) => t.id !== id));
  }, []);

  const push = useCallback(
    (level: ToastLevel, message: string) => {
      const id = (nextId.current += 1);
      setToasts((current) =>
        // De-dupe identical toasts already on screen (rerender / retry safety).
        current.some((t) => t.level === level && t.message === message)
          ? current
          : [...current, { id, level, message }],
      );
      window.setTimeout(() => remove(id), AUTO_DISMISS_MS);
    },
    [remove],
  );

  const api = useMemo<ToastApi>(
    () => ({
      push,
      success: (message) => push('success', message),
      error: (message) => push('error', message),
      info: (message) => push('info', message),
    }),
    [push],
  );

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div
        className="pointer-events-none fixed inset-x-0 bottom-0 z-[60] flex flex-col items-center gap-2 p-4 sm:items-end"
        aria-live="polite"
      >
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onClose={() => remove(toast.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

const TONE: Record<ToastLevel, { icon: typeof Info; className: string }> = {
  success: { icon: CheckCircle2, className: 'border-green-300 bg-green-50 text-green-800' },
  error: { icon: AlertTriangle, className: 'border-danger/30 bg-danger/5 text-danger' },
  info: { icon: Info, className: 'border-border bg-surface text-text' },
};

function ToastItem({ toast, onClose }: { toast: Toast; onClose: () => void }) {
  const tone = TONE[toast.level];
  const Icon = tone.icon;
  return (
    <div
      role={toast.level === 'error' ? 'alert' : 'status'}
      className={`pointer-events-auto flex w-full max-w-sm items-start gap-2 rounded-md border p-3 text-sm shadow-md ${tone.className}`}
    >
      <Icon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span className="flex-1">{toast.message}</span>
      <button
        type="button"
        onClick={onClose}
        aria-label="Dismiss notification"
        className="rounded p-0.5 opacity-70 hover:opacity-100"
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </button>
    </div>
  );
}
