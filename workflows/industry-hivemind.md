# Industry Hivemind

## Purpose

Systematically scan, collect, and synthesise expert opinions, industry trends, and authoritative takes across all of Distl's core verticals. This feeds three outputs:

1. **Team Newsletter** — A regular digest the team can skim to stay sharp
2. **Takes Bank** — A living repository of opinionated angles the team can draw from for content
3. **Blog Fuel** — Authoritative references and expert-backed positions that make blog posts credible and differentiated

## Client Relevance Lens

Everything in the Hivemind should be filtered through: **"Would this matter to our ideal client?"**

### Who we're talking to
- **Australian businesses** — content and takes should resonate with the AU market, reference AU-relevant examples where possible, and account for the AU competitive landscape
- **Annual agency spend: $50k–$250k+** — these are businesses that invest seriously in marketing, expect strategic thinking, and want an agency that knows its stuff. They're not shopping on price
- **Growth-oriented, ambitious** — they want to scale, launch into new markets, dominate their category. They're comfortable spending to get results
- **Typically SMBs through to mid-market** — owner-led or with a small marketing team. Not massive enterprises with 100+ employee marketing departments and layers of procurement. Think businesses where the founder, GM, or marketing manager is the decision-maker

### What this means for the Hivemind
- **Skip signals that only apply to enterprise** — global brand governance frameworks, Fortune 500 case studies, massive multi-market campaigns. Unless there's a transferable insight for smaller businesses, it's noise
- **Skip budget-conscious / bootstrap content** — "how to do marketing with no budget" or "free tools for startups" isn't our world. Our clients invest in quality
- **Prioritise practical, results-driven takes** — our clients care about what works, what's changing, and what they should do about it. Theory is fine if it leads somewhere actionable
- **AU-specific signals are gold** — Australian market data, AU platform rollouts, AU consumer behaviour shifts, and AU industry events should be flagged prominently
- **Think owner/operator language** — the content we produce from this should speak to business leaders who are smart but not marketing professionals. Avoid jargon-heavy, agency-to-agency navel-gazing unless it genuinely informs a client-facing take

### Relevance check for every signal
Before adding a signal or take, ask:
1. Would our ideal client care about this?
2. Can we turn this into advice or a perspective that's relevant to their business?
3. Does this help position Distl as the agency that *gets* businesses like theirs?

If the answer to all three is no, skip it.

## Core Verticals to Monitor

| Vertical | What to track |
|---|---|
| SEO | Algorithm updates, ranking factor debates, technical SEO shifts, local SEO, content strategy for organic, link building discourse, AI overviews & search generative experience |
| Google Ads | Search & Shopping campaign strategies, Performance Max debates, bidding strategies, Quality Score factors, attribution, auction insights, Google Ads platform changes |
| Organic Social Media | Platform algorithm changes, content formats & trends, community building, social SEO, engagement tactics, organic reach debates, creator economy shifts |
| Paid Social Media | Meta/TikTok/LinkedIn ad platform changes, creative performance trends, audience targeting shifts, attribution & measurement, ad format innovation, ROAS debates |
| Website Development | Core Web Vitals, CMS & tech stack debates, accessibility, page speed, CRO tactics, UX patterns, headless/composable architecture, AI in web dev |
| Branding | Brand strategy frameworks, visual identity trends, brand voice & tone, positioning debates, rebrand case studies, brand measurement, brand vs performance marketing discourse |
| AI in Marketing | AI tool adoption & reviews, LLM/agent workflows, AI content generation debates, marketing automation, ethical considerations, competitive implications, AI search & discovery |

## Intelligence Sources

The Hivemind pulls from four source channels, in priority order. The richest signals come from expert voices on LinkedIn and their personal platforms — not from generic web articles.

### Source Channel 1: LinkedIn (Primary)
LinkedIn is where industry experts share raw, real-time takes before they become polished blog posts. This is the most valuable signal source.

**How to scan LinkedIn (depends on available connectors):**

