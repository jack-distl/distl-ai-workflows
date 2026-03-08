# Ecommerce Prospect Research

## Objective

Identify and profile mid-market ecommerce brands headquartered in Perth/Western Australia as prospective agency clients for Distl. Output a structured XLSX report with qualified prospects, uploaded to Google Drive.

## Target Profile

The ideal prospect is a mid-market ecommerce brand with these characteristics:

- **Location:** Headquartered in Perth or Western Australia (warehouse, head office, or founders based in WA)
- **Business model:** Sells physical products online via their own website (Shopify, WooCommerce, Magento, or custom), shipping nationally or internationally
- **Revenue:** Estimated $2M–$50M annual revenue, or indicators like 10+ employees, multiple retail locations, active paid media presence
- **Agency spend:** Likely $100k–$200k/year across SEO, Google Ads, Meta Ads, creative, and web
- **Catalogue:** Meaningful product range — not a single-product or pure service business

**Reference examples:** iTechworld (solar/camping tech), Adultshop (adult retail), Adore Home Living (homewares), Avocado Zinc (sunscreen DTC), Orbit Fitness (gym equipment), Funky Monkey Bars (outdoor play equipment), Supplement Mart (sports nutrition), Retravision (consumer electronics), We Are Feel Good Inc (sunscreen DTC), SkinKandy (piercing/jewellery retail + ecomm).

## Required Inputs

- **Target verticals** — defaults to the standard list below, but can be customised by the user
- **Geographic scope** — default: Perth / Western Australia
- **Revenue range** — default: $2M–$50M
- **Output filename** — default: `prospect_research_YYYY-MM-DD.xlsx`

### Default Verticals

1. Fitness equipment
2. Outdoor / camping / 4WD
3. Pet supplies
4. Health supplements
5. Skincare / beauty
6. Homewares / furniture
7. Fashion / apparel
8. Food / beverage DTC
9. Pool / garden
10. Electronics / consumer tech
11. Kids / baby products
12. Automotive accessories
13. Workwear / safety
14. Sporting goods

## How It Works

