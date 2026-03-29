# LinkedIn Connector for the Hivemind

## The Problem

LinkedIn is where industry experts share their rawest, most opinionated takes — before they become polished blog posts. But LinkedIn has no public API for searching or reading other people's posts. This makes it the hardest source channel to automate.

## What Exists Today

### Option 1: stickerdaniel/linkedin-mcp-server (Best Current Option)
**GitHub:** https://github.com/stickerdaniel/linkedin-mcp-server

An open-source MCP server that uses browser automation (Patchright) to interact with LinkedIn through Claude.

**What it can do:**
- `get_person_profile` — Scrape a profile including their recent **posts**, experience, education, contact info
- `get_company_profile` — Get company page info
- `search_jobs` / `get_job_details` — Job search (not relevant for us)
- `close_session` — Session management

**What it can't do:**
- Search LinkedIn posts by keyword or topic
- Browse a feed
- Search for new experts by topic
- Read comment threads on posts

**How it helps the Hivemind:** We can pull recent posts from each expert on the watchlist by scraping their profile. This gives us their latest takes without relying on web search indexing. It doesn't solve discovery (finding new voices), but it covers monitoring known experts.

**Setup:**
```bash
# Install
uvx linkedin-scraper-mcp

# First-time login (opens a browser window)
uvx linkedin-scraper-mcp --login

# Add to Claude as MCP server
claude mcp add linkedin-mcp-server -- uvx linkedin-scraper-mcp
```

**Caveats:**
- Uses browser automation, not official API — LinkedIn may block or rate-limit
- As of Feb 2026, users sometimes get captcha challenges
- Tool calls are serialised (one at a time) to protect the browser session
- Requires a real LinkedIn account logged in

### Option 2: Composio LinkedIn MCP
**URL:** https://composio.dev/toolkits/linkedin

A managed MCP integration via Composio's platform.

**What it can do:**
- Create and delete LinkedIn posts
- Get authenticated user's profile info
- Get company page info

**What it can't do:**
- Read other people's posts
- Search posts by keyword
- Browse feeds

**Verdict:** Not useful for the Hivemind's scanning needs. Only useful if we want to *post* to LinkedIn (e.g. sharing newsletter content).

### Option 3: LinkedIn Official API
**URL:** https://developer.linkedin.com/

**What it can do (with approval):**
- Posts API — create/manage posts on your own profile or company page
- Member Post Analytics API (new in 2026) — detailed engagement data on your own posts
- Organisation API — manage company pages

**What it can't do (for most developers):**
- Feed API and Search API are restricted to approved LinkedIn partners only
- No way to search or read other people's posts programmatically via official channels

**Verdict:** Not viable for scanning expert posts unless Distl gets approved as a LinkedIn partner (unlikely and unnecessary).

### Option 4: Web Search Proxy (Already in the Workflow)
Use `site:linkedin.com/posts [expert name]` and `site:linkedin.com/pulse [topic]` via web search.

**What it can do:**
- Find public LinkedIn posts that have been indexed by search engines
- Works without any API key or authentication
- Catches high-engagement posts that tend to get indexed

**What it can't do:**
- Find posts that haven't been indexed (many aren't)
- Real-time scanning — there's a delay before posts get indexed
- Read comment threads
- Guarantee comprehensive coverage

## Custom Distl LinkedIn MCP Server — Build Spec

Since the existing open-source options don't cover what the Hivemind needs (especially post search and comment threads), we're building our own.

### Required MCP Tools

The server should expose these tools for Claude to call during scans:

#### Tool 1: `get_expert_posts`
**Purpose:** Pull recent posts from a specific expert by their LinkedIn profile URL or username.

**Input:**
```json
{
  "profile_url": "string — LinkedIn profile URL (e.g. linkedin.com/in/lily-ray-44755615)",
  "days_back": "number — How many days of posts to retrieve (default: 14)",
  "include_reposts": "boolean — Whether to include reshares/reposts (default: false)"
}
```

**Output:**
```json
{
  "expert_name": "Lily Ray",
  "headline": "VP, SEO Strategy & Research at Amsive",
  "posts": [
    {
      "date": "2026-03-25",
      "text": "Full post text content...",
      "post_url": "https://linkedin.com/posts/...",
      "likes": 342,
      "comments": 87,
      "shares": 45,
      "media_type": "text | image | video | article | carousel",
      "linked_url": "https://... (if they linked to an article/resource)",
      "is_repost": false
    }
  ]
}
```

**Why this matters:** This is the core tool. During a scan, Claude loops through the expert watchlist and pulls each person's recent posts. Without this, we're relying on web search indexing which misses ~30–40% of posts.

#### Tool 2: `search_posts`
**Purpose:** Search LinkedIn posts by keyword/topic to discover signals and new expert voices.

