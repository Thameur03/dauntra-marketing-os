# DAUNTRA growth diagnosis — 27 September 2026

## Business baseline

Founder supplied, not independently queried: approximately 110 visits / 270 pageviews in 30 days; Search Console 2 clicks / 2 indexed pages; 8 lifetime waitlist signups, 3 recently (2 Reddit, 1 friend). These windows are not aligned: **8 / 110 is not a valid conversion rate**. No demonstrated Meta-to-waitlist conversion. Facebook 276 views, 36 three-second views and 728 seconds total watch time; 36/276 ≈13% is an indicative ratio, not a platform-normalized retention cohort. 728/276 ≈2.64 seconds per reported view is descriptive only. Instagram small counts cannot support statistical conclusions.

The acquisition bottlenecks are discoverability, immediate creative comprehension, product proof and attribution. Beta activation cannot happen at scale before product distribution/backend readiness. This project improves the attention-to-signup segment; it does not resolve Apple/TestFlight/StoreKit readiness.

## Read-only website audit

Verified package: Next 16.3.4 range, React 19.2.4, OpenNext 1.20.6 range, Cloudflare Workers, Supabase, gray-matter, next-mdx-remote 6, posthog-js 1.416 range. Empty content/blog directory. Homepage consists of one hero/form, decorative portal and footer; authentic recordings exist but are not exposed in the current hero. Public live H1: Track / Understand / Improve. Local uncommitted H1: See what your training is actually doing (preserve).

Live HTTPS 200; HTTP→HTTPS 301; unknown path 404. www did not resolve from this environment: no evidence of a functioning www redirect. No horizontal overflow observed at 390/1440. Canonical homepage exists. robots allows public site; sitemap has homepage, privacy, terms, account deletion and FAQ. No acquisition pages or tools. Blog hub is empty and absent from sitemap. The metadata OG/Twitter title differs from page title; social image is an 830×178 SVG wordmark, not a useful large social preview.

Manifest audited 18 September, product commit a483f58b4ccb441a723f1df7258cbd5b05c6676d. Lab Insights marketing_allowed=false. Homepage description promises coach-style Lab Insights, hero promises a next action, footer/FAQ advertise Lab Insights. Correct these before increasing exposure. Available claims: sets/reps/load, previous performance, history/programs, Epley estimates/PRs, weekly volume/frequency, muscle distribution, meal/calorie/macro tracking. No automatic progression prescription, bodyweight history, adaptive diet, AI coach, medical analysis, premium offer or free trial.

## Attribution audit

POST /api/waitlist accepts only email/company, checks exact Origin, 2KB body, JSON, normalized email, honeypot, 8s database timeout, duplicate 23505→same 201, follow-up email after new insert. Table has created_at, source constrained to website, consent_version; no acquisition columns. Browser calls hardcode page='/' and use inconsistent success name. Source/referrer/UTMs discarded.

Checked-in code has no PostHog init. **Live browser did load PostHog remote config, recorder, dead-click and web-vitals modules**, alongside Cloudflare beacon; therefore live deployment and source are not fully aligned. Loading recorder does not prove a recording was sent. No authenticated dashboard validation was available. Do not label production analytics inactive solely from local source. Release must verify actual opt-in settings and exclude replay/PII. Aggregate Cloudflare traffic cannot join individual conversions by itself.

## Decoded-video audit

Decoded MP4 frames at 0, .1, .5, 1, 4, 8, 12, 20 seconds; reviewed existing sheets as well. Motion proxy: resize RGB frames to 108×192, 30fps; mean absolute adjacent-frame channel difference on 0–1.05s. Density proxy: fraction of frame-zero pixels with max RGB >70. These measure visual activity, **not attention or retention**.

| Sample | Duration | First-frame bright fraction | First-second difference /255 | First >.5 difference | Main copy changes | UI | Audio |
|---|---:|---:|---:|---:|---|---|---|
| reel_8a… d04s2 creatine |24.1s|0.07%|0.2399|0.10s|4.0,10.2,17.1s|none|AAC|
| reel_8a… d01s3 split |24.5s|0.07%|0.2120|0.167s|~5.3,10.5,17.5s|none|AAC|
| reel_f7… d02s1 energy |25.0s|0.07%|0.2312|0.10s|~4.8,11.7,18.4s|none|AAC|

Frame zero contains tiny brand chrome and a dark background; main hook is invisible, starts fading by .1s and readable around .5s. First detectable change is not first meaningful story change. Typical scene holds 4–7s. Creatine timeline has main copy word counts 7/20/24/35 (CTA included; chrome excluded), mean 21.5; CTA shares last 7s with longest passage. Current headline sizes 64–76px at 1080; much smaller displayed on a phone. Formulaic visual sameness, no exercise interaction, no training receipts. First-frame failure is more pressing than comment CTA details.

Authentic Workout_tracking_opt.mp4: 1080×2400, 61.16s, variable framerate, AAC. Initial second nearly still; must choose a moving segment and use seekable pan/zoom from frame zero. Footage demonstrates logging, completion and rest timer. Previous-performance proof must be verified in footage/demo; never manufacture a history value.

## Pipeline/safety findings

ResearchPacket source-index validation and sensitivity flags; grounding validator; explicit capability allowlist; QA schema/factual/capability/health/platform/visual/duplicate/brand/human checks; immutable experiment identity and asset hashes; individual review decisions. Motion C adaptation preserves copy and chunks. Production Reel contract requires TRACK CTA and 18–25s; visual QA minimum 18s and audible 48kHz stereo AAC. A 15s link-in-bio canary cannot simply enter that contract. Keep creative experimentation separate until a later versioned contract is reviewed.

The dual scheduler's qa_passed() scans arbitrary JSON recursively for broad PASS strings rather than verifying the exact asset-bound QA/human decision. This is an existing operational risk; **not changed here**. Never connect the prototype to that path. The stricter publishing/export system already models approval and identities. Reconcile the scheduler's checks in a separately authorized change.

Instagram worker emits tracked URLs; Facebook TRACK worker also emits UTMs. Both inspected read-only, untouched. No verified account-level Reddit posting archive found; configuration keeps Reddit drafts/manual posting. Founder attribution is stronger evidence of current value than public brand-search absence. Do not invent the founder's username or posts.

## Decisions

Build useful, ungated tools with a product bridge; prioritize comparable-history problems over generic supplements/splits. Show truthful UI early. Use Request Early Access. Measure unique new signups with database timestamps, not duplicate form acknowledgements. Keep science/education review explicit. Stage everything locally; do not deploy or publish.
