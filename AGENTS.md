# AGENTS.md — mba-ia-refactor-projects-skill

## What this repo is

MBA challenge: create a Claude Code Skill (`refactor-arch`) that analyzes, audits, and refactors legacy projects to MVC. The skill must be tech-agnostic and work across 3 target projects with different stacks.

## Repository layout

```
code-smells-project/     # Project 1 — Python/Flask e-commerce API (monolithic, no layer separation)
ecommerce-api-legacy/    # Project 2 — Node.js/Express LMS API with checkout flow
task-manager-api/        # Project 3 — Python/Flask task manager (partial organization: models/, routes/, services/, utils/)
references/              # Pre-researched reference docs for skill construction (do not re-research)
reports/                 # Audit reports from Phase 2 execution (to be created)
```

## Target projects — how to run

- **Project 1** (Python/Flask): `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` → `python app.py`
- **Project 2** (Node.js/Express): `npm install` → `npm start`
- **Project 3** (Python/Flask): `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` → `python app.py`

All 3 use SQLite (file-based, auto-created). No external DB setup needed.

## Skill to create: `.claude/skills/refactor-arch/`

The skill must be created inside `code-smells-project/` first, then copied to the other two projects.

### Structure

```
.claude/skills/refactor-arch/
├── SKILL.md               # Mandatory — frontmatter (name + description) + 3-phase instructions
└── (reference .md files)  # Must cover ALL 5 knowledge areas below
```

### 5 mandatory knowledge areas for reference files

1. **Project analysis** — heuristics for detecting language, framework, DB, architecture
2. **Anti-patterns catalog** — min 8 patterns with detection signals and severity (CRITICAL/HIGH/MEDIUM/LOW); must include deprecated API detection
3. **Audit report template** — standardized format for Phase 2 output
4. **MVC architecture guidelines** — Models, Views/Routes, Controllers responsibilities
5. **Refactoring playbook** — min 8 transform patterns with before/after code examples

### 3-phase workflow (defined in SKILL.md)

| Phase | Action | Key rule |
|---|---|---|
| 1 — Analysis | Detect stack, map architecture, print summary | Must correctly identify language + framework + domain |
| 2 — Audit | Cross-reference code against anti-patterns catalog, generate report | **Must pause and ask for confirmation before Phase 3** |
| 3 — Refactoring | Restructure to MVC, validate app boots + endpoints respond | Non-destructive: original endpoints must keep working |

### SKILL.md frontmatter

```yaml
---
name: refactor-arch
description: Analyzes legacy codebases, generates architecture audit reports, and refactors to MVC pattern
---
```

The skill name `refactor-arch` and filename `SKILL.md` are fixed — do not rename.

## Acceptance criteria (all 3 projects, not just one)

- Phase 1 detects stack correctly (3/3)
- Phase 2 finds >= 5 findings per project (3/3)
- Phase 2 includes at least 1 CRITICAL or HIGH per project (3/3)
- Phase 3: app starts without errors + all original endpoints respond (3/3)

## How to invoke the skill

```bash
cd code-smells-project && claude "/refactor-arch"
cd ../ecommerce-api-legacy && claude "/refactor-arch"
cd ../task-manager-api && claude "/refactor-arch"
```

After Phase 2, save the audit report to `reports/audit-project-{1,2,3}.md`.

## Key constraints

- Skill must be **copy-paste portable** — same skill folder works in all 3 projects without modification
- Project 3 already has partial layer separation (`models/`, `routes/`, `services/`, `utils/`) — the skill must still find and fix problems, not assume it's fine
- Severity scale is defined in README.md "Definição de Severidades" — use it exactly
- References in `/references/` are already researched; use them to inform the skill, don't re-fetch URLs
- Expect 2–4 iterations to get the skill working across all 3 projects

## Validation after refactoring

For each project, verify:
1. App boots without errors
2. All original endpoints still respond
3. New structure follows MVC (config extracted, models/controllers/routes separated, error handling centralized, clear entry point)
4. No hardcoded credentials or secrets remaining
