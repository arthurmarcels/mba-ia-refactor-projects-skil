---
name: refactor-arch
description: Analyzes legacy codebases, generates architecture audit reports, and refactors to MVC pattern. Use when the user invokes /refactor-arch or asks to analyze, audit, and refactor a project's architecture.
---

# refactor-arch

You are an architecture auditor and refactoring specialist. You will analyze the current project's codebase, identify anti-patterns and code smells, generate a structured audit report, and refactor the project to follow the MVC pattern — all without breaking existing functionality.

## Instructions

This skill executes in **3 sequential phases**. You MUST complete each phase before proceeding to the next.

Use **sequential-thinking** as your reasoning engine in every phase. Before producing any output, invoke `sequential-thinking` to reason through the steps systematically. This prevents jumping to conclusions and ensures thorough analysis.

---

## PHASE 1: Project Analysis

**Goal:** Detect the project's technology stack, map its current architecture, and print a formatted summary.

### Step 1.1 — Use sequential-thinking to plan analysis

Before reading any files, invoke sequential-thinking with the following prompt:

```
I need to analyze an unknown project in the current directory. I will:
1. First look for project configuration files (package.json, requirements.txt, etc.) to determine language and framework
2. Check for database configuration and ORM usage
3. Map the directory structure and file organization
4. Identify the application domain from model/route names
5. Classify the current architecture pattern

Let me think through what to look for in each step.
```

### Step 1.2 — Detect language and framework

Read the reference file `project-analysis.md` in this skill's directory for detailed heuristics, then:

1. List files in the project root to identify configuration files
2. Check for `requirements.txt` → Python, `package.json` → Node.js/JavaScript
3. Read imports in main source files to identify framework:
   - `from flask import` → Flask (extract version from requirements.txt)
   - `require('express')` or `require("express")` → Express (extract version from package.json)
4. Confirm by examining additional source files

### Step 1.3 — Detect database

1. Search for database imports: `sqlite3`, `sqlalchemy`, `mongoose`, `prisma`
2. Look for connection strings or database file references (`.db`, `.sqlite`, `:memory:`)
3. Identify ORM vs raw SQL usage

### Step 1.4 — Map architecture

1. List all source files and directory structure
2. Count lines of code per file
3. Classify architecture using these categories:
   - **Monolithic** — 2-4 files in root, no layer separation
   - **God Class** — 1 dominant file handling everything (routes, DB, business logic)
   - **Partially Organized** — has directories like `models/`, `routes/` but poor separation of responsibilities
   - **MVC** — proper separation with config, models, routes/controllers, middlewares

### Step 1.5 — Detect application domain

1. Examine model/table names and route endpoints
2. Map vocabulary to a domain (e-commerce, LMS, task manager, etc.)

### Step 1.6 — Print formatted summary

Use sequential-thinking to synthesize all findings, then print:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language>
Framework:     <framework> <version>
Dependencies:  <list key deps>
Domain:        <application domain>
Architecture:  <classification>
Source files:  <N> files analyzed
DB tables:     <list tables or schemas>
================================
```

---

## PHASE 2: Architecture Audit

**Goal:** Cross-reference the codebase against the anti-patterns catalog, generate a structured audit report, and **pause for user confirmation** before Phase 3.

### Step 2.1 — Use sequential-thinking to plan audit

Invoke sequential-thinking with:

```
I have detected the project stack: [insert results from Phase 1].
Now I need to audit the codebase against the anti-patterns catalog.
For each anti-pattern in the catalog, I will:
1. Check if the detection signals are present in the source files
2. Record exact file paths and line numbers
3. Classify severity according to the catalog
4. Only include patterns applicable to the detected stack

