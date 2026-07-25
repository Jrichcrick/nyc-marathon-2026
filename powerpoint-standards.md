# PowerPoint Standards

**What this is:** the canonical quality bar for any deck built in this repo. It exists so
that "make it better" has a fixed target instead of a moving one. An LLM's default bar is
lower than JR's; this file raises the floor to JR's bar and writes it down so it can be
checked mechanically rather than argued about.

**How to use it:** build the deck, then score it against §5. Fix the lowest-scoring row.
Re-score. Stop when the gate in §5 is met — not when the deck "looks fine."

Three things this file is specifically here to settle, because they are the three that
never come out right on the first pass:

1. **Color** (§2) — decided in advance, no taste required
2. **Speaker notes** (§3) — what "meaty" actually means, with a template
3. **Metric updates** (§4) — how numbers enter a deck and how they get changed

---

## 1. Slide fundamentals

Non-negotiable, checked first because everything else assumes them:

| Rule | Value |
|---|---|
| Aspect ratio | 16:9 — 13.333 in × 7.5 in (33.87 cm × 19.05 cm) |
| Typeface | One sans, everywhere. `Aptos` / `Calibri` / `Segoe UI` — never mix, never a serif or display face |
| Title size | 32–40 pt |
| Body size | 18 pt floor. **If text must go below 18 pt to fit, the slide has too much on it** |
| Table / source line | 12 pt minimum, and only for source lines and table cells |
| Margins | 0.5 in hard edge margin. Nothing touches it |
| Ideas per slide | One. The title states it as a claim |
| Bullets per slide | ≤ 5, each ≤ 2 lines |
| Build/animation | None, unless a sequence is the point |

**Titles are claims, not labels.** "Q3 Revenue" is a label. "Q3 revenue grew 12%, all of it
from enterprise" is a claim. Every content slide gets a claim title. If you can't write the
claim, you don't yet know what the slide is for — that's a §5 zero, not a formatting nit.

**The slide is not the document.** If the argument needs prose, it belongs in the speaker
notes (§3) or an appendix slide, never crammed into the body at 14 pt.

---

## 2. Color

**You do not pick colors. You assign them.** Every color below has one job. Using a color
for a job it doesn't have is a defect, not a preference. All values are validated (see
§2.6) — do not substitute eyeballed hexes.

### 2.1 Surfaces and ink

| Role | Light slide | Dark slide (title/section only) |
|---|---|---|
| Slide background | `#fcfcfb` | `#1a1a19` |
| Primary text | `#0b0b0b` (19.2:1) | `#ffffff` (17.4:1) |
| Secondary text | `#52514e` (7.7:1) | `#c3c2b7` (9.7:1) |
| Muted — axis labels, source lines | `#898781` (3.5:1) | `#898781` (4.9:1) |
| Gridline (hairline) | `#e1e0d9` | `#2c2c2a` |
| Axis / baseline | `#c3c2b7` | `#383835` |

Pure `#ffffff` backgrounds and pure `#000000` text are both banned — they glare under
projection. Use the values above.

**Muted ink is for labels only.** At 3.5:1 it clears large-text contrast but not body text.
Never set a sentence in muted.

### 2.2 The categorical palette — identity, in fixed order

Assign slot 1 first, then 2, then 3. **Never cycle, never skip, never reorder.** The order
is what keeps the colors distinguishable to colorblind viewers; changing it breaks the
guarantee.

| Slot | Hue | Light slide | Dark slide |
|---|---|---|---|
| 1 | blue | `#2a78d6` | `#3987e5` |
| 2 | orange | `#eb6834` | `#d95926` |
| 3 | aqua | `#1baf7a` | `#199e70` |
| 4 | yellow | `#eda100` | `#c98500` |
| 5 | magenta | `#e87ba4` | `#d55181` |
| 6 | green | `#008300` | `#008300` |
| 7 | violet | `#4a3aa7` | `#9085e9` |
| 8 | red | `#e34948` | `#e66767` |

