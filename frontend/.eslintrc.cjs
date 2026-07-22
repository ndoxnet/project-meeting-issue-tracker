// Concept by MrHan (08974747477)
/* eslint-env node */
module.exports = {
  root: true,
  env: { browser: true, es2021: true },
  parser: '@typescript-eslint/parser',
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  plugins: ['@typescript-eslint', 'react-hooks', 'react-refresh'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', 'coverage', 'node_modules', 'src/api/generated/**'],
  rules: {
    'react-refresh/only-export-components': ['warn', { allowConstantExport: true }],
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'no-restricted-globals': 'off',
    // Guard against accidental token persistence.
    'no-restricted-properties': [
      'error',
      { object: 'localStorage', message: 'Do not persist tokens/session (ADR-017).' },
      { object: 'sessionStorage', message: 'Do not persist tokens/session (ADR-017).' },
    ],
  },
};
