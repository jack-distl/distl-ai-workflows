# Deep Creative Audit — Prospect Pitch Builder

## Objective
Run an intensive research and creative audit on a hand-picked prospect to produce specific, insight-led ad creative concepts and strategic recommendations that demonstrate Distl's thinking. This is a different workflow from signal prospecting — it's designed to win a specific prospect, not filter a list.

## When to use
- A prospect is interesting but didn't trigger strong signals in the standard workflow
- A prospect triggered a signal and you want to go deeper before outreach
- You want to pitch a specific company with creative ideas, not just data
- **Trigger:** User says "Run a deep creative audit on [company]" or "Pitch [company]"

## Prerequisites
- Read `workflows/prospecting-crm-setup.md` for board ID and column IDs
- Board ID: `18405791744`
- Prospect should already exist on the Monday.com board (add them first if not)
- Ahrefs MCP connector must be active (~900 units per audit)

## Ahrefs budget
- Each deep audit costs approximately 900 Ahrefs units
- Check current usage via `subscription-info-limits-and-usage` (free, no units consumed)
- At 150K units/month, you can run ~160 deep audits before hitting the limit
- Always report units remaining after the audit

---

## Step 1: Company research (free — WebSearch + WebFetch)

**Goal:** Understand who this company is, what makes them unique, and what story they're telling.

### 1a. Basic company info
WebSearch for:
```
"[company name]" [city] [industry]
"[domain]" about OR story OR founded
```

### 1b. Brand story and USP
WebFetch their About/Our Story page to extract:
- Founding story and founder backgrounds
- Mission statement and brand values
- Key claims and differentiators
- Certifications, awards, partnerships
- Celebrity/influencer affiliations or ownership
- Sustainability or social impact commitments

### 1c. Product positioning
WebFetch their homepage and key collection pages to extract:
- Price positioning (budget, mid, premium, luxury)
- Product range breadth
- Key selling points per product line
- How they describe their products (functional vs emotional language)
- Trust markers (reviews, certifications, guarantees)

### 1d. Social media presence
WebSearch for:
```
"[company name]" instagram OR tiktok OR facebook followers
"[company name]" social media
```
Note: follower counts, posting frequency (if visible), content style, engagement levels.

### 1e. Press and media coverage
WebSearch for:
```
"[company name]" interview OR feature OR article OR award
"[company name]" [founder name] interview
```
Look for: brand stories, PR angles, media hooks, recent news.

**Output from Step 1:** A company profile document with USP summary, brand story, product positioning, social presence, and notable press.

---

## Step 2: Competitor landscape (Ahrefs — ~300 units)

**Goal:** Understand who this company competes with and how they compare.

### 2a. Find organic competitors
Use `site-explorer-organic-competitors`:
```
target: [domain]
mode: subdomains
country: au
date: [today]
select: competitor_domain, keywords_common, keywords_competitor, traffic
limit: 10
```

### 2b. Benchmark competitors
Use `batch-analysis` on the prospect + top 3-4 relevant competitors:
```
select: ["paid_traffic", "paid_cost", "org_traffic", "domain_rating", "paid_keywords", "org_keywords"]
targets: [prospect + top competitors]
country: au
```

### 2c. Competitor website analysis (free)
WebFetch the homepages of the top 2-3 competitors to extract:
- How they position themselves
- What messaging they lead with
- What the prospect does differently (or could do differently)
- Visual/creative approach differences

**Output from Step 2:** Competitive landscape table + key differentiation gaps.

---

## Step 3: Ad creative intelligence (free — WebSearch + WebFetch)

**Goal:** Understand what ads the prospect and competitors are running, and identify creative gaps.

### 3a. Prospect's Meta ads
WebSearch for:
```
Meta Ad Library "[company name]" [country] ads
facebook.com/ads/library [company name]
```

Attempt WebFetch on Meta Ad Library URL:
```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=AU&q=[company name]&search_type=keyword_unordered
```
Note: This may be blocked by Meta. If so, rely on WebSearch results and any screenshots/descriptions found.

### 3b. Competitor ads
Repeat 3a for top 2-3 competitors.

### 3c. Industry ad trends
WebSearch for:
```
[industry] ecommerce ads creative strategy 2025 2026
[industry] brand social media advertising australia
[product category] tiktok viral content marketing
```

### 3d. Identify creative gaps
Analyse what's missing:
- What angles are competitors NOT using?
- What's the prospect's biggest untold story?
- Are there content formats nobody in the space is using (UGC, behind-the-scenes, comparison content, educational)?
- Is there a cultural moment or trend the prospect could own?

**Output from Step 3:** Ad landscape summary + creative gap analysis.

---

## Step 4: SEO and content opportunities (Ahrefs — ~600 units)

**Goal:** Find specific, actionable SEO opportunities the prospect is missing.

### 4a. Current organic performance
Use `site-explorer-organic-keywords`:
```
target: [domain]
mode: subdomains
date: [today]
country: au
select: keyword, best_position, volume, sum_traffic
order_by: sum_traffic:desc
limit: 30
```

### 4b. Current paid keywords
Use `site-explorer-paid-pages`:
```
target: [domain]
mode: subdomains
date: [today]
country: au
select: top_keyword, top_keyword_volume, sum_traffic, value, keywords, url
limit: 20
```

