# Codex Task — Add a Data Analysis subpage to Risk & Stability Insights

You are working inside the **Risk & Stability Insights** website repository at:

```
/Users/veerr_89/Work/website/risk-stability-insights
```

Your task is to **extend** this existing app with one new interactive Data Analysis page, driven entirely by a completed analysis handoff that lives in a separate repository on the same machine. You are **not** redesigning this site and you are **not** redoing any analysis.

---

## 0. Read this before writing any code

The analytical work is already finished, validated, and curated. It lives here:

```
/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/website-handoff/
```

From this website repository's root, that is:

```
../../projects/Profit-Stabilization-Predictive-Risk-Retention/website-handoff/
```

**Read this file first, completely, before anything else:**

```
../../projects/Profit-Stabilization-Predictive-Risk-Retention/website-handoff/HANDOFF.md
```

It contains the project question, the data description, six final insights with exact numbers, the headline metrics, the recommended page order, the synthesis copy, methodology, limitations, follow-up questions, and a full file manifest.

The other directories in the handoff:

```
../../projects/Profit-Stabilization-Predictive-Risk-Retention/website-handoff/assets/       # 6 static PNG figures
../../projects/Profit-Stabilization-Predictive-Risk-Retention/website-handoff/data/         # 16 small CSV/JSON files (~90 KB total)
../../projects/Profit-Stabilization-Predictive-Risk-Retention/website-handoff/supporting/   # insight_metrics.json — full validated metric dump
```

**Confidence intervals.** Every CI published anywhere in this package comes from a single seeded bootstrap run (percentile method, 4,000 resamples, seed 20260824) and is listed by name in `data/ci-registry.json`. That file is the canonical source. The data files, `insight_metrics.json`, `HANDOFF.md` and the PNG captions have all been verified against it — if you display a CI, it must match the registry.

Verify each path exists before proceeding. If any is missing, stop and report it rather than improvising.

---

## 1. Context: what this analysis is about

The site is a healthcare risk-analytics platform built on MEPS (Medical Expenditure Panel Survey) 2023 data. It scores members with a deployed XGBoost model and identifies a "low-risk" cohort.

The handoff is a focused **tail-risk analysis** of the same data. Its central question:

> Healthcare cost is extremely concentrated. Given that, what does a "low-risk member" actually mean — and does identifying one make a pool cheaper, or make it more predictable?

The six findings, in the order they should appear on the page:

1. **The "average member" does not exist** — 79% of people spend below the mean; the top 5% carry 49% of all spending.
2. **Income predicts routine spending, not catastrophic spending** — the poor-vs-rich cost gap is 62% on the median but only 18% on the mean.
3. **Counting diagnoses misses tail risk** — functional limitations carry more tail signal per unit than chronic conditions.
4. **The cheapest median in the population is also the most emergency-driven** — 9.2M people with 3+ chronic conditions and zero office visits.
5. **"Low spend" is partly a measure of access, not health** — at identical disease burden, uninsured members are ~5× more likely to be labelled low-risk.
6. **Risk selection lowers the cost level but makes the pool more tail-concentrated** — it is risk reduction, not risk elimination.

Insight 6 is deliberately self-critical about this platform's own model. Keep that framing — do not soften it.

This is a portfolio and interview artefact. The page should read as careful analytical reasoning, not as a marketing dashboard.

---

## 2. FIRST STEP — inspect the existing website. Do not start coding.

Before writing a single component, explore this repository and build an accurate mental model of it. At minimum, understand:

