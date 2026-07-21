// Concept by MrHan (08974747477)
// Phase 1 placeholder login screen (no real authentication yet — Phase 3).
export default function Login() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-4">
      <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-lg font-semibold text-slate-800">
          Project Meeting Issue Tracker
        </h1>
        <p className="mt-1 text-sm text-slate-500">Masuk untuk melanjutkan</p>
        <form className="mt-6 space-y-4" onSubmit={(e) => e.preventDefault()}>
          <div>
            <label className="block text-sm text-slate-600">Username / Email</label>
            <input
              type="text"
              disabled
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="username"
            />
          </div>
          <div>
            <label className="block text-sm text-slate-600">Password</label>
            <input
              type="password"
              disabled
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled
            className="w-full rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white opacity-60"
          >
            Login (Phase 3)
          </button>
        </form>
      </div>
    </div>
  );
}