### 4c. Content gap analysis (manual — no extra Ahrefs cost)
From the organic keywords data, identify:
- **Informational vs commercial split:** Are they getting traffic from "how to" queries but not "buy" queries?
- **Brand vs non-brand:** What % of their organic traffic is people searching their brand name vs discovering them through product/category searches?
- **Low-hanging fruit:** Keywords ranking 5-15 where a content refresh could push them to page 1
- **Missing categories:** Product types or use cases they sell but don't rank for
- **Competitor keywords they're missing:** Cross-reference with competitor data from Step 2

### 4d. Quick-win SEO recommendations
Based on the analysis, identify 3-5 specific SEO actions:
- Collection/category pages that need optimisation
- Blog content topics with clear search demand
- Internal linking improvements
- Product page title/meta description opportunities

**Output from Step 4:** SEO opportunity document with specific keywords, volumes, and recommended actions.

---

## Step 5: Creative pitch generation (free — Claude synthesis)

**Goal:** Combine all research into 3-4 specific, pitched creative concepts.

### Framework for each concept

Each pitch should include:

1. **The insight** — What did we discover that the prospect likely doesn't know or hasn't acted on?
2. **The creative concept** — A specific campaign idea with a name, format, and hook
3. **Why competitors can't copy it** — What makes this unique to the prospect?
4. **What Distl would deliver** — Tangible outputs (video concepts, ad campaign structure, content calendar, landing page wireframe, etc.)
5. **Expected impact** — What metric this would move (traffic, conversion, brand awareness, ad spend efficiency)

### Pitch categories to consider

Not all will apply to every prospect. Pick the 3-4 most compelling:

- **USP-led ad creative:** Ads that communicate their unique positioning in a way competitors can't replicate
- **Challenger content play:** Side-by-side comparison content that positions their product as the better alternative
- **Celebrity/founder story:** If they have notable people involved, content that leverages their personal brand
- **Provenance/origin story:** Supply chain, sourcing, craft process content for premium brands
- **UGC/creator-led campaigns:** Authentic, user-generated style ads that outperform polished brand content
- **SEO content strategy:** Blog/landing page content plan targeting high-value keywords they're missing
- **Google Ads restructure:** More efficient campaign structure based on the paid/organic gap analysis
- **Social platform expansion:** If they're on Instagram but not TikTok (or vice versa), the case for expansion
- **Email/retention play:** If their focus is all acquisition, the case for lifecycle marketing
- **Seasonal/event campaigns:** Specific campaign concepts tied to upcoming events or seasons relevant to their industry

### Tone of the pitch
- Specific, not generic. Every recommendation references real data or observations.
- Confident but not arrogant. "Here's what we noticed and what we'd do" not "You're doing it wrong."
- Show creative thinking. The prospect should think "they actually understand our brand" not "this is a template."

**Output from Step 5:** 3-4 fully developed creative pitch concepts, each 200-400 words.

---

## Step 6: Update Monday.com and report

### Update the prospect item
Use `change_item_column_values`:
- `long_text_mm1vtebn` (Signal Detail): Brief summary of audit findings
- `date_mm1vpbs9` (Last Checked): today's date
- `long_text_mm1vxnza` (Notes): "Deep creative audit completed [date]. Key angles: [1-line summary of each pitch concept]."

### Present to user
Structure the report as:

```
## Deep Creative Audit: [Company Name]

### Company Profile
[1 paragraph summary: who they are, USP, market position]

### Competitive Landscape
[Table: prospect vs top 3 competitors — DR, organic traffic, paid spend, paid keywords]
[Key insight about competitive positioning]

### Ad Creative Analysis
[What they're running now (if anything)]
[What competitors are running]
[Key gaps and opportunities]

### SEO Opportunities
[Top 3-5 specific keyword/content opportunities with volumes]

### Creative Pitch Concepts

#### 1. [Concept Name]
[Full pitch per the framework above]

#### 2. [Concept Name]
[Full pitch]

#### 3. [Concept Name]
[Full pitch]

#### 4. [Concept Name] (if applicable)
[Full pitch]

### Recommended Next Steps
[What Distl would do first if the prospect engaged]
```

---

## Cost summary per audit

| Step | Tool | Estimated cost |
|---|---|---|
| 1. Company research | WebSearch + WebFetch | Free |
| 2a. Organic competitors | Ahrefs site-explorer-organic-competitors | ~130 units |
| 2b. Competitor benchmark | Ahrefs batch-analysis (5 domains) | ~170 units |
| 3. Ad creative intel | WebSearch + WebFetch | Free |
| 4a. Organic keywords | Ahrefs site-explorer-organic-keywords | ~550 units |
| 4b. Paid keywords | Ahrefs site-explorer-paid-pages | ~165 units |
| 5. Pitch generation | Claude (no tool cost) | Free |
| 6. Monday.com update | Monday MCP | Free |
| **Total** | | **~1,015 units** |

At 150,000 units/month: **~148 deep audits per month** before hitting the limit.

---

## Edge cases

- **Company has no paid ads at all:** Skip Step 4b. Focus pitches on organic SEO and social/Meta ads.
- **Company is too small for Ahrefs data:** Ahrefs may return empty results for very small sites. Lean on WebSearch, WebFetch, and creative analysis instead.
- **Company is already a Distl client:** Do not audit. Flag in Notes and move to "Not a Fit."
- **Meta Ad Library fetch is blocked:** Rely on WebSearch descriptions. Note in the report that direct ad library access was unavailable.
- **Competitor data is thin:** If the industry is niche and competitors have little digital presence, frame this as a blue-ocean opportunity — the prospect can dominate the space.
