# Prospecting CRM Setup — Monday.com Board

## Objective
Maintain the "Ecommerce Prospecting" board in Monday.com as the single source of truth for all Perth ecommerce prospect data, signal results, and outreach tracking.

## Board location
- **Workspace:** Sales & CRM (ID: `172993`)
- **Board:** Ecommerce Prospecting (ID: `18405791744`)
- **URL:** https://distl.monday.com/boards/18405791744

## Groups (pipeline stages)

| Group | ID | Purpose | Colour |
|---|---|---|---|
| New Prospects | `group_mm1vgcvz` | Uncontacted prospects. Default group for new items. | Blue |
| Signal Detected | `group_mm1vmffs` | Prospect has an actionable signal — ready for outreach draft. | Orange |
| Outreach Sent | `group_mm1vg0f8` | Outreach has been sent, awaiting response. | Purple |
| Responded | `group_mm1vcdme` | Prospect has responded (positive or negative). | Green |
| Not a Fit | `group_mm1vn0ay` | Disqualified or not a match for Distl's services. | Grey |

## Column reference

| Column | ID | Type | Values |
|---|---|---|---|
| Company Name | `name` | name | Free text |
| Website | `link_mm1v14np` | link | URL + display text |
| LinkedIn URL | `link_mm1vga4f` | link | URL + display text |
| Industry Vertical | `dropdown_mm1vwtx4` | dropdown | Fashion (1), Home (2), Sport (3), Food (4), Beauty (5), Health (6), Other (7) |
| Est. Team Size | `numeric_mm1v5s2` | numbers | Integer |
| Marketing Team Size | `numeric_mm1v4cs0` | numbers | Integer |
| Date Added | `date_mm1vzg53` | date | YYYY-MM-DD |
| Source | `color_mm1vdstv` | status | WebSearch (7), LinkedIn (4), Directory (6), Referral (9) |
| Signal Type | `color_mm1v81t6` | status | None (17), Paid/Organic Gap (7), SEEK Hiring (4), Complaint (2) |
| Signal Detail | `long_text_mm1vtebn` | long_text | Free text summary of signal findings |
| Signal Date | `date_mm1vft14` | date | YYYY-MM-DD |
| Outreach Angle | `long_text_mm1vc2h0` | long_text | Draft outreach message |
| Outreach Date | `date_mm1vtc85` | date | YYYY-MM-DD |
| Outreach Channel | `color_mm1ve2hj` | status | Email (7), LinkedIn (4), Phone (6) |
| Response Status | `color_mm1vqxr1` | status | No Response (17), Positive (1), Negative (2), Meeting Booked (7) |
| Notes | `long_text_mm1vxnza` | long_text | Free-form notes |
| Last Checked | `date_mm1vpbs9` | date | YYYY-MM-DD |

## How to add a prospect

Use `create_item` with board ID `18405791744`. Items default to the "New Prospects" group.

Example column values:
```json
{
  "link_mm1v14np": {"url": "https://example.com.au", "text": "example.com.au"},
  "link_mm1vga4f": {"url": "https://linkedin.com/company/example", "text": "Example LinkedIn"},
  "dropdown_mm1vwtx4": "Fashion",
  "numeric_mm1v5s2": "25",
  "numeric_mm1v4cs0": "2",
  "date_mm1vzg53": {"date": "2026-03-27"},
  "color_mm1vdstv": {"label": "WebSearch"},
  "color_mm1v81t6": {"label": "None"}
}
```

## How to update a prospect with signal data

Use `change_item_column_values` with the item ID and:
```json
{
  "color_mm1v81t6": {"label": "Paid/Organic Gap"},
  "long_text_mm1vtebn": {"text": "Bidding on 8 keywords with no organic ranking. Top gaps: 'perth activewear', 'gym clothes perth', 'workout gear australia'."},
  "date_mm1vft14": {"date": "2026-03-27"},
  "date_mm1vpbs9": {"date": "2026-03-27"}
}
```

Then move the item to "Signal Detected" group (`group_mm1vmffs`) using `move_object`.

## How to check for duplicates (dedup)

Before adding a new prospect or flagging for outreach, use `board_insights` to check:

1. **Check if company already exists:**
   - Filter by `name` column using `contains_text` operator with the company name

2. **Check if signal already used:**
   - Filter by `color_mm1v81t6` (Signal Type) to see what signal was last used
   - Filter by `color_mm1vqxr1` (Response Status) to check outreach history

3. **Rules:**
   - Never add a duplicate company (same domain)
   - Never flag the same signal type twice for the same company
   - Never move a prospect back to "Signal Detected" if they're in "Responded" or "Not a Fit"
   - If a new, different signal is found for an existing prospect, update Signal Type and Detail but note the prior signal in Notes

## Maintenance

- **Archive stale prospects:** If a prospect has been in "Outreach Sent" for 60+ days with "No Response", consider moving to "Not a Fit"
- **Board limits:** Monday.com board limit is 10,000 items. Current count can be checked via `get_board_info`
- **Column changes:** If new columns are needed, update this workflow document with the new column IDs after creation
