// Concept by MrHan (08974747477)
import { Component, type ErrorInfo, type ReactNode } from 'react';
import { ApiError } from '@/api/errors';

interface Props {
  children: ReactNode;
}
interface State {
  error: Error | null;
}

/** Top-level boundary. Shows a generic message + request id; never a stack. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(_error: Error, _info: ErrorInfo): void {
    // Intentionally no console logging of tokens/PII. Hook a monitoring service
    // here later (without secrets).
  }

  handleReload = () => {
    this.setState({ error: null });
    window.location.reload();
  };

  render() {
    const { error } = this.state;
    if (!error) return this.props.children;

    const requestId = error instanceof ApiError ? error.requestId : undefined;
    return (
      <div
        role="alert"
        className="flex min-h-screen flex-col items-center justify-center bg-background p-6 text-center"
      >
        <h1 className="text-lg font-semibold text-text">Something went wrong</h1>
        <p className="mt-2 max-w-md text-sm text-muted">
          An unexpected error occurred. Please reload the page. If it persists, contact support with
          the request ID below.
        </p>
        {requestId && (
          <p className="mt-2 text-xs text-muted">
            Request ID: <code className="font-mono">{requestId}</code>
          </p>
        )}
        <button
          type="button"
          onClick={this.handleReload}
          className="mt-4 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-fg"
        >
          Reload
        </button>
      </div>
    );
  }
}
