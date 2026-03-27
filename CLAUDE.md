# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

This is a **team framework**. Multiple people use this repo, each running Claude Code locally on their own machine via the Claude desktop app. The repo contains shared instructions and logic. It never contains credentials, API keys, or anything sensitive.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## Credentials and Security

**This is critical. Read this section carefully.**

Credentials and API keys are **never stored in this repo**. They live locally on each team member's machine and are loaded from a `.env` file in the repo's root directory. That `.env` file is excluded from git via `.gitignore` and must never be committed.

**How credentials work:**
- Each team member creates their own `.env` file locally after cloning the repo
- The repo includes a `.env.example` file that lists every required variable name with placeholder values and comments explaining what each one is for
- Google OAuth files (`credentials.json`, `token.json`) also live locally and are gitignored
- MCP connectors (Google Drive, SharePoint, Ahrefs, Meta Ads, Figma, Monday, etc.) authenticate through the Claude desktop app settings per user. These don't need any config in the repo.

**What goes in `.env`:**
- API keys for services that aren't covered by an MCP connector
- Custom configuration values (base URLs, project IDs, etc.)
- Anything a tool script needs at runtime that shouldn't be shared

**What does NOT go in `.env` or anywhere in this repo:**
- Passwords
- OAuth tokens (these are generated locally per user)
- Client-specific data or credentials
- Anything you wouldn't want visible if the repo were accidentally made public

**The rule is simple: if you wouldn't put it on a whiteboard in the office, it doesn't go in the repo.**

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with the user before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behaviour)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking the user unless they explicitly tell you to. These are shared team instructions and need to be preserved and refined, not tossed after one use.

**4. Proposing workflow changes**
Because this repo is shared across the team, workflow changes should be intentional:
- Small fixes (typos, clarifying a step) can be committed directly
- Meaningful changes to how a workflow operates should be flagged to the user so they can decide whether to commit and push
- New workflows should be discussed before being added to the repo
- The user will handle git operations (committing, pushing, pulling). You help with the content.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time. When running locally, these improvements benefit the individual user immediately. Once committed and pushed, they benefit the whole team.

## File Structure

**What goes where:**
- **Deliverables**: Final outputs go to cloud services (Google Sheets, Google Docs, SharePoint, etc.) where the team can access them directly
- **Intermediates**: Temporary processing files that can be regenerated

**Directory layout:**
```
.tmp/               # Temporary files (scraped data, intermediate exports). Regenerated as needed. Gitignored.
tools/              # Scripts for deterministic execution
workflows/          # Markdown SOPs defining what to do and how
.env.example        # Template listing all required environment variables (committed to repo)
.env                # Actual API keys and config (LOCAL ONLY, never committed)
credentials.json    # Google OAuth credentials (LOCAL ONLY, never committed)
token.json          # Google OAuth token (LOCAL ONLY, never committed)
.gitignore          # Ensures sensitive and temporary files stay out of the repo
```

**Core principle:** Local files are just for processing. Anything the team needs to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Team Setup

**For the repo maintainer (first-time setup):**
1. Create the repo with the directory structure above
2. Add the `.gitignore` (template below)
3. Create `.env.example` with all required variable names and comments
4. Commit the framework files, workflows, and tools
5. Share the repo with team members who'll be using Claude Code

**For each team member (onboarding):**
1. Clone the repo to your local machine
2. Open the Claude desktop app
3. Copy `.env.example` to `.env` and fill in your own API keys
4. Set up your own Google OAuth credentials if needed (`credentials.json`, `token.json`)
5. Connect any MCP integrations you need (Google Drive, SharePoint, etc.) through the Claude desktop app settings
6. Pull from the repo before each session to get the latest workflows and tools

**`.gitignore` (minimum required):**
```
# Credentials and secrets
.env
credentials.json
token.json
*.pem
*.key

# Temporary and generated files
.tmp/
__pycache__/
*.pyc
node_modules/

# OS files
.DS_Store
Thumbs.db

# Local editor and IDE config
.vscode/
.idea/
```

## Bottom Line

You sit between what the user wants (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