- **Framework and build** — `package.json`, `vite.config.ts`, `tsconfig*.json`, `tailwind.config.ts`, `components.json`
- **Routing** — how routes are declared and named, and how a new route is registered
- **Layout and navigation** — the app shell, sidebar, top bar, and how a page slots into it
- **Design tokens** — the CSS custom properties in `src/index.css`, the Tailwind theme extension, and which semantic colour names exist (`primary`, `muted`, `card`, `accent`, `border`, …)
- **Typography** — the font families already loaded and how headings, body copy and monospace text are styled
- **Spacing, card and section conventions** — how existing pages structure a page header, a section, a card, a chart container
- **Existing chart components** — look at `src/components/dashboard/` and learn the established charting library, colour usage, tooltip style, axis style, responsive-container pattern, and empty states
- **Reusable primitives** — `src/components/ui/` (shadcn), `src/components/InsightBlock.tsx`, `src/components/EmptyState.tsx`, `src/components/NavLink.tsx`
- **Existing storytelling patterns** — how the app already narrates results (for example the story/narrative panel on the Overview page and `src/lib/narratives.ts`)
- **State and data access** — `src/contexts/DataContext.tsx`, `src/lib/`, and how existing pages get their data
- **Access control** — check whether pages are gated by a Researcher/Customer role. If such gating exists, the new page must respect it and be visible to both roles (it uses no uploaded data)
- **Light/dark behaviour** — check whether a theme toggle actually ships. Match whatever the app really does; do not introduce a new theming mechanism
- **Responsive behaviour** — how existing pages handle small screens

Write a short summary of what you found before you implement. If anything in this brief conflicts with the real conventions of the repository, **follow the repository** and note the deviation.

---

## 3. Hard constraints — do NOT redesign this website

**Do NOT:**

- redesign or restructure the Overview/home page beyond adding one entry-point CTA
- replace or alter the existing visual identity
- introduce an unrelated dashboard aesthetic, or a "landing page" aesthetic
- change typography globally, or add new font families
- change the site's colour palette, or add colours outside the existing token set
- add generic gradients, glassmorphism, neon accents, or decorative blur
- wrap every paragraph in a card — use cards only where the existing app uses cards
- rewrite unrelated content or copy
- refactor, "clean up", or alter working functionality that is unrelated to this task
- add heavy new dependencies when something already installed does the job
- modify anything inside the analysis repository

**DO reuse:**

- the existing design system and CSS custom properties
- existing shadcn/ui primitives and existing dashboard chart components (or components built in exactly their style)
- the existing charting library already used by this app — do not introduce a second one
- existing navigation, layout, spacing, typography and transition conventions
- the existing page-header and section patterns

The new page must look as though it has always belonged to this project. **Only extend the site.**

---

## 4. Entry point

Add one tasteful call-to-action on the existing Overview page that links to the new analysis route. Choose the label that fits this app's tone better:

- **"What the Data Tells Us"** — preferred if the app's voice is narrative
- **"Explore Data Analysis"** — preferred if the app's voice is utilitarian

Place it where it reads naturally within the existing Overview layout — near the existing narrative/story panel is likely right. It should be a single, understated element consistent with existing button and link styling. Do not add a hero banner, a promotional card, or multiple CTAs.

Also register the page in the sidebar navigation using the existing navigation-item pattern and an appropriate `lucide-react` icon consistent with the icons already in use.

**Route.** `/analysis` fits the existing flat kebab-case route convention (`/risk-lab`, `/low-risk`, `/member-scorer`). Confirm that against the real router before committing to it, and use a different route only if the repository's actual convention demands it.

---

## 5. The analysis page

Build a single scrollable analytical story. Use the ordering from `HANDOFF.md` ("Recommended page order"):

1. **Analytical question** — a short intro (2–4 sentences) framing the tail-risk question and naming the data (MEPS HC-251 2023, 18,463 weighted person-years, 334.5M people represented). Copy is in `HANDOFF.md`.
2. **Headline metrics** — four metric tiles. Use `data/headline-metrics.json` verbatim: `value` is the display string, `label` is the primary caption, `sub` is the supporting line. Style them like the existing KPI tiles on the Overview page.
3. **Insight 1** — cost concentration
4. **Insight 2** — income: routine vs catastrophic
5. **Insight 3** — chronic vs functional burden
6. **Insight 4** — the disengaged-chronic segment
7. **Insight 5** — the label measures access
8. **Insight 6** — selection concentrates the tail
9. **What the data collectively tells us** — the synthesis section. Use the prose in `HANDOFF.md`. Do not re-list the charts here.
10. **Limitations** — all eight, visible and honest. Not hidden behind an accordion that defaults closed unless that is an established pattern in this app.
11. **What I would investigate next** — the four follow-up questions from `HANDOFF.md`.

