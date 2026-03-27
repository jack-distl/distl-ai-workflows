# Signal: Paid vs Organic Gap

## Objective
Identify prospects who are spending on Google Ads for product keywords but have no meaningful organic ranking for those same keywords. This signals over-reliance on paid spend that SEO could reduce — a strong outreach angle.

## Prerequisites
- Read `workflows/prospecting-crm-setup.md` for board ID and column IDs
- Board ID: `18405791744`
- Ahrefs MCP connector must be active
- **Note:** Ahrefs API calls consume credits. Check with user before running large batches.

## When to run
- **Frequency:** As part of fortnightly signal checks
- **Trigger:** User says "Run signal checks" or "Run paid vs organic gap check"

## Step 1: Get prospect list from Monday.com

Use `get_board_items_page` on board `18405791744` to retrieve prospects.

**Filter to relevant prospects:**
- Group: "New Prospects" (`group_mm1vgcvz`) — prospects that haven't been signalled yet
- Optionally include "Signal Detected" (`group_mm1vmffs`) to check for new signals on already-flagged prospects
- Skip prospects where Signal Type is already "Paid/Organic Gap"

Extract the Website URL (`link_mm1v14np`) for each prospect.

## Step 2: Run Ahrefs paid keyword check

For each prospect domain, use `site-explorer-paid-pages`:

```
target: [domain]
mode: subdomains
date: [today's date, YYYY-MM-DD]
country: au
select: keyword,position,traffic,volume
limit: 50
```

This returns the keywords the domain is bidding on via Google Ads.

**If no paid keywords are found:** Skip this prospect — no paid/organic gap exists. Update `date_mm1vpbs9` (Last Checked) and move on.

## Step 3: Run Ahrefs organic keyword check

For the same domain, use `site-explorer-organic-keywords`:

```
target: [domain]
mode: subdomains
date: [today's date, YYYY-MM-DD]
country: au
select: keyword,position,traffic,volume
limit: 200
```

This returns the keywords the domain ranks for organically.

## Step 4: Compare paid vs organic

Use `tools/compare_paid_organic.py` logic (or apply inline):

1. Extract the list of paid keywords from Step 2
2. For each paid keyword, check if it appears in the organic results from Step 3
3. A keyword is a **gap** if:
   - It's in the paid results but NOT in organic results at all, OR
   - It's in organic results but at position > 50 (effectively invisible)
4. Calculate:
   - Total paid keywords found
   - Number of gap keywords (paid but not ranking organically)
   - Gap percentage (gaps / total paid keywords)
   - Estimated monthly paid spend on gap keywords (sum of traffic values for gap keywords)

## Step 5: Evaluate and flag

**Flag the prospect if:**
- 3+ gap keywords exist, OR
- Gap percentage > 50%, OR
- Estimated monthly spend on gap keywords > $500 AUD equivalent

**Build the signal summary:**
```
Bidding on [X] keywords with no organic ranking.
Top gaps: '[keyword 1]' (vol: [X], pos: none), '[keyword 2]' (vol: [X], pos: none), '[keyword 3]' (vol: [X], pos: none).
Estimated paid spend on gap keywords: ~$[X]/month.
Gap percentage: [X]% of paid keywords have no organic presence.
```

## Step 6: Dedup check

Before flagging, query Monday.com via `board_insights`:

1. Has this prospect been contacted before?
   - Filter by `name` and check `color_mm1vqxr1` (Response Status) and `date_mm1vtc85` (Outreach Date)
2. Was "Paid/Organic Gap" the previous signal?
   - If yes, don't flag again
3. Is the prospect in "Responded" or "Not a Fit"?
   - If yes, don't move them back

## Step 7: Update Monday.com

If the prospect passes the dedup check:

1. Update the prospect item via `change_item_column_values`:
   - `color_mm1v81t6` (Signal Type): `{"label": "Paid/Organic Gap"}`
   - `long_text_mm1vtebn` (Signal Detail): signal summary from Step 5
   - `date_mm1vft14` (Signal Date): today's date
   - `date_mm1vpbs9` (Last Checked): today's date

2. Move the item to "Signal Detected" group (`group_mm1vmffs`) via `move_object`

If not flagged, still update:
   - `date_mm1vpbs9` (Last Checked): today's date

## Step 8: Report to user

After processing all prospects, present a summary:
- Total prospects checked
- Number flagged with Paid/Organic Gap signal
- Top findings (company name + key gap keywords)
- Any prospects skipped due to dedup

## Ahrefs credit management

- Each domain check uses ~2 API calls (paid pages + organic keywords)
- Before running on the full prospect list, tell the user how many domains will be checked and confirm they want to proceed
- For large lists (20+ domains), consider using `batch-analysis` first to pre-filter domains that have paid traffic

## Outreach angle (for reference)

When this signal is detected, the outreach angle is:
> "We noticed you're running Google Ads for [keyword examples] but not ranking organically for these terms. There's an opportunity to reduce your dependence on paid spend with targeted SEO — we've helped similar businesses cut their ad costs while maintaining the same traffic."
