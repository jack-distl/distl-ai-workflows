# Google Ads Monthly Reporting

## Objective

Generate a comprehensive monthly Google Ads performance report for a client. Automates data pulls via the Google Ads API and manages client briefs/reports through Google Drive. The specialist provides strategic context; everything else is handled by tools.

## Required Inputs

- **Client name** — used to locate brief and reports on Google Drive
- **Reporting month** — e.g. "2026-02" or "February 2026"
- **Customer ID** — Google Ads account ID (optional if set in .env)

## Prerequisites

Before first run:
1. Run `python tools/google_ads_auth_setup.py` to generate your Ads refresh token
2. Run `python tools/google_drive_auth_setup.py` to authenticate with Drive
3. Populate `.env` with all required variables (see `.env.example`)
4. Create the "Google Ads Reporting" root folder in Google Drive and set its ID in `.env`

> **Test Mode:** If `TEST_MODE=true` in `.env`, all Google Ads data tools load sample data from `.tmp/sample_data/`. Generate sample data first: `python tools/generate_sample_data.py --client-name "Test Client" --month 2026-02`

---

## Stage 1: Load Client Context

**Goal:** Retrieve the client's strategy brief and most recent report from Google Drive.

**Steps:**
1. Find the client's folder:
   ```
   python tools/gdrive_list_files.py --name-filter "{client_name}"
   ```
2. If found, download the brief:
   ```
   python tools/gdrive_read_file.py --file-name "brief.md" --folder-id {client_folder_id} --output-path .tmp/client_brief.md
   ```
3. Look for previous reports in the client's `reports/` subfolder:
   ```
   python tools/gdrive_list_files.py --folder-id {reports_folder_id}
   ```
4. If a previous report exists, download the most recent one:
   ```
   python tools/gdrive_read_file.py --file-id {latest_report_id} --output-path .tmp/previous_report.md
   ```

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

Save the brief locally to `.tmp/client_brief.md`, then upload:
```
python tools/gdrive_write_file.py --local-path .tmp/client_brief.md --drive-file-name "brief.md" --folder-id {client_folder_id}
```

**If brief needs updating:** Edit `.tmp/client_brief.md`, then update:
```
python tools/gdrive_write_file.py --local-path .tmp/client_brief.md --file-id {existing_brief_id}
```

---

## Stage 3: Pull Data + Gather Context

**Goal:** Get all performance data and understand what happened this month.

### Automated: Pull data from Google Ads

Calculate date ranges from the reporting month. Example for February 2026:
- Current: 2026-02-01 to 2026-02-28
- Comparison: 2026-01-01 to 2026-01-31

Run these tools (can run in parallel):
```
python tools/fetch_campaign_performance.py --start-date {current_start} --end-date {current_end} --compare-from {prev_start} --compare-to {prev_end}
python tools/fetch_search_terms.py --start-date {current_start} --end-date {current_end}
python tools/fetch_search_terms.py --start-date {prev_start} --end-date {prev_end} --output-file .tmp/search_terms_prev.csv
python tools/fetch_keyword_performance.py --start-date {current_start} --end-date {current_end}
python tools/fetch_change_history.py --start-date {current_start} --end-date {current_end}
```

### Automated: Review change history

Read `.tmp/change_history_summary_{dates}.md` and present to the specialist:
> "I detected these changes in the account this month: {summary}. Is this complete, or was there anything else?"

### Manual: Ask specialist for context not available in the API

- Any landing page changes?
- Seasonality, promotions, or competitor activity?
- Anything the client specifically requested?
- Are all conversion types weighted equally?

Skip questions where the brief or change history already provides the answer.

---

## Stage 4: Analyse

**Goal:** Read all data from `.tmp/` and produce analysis tied to the client's goals.

### Performance vs Goals
- Budget pacing: on track, underspend, overspend?
- CPA/ROAS vs target by campaign
- Conversion volume trend
- If off-track: why? (market size, competition, targeting, landing page, budget caps)
- If previous report available: continuation or new trend?

### Search Term Quality
Read `.tmp/search_terms_{dates}.csv`:
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

Save report to `.tmp/{client_name}_report_{month}.md`

---

## Stage 6: Store Report

**Goal:** Save the report to Google Drive and present for review.

1. Upload report:
   ```
   python tools/gdrive_write_file.py --local-path .tmp/{client_name}_report_{month}.md \
       --drive-file-name "{Client Name} - Google Ads Report - {Month Year}.md" \
       --folder-id {reports_folder_id}
   ```
2. Present the report text to the specialist for review
3. If revisions needed: make changes locally, re-upload using `--file-id` to update

---

## Stage 7: Update Brief (if needed)

If this month's reporting revealed changed goals, new KPIs, or strategic shifts:

1. Update `.tmp/client_brief.md` with new information
2. Re-upload:
   ```
   python tools/gdrive_write_file.py --local-path .tmp/client_brief.md --file-id {brief_file_id}
   ```

---

## Error Handling

| Error | Action |
|-------|--------|
| Auth expired | Re-run the relevant auth setup tool |
| API rate limit | Wait and retry. Test accounts: ~15,000 ops/day. Explorer access: 2,880/day. Monthly reporting is well within limits. |
| Empty data | Check if running against test account. Remind specialist about token access level. |
| Change history empty | Change Event API only covers 30 days. Note limitation and ask specialist for manual context. |
| Drive file not found | Confirm folder ID and file names. Offer to create new brief. |

## Edge Cases

- **First-time client:** No previous report. Skip trend comparison. Focus on baselines.
- **Mid-month report:** Adjust date ranges. Note partial data in report.
- **Multiple accounts for one client:** Run workflow once per account. Brief notes multi-account structure.

## Report Principles

1. **Goals-first** — every observation ties back to what the client is trying to achieve
2. **Search term scrutiny** — look at what's triggering ads, not just how they're performing
3. **Explain the why** — numbers need context to be useful
4. **Clear structure** — lead with status, then detail, then actions
5. **Honest assessment** — if it's underperforming, say so plainly
6. **Full cycle thinking** — if platform levers are exhausted, flag landing page/conversion path