**If LinkedIn MCP connector is installed** (see `tools/linkedin-connector.md`):
- Use `get_person_profile` with `posts` section for each expert on the watchlist — this pulls their recent posts directly
- This is the most reliable method — doesn't depend on search engine indexing
- Run through the full expert watchlist for the vertical being scanned

**If no LinkedIn MCP connector:**
- Use web search with `site:linkedin.com/posts [expert name]` and `site:linkedin.com/pulse [topic]` to catch high-engagement public posts that have been indexed
- This won't catch everything — many posts aren't indexed by search engines
- Supplement heavily with team LinkedIn drops (see "How the Team Contributes")

**Team LinkedIn drops (always, regardless of connector):**
- Team members should actively drop LinkedIn posts into the Hivemind as they scroll — this human curation layer catches posts that neither web search nor scraping will find
- Every team member should follow all experts on the watchlist on LinkedIn — their daily scroll becomes a passive scanning tool

**What to look for on LinkedIn:**
- Expert hot takes and opinion posts (not corporate announcements)
- Debates and disagreements in comment threads — these often surface nuance that articles miss
- Data screenshots and case study snippets shared directly in posts
- "Unpopular opinion" or "here's what nobody's talking about" posts — high signal-to-noise ratio
- Posts with 100+ comments — the discourse is often more valuable than the original post

### Source Channel 2: Expert Newsletters & Substacks (High Value)
Many watchlist experts publish regular newsletters that expand on their LinkedIn takes. These are consistently high-quality, opinionated, and often contain original data.

**Expert newsletter directory (scan these directly):**

| Expert | Newsletter/Substack | Vertical | URL |
|---|---|---|---|
| Lily Ray | Lily Ray SEO | SEO | lilyraynyc.substack.com |
| Kevin Indig | Growth Memo | SEO | growth-memo.com |
| Aleyda Solis | SEOFOMO | SEO | seofomo.co |
| Barry Schwartz | SE Roundtable | SEO | seroundtable.com |
| Frederick Vallaeys | Optmyzr Blog | Google Ads | optmyzr.com/blog |
| Navah Hopkins | Optmyzr / personal | Google Ads | linkedin.com/in/navahhopkins |
| Jon Loomer | Pubcast | Paid Social Media | pubcast.jonloomer.com |
| Rachel Karten | Link in Bio | Organic Social Media | linkinbio.beehiiv.com |
| Matt Navarra | Geekout | Organic Social Media | geekout.mattnavarra.com |
| Amanda Natividad | SparkToro Blog | Organic Social Media | sparktoro.com/blog |
| Mark Ritson | Marketing Week column | Branding | marketingweek.com/mark-ritson |
| Bob Hoffman | The Ad Contrarian | Branding | adcontrarian.substack.com |
| Rand Fishkin | SparkToro Blog | Branding / SEO | sparktoro.com/blog |
| Scott Galloway | No Mercy / No Malice | Branding / Strategy | profgalloway.com |
| Paul Roetzer | Marketing AI Institute | AI in Marketing | marketingaiinstitute.com/blog |
| Christopher Penn | Almost Timely | AI in Marketing | christopherspenn.com/newsletter |
| Vitaly Friedman | Smashing Newsletter | Website Development | smashingmagazine.com/the-smashing-newsletter |
| Peep Laja | CXL Blog / Wynter | Website Development / CRO | cxl.com/blog |

### Source Channel 3: Authoritative Publications & Sites
Verified, industry-leading sources with editorial standards. Useful for data, research, and trend validation — but often lag behind LinkedIn and newsletters.

| Vertical | Sources |
|---|---|
| SEO | Search Engine Journal, Search Engine Land, Moz Blog, Ahrefs Blog, Google Search Central Blog, Semrush Blog |
| Google Ads | Google Ads Blog, Search Engine Land (PPC), PPC Hero, WordStream Blog, Optmyzr Blog |
| Organic Social Media | Social Media Examiner, Later Blog, Hootsuite Blog, Sprout Social Insights, Buffer Blog, platform creator blogs |
| Paid Social Media | AdExchanger, Meta Business Blog, Jon Loomer Blog, Social Media Examiner (paid), TikTok for Business Blog |
| Website Development | Smashing Magazine, Web.dev, CXL, Nielsen Norman Group, A List Apart, CSS-Tricks |
| Branding | Harvard Business Review (marketing), Marketing Week, Digiday, The Drum, Brand New (Under Consideration) |
| AI in Marketing | The Neuron, TLDR AI, Ben's Bites, Anthropic Blog, OpenAI Blog, Marketing AI Institute, Import AI |

