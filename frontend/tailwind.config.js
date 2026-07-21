// Concept by MrHan (08974747477)
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Consistent status colors (paired with text/badges, never color-only).
        status: {
          open: '#2563eb',
          progress: '#0891b2',
          pending: '#d97706',
          closed: '#16a34a',
          reopened: '#7c3aed',
          overdue: '#dc2626',
        },
      },
    },
  },
  plugins: [],
};
