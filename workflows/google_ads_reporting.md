# Google Ads Monthly Reporting

## Objective

Generate a comprehensive monthly Google Ads performance report for a client. Data is pulled automatically via MCP tools (Google Ads API + Google Drive). The specialist provides strategic context; everything else is handled by the system.

## Required Inputs

- **Client name** — used to locate brief and reports on Google Drive
- **Reporting month** — e.g. "2026-02" or "February 2026"
- **Customer ID** — Google Ads account ID (ask specialist if unknown; use `google_ads_list_accounts` to look up)

## How It Works

This workflow uses MCP tools that connect to Google Ads and Google Drive through a secure server. All API credentials are held server-side — they never appear in the Claude Code session. The tools are:

**Google Ads tools:**
- `google_ads_list_accounts` — list accounts under the MCC
- `google_ads_campaign_performance` — campaign metrics
- `google_ads_search_terms` — search terms + coverage %
- `google_ads_keyword_performance` — keyword metrics + quality scores
- `google_ads_change_history` — what changed in the account

**Google Drive tools:**
- `drive_read_brief` — read client strategy brief
- `drive_save_brief` — save/update brief
- `drive_get_latest_report` — read most recent report
- `drive_save_report` — save monthly report

---

## Stage 1: Load Client Context

**Goal:** Retrieve the client's strategy brief and most recent report from Google Drive.

**Steps:**
1. Read the client brief:
   - Use the `drive_read_brief` tool with the client name
2. Read the most recent previous report:
   - Use the `drive_get_latest_report` tool with the client name

**If no brief exists:** Proceed to Stage 2 to create one.
**If no previous report:** Skip trend comparison context — establish baselines this month.

---

## Stage 2: Confirm Strategy Brief

**Goal:** Ensure the brief is current before analysing data against it.

**If brief exists:**
Present the brief to the specialist:
> "For {Client}, I have the following on file:
> - Offering: {X}
> - Goal: {Y} leads at under ${Z} CPA
> - Budget: ${X}/month
> - {Other context}
>
> I also found {previous report summary / no previous report}.
> Is this still accurate, or has anything changed?"

**If brief doesn't exist:** Gather from the specialist:
- What does the client sell/offer?
- Who are they trying to reach?
- Primary goal (leads, sales, bookings)
- Target CPA or ROAS
- Monthly budget
- Geographic focus
- Known no-go areas

Save the brief using `drive_save_brief` with the client name and full brief text.

**If brief needs updating:** Edit the brief content and use `drive_save_brief` to update.

---

## Stage 3: Pull Data + Gather Context

**Goal:** Get all performance data and understand what happened this month.

### Automated: Pull data from Google Ads

Calculate date ranges from the reporting month. Example for February 2026:
- Current: 2026-02-01 to 2026-02-28
- Comparison: 2026-01-01 to 2026-01-31

Use these MCP tools (can be called in sequence):
1. `google_ads_change_history` — with customer_id, current start/end dates
2. `google_ads_campaign_performance` — with customer_id, current start/end dates
3. `google_ads_campaign_performance` — with customer_id, comparison start/end dates (for MoM comparison)
4. `google_ads_search_terms` — with customer_id, current start/end dates
5. `google_ads_keyword_performance` — with customer_id, current start/end dates

### Automated: Review change history

Present the change history results to the specialist:
> "I detected these changes in the account this month: {summary}. Is this complete, or was there anything else?"

### Manual: Ask specialist for context not available in the API

- Any landing page changes?
- Seasonality, promotions, or competitor activity?
- Anything the client specifically requested?
- Are all conversion types weighted equally?

Skip questions where the brief or change history already provides the answer.

---

## Stage 4: Analyse

**Goal:** Analyse all pulled data and produce insights tied to the client's goals.

### Performance vs Goals
- Budget pacing: on track, underspend, overspend?
- CPA/ROAS vs target by campaign
- Conversion volume trend
- If off-track: why? (market size, competition, targeting, landing page, budget caps)
- If previous report available: continuation or new trend?

### Search Term Quality
From the search terms data:
- High-converting terms (winners to protect/expand)
- Spending without converting (flag for review/negative)
- Irrelevant queries or competitor brand leakage
- Note the search term coverage % — if low, flag that significant data is hidden by Google

### Impression Share & Efficiency
From campaign data:
- Are we capturing available demand?
- Lost to budget vs lost to rank
- CPC trends vs previous period

### Changes → Outcomes
Cross-reference change history with performance shifts:
- Did budget increases lead to more volume?
- Did bid strategy changes improve CPA?
- Any unexplained shifts?
- If previous report exists: were last month's recommendations actioned? What resulted?

### Conversion Path Check
- High-intent terms not converting = potential landing page issue
- If in-platform levers exhausted, flag for landing page review

---

## Stage 5: Generate Report

**Goal:** Produce a structured text report that answers core business questions.

### Report Structure

```
# {Client Name} — Google Ads Report — {Month Year}

## 1. Are We On Track?
- Spend vs budget
- CPA vs target
- Trend direction (improving, declining, stable)
- If no: why not, what can we fix vs what's outside our control
- If yes: opportunities to improve further or scale

## 2. Key Metrics Overview
| Metric | This Month | Last Month | Change |
|--------|-----------|------------|--------|
(impressions, clicks, CTR, cost, CPC, conversions, CPA, conv rate, impression share)

## 3. Campaign Performance
(Table + commentary per campaign)

## 4. What We Changed & Impact
(From change history + specialist context)
(What changed, when, and what resulted)

## 5. Search Term Insights
- Terms to add as negatives (with rationale)
- Terms to consider pausing (with spend, conversions, rationale)
- Terms worth expanding
- Coverage note if significant data is hidden

## 6. Impression Share Analysis
- Where we're losing share
- Budget vs rank attribution
- Opportunities to capture more demand

## 7. Recommendations for Next Month
(Specific, actionable, tied to data)

## 8. Internal Notes (Specialist Only)
- Context that shouldn't go to client but matters for continuity
- Flags for next month
- Things to watch
```

---

## Stage 6: Store Report

**Goal:** Save the report to Google Drive and present for review.

1. Save the report using `drive_save_report` with client name, month, and report content
2. Present the report text to the specialist for review
3. If revisions needed: make changes and use `drive_save_report` again to update

---

## Stage 7: Update Brief (if needed)

If this month's reporting revealed changed goals, new KPIs, or strategic shifts:
- Update the brief content and use `drive_save_brief` to save

---

## Error Handling

| Error | Action |
|-------|--------|
| MCP tool returns error | Read the error message. Most will be auth or configuration issues on the server side — inform the specialist and ask them to check with the admin. |
| Empty data | Check if running against a test account. Remind specialist about token access level. |
| Change history empty | Change Event API only covers 30 days. Note limitation and ask specialist for manual context. |
| No client folder on Drive | The tools will create it automatically when saving the first brief or report. |

## Edge Cases

- **First-time client:** No previous report. Skip trend comparison. Focus on baselines.
- **Mid-month report:** Adjust date ranges. Note partial data in report.
- **Multiple accounts for one client:** Run workflow once per account. Brief notes multi-account structure.
- **Unknown customer ID:** Use `google_ads_list_accounts` to look up accounts.

## Report Principles

1. **Goals-first** — every observation ties back to what the client is trying to achieve
2. **Search term scrutiny** — look at what's triggering ads, not just how they're performing
3. **Explain the why** — numbers need context to be useful
4. **Clear structure** — lead with status, then detail, then actions
5. **Honest assessment** — if it's underperforming, say so plainly
6. **Full cycle thinking** — if platform levers are exhausted, flag landing page/conversion path