### Source Channel 4: Community & Emerging Signals
Where raw, unfiltered discourse happens. Good for spotting trends early, validating takes, and finding new expert voices.

- **Reddit:** r/SEO, r/PPC, r/digital_marketing, r/webdev, r/socialmedia, r/branding, r/artificial
- **X/Twitter:** Industry hashtags and expert accounts
- **Slack/Discord communities:** Superpath, DGMG, Traffic Think Tank, Demand Curve
- **Podcasts:** Marketing Over Coffee, Everyone Hates Marketers, The Search Engine Journal Show, Marketing AI Show, The Google Ads Podcast, The Marketing Millennials

### Expert Watchlist (with LinkedIn profiles)

These are the named individuals to actively track across LinkedIn, newsletters, and publications. Their LinkedIn profiles should be checked during every scan.

**SEO:**
| Name | LinkedIn | Newsletter/Platform | Why they matter |
|---|---|---|---|
| Lily Ray | linkedin.com/in/lily-ray-44755615 | lilyraynyc.substack.com | VP SEO at Amsive. Leading voice on AI content, E-E-A-T, algorithm updates. Data-driven, opinionated. |
| Kevin Indig | linkedin.com/in/kevinindig | growth-memo.com | Ex-Shopify/G2 growth lead. Publishes original research on AI Overviews traffic impact. Sharp strategic thinker. |
| Aleyda Solis | linkedin.com/in/aleydasolis | seofomo.co | International SEO consultant. Curates SEOFOMO newsletter — excellent weekly roundup of SEO signals. |
| Marie Haynes | linkedin.com/in/mariehaynes | mariehaynes.com | E-E-A-T and Google quality specialist. Deep on algorithm recovery and quality signals. |
| Cyrus Shepard | linkedin.com/in/cyrusshepard | zyppy.com/blog | Founder of Zyppy. Runs large-scale SEO experiments with original data. |
| Barry Schwartz | linkedin.com/in/barryschwartz | seroundtable.com | Breaks Google news faster than anyone. Essential for staying across updates in real time. |
| John Mueller | linkedin.com/in/johnmu | Google Search Central Blog | Google's Search Advocate. Official source — what he says (and doesn't say) matters. |

**Google Ads:**
| Name | LinkedIn | Newsletter/Platform | Why they matter |
|---|---|---|---|
| Frederick Vallaeys | linkedin.com/in/frederickvallaeys | optmyzr.com/blog | Ex-Google employee #500. CEO of Optmyzr. Deep expertise on PMax, automation, and smart bidding. |
| Aaron Levy | linkedin.com/in/aaronmlevy | Tinuiti blog | VP of Paid Search at Tinuiti. Practical, data-backed takes on Google Ads changes. |
| Brad Geddes | linkedin.com/in/bgtheory | bgtheory.com | Founder of Adalysis. Wrote the book on AdWords. Deep Quality Score and auction expertise. |
| Navah Hopkins | linkedin.com/in/navahhopkins | optmyzr.com/blog | Evangelist at Optmyzr. Prolific LinkedIn poster — shares PPC tests and results regularly. |
| Mike Rhodes | linkedin.com/in/mikerhodes | websavvy.com.au | **Australian-based.** Founder of WebSavvy. Local Google Ads expertise with AU market context. |

