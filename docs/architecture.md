# Architecture

## Runtime shape

The site is a Next.js 16 App Router application using React 19 and TypeScript. `next.config.ts` enables `reactStrictMode` and `trailingSlash`, so application URLs are published with a trailing slash. `app/layout.tsx` owns global metadata, the theme bootstrap script, `SitePreferencesProvider`, and Vercel Analytics.

The runtime route set is intentionally small:

- `/` is the home page.
- Eleven article routes live under `/Demand/`, `/Supply/`, and `/Agora/`.
- `/Demand/Dev_npm_downloads/` renders the download dashboard.
- `/Resources/Agora_Key_Metrics/` renders the quarterly metrics table.
- `/api/search/` is the server-side search endpoint.

`Resources/` links in the navigation point to the GitHub resource directory and are not application routes.

## Content flow

```text
articles/*.md
      │
      ▼
lib/content-manifest.ts ──► navigation (site-header.tsx)
      │                     search index (site-search.ts)
      ▼
components/manifest-article-page.tsx
      │
      ▼
app/**/page.tsx ──► LocalizedMarkdownArticle
```

`lib/content-manifest.ts` is the canonical mapping for article IDs, URL paths, section order, localized titles, source files, metadata, and search visibility. It currently contains 11 searchable articles, two internal special routes, and one external resource entry. Article route files should remain thin and retrieve metadata/content through the manifest.

The server article loader reads the selected Chinese or English Markdown file from `articles/` using `process.cwd()`. `Research_Report/` is deliberately outside this runtime path; it is a research workspace, not an implicit publication source.

## Search

`lib/site-search.ts` builds the index from manifest entries marked `searchable`. `app/api/search/route.ts` accepts:

```text
GET /api/search/?q=<term>&lang=zh|en
```

Successful responses have the shape `{ "results": [...] }`, where each result contains the article title, href, section title, and snippet. Empty or whitespace-only queries return an empty result set. Queries longer than 80 characters return `400 QUERY_TOO_LONG`; an index loading failure returns `503 SEARCH_UNAVAILABLE`. Successful responses may be cached briefly; error responses are not cached.

The browser search component must treat non-2xx responses and malformed JSON as errors rather than as an empty search result.

## Data flow

The download dashboard reads six CSV/metadata pairs plus a generated manifest from `public/data/dev-npm-downloads/`. The unified updater in `scripts/update_dashboard_data.py` calls the guarded builders in `lib/`. The dashboard component parses only the validated data contract and renders charts as inline SVG; there is no chart-library runtime dependency.

`npm run validate:data` checks the committed artifacts without network access. CI runs typecheck, build, tests, and data validation before a PR can be merged.

## Styles and special pages

Global CSS is imported from `app/globals.css` in this order: tokens, base/reset, header, home, dashboard, and article. Keeping this order explicit is part of the cascade contract. The key metrics page uses a locally scoped CSS Module while retaining its existing global DOM class names for visual compatibility.

`Demand/Dev_npm_downloads` and `Resources/Agora_Key_Metrics` are special pages with dedicated components. They should not be forced into the article loader or the article manifest union merely to reduce the number of route files.