This workflow uses web search (agent's WebSearch/WebFetch tools) for discovery and research, `tools/detect_platform.py` for ecommerce platform detection, and `tools/generate_prospect_xlsx.py` for the final XLSX output. The XLSX is uploaded to Google Drive via the `drive_upload_file` MCP tool.

**Tools used:**
- `tools/detect_platform.py` — detects ecommerce platform from website source
- `tools/generate_prospect_xlsx.py` — generates formatted XLSX from JSON prospect data
- `drive_upload_file` MCP tool — uploads XLSX to Google Drive

---

## Stage 1: Category Sweep

**Goal:** Cast a wide net across all target verticals to build an initial prospect list.

### For each vertical, run web searches using variations like:

- `"{vertical}" online store Perth WA`
- `"{vertical}" ecommerce brand Western Australia`
- `"{vertical}" Shopify store Perth`
- `"buy {product type} online" Perth WA`
- `best {vertical} brands Perth Western Australia`

### For each result, capture:
- Brand name
- Website URL
- Category/vertical

### Search tips:
- Try 2–3 search variations per vertical to maximise coverage
- Look past the first page of results — smaller brands often rank lower
- Check "People also ask" and related searches for adjacent brands
- Note brands that appear across multiple verticals

### After all verticals are searched:
- Deduplicate by domain name
- Note which verticals returned few or no results

---

## Stage 2: Agency Reverse-Engineering

**Goal:** Find ecommerce brands by checking Perth agency portfolios and case studies.

### Perth Shopify / ecommerce agencies to check:
- The Cut (thecut.net.au)
- 76Creative
- Flux
- Lethal Digital
- PWD (pwd.com.au)

### Perth digital marketing agencies to check:
- Bonfire
- Living Online
- Dilate Digital
- Bloom Digital
- Clue Design

### For each agency:
1. Search for `"{agency name}" portfolio clients ecommerce Perth`
2. If possible, visit the agency's portfolio or case studies page via WebFetch
3. Extract any ecommerce brand names mentioned
4. Cross-reference with Stage 1 results and add new brands
5. **Record which agency is associated with each brand** — this is critical for conflict detection later

---

## Stage 3: Directory & Platform Search

**Goal:** Supplement the list using platform directories and business databases.

### Searches to run:
- `site:builtwith.com Shopify Perth Western Australia`
- `site:storeleads.app Perth Australia Shopify`
- `WA ecommerce business awards`
- `Western Australian ecommerce companies`
- `"Perth" ecommerce company LinkedIn`
- `Telstra Business Awards WA ecommerce`
- `WA Young Achiever Awards ecommerce`

### Add any new brands found, noting the source.

---

## INTERACTIVE PAUSE

**Stop here and present findings to the user before proceeding.**

Present a summary including:
1. **Total prospects found** (count)
2. **Prospects by vertical** — table showing category and count
3. **Full list** — brand name, URL, category for each prospect
4. **Empty verticals** — which verticals returned no results
5. **Agency-sourced prospects** — which brands were found via agency portfolios (flag for conflicts)

Ask the user:
> "I've found {N} potential prospects across {X} verticals. Before I deep-dive into profiling each one, would you like to:
> 1. Add any specific brands or verticals to research?
> 2. Remove any brands that aren't relevant (e.g. already a Distl client)?
> 3. Adjust the target criteria?
> 4. Proceed with the full list?"

**Wait for user response before continuing to Stage 4.**

---

## Stage 4: Deep Profile Research

**Goal:** Build a complete profile for each confirmed prospect.

### For each prospect, research the following:

#### 4a. HQ Location Verification
- Search for the brand's About page, Contact page, or footer
- Look for physical address, ABN lookup, or "proudly based in Perth/WA" language
- If location cannot be confirmed to WA, downgrade confidence or exclude

#### 4b. Business Summary
- Write 1–2 sentences describing what they sell and their market position
- Source from their website About page and web search results

#### 4c. Ecommerce Platform Detection
Run the detection tool:
```bash
python tools/detect_platform.py --url {website_url}
```
Record the platform and confidence from the JSON output.

#### 4d. Size Indicators
Search for:
- LinkedIn company page → employee count
- Social media accounts → follower counts (Instagram, Facebook)
- Number of retail/showroom locations
- Any press mentions of revenue, funding, or growth milestones
- Job ads (indicate growth/scale)

#### 4e. Key Contacts
Search LinkedIn for:
- Founder / CEO / Managing Director
- Marketing Manager / Head of Digital / Ecommerce Manager

For each contact found, record:
- Full name
- Role/title
- LinkedIn profile URL

**Do NOT record:**
- Personal email addresses
- Phone numbers
- Contacts that can't be verified on LinkedIn or the company website

If no contacts can be found, leave the fields blank.

#### 4f. Current Digital Agency
Check:
- Website footer for agency credits (e.g. "Site by Agency Name")
- Search for `"{brand name}" digital agency` or `"{brand name}" marketing agency Perth`
- Check if the brand appears in any agency portfolio (from Stage 2 data)

#### 4g. Channel Opportunity Notes
Based on the prospect's product type and current online presence, note which Distl services would be most relevant:
- **SEO** — if they have a large catalogue, competitive category, or poor organic visibility
- **Google Ads / Shopping** — if they sell products people actively search for
- **Meta Ads** — if their products are visually appealing, impulse-buy, or DTC
- **Web / Shopify** — if their site is outdated, slow, or on a legacy platform
- **Content** — if they have a blog or content marketing opportunity

---

## Stage 5: Scoring & Classification

**Goal:** Assign a confidence tier and flag any conflicts.

### Confidence Tiers:

| Tier | Criteria |
|------|----------|
| **High** | Confirmed WA HQ + confirmed ecommerce + revenue/size indicators suggest $2M–$50M range |
| **Medium** | Likely WA-based + has ecommerce presence, but revenue or agency spend not confirmed |
| **Low** | Possible fit but needs manual validation (e.g. location uncertain, revenue unclear, minimal online presence) |

### Conflict Flagging:

Flag any prospect where:
- They were found in an agency portfolio from Stage 2
- Their current agency is known to have a close relationship with Distl
- They are a known existing Distl client

Add the agency name and flag in the "Current Digital Agency" field.

---

## Stage 6: Generate XLSX & Upload

**Goal:** Produce the final deliverable and upload to Google Drive.

### Step 1: Prepare the JSON data

Create a JSON file at `.tmp/prospects.json` with this structure:

```json
{
  "prospects": [
    {
      "brand_name": "Example Brand",
      "website_url": "https://example.com.au",
      "category": "Fitness Equipment",
      "hq_location": "Osborne Park, WA",
      "business_summary": "Online retailer of commercial and home gym equipment...",
      "ecommerce_platform": "Shopify",
      "size_indicators": "~25 employees on LinkedIn, 15k Instagram followers, 2 showrooms",
      "key_contact_1_name_role": "Jane Smith — Founder & CEO",
      "key_contact_1_linkedin": "https://linkedin.com/in/janesmith",
      "key_contact_2_name_role": "John Doe — Head of Digital",
      "key_contact_2_linkedin": "https://linkedin.com/in/johndoe",
      "current_agency": "Unknown",
      "channel_opportunity_notes": "Strong SEO opportunity (large catalogue), Google Shopping, Meta Ads for visual products",
      "confidence_tier": "High"
    }
  ],
  "searched_verticals": ["Fitness Equipment", "Outdoor/Camping", "..."],
  "empty_verticals": ["Pool/Garden"]
}
```

### Step 2: Generate the XLSX

```bash
python tools/generate_prospect_xlsx.py --input .tmp/prospects.json --output .tmp/prospect_research_YYYY-MM-DD.xlsx
```

### Step 3: Upload to Google Drive

Use the `drive_upload_file` MCP tool:
- `folder_name`: "Prospect Research"
- `file_name`: the XLSX filename
- `file_base64`: base64-encoded content of the XLSX file
- `mime_type`: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

### Step 4: Present the result

Share the Google Drive link with the user, along with a summary:
- Total prospects by tier
- Top verticals by count
- Any notable findings or patterns

---

## Error Handling

| Error | Action |
|-------|--------|
| Web search returns no results for a vertical | Note the vertical as empty, try alternative search terms, move on |
| `detect_platform.py` fails for a URL | Record platform as "Unknown", note the error, continue with other prospects |
| Website is behind Cloudflare/bot protection | Skip platform detection for that site, note as "Could not detect — bot protection" |
| LinkedIn search returns no contacts | Leave contact fields blank — do not fabricate |
| `generate_prospect_xlsx.py` fails | Check JSON format, fix any invalid fields, retry |
| `drive_upload_file` fails | Save XLSX locally and inform the user of the file path |

## Edge Cases

- **Brand has both WA and interstate presence:** Include if HQ/founders are in WA. Note multi-state presence in business summary.
- **Brand is a franchise:** Only include if the WA franchise entity operates its own ecommerce. National franchise sites (e.g. franchisee of a national chain) should be excluded.
- **Brand is on marketplace only (Amazon, eBay) with no own website:** Exclude — Distl's services focus on owned ecommerce.
- **Brand appears to be a Distl competitor rather than prospect:** Exclude digital agencies and web dev firms.
- **Very large brand (>$50M):** Include but note in size indicators — may still be a good prospect.
- **Very small brand (<$2M):** Include at Low confidence if they show growth signals (new hires, recent funding, expanding product range).

## Important Constraints

1. **Only WA-headquartered brands** — not national chains that happen to have a Perth store
2. **No fabricated contacts** — if a name or role can't be verified, leave blank
3. **No email addresses** — LinkedIn URLs and names only for contacts
4. **No phone numbers** — do not include personal contact numbers
5. **Flag agency conflicts** — note any brands found in agency portfolios
6. **Interactive pause** — always stop after Stage 3 to get user input before deep research
