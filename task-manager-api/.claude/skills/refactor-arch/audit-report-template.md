# Audit Report Template

This reference defines the standardized format for architecture audit reports generated during Phase 2.

---

## Report Format

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project:       <project directory name>
Stack:         <language> + <framework> <version>
Files:         <N> analyzed | ~<LOC> lines of code
Database:      <database type and storage mode>
Domain:        <application domain>

## Summary

| Severity | Count |
|---|---|
| CRITICAL | <n> |
| HIGH | <n> |
| MEDIUM | <n> |
| LOW | <n> |
| **Total** | **<sum>** |

## Findings

### [SEVERITY] Anti-Pattern Name

- **File:** `<path/to/file>:<line_number>` or `<path/to/file>:<start_line>-<end_line>`
- **Description:** <clear description of the problem found, including what code pattern was detected>
- **Impact:** <what happens if this is not fixed — security risk, maintainability issue, performance degradation, etc.>
- **Recommendation:** <specific, actionable fix — reference the playbook transformation name if applicable>

[... repeat for each finding ...]

================================
Total: <N> findings
================================
```

---

## Finding Field Specifications

### Severity

Must be one of:
- `[CRITICAL]` — Security vulnerabilities, exposed credentials, SQL injection, complete absence of auth
- `[HIGH]` — Strong MVC/SOLID violations, insecure storage, callback hell, significant code duplication
- `[MEDIUM]` — Performance issues, missing validation, dead code, inadequate error handling
- `[LOW]` — Readability issues, poor naming, magic numbers, unused imports

### File

Format: `<relative/path/to/file>:<line_number>` or `<relative/path/to/file>:<start_line>-<end_line>`

Examples:
- `app.py:8`
- `models.py:109-110`
- `src/AppManager.js:45`

Always use the path relative to the project root.

### Description

- State what the problematic code does
- Include the actual code snippet or pattern detected if helpful
- Be specific — avoid vague descriptions like "bad code" or "could be improved"
- Example: `"All SQL queries use string concatenation instead of parameterized queries. The login function at line 109 concatenates email and password directly into the WHERE clause."`

### Impact

- Describe the consequence of not fixing this issue
- Relate to security, maintainability, testability, performance, or reliability
- Example: `"Any user input can execute arbitrary SQL on the database. Classic security vulnerability allowing data exfiltration or destruction."`

### Recommendation

- Provide a specific, actionable fix
- Reference the playbook transformation name when applicable
- Example: `"Apply 'Parameterize Queries' transformation from the refactoring playbook. Replace string concatenation with parameterized queries using ? placeholders."`

---

## Ordering Rules

Findings MUST be ordered by:

1. **Primary sort:** Severity in descending order
   - CRITICAL first
   - Then HIGH
   - Then MEDIUM
   - Then LOW

2. **Secondary sort:** File path alphabetically within the same severity level
   - `app.py:8` before `models.py:28`
   - `src/AppManager.js:45` before `src/utils.js:3`

3. **Tertiary sort:** Line number ascending within the same file and severity
   - `app.py:8` before `app.py:59`

---

## Report Persistence

After generating the report:

1. Print the full report to output
2. Suggest saving to: `reports/audit-report.md` (or `reports/audit-project-{N}.md` with N inferred from the project directory name)
3. The `reports/` directory is at the repository root (parent of the project directory)
