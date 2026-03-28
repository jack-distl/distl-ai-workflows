# Hivemind Scan Tool

## What This Does

This is a **reference script** for Claude to follow when running an industry hivemind scan. It's not executable code — it's a structured procedure that Claude follows using MCP connectors and web search.

## Scan Procedure

### Input
- **Scope**: "all" (full scan) or a specific vertical (e.g. "SEO", "Paid Media")
- **Timeframe**: Number of days to look back (default: 14)
- **Depth**: "quick" (top signals only) or "deep" (comprehensive sweep)

### Execution Steps

The scan works through four source channels in priority order. LinkedIn and expert newsletters come first because they contain the freshest, most opinionated takes. Publications and communities fill in data and validation.

#### 1. LinkedIn Expert Scan (Highest Priority)

For each expert on the watchlist for the vertical in scope, run targeted searches:

```
LinkedIn search patterns per vertical:

SEO:
- "Lily Ray" site:linkedin.com/posts (recent)
- "Kevin Indig" site:linkedin.com/posts SEO
- "Aleyda Solis" site:linkedin.com/posts
- "Marie Haynes" site:linkedin.com/posts Google
- "Barry Schwartz" site:linkedin.com/posts algorithm
- "Cyrus Shepard" site:linkedin.com/posts SEO
- Generic: "SEO" OR "algorithm update" OR "AI overviews" site:linkedin.com/posts (last [timeframe] days)

Google Ads:
- "Frederick Vallaeys" site:linkedin.com/posts
- "Navah Hopkins" site:linkedin.com/posts Google Ads
- "Brad Geddes" site:linkedin.com/posts PPC
- "Mike Rhodes" site:linkedin.com/posts (AU-based — prioritise)
- Generic: "Performance Max" OR "Google Ads" site:linkedin.com/posts (last [timeframe] days)

Organic Social Media:
- "Matt Navarra" site:linkedin.com/posts Instagram OR TikTok
- "Rachel Karten" site:linkedin.com/posts social media
- "Amanda Natividad" site:linkedin.com/posts
- Generic: "organic social" OR "Instagram algorithm" OR "TikTok organic" site:linkedin.com/posts

Paid Social Media:
- "Jon Loomer" site:linkedin.com/posts Meta ads
- "Savannah Sanchez" site:linkedin.com/posts
- "Depesh Mandalia" site:linkedin.com/posts Facebook ads
- "Andrew Foxwell" site:linkedin.com/posts
- Generic: "Meta ads" OR "paid social" OR "Facebook ads creative" site:linkedin.com/posts

Website Development:
- "Vitaly Friedman" site:linkedin.com/posts
- "Peep Laja" site:linkedin.com/posts CRO OR conversion
- "Wil Reynolds" site:linkedin.com/posts
- "Addy Osmani" site:linkedin.com/posts performance
- Generic: "Core Web Vitals" OR "CRO" OR "website performance" site:linkedin.com/posts

Branding:
- "Mark Ritson" site:linkedin.com/posts brand
- "Rand Fishkin" site:linkedin.com/posts
- "Bob Hoffman" site:linkedin.com/posts advertising
- "Scott Galloway" site:linkedin.com/posts
- Generic: "brand strategy" OR "brand vs performance" site:linkedin.com/posts

AI in Marketing:
- "Paul Roetzer" site:linkedin.com/posts AI marketing
- "Christopher Penn" site:linkedin.com/posts AI
- Generic: "AI marketing" OR "AI agents" OR "generative engine" site:linkedin.com/posts
```

**What to look for:**
- The expert's actual opinion, not a reshare or link drop
- High engagement posts (100+ reactions, 50+ comments)
- Comment threads where other experts weigh in — these contain hidden gold
- Contrarian takes, "hot take" posts, and "unpopular opinion" framing

If a LinkedIn MCP connector is available, search directly within LinkedIn for each expert's recent posts instead of using web search proxying.

#### 2. Newsletter & Substack Scan

For each expert newsletter listed in the workflow's newsletter directory, check for recent editions:

```
Newsletter scan queries:

SEO:
- site:lilyraynyc.substack.com (Lily Ray)
- site:growth-memo.com (Kevin Indig — Growth Memo)
- site:seofomo.co (Aleyda Solis — SEOFOMO)
- site:seroundtable.com (Barry Schwartz)
- site:zyppy.com/blog (Cyrus Shepard)

Google Ads:
- site:optmyzr.com/blog (Frederick Vallaeys / Navah Hopkins)
- site:wordstream.com/blog Google Ads

Organic Social Media:
- site:geekout.mattnavarra.com (Matt Navarra — Geekout)
- site:linkinbio.beehiiv.com (Rachel Karten — Link in Bio)
- site:sparktoro.com/blog (Amanda Natividad)

Paid Social Media:
- site:pubcast.jonloomer.com (Jon Loomer — Pubcast)
- site:jonloomer.com/blog (Jon Loomer)
- site:thesocialsavannah.com (Savannah Sanchez)

Website Development:
- site:smashingmagazine.com/the-smashing-newsletter (Vitaly Friedman)
- site:cxl.com/blog (Peep Laja)
- site:addyosmani.com (Addy Osmani)

Branding:
- site:marketingweek.com/mark-ritson (Mark Ritson)
- site:sparktoro.com/blog brand OR zero-click (Rand Fishkin)
- site:adcontrarian.substack.com (Bob Hoffman)
- site:profgalloway.com (Scott Galloway)

AI in Marketing:
- site:marketingaiinstitute.com/blog (Paul Roetzer)
- site:christopherspenn.com/newsletter (Christopher Penn)
```

**Why newsletters matter:** Experts use LinkedIn for hot takes and newsletters for expanded analysis. The newsletter version usually includes data, examples, and nuance that the LinkedIn post didn't. Capture both where they exist — the LinkedIn post for the punchy take, the newsletter for the evidence.

#### 3. Publication & Ahrefs Scan

For each vertical, check authoritative publications and use Ahrefs for trend data:

```
Publication scan queries per vertical:

SEO:
- site:searchengineland.com [topic] (last [timeframe] days)
- site:searchenginejournal.com [topic]
- site:moz.com/blog [topic]
- "[topic] Australia SEO"

Google Ads:
- site:searchengineland.com Google Ads [topic]
- Google Ads official blog
- site:wordstream.com/blog [topic]

Organic Social Media:
- site:socialmediaexaminer.com [topic]
- site:hootsuite.com/research [topic]
- site:sproutsocial.com/insights [topic]

Paid Social Media:
- site:adexchanger.com [topic]
- Meta Business Blog
- site:socialmediaexaminer.com paid [topic]

Website Development:
- site:smashingmagazine.com [topic]
- site:web.dev/blog [topic]
- site:nngroup.com [topic]

Branding:
- site:marketingweek.com [topic]
- site:thedrum.com [topic]
- site:digiday.com [topic]

AI in Marketing:
- "AI marketing" [current year] latest
- site:marketingaiinstitute.com [topic]
```

**Ahrefs check (via MCP):**
- Check trending content in the vertical's key topics
- Identify which articles are gaining backlinks (signals authority)
- Note any ranking shifts for key industry terms
- Cross-reference: are the trending articles citing the same experts from our watchlist?

#### 4. Community & Emerging Signals Scan

Check relevant communities for practitioner perspectives and emerging discourse:

```
Community scan queries:

- site:reddit.com/r/SEO [topic]
- site:reddit.com/r/PPC [topic]
- site:reddit.com/r/digital_marketing [topic]
- site:reddit.com/r/webdev [topic]
- site:reddit.com/r/socialmedia [topic]
- "[topic]" expert opinion OR hot take (general web — catches X/Twitter, forums, etc.)
```

**What to look for:** Real practitioner results (not theory), debates that contradict expert consensus, new voices sharing original data or case studies, AU-specific discussions.

#### 5. Signal Extraction

For each relevant result found across all four channels, apply the **Client Relevance Lens** before capturing:
- Would an ambitious AU business spending $50k–$250k+ on marketing care about this?
- Is this actionable for SMBs and mid-market businesses (not enterprise-only)?
- Can Distl turn this into a useful perspective for clients?

