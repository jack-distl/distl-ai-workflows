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

## Recommended Approach

### Phase 1: Now (No Build Required)
Use **Option 4 (web search proxy)** + **team LinkedIn drops** (human curation).

This is already built into the workflow. The team follows experts on LinkedIn, flags good posts to Claude via "add this to the hivemind", and Claude processes them. Web search with `site:linkedin.com` catches the high-engagement posts that get indexed.

**This covers ~60–70% of expert LinkedIn output.**

### Phase 2: Quick Win (Minimal Build)
Add **Option 1 (stickerdaniel/linkedin-mcp-server)** as an MCP connector.

This lets Claude directly scrape each expert's profile and pull their recent posts during a scan. Instead of hoping web search indexed the post, we go straight to the source.

**Setup steps:**
1. Install the MCP server: `uvx linkedin-scraper-mcp`
2. Log in with a Distl LinkedIn account: `uvx linkedin-scraper-mcp --login`
3. Add to Claude: `claude mcp add linkedin-mcp-server -- uvx linkedin-scraper-mcp`
4. Update the scan tool to use `get_person_profile` with `posts` section for each expert

**This covers ~80–85% of expert LinkedIn output.** The gap is keyword-based discovery (finding new experts) and comment thread analysis.

### Phase 3: Custom Build (If Needed)
Build a custom LinkedIn scraping tool that can:
- Search LinkedIn posts by keyword/topic
- Pull comment threads from high-engagement posts
- Discover new expert voices based on engagement patterns
- Run on a schedule and cache results

**Technical approach:**
- Use Patchright or Playwright for browser automation (same approach as stickerdaniel's server)
- Authenticate with a LinkedIn account
- Build specific scraping functions:
  - `search_posts(keyword, timeframe)` — Search LinkedIn's post search
  - `get_post_comments(post_url)` — Pull comment threads
  - `get_feed_posts(topic)` — Browse topic-filtered feeds
  - `discover_experts(keyword, min_engagement)` — Find high-engagement posters on a topic
- Wrap as an MCP server so Claude can call it during scans
- Add rate limiting and session management to avoid LinkedIn blocks

**Important considerations:**
- LinkedIn actively fights scraping — expect captchas and blocks
- Use delays between requests (2–5 seconds minimum)
- Don't run more than ~50 profile scrapes per session
- Rotate sessions or use persistent browser profiles
- This approach is against LinkedIn's ToS — use at your own risk and keep volumes reasonable

**This would cover ~95% of expert LinkedIn output.** The remaining 5% is LinkedIn-only content that requires being logged in and scrolling (which is where team drops fill the gap).

## Recommendation

**Start with Phase 2.** The stickerdaniel MCP server is a 10-minute setup, gives you direct access to expert posts, and doesn't require building anything. Run it alongside the web search proxy and team drops.

Only move to Phase 3 if you find that Phases 1+2 aren't surfacing enough expert content — and even then, the custom build should be focused on the specific gaps (post search and comment threads), not a full LinkedIn scraper.

## Updating the Scan Tool

Once a LinkedIn MCP connector is installed, update the scan procedure:

**During Step 1 (LinkedIn Expert Scan):**
```
For each expert in the watchlist for the vertical:
1. Call get_person_profile(linkedin_url, sections=["posts"]) via MCP
2. Extract their recent posts (last 14 days)
3. For each post, capture:
   - The post text (their actual words)
   - Engagement metrics (likes, comments, shares)
   - Date posted
   - Any links or media shared
4. Apply the Client Relevance Lens
5. Log relevant signals to the Signal Feed
```

This replaces the `site:linkedin.com` web search for known experts (keep web search for discovery of new voices).
