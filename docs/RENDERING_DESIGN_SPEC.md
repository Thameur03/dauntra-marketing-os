# DAUNTRA Marketing Rendering Design System

## Status

Section 4 visual specification.

The C02 social renderer adopts the visual language established by the
DAUNTRA Lab Insights interface while remaining a marketing surface rather
than a literal reproduction of application navigation.

Public marketing must not imply that Lab Insights is currently a marketed,
production-ready capability unless product truth is updated to allow it.

For this reason, the public rendering label is:

`DAUNTRA // EVIDENCE`

rather than:

`DAUNTRA LAB`

The label can be changed later without changing the renderer architecture.

---

# 1. Core Visual Character

The system should feel:

- analytical
- premium
- quiet
- performance-oriented
- technical without looking clinical
- data-aware
- product-native
- recognizably DAUNTRA

Avoid:

- generic social-media templates
- motivational-poster aesthetics
- excessive decoration
- neon cyberpunk styling
- medical/laboratory claims
- crowded cards
- unnecessary icons
- orange as the primary accent for this template family

---

# 2. Canvas

Instagram carousel:

- width: 1080 px
- height: 1350 px
- ratio: 4:5
- output: JPEG

The source Lab interface uses approximately 55 px side margins on a
1080 px-wide device.

The marketing renderer increases this to approximately 72–76 px to create
a safer social-media reading area.

---

# 3. Palette

## Background

Primary:
`#020812`

Secondary:
`#061426`

Raised/deep surface:
`#08182B`

## Text

Primary:
`#F7F8FA`

Secondary:
`#D6DCE5`

Muted:
`#77879B`

## Signal Blue

Primary:
`#2F91FF`

Bright:
`#55A9FF`

Dim:
`#1759A6`

Ghost:
blue at approximately 10–24% opacity

The blue signal system is specific to this evidence/insight visual family
and does not replace DAUNTRA's global product brand tokens.

---

# 4. Typography

## System label

Examples:

- DAUNTRA // EVIDENCE
- YOUR LATEST READ
- WHAT IT MEANS
- ONE NEXT MOVE

Characteristics:

- uppercase
- medium/bold
- wide tracking
- electric blue
- small relative to headline

## Hero headline

Characteristics:

- uppercase
- condensed
- heavy
- extremely high contrast
- short lines
- dominant visual element

Preferred local family:

`DejaVu Sans Condensed`

Fallbacks:

- Liberation Sans
- DejaVu Sans
- sans-serif

## Supporting copy

Characteristics:

- normal-width sans serif
- white / light gray
- readable line spacing
- no giant paragraphs
- secondary to the hero headline

---

# 5. Signature Signal Graphic

The renderer uses a DAUNTRA signal motif:

- diagonal ascending blue trajectory
- glowing endpoint
- secondary dotted line
- faint parallel ghost trajectories
- restrained blue atmospheric glow

It communicates:

- trend
- progress
- direction
- comparison
- data
- interpretation

The signal is decorative in C02 educational posts.

It must not visually imply a numeric result that is absent from the
underlying evidence.

---

# 6. Progress Rail

Top of every carousel slide:

- one segment per carousel slide
- completed/current segments use blue
- future segments use muted gray
- no fake mobile "Skip" control

This borrows the Lab Insights rhythm while adapting it to social media.

---

# 7. C02 Slide Roles

## Opening slide

Kicker:
`YOUR LATEST READ`

Purpose:

- introduce one evidence question
- strongest visual hierarchy
- large negative space
- signal graphic prominent

## Evidence / interpretation slides

Kicker:
`WHAT IT MEANS`

Purpose:

- explain one evidence point per slide
- maintain strong headline
- body remains readable
- emphasis treatment functions like a concise interpretation legend

## Final slide

Kicker:
`ONE NEXT MOVE`

Purpose:

- practical interpretation
- strongest action/takeaway treatment
- emphasis box becomes a blue action panel

This does not turn scientific uncertainty into certainty.
Copy remains governed by research and factual QA.

---

# 8. Navigation Adaptation

Do not reproduce application navigation literally.

Do not include:

- Skip
- fake tappable arrows
- application tab bars
- fake buttons implying an unavailable feature

Allowed:

- segmented progress rail
- simple slide number
- visual line/arrow motifs
- social CTA copy when supplied by the content system

---

# 9. Rendering Rules

All outputs must:

- be deterministic for the same input and renderer version
- pass geometry/overflow detection
- be exactly 1080×1350 for INSTAGRAM_FEED
- produce SHA-256 metadata
- preserve template version
- preserve renderer version
- create no database write during local visual QA

---

# 10. Current Version

Template:

`c02_lab_v1-dev`

Renderer:

`render_v1-dev`

The template remains development status until visual QA is approved.
