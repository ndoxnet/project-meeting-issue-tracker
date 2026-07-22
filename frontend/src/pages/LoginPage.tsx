// Concept by MrHan (08974747477)
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '@/auth/useAuth';
import { usePageTitle } from '@/hooks/usePageTitle';
import { Button } from '@/components/ui/Button';
import { InlineError } from '@/components/feedback/InlineError';
import { ApiError } from '@/api/errors';
import { safeRedirect } from '@/lib/validateRedirect';

const schema = z.object({
  username: z.string().min(1, 'Username or email is required'),
  password: z.string().min(1, 'Password is required'),
});
type FormValues = z.infer<typeof schema>;

interface LocationState {
  from?: string;
}

export function LoginPage() {
  usePageTitle('Sign in');
  const { status, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [error, setError] = useState<unknown>(null);
  const [showPassword, setShowPassword] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { username: '', password: '' } });

  // Already signed in → go to the app.
  if (status === 'authenticated') {
    const target = safeRedirect((location.state as LocationState | null)?.from);
    return <Navigate to={target} replace />;
  }

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await login(values);
      reset({ username: values.username, password: '' }); // clear password
      const target = safeRedirect((location.state as LocationState | null)?.from);
      navigate(target, { replace: true });
    } catch (err) {
      // Generic message — never reveal whether username or password was wrong.
      setError(
        err instanceof ApiError && err.isAuth
          ? new ApiError({
              code: err.code,
              message: 'Invalid username or password.',
              status: err.status,
              requestId: err.requestId,
            })
          : err,
      );
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <main className="w-full max-w-sm rounded-xl border border-border bg-surface p-6 shadow-sm">
        <h1 className="text-lg font-semibold text-text">Project Meeting Issue Tracker</h1>
        <p className="mt-1 text-sm text-muted">Use your authorized account to sign in.</p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit(onSubmit)} noValidate>
          <div>
            <label htmlFor="username" className="block text-sm text-text">
              Username or email
            </label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              aria-invalid={!!errors.username}
              aria-describedby={errors.username ? 'username-error' : undefined}
              className="mt-1 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm"
              {...register('username')}
            />
            {errors.username && (
              <p id="username-error" className="mt-1 text-xs text-danger">
                {errors.username.message}
              </p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm text-text">
              Password
            </label>
            <div className="relative mt-1">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                aria-invalid={!!errors.password}
                aria-describedby={errors.password ? 'password-error' : undefined}
                className="w-full rounded-md border border-border bg-surface px-3 py-2 pr-10 text-sm"
                {...register('password')}
              />
              <button
                type="button"
                onClick={() => setShowPassword((s) => !s)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                className="absolute inset-y-0 right-0 flex items-center px-3 text-muted"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {errors.password && (
              <p id="password-error" className="mt-1 text-xs text-danger">
                {errors.password.message}
              </p>
            )}
          </div>

          {error != null && <InlineError error={error} />}

          <Button type="submit" loading={isSubmitting} className="w-full">
            Sign in
          </Button>
        </form>
      </main>
    </div>
  );
}
