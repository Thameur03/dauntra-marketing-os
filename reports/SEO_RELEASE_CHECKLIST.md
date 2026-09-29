# SEO release checklist — approval-gated

**Do not deploy from this task.** Website deployment and production migration require founder approval; guide publication requires documented human review. Search Console access was not available during implementation.

## Pre-release validation

- Confirm the capability manifest still allows every product claim; visually compare the actual product recordings to surrounding copy. The analytics page must reference only the audited 5.507-second `Progress_Analytics_audited_excerpt.mp4`, not the longer source with the unapproved Insights/recovery panel. No Lab Insights marketing, App Store availability, trials, coach prescription, launch date or implied TestFlight invite.
- Run `npm run lint` (or scoped ESLint if whole-repo scanning exhausts the Node heap), `npx tsc --noEmit`, `npm run build`, `npm run cf:build`, `node --experimental-strip-types --test tests/growth.test.mjs`; fix regressions. Check content-guide review gating and `git diff --check`.
- Test 390px and 1440px: no horizontal overflow, form/keyboard/links usable, one H1, tool labels/results accessible, authentic video posters load with no autoplay. Recheck local Lighthouse/PageSpeed resources and LCP; the latest measured local mobile LCP was about 4.5 seconds, not a performance pass. Then verify on real devices.
- Inspect environment: enable website PostHog only intentionally. The approved website Session Replay starts lazily after the first approved growth event; verify masked inputs, no email/form contents, no full-URL capture, no waitlist `identify()`, and no automatic event capture. Keep `WAITLIST_ATTRIBUTION_DB_ENABLED=false` until migration applied and verified.
- Human-review pending guides: `/guides/how-to-track-progressive-overload`, `/guides/how-to-track-workout-progress` must return `noindex` and must **not** appear in `/sitemap.xml` or hub links. The `/guides` hub itself is noindex until at least one guide is approved. Do not set `approved` without reviewer/date/source packet decision.

## After separately approved deployment

- Confirm `https://dauntra.com/robots.txt` allows public pages, disallows `/api/`, points to `https://dauntra.com/sitemap.xml`; submit that sitemap in Search Console. The sitemap should include `/`, three product pages, `/tools`, two tool pages, `/methodology`, `/faq`, `/privacy`, `/terms` (11 URLs) and only later approved guides/hub.
- URL Inspect `/workout-tracker`, `/progressive-overload-tracker`, `/workout-analytics`, `/tools/progressive-overload-calculator`, `/tools/workout-volume-calculator`, `/methodology`. Ask indexing for priority URLs after the actual crawl shows correct canonical; sitemap submission does not guarantee indexation.
- Inspect `/blog` → `/guides` redirect, `/delete-account` noindex and sitemap exclusion, pending-guide noindex, true unknown URL 404, HTTPS, non-www host canonical. **www was not resolvable from this environment**; either configure a 301 host redirect in Cloudflare/DNS or keep it unresolved, not a duplicate 200 host.
- Check each page's `<title>`, description, canonical, OpenGraph/Twitter card, image 200/content-type/size, one H1, crawlable links, returned HTML content and status. Verify no accidental `noindex` on money/tools pages. Tool query/filter states must not generate indexable duplicates.
- Test Organization/Breadcrumb and approved-only Article markup with Google Rich Results Test or Schema Markup Validator. Avoid FAQ/VideoObject/SoftwareApplication claims without eligibility and metadata. A valid schema is not a rich-result entitlement.
- Manually submit a test waitlist request from a known campaign URL, verify only one insert for repeated email and no PII in event payload/URL. Test the form without analytics. Do not use a real person's email without permission.
- Run a post-deploy crawl (manual or crawler) for broken links/media, assets, title duplication, redirects and accidental utilities. Check 390px/1440px live rendering and mobile LCP/INP/CLS field data after enough traffic. An above-fold 61s recording should stay poster/preload-none/user initiated.

## Days 1 / 7 / 30 / 90

Day 1: sitemap and seven priority URLs inspected, event/form smoke test, 404/robots/canonical, media and noindex verified. Day 7: index coverage and query/page export; diagnose exclusions, crawl errors and CTA tracking. Day 30: non-brand impressions/clicks, tool starts/completions, new signups by source/landing **only if attribution migration is approved**, and top queries/intent mismatch. Day 90: refresh, merge or expand based on qualified signups and beta activation; do not add pages merely because pages were indexed.

## Independent approval gates

1. Website deployment: founder reviews rendered desktop/mobile and privacy/copy.
2. Database: founder explicitly approves `supabase/migrations/20260927_waitlist_attribution.sql`; run in staging/local first, make backup, then set flag only after verifying production schema. Without this, event-level attribution is provisional, not durable signup attribution.
3. Guides: create/link a real source-validated research packet, then a real human evidence reviewer signs it, sets reviewer/reviewedAt/publishedAt, and confirms all citations/claims. Current `researchPacket: null` is deliberately not an approval. Only then may a guide enter the sitemap.
4. Creative: separate visual/factual/human approval bound to asset SHA. This task does not publish anything.
