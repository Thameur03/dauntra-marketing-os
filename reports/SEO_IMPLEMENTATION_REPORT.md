# SEO implementation report — 27 September 2026

Status: local code only. **Not deployed.** Search rankings, indexing and production analytics have not changed as a result of this work.

## Acquisition surface built

| Route | Purpose / unique value | Conversion bridge |
|---|---|---|
| `/workout-tracker` | Commercial entry for recording sets/reps/load and seeing prior performance; authentic DAUNTRA workout recording | Inline Request Early Access form; related progression/tool links |
| `/progressive-overload-tracker` | Tracking, not automatic load prescription; prior-set proof and comparison boundaries | Inline form; two-set comparison tool |
| `/workout-analytics` | Weekly logged volume/sets/frequency and muscle-distribution interpretation, with real analytics recording | Inline form; volume tool |
| `/tools/progressive-overload-calculator` | Ungated comparison of two completed sets; load/reps shown separately; one consistent Epley estimate and limits | Tool result → tracker → form |
| `/tools/workout-volume-calculator` | Ungated set/exercise volume-load breakdown, visual bars and CSV; explicit limits of tonnage | Tool result → analytics → form |
| `/tools`, `/methodology` | Crawlable tool navigation and an honest evidence/process explanation | Relevant tool/product, then form |
| `/guides` | Navigation while guides await evidence approval; **noindex until it contains approved guides** | Tool/product links, then form |

Two detailed guide drafts exist at `/guides/how-to-track-progressive-overload` and `/guides/how-to-track-workout-progress`. They are **noindex, absent from sitemap and unpromoted** because source-linked research packets and named human approval are not yet attached. Their content has concrete examples and links, but code compilation is not editorial clearance. No Lab Insights page was created because the capability manifest forbids marketing that feature.

## Technical foundation

- A single canonical utility uses the HTTPS non-www host and strips non-root trailing slashes; `/blog` redirects to `/guides` instead of an empty content hub. Each public acquisition page has a unique title/description, canonical, OpenGraph/Twitter metadata, semantic H1, and crawlable internal links. Root canonical/sitemap both use `/`.
- `sitemap.ts` lists 11 intended public URLs, with actual edit dates rather than build-time timestamps. Pending guides, the thin guide hub, account deletion and API are excluded. `robots.ts` points to the sitemap and disallows API crawling, not site crawling. The guide hub, account deletion and draft guides have `noindex`.
- Sitewide Organization JSON-LD and visible BreadcrumbList JSON-LD use only true fields. No invented review/rating/offer schema, FAQ rich-result bait or VideoObject without publication metadata. An OG image is generated locally.
- Homepage claim language, FAQs and privacy copy were aligned with `brand/capability_manifest.yaml`: no marketed Lab Insights, automatic prescriptions, launch dates, Store availability or trial promises. The founder's pre-existing homepage H1 edit was preserved. Real product recordings and posters are user-initiated, `preload=none`, not autoplay. A second visual pass replaced a workout poster caught on a loading state with an authentic completed-set/“Match Last” frame. It also limited the analytics proof to an authentic 5.507-second workout-analytics excerpt (295,686 bytes) because later footage opened an unapproved Insights/recovery panel; the page does not link the long source.
- Server-rendered content and plain HTML links carry the SEO explanation; calculators alone are client components. Input labels, keyboard controls, fieldsets, status messages and mobile layout are present. Screenshots and route inspections covered 390px and 1440px.
- A structured JSON guide format and restricted renderer provide maintainable content metadata without a heavy CMS. `approved` requires a real packet, reviewer and date. The legacy empty MDX blog route remains non-discoverable and redirects from `/blog`.

## Conversion and attribution

The primary CTA is Request Early Access. Tools show results without email. The site records allowlisted, privacy-safe client events for landing, tool, product proof, demo and form steps. Events do **not** carry email or calculator inputs. UTMs are character/length constrained; referrer is origin-only; landing paths are known-route only. First touch lasts only for the browser session, not cross-device.

The waitlist API accepts sanitized optional attribution without changing its existing `source=website`, origin protections, honeypot or duplicate-email success behavior. Durable per-signup attribution is **off by default**. `supabase/migrations/20260927_waitlist_attribution.sql` adds one nullable JSONB column; it passed a disposable local PostgreSQL test but was **not applied to production**. After founder approval, apply the migration, verify privacy/analytics configuration, then set `WAITLIST_ATTRIBUTION_DB_ENABLED=true`. Until then, source→new-row conversion is not reliably measurable. A browser success event may include a duplicate acknowledgement; new rows are the authoritative lead metric.

The second-pass Lighthouse audit found a missed root-level `instrumentation-client.ts`: it eagerly initialized full PostHog with session replay, remote flags and third-party bundles on every page. The local production build loaded `posthog-recorder.js` and `dead-clicks-autocapture.js`, with a 55/100 mobile performance score. That eager bootstrap is now replaced by one lazy, slim, explicit-event client: replay/autocapture/pageview/external dependency loading and remote flags are off, persistence is memory-only, and legacy waitlist/demo event names are emitted alongside the new event names for dashboard continuity. Cloudflare Web Analytics remains the pageview baseline. A subsequent valid local run scored 65 performance / 100 SEO / 100 accessibility; two later runs ended in local Chrome `NO_FCP`, so no valid final-run score is claimed. A 4.5-second LCP in the valid run and run-to-run variance remain concerns, not a production Core Web Vitals pass. Production tags/data policy still need a separate release review; no production collector was changed here.

A synthetic-browser QA run observed local growth events and confirmed the slim client initialized and called `capture()`, but did **not** observe an outbound PostHog request. The SDK contains a bot-event filter, so this is not proof of a production failure or delivery. Collector receipt needs a separately approved staging/real-browser test. The local interceptor prevented any potential test request from reaching the production collector.

A separate fully mocked form run verified the client POST body: `/tools/progressive-overload-calculator` was retained as `landing_path`, `reddit/organic/compare_sets` UTMs and `first_touch_source=reddit` were present, and the fake email appeared only in the body. The form emitted start/success events after an intercepted 201. It did not call Supabase and does not prove a new-row insert or durable source attribution.

## Verification and limits

- `npm run build` passed, including static generation of intentional routes. `npm run cf:build` passed after removing the legacy MDX runtime import from the empty blog route.
- `npm run lint` passed after excluding generated `.open-next` bundles and vendored `.agents` scripts; scoped application lint had already passed. `npx tsc --noEmit` passed. Five local arithmetic/CSV/attribution tests passed.
- Local HTTP smoke checks: 11 intentional sitemap URLs have titles/descriptions/canonicals/one H1; unknown page 404, `/blog` redirect 308, `robots.txt`, `sitemap.xml` and OG image 200; pending guides carry `noindex`. At both 390px and 1440px, browser checks found no horizontal overflow; calculator interaction and safe local event emission worked. The SEO smoke suite has five tests, including the audited analytics excerpt media check.
- Disposable PostgreSQL migration test passed. The actual production schema, source-tagged signup and Cloudflare deploy still require approved release testing. Lighthouse, rich-result validation and GSC URL Inspection are release tasks; local build does not prove field CWV or indexing.
- The prior SEO baseline had two indexed pages and two clicks, supplied by the founder. There is no GSC export or reliable keyword-volume data; do not interpret implementation as demonstrated organic growth.

## Release gate

Do not deploy until product-copy/human guide review, privacy/PostHog review, migration choice, and local→staging signup tests are accepted. The exact checklist is `SEO_RELEASE_CHECKLIST.md`. No production DB migration, deployment or sitemap submission occurred during this task.