**Each insight section must contain:**

- a **finding-based headline** (the insight title from `HANDOFF.md` — a claim, never a topic label like "Cost by Segment")
- the **visualization** (interactive or static, per section 6)
- the **key numbers**, surfaced so they are readable without parsing the chart
- the **"Why it matters"** interpretation
- the **implication**, where `HANDOFF.md` gives one
- the **caveat**, visibly attached to the insight — not collected into a footnote at the bottom of the page

Keep the reading rhythm consistent across all six sections. Do not make one section a showcase and the rest an afterthought.

---

## 6. Visualizations — which are interactive, which stay static

Use the app's existing charting library. Data files live in `../../projects/Profit-Stabilization-Predictive-Risk-Retention/website-handoff/data/`.

| Insight | Chart | Treatment | Data files |
|---|---|---|---|
| 1 | Cost concentration | **Interactive** | `chart-01-concentration-curve.csv`, `chart-01-spend-distribution.csv`, `chart-01-summary.json` |
| 2 | Income routine vs catastrophic | **Interactive** | `chart-06-income-decomposition.csv`, `chart-06-gap-metrics.csv` |
| 3 | Chronic vs functional burden | **Interactive** | `chart-03-burden-matrix.csv`, `chart-03-logit-effects.json` |
| 4 | Disengaged-chronic segment | **Interactive** | `chart-04-engagement-bands.csv`, `chart-04-segment-profile.csv`, `chart-04-summary.json` |
| 5 | Label measures access | **STATIC — use the PNG as-is** | `chart-05-*.csv` supplied for reference only |
| 6 | Selection concentrates the tail | **Interactive** | `chart-02-pool-concentration-curves.csv`, `chart-02-pool-stats.csv` |

**Insight 5 stays static on purpose.** Its value is the side-by-side juxtaposition of a controlled comparison and a composition breakdown — a designed-figure job. Rebuilding it interactively would add hover without adding comprehension. Render `assets/chart-05-label-measures-access.png` as an image with proper `alt` text and responsive sizing.

**Suggested interactions — only where they help answer the analytical question:**

- **Insight 1** — hover the concentration curve to read "top X% of members = Y% of spending"; mark the 1/5/10% points; draw the mean and median as annotated reference lines on the distribution
- **Insight 2** — hover the stacked bars to break out routine vs catastrophic; a toggle between "median view" and "mean view" makes the whole point of the finding tangible
- **Insight 3** — heatmap with hover revealing n, median, $20k+ rate and its CI; optionally a toggle between colouring by catastrophic rate and colouring by median cost. Suppressed cells (`suppressed = 1`) must render as visibly suppressed with an "n < 40" note, never as zero or as a gap
- **Insight 4** — hover the acute-share line to compare the two burden groups at each office-visit band
- **Insight 6** — a selector or legend toggle between the three pools, with the concentration curves overlaid so the "selected pools are steeper" point is visible directly

**Do not make everything interactive.** No animation for its own sake, no drag/zoom that serves nothing, no filters that do not change an answer.

**Do not invent data.** Never interpolate, smooth, extend, or synthesise points to make a chart look better. If a chart needs a value the data does not contain, leave it out and say so.

Charts must be responsive, must degrade gracefully on mobile (the heatmap and the multi-series curves especially), and must use the app's existing tooltip and axis styling.

---

## 7. Getting the assets and data into this repository

