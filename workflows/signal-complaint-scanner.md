# Signal: Public Complaint Scanner

## Objective
Search public forums, review sites, and social platforms for customer complaints about prospects' brands. These are real customers flagging conversion problems the brand may not be monitoring — a strong, specific outreach angle.

## Prerequisites
- Read `workflows/prospecting-crm-setup.md` for board ID and column IDs
- Board ID: `18405791744`

## When to run
- **Frequency:** Fortnightly
- **Trigger:** User says "Run signal checks" or "Run complaint scan"

## Step 1: Get prospect list from Monday.com

Use `get_board_items_page` on board `18405791744` to retrieve prospects from:
- "New Prospects" group (`group_mm1vgcvz`)
- Optionally "Signal Detected" group (`group_mm1vmffs`) to look for additional signals

For each prospect, extract:
- Company name (the `name` column)
- Website domain (`link_mm1v14np`) — strip to brand name for search
- Current Signal Type — skip if already "Complaint"

**Derive the brand name:** Take the company name and also extract the domain name without TLD (e.g., "examplestore.com.au" → "examplestore"). Search both.

## Step 2: Search for complaints

For each prospect brand, run WebSearch queries:

**Reddit:**
```
"[brand name]" (complaint OR "doesn't work" OR slow OR confusing OR "bad experience" OR "terrible" OR "worst") site:reddit.com
```

**Trustpilot:**
```
"[brand name]" site:trustpilot.com
```

**ProductReview (Australian review site):**
```
"[brand name]" site:productreview.com.au
```

**Google Reviews / general:**
```
"[brand name]" review (complaint OR "poor service" OR "slow delivery" OR "can't find" OR "website broken" OR "checkout" OR "won't load")
```

## Step 3: Analyse results

For each search that returns results:

1. Use WebFetch on the top 3–5 relevant results to extract:
   - The specific complaint text
   - The date of the complaint
   - The platform (Reddit, Trustpilot, ProductReview, Google)
   - The complaint category (see categories below)

2. **Complaint categories:**
   - **Website/UX issues:** slow loading, confusing navigation, broken checkout, mobile issues
   - **Search/findability:** can't find products, poor search, bad filtering
   - **Delivery/shipping:** slow delivery, tracking issues, missing orders
   - **Customer service:** unresponsive, slow replies, unhelpful
   - **Product quality:** not as described, quality issues, returns problems
   - **Payment issues:** checkout errors, payment failures, refund problems

3. **Focus on complaints Distl can help with:**
   - Website/UX issues → web design/development
   - Search/findability → SEO, site search, UX
   - Customer service (if digital) → automation, chatbots, CRM
   - Skip delivery/shipping and product quality — these aren't digital marketing problems

## Step 4: Evaluate and flag

**Flag the prospect if:**
- 2+ complaints of the same category (within the last 12 months)
- OR 1 very detailed, specific complaint about a website/UX issue that clearly indicates a fixable problem

**Build the signal summary:**
```
Found [X] public complaints about [brand name]:
- [Category]: [X] complaints. Example: "[quote or paraphrase]" ([platform], [date])
- [Category]: [X] complaints. Example: "[quote or paraphrase]" ([platform], [date])
Most common theme: [category]. This suggests [interpretation — e.g., "website performance issues may be hurting conversions"].
```

## Step 5: Dedup check

Before flagging, query Monday.com via `board_insights`:

1. Has this prospect been contacted before with the Complaint signal?
   - Filter by `color_mm1v81t6` (Signal Type) — if already "Complaint", skip
2. Is the prospect in "Responded" or "Not a Fit"?
   - If yes, don't move them back
3. Was a different signal used previously?
   - If yes, this is a new signal — flag it, but note the prior signal in Notes

## Step 6: Update Monday.com

If the prospect passes the dedup check:

1. Update the prospect item via `change_item_column_values`:
   - `color_mm1v81t6` (Signal Type): `{"label": "Complaint"}`
   - `long_text_mm1vtebn` (Signal Detail): signal summary from Step 4
   - `date_mm1vft14` (Signal Date): today's date
   - `date_mm1vpbs9` (Last Checked): today's date

2. Move the item to "Signal Detected" group (`group_mm1vmffs`) via `move_object`

If not flagged, still update:
   - `date_mm1vpbs9` (Last Checked): today's date

## Step 7: Report to user

After processing all prospects, present:
- Total prospects scanned
- Number flagged with Complaint signal
- Top findings (company name + complaint theme + example complaint)
- Any prospects skipped due to dedup

## Rate limiting and efficiency

- WebSearch queries are rate-limited. For large prospect lists (20+ companies), batch in groups of 10 and pause between batches if needed.
- WebFetch calls should be limited to the most relevant results (top 3–5 per query)
- Skip prospects where the brand name is too generic (e.g., "The Store") — these will return noisy results. Note the skip reason.

## Edge cases

- **Brand name is very common:** Add the city ("Perth") or domain to the search to reduce noise
- **Complaints are very old (2+ years):** Discount these — the issue may be resolved. Only flag if recent complaints exist (last 12 months)
- **Complaints are about a different company with the same name:** Verify by checking if the complaint references the same products/services as the prospect
- **Positive reviews heavily outweigh complaints:** Note this in the signal detail — outreach should acknowledge the brand is generally well-regarded

## Outreach angle (for reference)

When this signal is detected, the outreach angle is:
> "We came across some customer feedback about [brand name] that flagged [specific issue — e.g., 'website speed' or 'difficulty finding products']. We've helped similar ecommerce brands fix these kinds of issues — [specific example of a fix, e.g., 'reducing page load time by 40%' or 'redesigning product filtering']. Happy to share what we've seen work if it's useful."