**One series = slot 1 only.** A single-series bar chart is all blue. Coloring each bar
differently spends the identity channel on nothing.

**Series cap on scatter / bubble / map / small-multiples: three.** In those forms any two
marks can end up adjacent, and past three slots the pairs stop being reliably
distinguishable. Fold the rest into "Other" or split into facets — do not add a ninth color.

**On light slides, slots 3, 4, and 5 sit below 3:1 against the background** (aqua 2.74,
yellow 2.11, magenta 2.62). They are legal only with a visible direct label on the mark. No
label, no sub-3:1 fill.

### 2.3 Magnitude, order, and polarity

- **Sequential** (how much — heatmap, choropleth): one hue, light→dark. Blue:
  `#cde2fb` `#b7d3f6` `#9ec5f4` `#86b6ef` `#6da7ec` `#5598e7` `#3987e5` `#2a78d6` `#256abf`
  `#1c5cab` `#184f95` `#104281` `#0d366b`. Never a rainbow.
- **Ordinal** (ordered stages — funnel, tiers, S/M/L): same blue ramp, but start no lighter
  than `#86b6ef` on a light slide, so the lightest step stays visible.
- **Diverging** (above/below a baseline): blue ↔ red, with gray `#f0efec` at the midpoint.
  Equal steps each arm. Never a hue at the midpoint.

### 2.4 Status colors — reserved, never decorative

| Role | Hex |
|---|---|
| good | `#0ca30c` |
| warning | `#fab219` |
| serious | `#ec835a` |
| critical | `#d03b3b` |

These four mean state and nothing else. Never reuse one as "series 4." Always paired with an
icon **and** a word — on a light slide, warning and serious fall below 3:1 by design, and
the label is the mitigation. A red number that only reads as bad because it's red fails.

For up/down deltas in text: good `#006300` (7.4:1), bad `#d03b3b` (4.7:1) — and always with
an arrow or a sign, never color alone.

### 2.5 Hard color rules

- **Text wears text colors.** Values, labels, and legend text stay in primary/secondary/muted
  ink. A colored swatch next to a label carries the identity — the label itself does not turn
  blue.
- **Never encode with color alone.** Every color distinction is backed by a label, a legend, a
  shape, or a position. Assume one viewer in twelve can't see the hue difference and one is
  looking at a grayscale printout.
- **No gradients on fills, no drop shadows, no 3-D anything, no transparency to "soften."**
- **Color follows the entity.** If a filter drops two series, the survivors keep their
  original slots — they don't get repainted.
- **≥ 2 series always gets a legend**; ≤ 4 series also gets direct labels. One series gets no
  legend — the title names it.
- **Never a dual-axis chart.** Two y-scales is the single most common chart defect. Two
  measures of different scale → two charts, or index both to a common base.

### 2.6 Validating a palette change

If the palette above is ever swapped for a brand palette, it is not a judgment call — it is
a script run. The values in §2.1–2.4 were validated with the `dataviz` skill's
`scripts/validate_palette.js` against these exact slide surfaces, in both modes:

```
node scripts/validate_palette.js "#2a78d6,#eb6834,#1baf7a,#eda100,#e87ba4,#008300,#4a3aa7,#e34948" \
  --mode light --surface "#fcfcfb"
node scripts/validate_palette.js "#3987e5,#d95926,#199e70,#c98500,#d55181,#008300,#9085e9,#e66767" \
  --mode dark  --surface "#1a1a19"
```

Both pass all six checks. Add `--pairs all` for scatter/bubble/map/small-multiples — that
run is what sets the three-series cap in §2.2. Any replacement palette must clear the same
gates before it ships. **Do not reason about whether colors are colorblind-safe. Run it.**

---

## 3. Speaker notes

The notes are where the substance lives. A deck whose notes say "discuss the numbers" is not
finished — it's a wireframe. **Every content slide gets notes. No exceptions.**

