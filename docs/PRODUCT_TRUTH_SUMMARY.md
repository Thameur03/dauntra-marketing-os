# DAUNTRA Product Truth Summary

Audit date: 2026-09-18

Audited product repository:

    Thameur03/forgefit-front

Audited commit:

    a483f58b4ccb441a723f1df7258cbd5b05c6676d

This summary is intentionally conservative.

---

## Current product state

DAUNTRA is pre-launch.

The audited repository indicates that the application had not yet been
published to the App Store, TestFlight, or Google Play at audit time.

Marketing must not describe the application as currently downloadable
until launch is verified separately.

---

## Strong current capabilities

The audited application supports:

- resistance workout logging
- sets, repetitions, and load
- previous-workout performance display
- local workout draft recovery
- rest timer and local rest-completion alert
- exercise search and animated demonstrations
- estimated 1RM calculation
- personal-record detection
- multi-week workout programs
- workout calendar scheduling
- training-volume analytics
- interactive anatomical muscle-volume visualization
- USDA-backed food search
- packaged-food barcode scanning through Open Food Facts
- daily calorie and macro tracking
- user-defined calorie and macro targets
- supported micronutrient tracking
- favorite individual foods

---

## Important unsupported capabilities

Do not market:

- conversational AI coach
- AI workout generation
- adaptive programming
- automatic progressive overload
- recovery prediction
- medical laboratory analysis
- blood-test analysis
- biomarker analysis
- Apple Health
- Apple Watch
- HealthKit
- Garmin
- Whoop
- Oura
- Fitbit
- Google Health Connect
- body-weight history
- body-fat tracking
- body measurements
- progress photos
- social community features
- data export
- public free trial
- 30-day waitlist rewards
- 60-day founding-member rewards

---

## Critical naming rule

The product contains a feature historically called "Lab Insights."

This feature does NOT involve:

- medical laboratories
- blood tests
- biomarkers
- diagnostics
- clinical interpretation

The audited implementation concerns patterns in training frequency and
nutrition-logging consistency.

Marketing should not use the name "Lab Insights" until its naming and
production deployment are intentionally verified.

---

## Audience conclusion

The strongest evidence-supported V1 audience is:

    data-oriented gym / resistance-training users

Secondary audiences:

    hypertrophy-focused trainees
    nutrition-data trackers

DAUNTRA is currently a weak fit for:

    endurance athletes
    wearable-first users
    medical-health trackers
    users seeking body-transformation photo/weight tracking

---

## Brand direction

Official product tagline:

    THE WORK, UNDERSTOOD.

Brand palette:

    Obsidian        #0A0A0A
    Graphite        #6B717C
    Mineral White   #F2F2F2
    Oxide Orange    #FF4A18
    Positive Green  #22C55E

Marketing should favor the DAUNTRA dark/orange identity.

---

## Source-of-truth hierarchy

For marketing:

1. `brand/capability_manifest.yaml`
2. `brand/product_truth.yaml`
3. `brand/brand_profile.yaml`
4. `brand/audience_profile.yaml`
5. `brand/content_strategy.yaml`

If documents conflict:

    capability_manifest.yaml wins for product claims.
