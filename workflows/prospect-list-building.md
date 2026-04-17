# Prospect List Building — Perth Ecommerce

## Objective
Build and maintain a master list of Perth-based ecommerce businesses that fit Distl's target profile, stored on the Monday.com Ecommerce Prospecting board.

## Target profile
- **Location:** Perth, Western Australia
- **Business type:** B2C ecommerce, physical products preferred
- **Team size:** 5–50 employees total
- **Marketing team:** 1–3 people (big enough to have budget, small enough to need agency support)
- **Not:** Enterprise companies with full in-house digital teams

## Prerequisites
- Read `workflows/prospecting-crm-setup.md` for board ID, column IDs, and group IDs
- Board ID: `18405791744`

## Step 1: WebSearch for directories and lists

Run these searches to find Perth ecommerce companies. Adjust keywords as needed.

**Directory searches:**
```
Perth ecommerce companies directory
Perth online stores Western Australia
"Perth" "online store" site:shopify.com
Perth ecommerce businesses list 2026
Western Australia ecommerce brands
Perth retail online shopping
```

**Industry-specific searches:**
```
Perth fashion ecommerce brands
Perth health supplements online store
Perth homewares online shop
Perth activewear brands
Perth food delivery ecommerce Western Australia
Perth beauty products online
Perth sporting goods online store
```

**Shopify/platform detection:**
```
"myshopify.com" Perth
"powered by Shopify" Perth Western Australia
site:*.com.au Perth ecommerce
```

For each search, use WebFetch on promising directory pages to extract company names and domains.

## Step 2: LinkedIn search (manual)

LinkedIn requires manual searching by a team member. Claude cannot access LinkedIn directly.

**Search instructions for the team member:**

1. Go to LinkedIn > Companies search
2. Apply these filters:
   - **Location:** Perth, Western Australia, Australia
   - **Company size:** 11–50 employees (closest to our 5–50 range)
   - **Industry:** Retail, Consumer Goods, Apparel & Fashion, Food & Beverages, Health, Wellness & Fitness, Sporting Goods
3. Browse results and identify companies that:
   - Have an ecommerce/online store component (check their website)
   - Have 1–3 employees with marketing-related titles (Marketing Manager, Digital Marketing, Social Media, etc.)
4. For each qualifying company, tell Claude:
   - Company name
   - Website URL
   - LinkedIn URL
   - Approximate team size
   - Number of marketing staff spotted
   - Industry vertical (Fashion, Home, Sport, Food, Beauty, Health, Other)

Claude will then create the item on the Monday.com board.

## Step 3: Record prospects on Monday.com

For each qualifying company found (from WebSearch or LinkedIn), create an item on the board.

**Before adding, always dedup check:**
1. Use `board_insights` to search for the company name in the `name` column
2. If the company already exists, skip it (or update if new info is available)

**To add a new prospect, use `create_item`:**
- Board ID: `18405791744`
- Group: defaults to "New Prospects" (`group_mm1vgcvz`)
- Set column values:
  - `link_mm1v14np` (Website): company URL
  - `link_mm1vga4f` (LinkedIn URL): LinkedIn company page
  - `dropdown_mm1vwtx4` (Industry Vertical): best fit category
  - `numeric_mm1v5s2` (Est. Team Size): estimated employee count
  - `numeric_mm1v4cs0` (Marketing Team Size): estimated marketing headcount
  - `date_mm1vzg53` (Date Added): today's date
  - `color_mm1vdstv` (Source): how the company was found (WebSearch, LinkedIn, Directory, Referral)
  - `color_mm1v81t6` (Signal Type): set to "None" initially

## Step 4: Validate prospects

After a batch of prospects has been added, present a summary to the user:
- Company name, website, industry, team size
- Ask the user to confirm each prospect fits the target profile
- Move any that don't fit to the "Not a Fit" group (`group_mm1vn0ay`)

## Ongoing maintenance

- **Frequency:** Run prospect discovery monthly, or when the pipeline needs refilling
- **Goal:** Maintain 50–100 active prospects in "New Prospects" at any time
- **Sources to revisit:** Re-run WebSearch queries periodically as new businesses launch
- **Team contributions:** Any team member can add prospects via Claude by providing company details

## Edge cases

- **Company has multiple brands:** Add each brand as a separate prospect if they have different websites
- **Company is already a Distl client:** Do not add. If discovered, move to "Not a Fit" with a note.
- **Company is too large (50+ employees):** Skip unless marketing team is clearly small (1–2 people)
- **Company doesn't clearly sell online:** Skip. We want confirmed ecommerce businesses.
