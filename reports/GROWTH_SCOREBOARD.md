# DAUNTRA growth scoreboard — baseline 27 September 2026

North-star chain: qualified attention → organic/social landing → **new waitlist row** → invited beta → activated user → eventual paid user. A duplicate 201 acknowledgement is not a new row. Do not divide the eight lifetime waitlist signups by the last-30-day 110 visits: the windows differ.

| Layer / metric | Definition and source | Baseline | First decision use |
|---|---|---:|---|
|Business · new leads|New unique `waitlist_signups` rows by `created_at`, excluding duplicates and tests; Supabase read-only export|8 lifetime (founder)|Weekly source/landing cohorts after approved migration|
|Business · landing conversion|New rows attributed to path ÷ eligible sessions on that same path and window|Unknown|Compare tool vs product vs homepage; sample-size caution|
|Business · source conversion|New rows by first-touch source ÷ source sessions, same period|Unknown; founder attributes 2 recent to Reddit, 1 friend|Put manual effort where qualified leads occur|
|Business · beta activation|Invited users completing a defined first workout + first return visit, with consented internal join key|Unavailable|Define with product team when beta exists|
|SEO · coverage|Indexed intentional pages, sitemap status, canonical and exclusion reasons; GSC|2 indexed pages (founder)|Inspect newly launched routes; do not equate submitted with indexed|
|SEO · query demand|Non-brand impressions/clicks/CTR, GSC query+page weekly exports|2 total search clicks; non-brand split unknown|Re-rank opportunities from actual queries after release|
|SEO · useful entrances|Organic landing sessions into tools and product pages, by page|0 known on new routes|Tool completion and signup downstream|
|SEO · assisted conversion|Organic landing → tool_completed → product proof/form → new row, same consented session|Unknown|Identify the pages that assist, not only last-click|
|Social · attention quality|3-second survival = 3-sec plays / eligible starts; average watch time; completion|Facebook 36 3-second views/276 reported views; 728s aggregate (not cohort-normalized)|Creative V2 first-frame test|
|Social · intent|Profile visits/reach, link clicks/reach; UTMs where permitted|Instagram 6 profile visits reported, no reliable link clicks|Bridge from video to the right page|
|Social · leads|Unique new signup rows tied to source/UTM after migration|Meta effectively none observed|Do not scale a Reel based only on views|

## Instrumentation state

Client events: `seo_landing_view`, `tool_started`, `tool_completed`, `tool_result_shared`, `product_proof_viewed`, `demo_clicked`, `waitlist_form_started`, `waitlist_signup_success`, `waitlist_signup_failed`. Event payload is allowlisted: known paths, referring **origin**, sanitized UTMs, tool/proof ID; never email, entered weights/reps or full URL. Dispatch locally even if PostHog opt-in is off so tests can inspect. When enabled, a lazy slim PostHog client also emits the old `waitlist_started`, `waitlist_signup_succeeded` and `hero_demo_clicked` aliases for existing dashboards; the eager session-replay bootstrap was removed. The optional collector requires a validated project token and release privacy review. Cloudflare remains the pageview baseline. Browser form success means server acknowledgement, not a *new* row; use Supabase insert timestamp as lead truth. A first-touch session value is not durable cross-device identity.

The API accepts sanitized attribution now but stores it only after a founder-approved, locally tested nullable `attribution_json` migration and explicit `WAITLIST_ATTRIBUTION_DB_ENABLED=true`. Until then the only durable acquisition field remains `source=website`; source conversion remains unmeasurable in Supabase. If deployment uses a different analytics initialization than the checked-in code, verify its remote config, replay/autocapture and URL/PII policy before turning on new collection.

## Reporting cadence and quality checks

Every Monday, use matched seven-day windows and a 28-day context: GSC pages/queries, Cloudflare sessions, event funnel, unique new rows (read-only), and manual campaign log. Exclude internal/test traffic. Inspect denominators, bot spikes and duplicate rate. Qualitative Reddit notes are kept separate from attribution certainty. At 7 days validate routes/events, at 30 days use impressions and conversions to revisit keyword priorities, at 90 days evaluate activation and source quality. No page/rank/virality guarantee.