Let me think through which patterns are relevant for [Python/Flask | Node.js/Express].
```

### Step 2.2 — Load reference files

Read the following files from this skill's directory:
- `anti-patterns-catalog.md` — for detection signals and severity levels
- `audit-report-template.md` — for report formatting

### Step 2.3 — Execute anti-pattern scan

For each source file in the project:

1. Use sequential-thinking to reason about each anti-pattern's applicability
2. Search for detection signals listed in the catalog
3. For each finding, record:
   - Severity (CRITICAL / HIGH / MEDIUM / LOW)
   - Anti-pattern name
   - File path and line number(s)
   - Description of the problem
   - Impact
   - Recommendation

### Step 2.4 — Check for deprecated APIs via context7

After identifying the framework and version in Phase 1:

1. Call `resolve-library-id` with the framework name (e.g., "Flask" or "Express")
2. Call `query-docs` with the resolved library ID, asking: "What APIs are deprecated in [framework version]? List deprecated methods, functions, or patterns with their modern replacements."
3. If deprecated APIs are found in the project's code, add them as findings with severity HIGH

If context7 is unavailable or returns no results, skip this step and note it in the report.

### Step 2.5 — Generate audit report

Format the report following `audit-report-template.md` exactly:

1. Header with project name, stack, files analyzed, LOC
2. Summary section with counts per severity
3. Findings section sorted by severity (CRITICAL → HIGH → MEDIUM → LOW), then by file within each severity
4. Total findings count

### Step 2.6 — Present report and pause

Print the full audit report to output.

Then **STOP and ask the user:**

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**Do NOT proceed to Phase 3 without explicit user confirmation.** This is a mandatory gate.

Also suggest saving the report to `reports/audit-project-{N}.md` (where N is the project number).

---

## PHASE 3: Refactoring to MVC

**Goal:** Restructure the project to follow the MVC pattern while keeping all original endpoints working.

### Step 3.1 — Use sequential-thinking to plan refactoring

Invoke sequential-thinking with:

```
I have completed the audit with [N] findings. The project uses [stack].
The current architecture is [classification from Phase 1].

I need to refactor to MVC. Let me plan the transformations:
1. Which anti-patterns need fixing? (List each finding)
2. Which transformations from the playbook apply? (Map each finding to a playbook pattern)
3. What should the new directory structure look like?
4. What is the order of operations to avoid breaking things?
5. How will I validate that everything still works?

Key constraint: All original endpoints MUST keep working after refactoring.
```

### Step 3.2 — Load reference files

Read the following files from this skill's directory:
- `mvc-guidelines.md` — for target architecture rules
- `refactoring-playbook.md` — for transformation patterns with code examples

### Step 3.3 — Execute transformations

For each anti-pattern identified in the audit, apply the corresponding transformation from the playbook:

1. Read the transformation's before/after examples in the playbook
2. Apply the transformation to the project code
3. Keep changes minimal and focused — fix one anti-pattern at a time

**Order of transformations (recommended):**
1. Extract Config (remove hardcoded credentials first)
2. Decompose God Class (split monolithic files)
3. Parameterize Queries (fix SQL injection)
4. Secure Password Storage (fix weak hashing)
5. Add Auth Middleware (add real authentication)
6. Extract Service Layer (separate business logic)
7. Flatten Callback Nesting (for Node.js projects)
8. DRY Extract (remove duplicated code)
9. Batch Query Optimization (fix N+1 queries)
10. Add Input Validation (add missing validation)
11. Centralize Error Handling (replace bare excepts)
12. Remove Dead Code (clean up unused code)

### Step 3.4 — Validate refactoring

After all transformations are applied:

1. **Structure check:** Verify the project now has:
   - `config/` or `config.py` — configuration module reading from env vars
   - `models/` — data models with DB access only
   - `routes/` — endpoint definitions delegating to controllers
   - `controllers/` — orchestration logic
   - `middlewares/` — error handling and auth
   - Clear entry point (app.py or equivalent)

2. **Boot check:** Start the application and verify it starts without errors:
   - Python/Flask: `python app.py`
   - Node.js/Express: `npm start`

3. **Endpoint check:** Test all original endpoints respond correctly:
   - List all endpoints that existed before refactoring
   - Make a request to each endpoint and verify response

### Step 3.5 — Print results

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
[print directory tree]

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ [N] anti-patterns fixed
  ✓ Zero hardcoded credentials remaining
================================
```

If validation fails, use sequential-thinking to diagnose the issue, fix it, and re-validate. Do not report success until the application actually starts and endpoints respond.
