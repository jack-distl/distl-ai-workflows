# Signal: SEEK Job Posting Monitor

## Objective
Identify Perth ecommerce companies advertising marketing-related roles on SEEK. A job posting signals a staffing gap or growth moment — an opportunity to explore whether agency support could be more efficient than a hire.

## Prerequisites
- Read `workflows/prospecting-crm-setup.md` for board ID and column IDs
- Board ID: `18405791744`

## When to run
- **Frequency:** Fortnightly
- **Trigger:** User says "Run signal checks" or "Run SEEK job check"

## Step 1: Search SEEK via WebSearch

Run these WebSearch queries:

**Primary search:**
```
site:seek.com.au "Perth" (ecommerce OR "e-commerce" OR "online store" OR "online retail") (marketing OR "digital marketing" OR SEO OR "paid media" OR "social media" OR "content marketing")
```

**Broader fallback (if primary returns few results):**
```
site:seek.com.au Perth marketing manager ecommerce 2026
site:seek.com.au Perth digital marketing ecommerce
site:seek.com.au Perth SEO specialist retail
site:seek.com.au Perth "paid media" OR "performance marketing" online retail
```

## Step 2: Parse results

For each search result:

1. Use WebFetch on the SEEK listing URL to extract:
   - **Company name** (the advertiser)
   - **Role title** (e.g., "Digital Marketing Manager")
   - **Location** (confirm Perth/WA)
   - **Key responsibilities** (look for ecommerce-specific duties)
   - **Company description** (look for ecommerce indicators)
   - **Date posted**

2. **Qualify the listing:**
   - Is the company based in Perth? (Skip if not)
   - Does the company have an ecommerce component? (Skip pure services/B2B)
   - Is the role marketing-related? (Skip operations, finance, etc.)

3. **Extract the company's website** from the SEEK listing or a quick WebSearch for the company name

## Step 3: Cross-reference with prospect list

For each qualified company, query Monday.com via `board_insights`:

1. Search for the company name in the `name` column
2. **If found on the board:**
   - Check current Signal Type — if already "SEEK Hiring", skip
   - Check current group — if "Responded" or "Not a Fit", skip
   - Otherwise, update with SEEK signal (Step 5)
3. **If NOT found on the board:**
   - Assess if the company fits the target profile (Perth, ecommerce, 5–50 employees)
   - If yes, add as a new prospect AND flag with SEEK signal
   - If unsure, present to user for validation before adding

## Step 4: Dedup check

Before flagging any prospect:

1. Has this prospect been contacted before with the SEEK signal?
   - Filter by `color_mm1v81t6` (Signal Type) — if already "SEEK Hiring", skip
2. Is the prospect in "Responded" or "Not a Fit"?
   - If yes, don't move them back
3. Was a different signal used previously?
   - If yes, this is a new signal — flag it, but note the prior signal in Notes

## Step 5: Update Monday.com

**For existing prospects:**
Use `change_item_column_values` on the item:
- `color_mm1v81t6` (Signal Type): `{"label": "SEEK Hiring"}`
- `long_text_mm1vtebn` (Signal Detail): summary of the job posting
- `date_mm1vft14` (Signal Date): today's date
- `date_mm1vpbs9` (Last Checked): today's date

Move item to "Signal Detected" group (`group_mm1vmffs`) via `move_object`.

**For new prospects (not yet on the board):**
Use `create_item` with:
- Board ID: `18405791744`
- Name: company name
- Column values including website, source ("WebSearch"), signal type ("SEEK Hiring"), signal detail, dates

**Signal Detail format:**
```
Hiring for [Role Title] in Perth (posted [date]).
Key responsibilities: [brief summary of marketing duties].
This suggests [staffing gap / growth phase / expanding digital capabilities].
```

## Step 6: Report to user

After processing all results, present:
- Total SEEK listings found and screened
- Number of qualified listings (Perth, ecommerce, marketing role)
- Companies already on the board (updated with signal)
- New companies added to the board
- Companies skipped (dedup or not a fit)

## Edge cases

- **Multiple roles from same company:** Only flag once. Combine role details in Signal Detail.
- **Recruitment agency listings:** Skip — the actual company may not be identifiable.
- **Role is senior/executive level:** Still flag — senior marketing hires are even stronger signals of growth or capability gaps.
- **Role is clearly junior (intern, assistant):** Still flag but note the seniority — may indicate early-stage marketing build.

## Outreach angle (for reference)

When this signal is detected, the outreach angle is:
> "We noticed you're hiring for a [Role Title] — congrats on the growth. While you're building your team, an agency can hit the ground running on [specific capability from the job description]. We've helped similar Perth ecommerce brands bridge the gap during hiring, and sometimes the combination of a smaller in-house team plus agency support turns out to be more effective than a single hire."
