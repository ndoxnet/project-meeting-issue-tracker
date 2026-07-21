// Concept by MrHan (08974747477)
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <p className="text-4xl font-bold text-slate-300">404</p>
      <h1 className="mt-2 text-lg font-semibold text-slate-700">Halaman tidak ditemukan</h1>
      <Link to="/" className="mt-4 text-sm text-blue-600 hover:underline">
        Kembali ke Dashboard
      </Link>
    </div>
  );
}