**Organic Social Media:**
| Name | LinkedIn | Newsletter/Platform | Why they matter |
|---|---|---|---|
| Matt Navarra | linkedin.com/in/mattnavarra | geekout.mattnavarra.com | Former social media director at TNW. Breaks platform changes and features before anyone else. |
| Rachel Karten | linkedin.com/in/rachelkarten | linkinbio.beehiiv.com | "Link in Bio" newsletter. Deep on what's working in organic social with brand examples. |
| Adam Mosseri | instagram.com/mosseri | Instagram broadcast channel | Head of Instagram. His statements are the algorithm — when he speaks, strategies shift. |
| Amanda Natividad | linkedin.com/in/amandanatividad | sparktoro.com/blog | VP Marketing at SparkToro. Sharp on zero-click content strategy and audience research. |
| Jay Baer | linkedin.com/in/jaybaer | jaybaer.com | Content marketing veteran. Strong on word-of-mouth and organic amplification tactics. |

**Paid Social Media:**
| Name | LinkedIn | Newsletter/Platform | Why they matter |
|---|---|---|---|
| Jon Loomer | linkedin.com/in/jonloomer | pubcast.jonloomer.com | The Meta ads authority. First to test and document every platform change. His "19 Rules" post is essential reading. |
| Savannah Sanchez | linkedin.com/in/savannahsanchez | thesocialsavannah.com | Produces 200+ ads/week for 50+ clients. Pioneered the creative-as-targeting approach before Meta forced it. |
| Andrew Foxwell | linkedin.com/in/andrewfoxwell | foxwelldigital.com | Meta and paid social strategist. Practical, test-driven, shares real client results. |
| Depesh Mandalia | linkedin.com/in/depeshmandalia | depeshmandalia.com | BPM Method creator. Deep on Meta ad psychology and creative strategy. |
| Sarah Sal | linkedin.com/in/sarahsal | Facebook ad copywriting specialist. Known for long-form ad copy that converts — contrarian to short-copy trends. |

**Website Development:**
| Name | LinkedIn | Newsletter/Platform | Why they matter |
|---|---|---|---|
| Vitaly Friedman | linkedin.com/in/vitalyfriedman | Smashing Magazine / Newsletter | Founder of Smashing Magazine. Covers front-end, UX, performance. Runs workshops on measuring design impact. |
| Peep Laja | linkedin.com/in/peeplaja | cxl.com/blog + wynter.com | Founder of CXL and Wynter. CRO pioneer. Sharp on what actually moves conversion metrics. |
| Wil Reynolds | linkedin.com/in/wilreynolds | seerinteractive.com/blog | Founder of Seer Interactive. Bridges SEO, CRO, and web dev — strong on data-driven decision making. |
| Addy Osmani | linkedin.com/in/nicholasosmani | addyosmani.com | Engineering Manager at Google Chrome. The authority on web performance, Core Web Vitals, and JavaScript optimisation. |

**Branding:**
| Name | LinkedIn | Newsletter/Platform | Why they matter |
|---|---|---|---|
| Mark Ritson | linkedin.com/in/markritson | Marketing Week column | **Australian-based.** Professor and columnist. The loudest voice on brand vs performance balance. Uses Nike as a cautionary tale. |
| Rand Fishkin | linkedin.com/in/randfishkin | sparktoro.com/blog | Co-founder of SparkToro. Coined "zero-click marketing." Argues brand > attribution. Essential on search and brand intersection. |
| Bob Hoffman | linkedin.com/in/bobhoffman | adcontrarian.substack.com | "The Ad Contrarian." Calls out marketing BS. Sharp, irreverent takes on brand, advertising effectiveness, and industry hype. |
| Scott Galloway | linkedin.com/in/profgalloway | profgalloway.com | NYU professor. Covers brand, tech, and market dynamics. His "No Mercy / No Malice" newsletter is widely read. |

**AI in Marketing:**
| Name | LinkedIn | Newsletter/Platform | Why they matter |
|---|---|---|---|
| Paul Roetzer | linkedin.com/in/paulroetzer | marketingaiinstitute.com | Founder of Marketing AI Institute. Calls 2026 a "make-or-break" year. Tracks AI agent adoption in marketing. |
| Christopher Penn | linkedin.com/in/cspenn | christopherspenn.com/newsletter | Co-founder of Trust Insights. Data scientist applying AI to marketing analytics. Weekly "Almost Timely" newsletter. |
| Rand Fishkin | linkedin.com/in/randfishkin | sparktoro.com/blog | Tracking AI's impact on search traffic and brand visibility in AI-generated answers. Cross-listed with Branding. |
| Liza Adams | linkedin.com/in/lizaadams | Various publications | AI strategy advisor. Focuses on practical AI implementation for marketing teams. |