You have read access to both directories. Copy what you need **into this website repository** so it stays independently deployable. Do not modify the analysis repository. Do not create any runtime dependency on it, on notebooks, or on Python.

**Data (~80 KB total).** Preferred approach: convert the CSV/JSON files into typed TypeScript modules under `src/data/analysis/` (or wherever this repo keeps static data — check `src/data/` for the existing convention). At this size, inlining is better than a runtime fetch: no network failure mode, no loading state, no CORS, fully type-checked. If the repository's established pattern is clearly to serve static data from `public/data/` and parse it at runtime, follow that instead and use the CSV parser already installed.

**Images.** Copy only the PNGs you actually reference into `public/` (for example `public/analysis/`), and reference them by absolute path. `chart-05-label-measures-access.png` is required. The other five are optional — include them only if you provide a genuine "view the original figure" affordance next to the interactive version; do not ship 1.5 MB of images that nothing links to.

After copying, verify a production build succeeds and that no import reaches outside the repository.

---

## 8. Analytical integrity — the most important rule

**The handoff is the analytical source of truth. Do not redo the analysis and do not invent conclusions.**

You **may**: format, lay out, visualize, annotate, organize, make charts interactive, tighten wording for readability, and add transitional copy that carries the reader between sections.

You **may not** silently alter:

- any number, percentage, dollar figure, count, ratio, odds ratio, confidence interval or sample size
- any metric definition (for example: `LOW_RISK` = bottom-30% spend, $484 threshold, plus zero ER visits and zero inpatient stays; catastrophic = `$20,000`+; routine = the first `$5,000` of spend)
- any conclusion, interpretation, or implication
- any caveat or limitation
- the strength of any claim — in particular, Insight 3's compared cells have **overlapping confidence intervals** and must be described as *equivalent* tail risk, never as *higher*

Rounding for display is acceptable when the handoff itself shows a rounded form (for example `79%` for 78.9%, `49%` for 48.7%). Keep the exact values available in the underlying data and in tooltips. Never round in a direction that strengthens a claim.

Use the **weighted** figures throughout. The platform's older documentation quotes an unweighted mean of `$8,422`; this analysis uses the survey-weighted mean of `$7,487`. Do not mix them, and do not "correct" one to match the other.

Cross-check any number you display against `supporting/insight_metrics.json`, and every confidence interval against `data/ci-registry.json`. **If you find an inconsistency between `HANDOFF.md`, the data files, and the metric dump, stop and flag it in your report. Do not guess which one is right and do not quietly pick one.**

---

## 9. Definition of done

- [ ] You inspected the existing repository and summarised its conventions before implementing
- [ ] One new route exists, registered in the router and in the sidebar navigation using existing patterns
- [ ] One understated CTA on the Overview page links to it
- [ ] The page follows the 11-section order from `HANDOFF.md`
- [ ] Four headline metric tiles match `data/headline-metrics.json` exactly
- [ ] Six insight sections, each with a finding-based headline, visualization, key numbers, interpretation, implication where given, and a visible caveat
- [ ] Five charts are interactive and built from the handoff data; Insight 5 uses the supplied PNG
- [ ] Synthesis, all eight limitations, and all four follow-up questions are present
- [ ] No new fonts, no new colours outside the token set, no new charting library, no global style changes
- [ ] No file in the analysis repository was modified
- [ ] Data and images are copied into this repository; nothing imports across the repo boundary
- [ ] Production build passes and the linter is clean
- [ ] The page is responsive and readable on a phone
- [ ] Every displayed number traces back to `HANDOFF.md` or the data files

## 10. Report back with

1. What you found during the repository inspection, and any convention in this brief that you had to override to match the real codebase
2. The files you created and the files you modified
3. Which charts you made interactive and what interaction each one supports
4. Any inconsistency you found in the handoff — flagged, not resolved
5. Anything you deliberately left out, and why
