# Hivemind Scan Tool

## What This Does

This is a **reference script** for Claude to follow when running an industry hivemind scan. It's not executable code — it's a structured procedure that Claude follows using MCP connectors and web search.

## Scan Procedure

### Input
- **Scope**: "all" (full scan) or a specific vertical (e.g. "SEO", "Paid Media")
- **Timeframe**: Number of days to look back (default: 14)
- **Depth**: "quick" (top signals only) or "deep" (comprehensive sweep)

### Execution Steps

#### 1. Web Search Sweep
For each vertical in scope, run searches:

```
Search queries per vertical:

SEO:
- "SEO trends 2026"
- "Google algorithm update" (last [timeframe] days)
- "SEO expert opinion site:linkedin.com/posts"
- "technical SEO" latest news
- "AI overviews SEO impact"
- Check: searchengineland.com, searchenginejournal.com, moz.com/blog, ahrefs.com/blog

Google Ads:
- "Google Ads update 2026"
- "Performance Max" latest
- "Google Ads strategy site:linkedin.com/posts"
- "PPC bidding strategy" expert opinion
- Check: ads.google.com/home/resources, ppc hero, wordstream.com/blog, optmyzr.com/blog

Organic Social Media:
- "social media algorithm 2026"
- "organic social strategy" latest
- "social media trends site:linkedin.com/posts"
- "organic reach" expert opinion
- Check: socialmediaexaminer.com, hootsuite.com/research, sproutsocial.com/insights

Paid Social Media:
- "Meta ads update 2026"
- "TikTok ads" latest
- "paid social expert opinion site:linkedin.com/posts"
- "social ads ROAS" strategy
- Check: adexchanger.com, jonloomer.com, meta business blog

Website Development:
- "web development trends 2026"
- "Core Web Vitals update"
- "CRO expert" latest
- "headless CMS" opinion
- Check: smashingmagazine.com, web.dev/blog, cxl.com, nngroup.com

Branding:
- "brand strategy 2026"
- "rebrand case study" latest
- "brand vs performance marketing"
- "brand positioning" expert opinion
- Check: marketingweek.com, digiday.com, thedrum.com, underconsideration.com/brandnew

AI in Marketing:
- "AI marketing tools 2026"
- "AI content generation" expert opinion
- "marketing automation AI"
- "LLM marketing workflow"
- Check: marketingaiinstitute.com, Paul Roetzer latest, Christopher Penn latest
```

#### 2. Ahrefs Check (via MCP)
For each vertical, use Ahrefs to:
- Check trending content in the vertical's key topics
- Identify which articles are gaining backlinks (signals authority)
- Note any ranking shifts for key industry terms

#### 3. Signal Extraction
For each relevant result found:
- Extract the core claim/opinion/data point
- Identify the source and author
- Assign a vertical
- Rate credibility (Tier 1/2/3)
- Draft an initial "Our Angle" reaction

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
**Signals captured:** [number]
**Takes generated:** [number]
**Newsletter items flagged:** [number]

### Top Signals
1. [Most significant finding]
2. [Second most significant]
3. [Third most significant]

### New Takes
1. [Strongest new take]
2. [Second strongest]

### New Experts Discovered
- [Any new voices worth tracking]

### Sheet updated: [link to Google Sheet]
```

## Quick Add Procedure

When a team member says "add this to the hivemind":

1. Ask for (or infer from context):
   - The signal or take
   - The source/link
   - The vertical it belongs to
2. Determine if it's a raw signal or a formed take
3. Add to the appropriate tab in the Google Sheet
4. Confirm what was added and where

## Newsletter Compilation Procedure

When prompted to compile the newsletter:

1. Pull all items from Newsletter Queue where "Included in Edition" is blank
2. Group by vertical
3. For each item, ensure "Our Angle" is filled in
4. Draft the newsletter using the template in the workflow
5. Output to a new Google Doc
6. Mark items as included in the Newsletter Queue tab
7. Share the Doc link with the user