## How to Run a Scan

### Step 1: Gather Raw Signals

For each vertical in scope, work through the four source channels in order. Focus on the last 7–14 days (or whatever cadence the team decides).

**Channel 1 — LinkedIn Expert Scan (do this first):**
For each expert in the watchlist for the vertical:
- Search `site:linkedin.com/posts [expert name] [vertical topic]` to find recent public posts
- Search `site:linkedin.com/pulse [expert name]` for LinkedIn articles
- If a LinkedIn MCP connector is available, search directly for the expert's recent posts
- Look for posts with high engagement (100+ reactions, 50+ comments) — the comment threads often contain takes from other experts
- Capture the expert's opinion, not just the topic they're discussing

**Channel 2 — Newsletter & Substack Scan:**
For each expert newsletter in the directory for the vertical:
- Check recent editions (web search: `site:[newsletter-url] [vertical topic]`)
- These often contain original data, case studies, and expanded takes from their LinkedIn posts
- Newsletters are higher quality than news articles — prioritise these

**Channel 3 — Publication & Site Scan:**
- `[vertical topic] [current year]` on authoritative sites
- `[vertical topic] Australia` — AU-specific signals (prioritise these)
- Use Ahrefs (via MCP) to check what's ranking and trending in each vertical
- Cross-reference: are publications citing the same experts from our watchlist? If so, capture the expert's take, not the publication's summary

**Channel 4 — Community & Emerging Signals:**
- Check relevant subreddits and community threads for discussions that challenge or support what experts are saying
- Look for practitioner perspectives — people sharing real results, not theory
- Good for finding new expert voices to add to the watchlist

**Remember the Client Relevance Lens** — filter out enterprise-only content, budget-conscious advice, and anything that wouldn't resonate with an ambitious AU business investing seriously in marketing.