### 3.1 What "meaty" means

Meaty notes are what you would actually *say*, written out — not a summary of what's already
on the slide. Concretely, four things:

1. **The claim, spoken.** One or two sentences delivering the title claim in speech, not
   bullet-fragment shorthand.
2. **Where the number came from.** Source, as-of date, and how it was computed. If someone
   asks "is that gross or net," the answer is in the notes.
3. **The objection you expect, and the answer.** Name the pushback and answer it in one or two
   sentences. If there's no plausible objection, say what the slide *doesn't* claim.
4. **The transition.** One line that hands off to the next slide.

**Length: 80–200 words per content slide.** Under 80 and it's a label, not notes. Over 200
and it's a script nobody will read live. Section dividers and the title slide are exempt.

### 3.2 Template

```
CLAIM: <one or two spoken sentences delivering the title>
SOURCE: <system / file / query>, as of <YYYY-MM-DD>. <Basis: gross vs net, cohort, currency.>
OBJECTION: "<the pushback, in the audience's words>" → <the answer>
NEXT: <one line handing off to the following slide>
```

Keep the four labels. They make notes gradeable, and they make it obvious when one is
missing — which is the whole point of having a bar.

### 3.3 Notes rules

- **Notes never contradict the slide.** If the slide says 12% and the notes say 11.6%, that's
  a defect — state the rounding explicitly instead: "11.6%, shown rounded to 12%."
- **Notes are not a dumping ground.** Detail that a reader needs goes on an appendix slide;
  notes carry what the *speaker* needs.
- **No unsourced numbers in notes either.** §4 applies to notes exactly as it applies to
  slides.
- **Write them in the voice of the person presenting**, first person, contractions fine. Notes
  written in press-release voice don't survive being read aloud.

---

## 4. Metric updates

Numbers are where a deck goes stale and where it goes wrong, and re-running a deck with new
data is the most common edit. These rules make that edit safe.

### 4.1 Every number carries four things

A number is not shippable until all four are attached, either on the slide or in its notes:

| | |
|---|---|
| **Value** | the number, with its unit |
| **As-of date** | the date the data was pulled — `as of 2026-07-24`, never "recently" |
| **Basis** | gross/net, currency, cohort, included segments — whatever could be read two ways |
| **Comparison** | what it's being compared to, named explicitly (vs. prior month / same month last year / plan) |

A number with no comparison is decoration. A number with an ambiguous comparison is worse
than no number.

### 4.2 One source of truth per number

**A given number appears in exactly one place in the deck as its authoritative value.**
Everywhere else references it. If the same figure is typed into a headline, a chart label,
and a notes field, an update will miss one — and it always misses the one on screen during
the meeting.

When building a deck programmatically, hold every figure in one data block at the top of the
build script and render from it. Never inline a literal into slide text. When editing an
existing deck by hand, grep the whole deck — **including notes and appendix** — for the old
value before declaring the update done.

### 4.3 Updating numbers in an existing deck

Run this order, every time:

1. **Update the source data first**, then re-render. Never patch a rendered slide and
   backfill the data later.
2. **Re-check the direction words.** "Up," "grew," "improved," "ahead of plan" are claims
   about the *delta*, not the value. A refresh that flips the sign turns every one of them
   into a false statement — including in the title claim and the notes.
3. **Re-check the title claim.** New numbers can invalidate the claim entirely. If they do,
   the slide gets a new title, not just a new chart.
4. **Re-check axis bounds and scale.** A y-axis that was auto-fit to old data will mislead on
   new data. Bar charts start at zero, always — a truncated bar axis is a defect, not a
   zoom.
5. **Bump every as-of date you touched**, and only those.
6. **Diff the old and new number set** and state the deltas in the change summary. "Updated
   metrics" is not a description of what changed.

### 4.4 Never invent a number