If yes, capture:
- Extract the core claim/opinion/data point — **in the expert's own words where possible**
- Identify the source and author by name
- Note which channel it came from (LinkedIn / Newsletter / Publication / Community)
- Assign a vertical
- Rate credibility (Expert / Publication / Community)
- Note client relevance (how this affects AU businesses in our ICP)
- Draft an initial "Our Angle" reaction

**Skip:** Enterprise-only insights, budget/bootstrap advice, overly academic theory, US/UK-only regulatory changes with no AU impact.

**Prioritise:** Expert opinions over publication summaries. A LinkedIn post from Lily Ray is worth more than a Search Engine Journal article summarising the same update.

#### 4. Take Synthesis
Group signals by theme and generate takes:
- Look for consensus (3+ signals agreeing)
- Look for contradictions (signals that conflict)
- Look for emerging patterns (new topics appearing)
- Rate each take's strength and content potential

#### 5. Output to Google Sheets (via MCP)
- Append new signals to the Signal Feed tab
- Add synthesised takes to the Takes Bank tab
- Flag newsletter-worthy items in the Newsletter Queue tab
- Update Expert Directory if new voices were discovered

### Output Format

After the scan, provide a summary to the user:

```
## Hivemind Scan Complete — [Date]
**Scope:** [All / Specific vertical]
**Signals captured:** [number] (LinkedIn: [n] | Newsletters: [n] | Publications: [n] | Community: [n])
**Takes generated:** [number]
**Newsletter items flagged:** [number]

### Top Expert Takes
1. [Expert name] on [topic]: "[their take in their words]" — [channel]
2. [Expert name] on [topic]: "[their take in their words]" — [channel]
3. [Expert name] on [topic]: "[their take in their words]" — [channel]

### Strongest Distl Takes
1. [Our opinionated take, built from expert signals]
2. [Second strongest]

### Expert Debates / Disagreements
- [Where two experts disagree — these make the best content angles]

### New Experts Discovered
- [Any new voices worth tracking + their LinkedIn URL]

### AU-Specific Signals
- [Anything specific to the Australian market]

### Sheet updated: [link to Google Sheet]
```

## Team LinkedIn Drop Procedure

The automated scan can only catch public LinkedIn posts that get indexed by search engines. Many high-value posts — especially those from smaller accounts or behind LinkedIn's login wall — won't show up. The team's human curation layer fills this gap.

When a team member sees a good LinkedIn post:
1. They tell Claude: "Add this to the hivemind" and paste the post text, a screenshot, or the LinkedIn URL
2. Claude extracts the signal: who said it, what they said, which vertical it belongs to
3. Claude applies the Client Relevance Lens
4. If relevant, Claude logs it to the Signal Feed with `Channel: LinkedIn (team drop)` and credits the team member in `Added By`
5. If the post is from someone not on the watchlist, Claude flags them as a potential addition to the Expert Directory

**Encourage the team to:** Follow every expert on the watchlist on LinkedIn. Their feeds become a passive scanning tool — the team just needs to flag the good stuff.

## Quick Add Procedure

When a team member says "add this to the hivemind":

1. Ask for (or infer from context):
   - The signal or take
   - The source/link (LinkedIn URL, newsletter link, article, or just a pasted quote)
   - The vertical it belongs to
2. Determine if it's a raw signal or a formed take
3. Identify the channel (LinkedIn / Newsletter / Publication / Community / Team observation)
4. Apply the Client Relevance Lens
5. Add to the appropriate tab in the Google Sheet
6. Confirm what was added and where

## Newsletter Compilation Procedure

When prompted to compile the newsletter:

1. Pull all items from Newsletter Queue where "Included in Edition" is blank
2. Group by vertical
3. For each item, ensure "Our Angle" is filled in
4. Draft the newsletter using the template in the workflow
5. Output to a new Google Doc
6. Mark items as included in the Newsletter Queue tab
7. Share the Doc link with the user
