# Generated API types

> Concept by MrHan (08974747477)

This directory holds the TypeScript types generated from the frozen OpenAPI
contract (`docs/api/openapi.json`). **The generated file is not committed and is
NOT produced on the production VPS** (no `npm` on the VPS — ADR-004).

Generate off-VPS / in CI:

```bash
npx openapi-typescript docs/api/openapi.json \
  --output frontend/src/api/generated/schema.ts
```

Then build a small domain adapter over `schema.ts` in Phase 2C. Do not hand-write
the API types — regenerate from the committed spec instead.