If a figure isn't available, the placeholder is a literal **`TK`** with what's needed:
`TK — enterprise ARR, need Q3 close from finance`. Never a plausible-looking estimate, never
a round guess, never a number carried forward from a prior version without re-checking its
as-of date. **A deck that ships with a TK is recoverable. A deck that ships with an invented
number is not.**

Rounding is consistent deck-wide: pick a precision per metric type and hold it. Percentages
to one decimal or zero — not one slide each way. Never show more precision than the source
supports.

---

## 5. The rubric

Score every row 0–3. This is the canonical bar — the thing a review loop iterates against.

| # | Row | 0 | 1 | 2 | 3 |
|---|---|---|---|---|---|
| 1 | **Claim titles** | Labels throughout | Some claims | Claims, some weak | Every content slide's title is a specific, falsifiable claim |
| 2 | **One idea per slide** | Wall of text | Crowded, sub-18 pt | Mostly clean | ≤ 5 bullets, ≥ 18 pt, one idea, nothing in the margin |
| 3 | **Color assignment** | Invented/decorative colors | Palette used, wrong jobs | Right jobs, minor slips | Every color from §2, doing its stated job, fixed slot order |
| 4 | **Color accessibility** | Color-alone encoding | Legend only | Legend + most labels | No color-alone encoding anywhere; sub-3:1 fills all labeled; grayscale-legible |
| 5 | **Chart integrity** | Dual axis / truncated bars / 3-D | One integrity defect | Clean but generic form | Form matches the data's job, zero-baseline bars, one axis, recessive chrome |
| 6 | **Notes present** | Missing on some slides | All present, thin | Most meaty | Every content slide 80–200 words |
| 7 | **Notes substance** | Restates the slide | Claim only | Claim + source | All four template fields, real objection with a real answer |
| 8 | **Number provenance** | Unsourced numbers | Some sourced | Sourced, basis unclear | Every number has value + as-of + basis + comparison |
| 9 | **Update safety** | Numbers inlined, duplicated | Single source, no check | Single source, checked | One source of truth per figure; direction words and claims re-verified |
| 10 | **No fabrication** | Invented numbers present | Estimates unmarked | Estimates marked | Zero invented figures; gaps are explicit `TK` |

**The gate: rows 4, 5, 8, and 10 must be 3. No other row below 2. Total ≥ 26/30.**

Rows 4, 5, 8, and 10 are absolute because they are the ones that mislead an audience rather
than merely underwhelm it. A deck that is beautiful and wrong is worse than one that is plain
and right.

### The loop

1. Build or edit the deck.
2. Score all ten rows. Write the scores down — a score you didn't write down wasn't taken.
3. Find the lowest row. Fix **that** one. Not the easiest one.
4. Re-score. Repeat until the gate is met.
5. State the final scores when handing the deck over, including anything that fell short and
   why.

Do not self-report a 3 without the evidence the row asks for. Row 4 means the validator was
run and the labels are on the marks; row 8 means the dates are actually in the file. "Looks
good" is a 1.

---

## 6. Reject list

If the deck does any of these, it fails regardless of score:

- Dual-axis chart (two y-scales)
- Bar chart not starting at zero
- Pie chart with more than four slices, or any donut with a number in the hole that isn't the total
- 3-D chart, drop shadow, gradient fill, or beveled anything
- Text below 18 pt in a body position
- More than one typeface, or a serif/display face
- A color chosen because it "looked nice"
- Color as the only carrier of meaning
- A number without an as-of date
- An invented, estimated, or carried-forward-unchecked figure
- A content slide with no speaker notes
- Speaker notes that restate the bullets
- "Q3 Revenue"-style label titles
- Rainbow sequential scale, or a hue at a diverging midpoint
- A ninth categorical color
- More than three series in a scatter, bubble, map, or small-multiples chart
- Lorem ipsum, `[TBD]`, or a placeholder that isn't a labeled `TK`
