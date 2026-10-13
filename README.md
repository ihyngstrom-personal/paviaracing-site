# Pavia Racing Stable (static site)

Astro static site for paviaracing.com, deployed to Azure Static Web Apps from `main` via GitHub Actions
(secret `AZURE_STATIC_WEB_APPS_API_TOKEN`).

- Posts: `src/content/posts/*.md` (front matter: title, date, categories, youtube, image). Pages: `src/content/pages/*.md`.
- Images: `public/uploads` (optimize new photos first: `python3 scripts/optimize-images.py ingest FILES --dest public/uploads/YYYY/MM`).
- Dev: `npm install && npm run dev` · Build: `npm run build` (also builds the search index).
- `migration/` holds the one-time WordPress import script and report (not used at runtime).
