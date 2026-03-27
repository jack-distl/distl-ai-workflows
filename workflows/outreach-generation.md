# Outreach Draft Generation

## Objective
Generate personalised, insight-led outreach drafts for prospects that have been flagged with a digital signal. Every draft is based on a specific, real observation — never a generic pitch.

## Prerequisites
- Read `workflows/prospecting-crm-setup.md` for board ID and column IDs
- Board ID: `18405791744`

## When to run
- **Trigger:** User says "Generate outreach drafts" or "Draft outreach for flagged prospects"
- **Timing:** After signal checks have been completed and prospects are in the "Signal Detected" group

## Step 1: Get flagged prospects

Use `get_board_items_page` on board `18405791744`, filtered to the "Signal Detected" group (`group_mm1vmffs`).

For each prospect, extract:
- Company name (`name`)
- Website (`link_mm1v14np`)
- Industry Vertical (`dropdown_mm1vwtx4`)
- Signal Type (`color_mm1v81t6`)
- Signal Detail (`long_text_mm1vtebn`)
- Signal Date (`date_mm1vft14`)
- Notes (`long_text_mm1vxnza`) — check for prior outreach history

**Skip prospects that already have an Outreach Angle populated** (`long_text_mm1vc2h0`) — draft already exists.

## Step 2: Generate draft per signal type

### Paid/Organic Gap template

**Tone:** Helpful, data-driven, specific. Lead with the observation, not the pitch.

**Structure:**
1. Opening: Reference the specific finding (keywords, spend)
2. Insight: Explain what the gap means for their business
3. Credibility: Brief mention of relevant experience
4. CTA: Low-pressure — offer to share more detail, not book a meeting

**Example:**
```
Subject: Quick thought on your Google Ads for [keyword]

Hi [name],

I was looking at the search landscape for [industry] in Perth and noticed
[brand name] is running Google Ads for terms like "[keyword 1]" and
"[keyword 2]" — but isn't ranking organically for these same keywords.

That means every click is coming from paid spend. With targeted SEO, there's
a real opportunity to start capturing some of that traffic organically and
reduce your dependence on ads over time.

We've helped similar Perth ecommerce brands build organic rankings alongside
their paid campaigns — one reduced their ad spend by 30% while maintaining
the same traffic levels.

Happy to share what we've seen work for [industry] brands if it's useful.
No pressure either way.

[sign-off]
```

### SEEK Hiring template

**Tone:** Congratulatory, understanding, practical. Acknowledge the growth signal.

**Structure:**
1. Opening: Reference the specific role being hired
2. Insight: Acknowledge the challenge of finding good marketing talent
3. Offer: Position agency support as complementary, not competitive
4. CTA: Suggest a conversation, not a commitment

**Example:**
```
Subject: Saw you're hiring for marketing — quick thought

Hi [name],

I noticed [brand name] is hiring for a [role title] — congrats on the growth.

Finding the right person can take time, and in the meantime the marketing
work doesn't stop. We've worked with Perth ecommerce brands in similar
situations, either bridging the gap while recruiting or working alongside
a smaller in-house team to cover more ground.

If you're open to exploring what that could look like, happy to have a
quick chat. And if you've already found someone — even better, ignore me!

[sign-off]
```

### Complaint template

**Tone:** Empathetic, specific, solution-oriented. Never critical of the brand.

**Structure:**
1. Opening: Reference the specific issue customers are raising
2. Insight: Frame it as a common challenge, not a failure
3. Credibility: Mention a relevant fix or result
4. CTA: Offer to share specific recommendations

**Example:**
```
Subject: Customer feedback about [specific issue]

Hi [name],

I came across some customer feedback about [brand name] that mentioned
[specific issue — e.g., "slow page loading" or "difficulty finding products
on mobile"]. It's a really common challenge for growing ecommerce brands,
especially when the product range expands faster than the site can keep up.

We've helped similar brands tackle exactly this — [specific result,
e.g., "reducing page load time by 40%" or "redesigning product filtering
which lifted conversion by 15%"].

I've got a few specific ideas for [brand name] if you'd find that useful.
No obligation, just happy to share what we've seen work.

[sign-off]
```

## Step 3: Personalisation checklist

Before finalising each draft, verify:

- [ ] Company name is correct and consistently used
- [ ] Signal data is specific (actual keywords, actual role title, actual complaint quotes)
- [ ] Industry context is relevant (don't mention fashion examples for a food brand)
- [ ] Tone is helpful, not salesy
- [ ] CTA is low-pressure
- [ ] No claims about the prospect's business that aren't supported by the signal data
- [ ] Draft length is 100–150 words (concise, respectful of their time)

## Step 4: Write draft to Monday.com

For each generated draft, update the prospect item via `change_item_column_values`:
- `long_text_mm1vc2h0` (Outreach Angle): the full draft message

Do NOT update Outreach Date or Channel — that happens when the human actually sends it.

## Step 5: Present for review

Show the user all generated drafts with:
- Company name
- Signal type and key data point
- Full draft text
- Suggested channel (Email for detailed messages, LinkedIn for shorter ones)

**The user must approve each draft before it's sent.** Claude never sends outreach directly.

## Step 6: After user sends outreach

When the user confirms they've sent outreach, update the item:
- `date_mm1vtc85` (Outreach Date): date sent
- `color_mm1ve2hj` (Outreach Channel): channel used (Email, LinkedIn, Phone)
- `color_mm1vqxr1` (Response Status): set to "No Response" initially
- Move item to "Outreach Sent" group (`group_mm1vg0f8`)

## Guidelines

- **Never send the same angle twice:** If a prospect was previously contacted with the same signal type, don't generate a new draft for that signal
- **Freshness matters:** If the signal is more than 30 days old, suggest re-running the signal check before drafting
- **Quality over quantity:** Better to send 5 excellent, personalised messages than 20 generic ones
- **Human review is non-negotiable:** Every draft gets reviewed and potentially edited before sending