**Input:**
```json
{
  "query": "string — Search keywords (e.g. 'Google algorithm update', 'Meta ads creative')",
  "days_back": "number — How far back to search (default: 14)",
  "sort_by": "string — 'relevance' or 'date' (default: 'relevance')",
  "min_engagement": "number — Minimum total reactions to filter noise (default: 50)",
  "limit": "number — Max posts to return (default: 20)"
}
```

**Output:**
```json
{
  "query": "Google algorithm update",
  "results": [
    {
      "author_name": "Lily Ray",
      "author_headline": "VP, SEO Strategy & Research at Amsive",
      "author_profile_url": "https://linkedin.com/in/...",
      "date": "2026-03-25",
      "text": "Post text...",
      "post_url": "https://linkedin.com/posts/...",
      "likes": 342,
      "comments": 87,
      "shares": 45
    }
  ]
}
```

**Why this matters:** This is how we discover signals beyond our watchlist. We search by vertical topic and find who's saying what — including experts we haven't added to the watchlist yet.

#### Tool 3: `get_post_comments`
**Purpose:** Pull comment threads from a specific post. Comment threads often contain expert debates and counter-takes that are more valuable than the original post.

**Input:**
```json
{
  "post_url": "string — URL of the LinkedIn post",
  "limit": "number — Max comments to return (default: 30)",
  "sort_by": "string — 'relevance' or 'recent' (default: 'relevance')"
}
```

**Output:**
```json
{
  "post_url": "https://linkedin.com/posts/...",
  "comments": [
    {
      "author_name": "Kevin Indig",
      "author_headline": "Organic Growth Advisor",
      "author_profile_url": "https://linkedin.com/in/...",
      "text": "Comment text...",
      "likes": 23,
      "replies": [
        {
          "author_name": "Lily Ray",
          "text": "Reply text...",
          "likes": 12
        }
      ]
    }
  ]
}
```

**Why this matters:** When Lily Ray posts about an algorithm update and Kevin Indig disagrees in the comments — that's gold for the Hivemind. These debates surface nuance that no article captures.

#### Tool 4: `get_profile_summary` (Nice to Have)
**Purpose:** Quick profile check for new expert discovery — when we find someone posting great content, pull their profile to assess credibility.

**Input:**
```json
{
  "profile_url": "string — LinkedIn profile URL"
}
```

**Output:**
```json
{
  "name": "string",
  "headline": "string",
  "location": "string",
  "follower_count": "number",
  "current_role": "string",
  "company": "string",
  "about_summary": "string"
}
```

### Technical Considerations

**Browser automation approach (Patchright/Playwright):**
- Use persistent browser profiles to maintain login sessions
- Serialise requests (one at a time) to avoid detection
- Add random delays between requests (2–5 seconds)
- Handle captcha challenges gracefully — pause and notify user rather than crashing
- Session limit: ~50 requests per session before taking a break

**Rate limiting:**
- `get_expert_posts`: Max 40 per session (enough for the full watchlist across all verticals)
- `search_posts`: Max 10 per session (one or two per vertical)
- `get_post_comments`: Max 10 per session (only for high-value posts)
- Build in automatic cooldowns between batches

**Data freshness:**
- Consider caching results for 24 hours — if the same expert was scraped today, return cached data
- This reduces LinkedIn load and speeds up scans that span multiple verticals

**Error handling:**
- Captcha detected → pause, notify user, wait for manual resolution
- Rate limited → back off exponentially, retry after delay
- Profile not found → return empty result, don't crash
- Session expired → attempt re-login, notify user if it fails

### How It Integrates with the Scan

Once the MCP server is running, the scan tool's Step 1 (LinkedIn Expert Scan) changes from web search proxying to direct calls:

```
For each vertical being scanned:

1. EXPERT MONITORING (get_expert_posts)
   For each expert on the watchlist for this vertical:
   → Call get_expert_posts(profile_url, days_back=14)
   → For each post returned:
     - Apply Client Relevance Lens
     - If relevant, add to Signal Feed with Channel: "LinkedIn (direct)"
     - If post has 50+ comments, queue it for comment extraction

2. TOPIC DISCOVERY (search_posts)
   For the vertical's key topics:
   → Call search_posts(query="[vertical topic]", min_engagement=50)
   → For each result:
     - Check if author is already on watchlist
     - If not, assess if they should be added (get_profile_summary)
     - Apply Client Relevance Lens
     - If relevant, add to Signal Feed

3. DEBATE EXTRACTION (get_post_comments)
   For posts queued from step 1 with high comment counts:
   → Call get_post_comments(post_url, limit=30)
   → Look for:
     - Other watchlist experts commenting (expert-to-expert discourse)
     - Counter-arguments and disagreements
     - Data or case studies shared in comments
   → Add valuable comments as separate signals in the Signal Feed
```

### MCP Server Registration

Once built, register with Claude:
```bash
claude mcp add distl-linkedin -- [command to start your server]
```

The tools will then be available to Claude during any session where the MCP server is connected.