**What to capture for each signal:**
- **Source**: Who said it and where (name the expert, not just the platform)
- **Date**: When it was published/posted
- **Vertical**: Which vertical it maps to
- **Channel**: Which source channel it came from (LinkedIn / Newsletter / Publication / Community)
- **Signal**: The core claim, opinion, or data point (1–3 sentences) — in the expert's own words where possible
- **Link**: URL to the original source
- **Credibility**: Expert (named individual) / Publication (editorial source) / Community (unverified)
- **Client relevance**: How does this affect AU businesses spending $50k–$250k+ on marketing? (If it doesn't, skip it — see Client Relevance Lens)
- **Our angle**: Initial reaction — do we agree, disagree, or want to expand on this?

### Step 2: Synthesise into Takes

Group related signals and extract actionable angles:

1. **Consensus takes** — Multiple experts agree on something → we can add our perspective and evidence
2. **Contrarian takes** — We disagree with a popular opinion → strong blog angle
3. **Emerging trends** — Early signals that most people aren't talking about yet → thought leadership opportunity
4. **Data-backed takes** — Hard numbers or case studies that support a position → authoritative blog content
5. **Team-generated takes** — Things the team has observed from client work that align with or contradict industry discourse

For each take, document:
- **The take** (1–2 sentences, opinionated)
- **Supporting signals** (links to the evidence)
- **Strength** (Strong / Developing / Speculative)
- **Content potential** (Blog post / Social post / Newsletter mention / Internal only)
- **Assigned vertical**

### Step 3: Populate the Hivemind Sheet

Output goes to a shared Google Sheet (the "Hivemind") with these tabs:

#### Tab 1: Signal Feed
All raw signals captured during scans. Columns:
`Date | Vertical | Channel | Source | Expert/Pub | Signal Summary | Link | Credibility | Client Relevance | Our Angle`

#### Tab 2: Takes Bank
Synthesised takes ready for content use. Columns:
`Date Added | Vertical | The Take | Supporting Signals | Strength | Content Potential | Used In | Added By`

#### Tab 3: Newsletter Queue
Items flagged for the next team newsletter. Columns:
`Date | Vertical | Headline | Summary | Link | Added By | Included in Edition`

#### Tab 4: Expert Directory
Running list of experts and sources worth monitoring. Columns:
`Name | LinkedIn URL | Newsletter/Substack URL | Vertical | Why They Matter | Last Checked`

### Step 4: Draft the Newsletter

When it's time to compile (weekly or fortnightly), pull from the Newsletter Queue tab and structure it as:

```
# Distl Hivemind — Edition [#]
**Date range: [start] – [end]**

## Top Takes This Week
[2–3 biggest, most opinionated takeaways with our angle]

## By Vertical
### SEO
- [Signal + our take]

### Google Ads
- [Signal + our take]

### Organic Social Media
- [Signal + our take]

### Paid Social Media
- [Signal + our take]

### Website Development
- [Signal + our take]

### Branding
- [Signal + our take]

### AI in Marketing
- [Signal + our take]

## From the Team
[Any signals, observations, or takes added by team members from client work]

## Worth Bookmarking
[2–3 links to deeper reads]
```

Output the newsletter to a Google Doc in the shared drive, and optionally post a summary to the team's Monday board or Slack.

## How the Team Contributes

This isn't a one-way feed. The team should be able to drop signals and takes into the Hivemind at any time:

- **Quick add**: Tell Claude "add this to the hivemind" with a link or observation, and it gets logged to the Signal Feed or Takes Bank
- **Flag for newsletter**: "Flag this for the next newsletter" adds it to the Newsletter Queue
- **Challenge a take**: "I disagree with [take] because..." updates the take with a counter-perspective
- **Add an expert**: "Start tracking [name] for [vertical]" adds them to the Expert Directory

## Using the Hivemind for Blog Writing

When writing a blog post, the workflow is:

1. **Pick a take** from the Takes Bank that has strong supporting signals
2. **Pull the evidence** — the supporting signals give you expert quotes, data, and source links
3. **Write with authority** — reference specific experts and publications by name
4. **Add our angle** — the "Our Angle" field gives you the starting point for Distl's perspective
5. **Cross-reference** — check if other verticals have related takes for a more holistic piece

This means every blog post can say things like:
- "As [Expert] recently argued on LinkedIn..."
- "Data from [Authoritative Source] shows..."
- "While the industry consensus is X, our experience with clients suggests Y..."

## Cadence

| Activity | Frequency | Who |
|---|---|---|
| Full industry scan | Weekly or fortnightly | Claude (prompted by any team member) |
| Team signal drops | Anytime | Any team member via Claude |
| Newsletter compilation | Fortnightly or monthly | Claude (prompted by any team member) |
| Expert directory review | Monthly | Claude + team |
| Takes Bank cleanup | Monthly | Claude + team (archive stale takes) |

## Edge Cases

- **Paywalled content**: Note that a source is paywalled and capture whatever is available from previews, social shares, or summaries. Don't try to bypass paywalls.
- **Controversial takes**: Flag anything politically sensitive or potentially brand-damaging before adding it to the Takes Bank. Let the team decide.
- **Duplicate signals**: Before adding, check if a similar signal already exists. If so, merge or add as supporting evidence to the existing entry.
- **Source credibility disputes**: If unsure about a source's credibility, default to Tier 3 and note the uncertainty.

## Getting Started

To initialise the Hivemind:

1. **Create the Google Sheet** — Set up the four tabs (Signal Feed, Takes Bank, Newsletter Queue, Expert Directory) with the column headers listed above
2. **Seed the Expert Directory** — Populate with the starting watchlist from this workflow
3. **Run the first scan** — Do a full scan across all verticals to populate the initial Signal Feed
4. **Generate initial takes** — Synthesise the first batch of takes from the scan
5. **Review with the team** — Walk through the first output and adjust verticals, sources, or format as needed

To kick off a scan, just say: **"Run a hivemind scan"** or **"Scan [vertical] for the hivemind"**
