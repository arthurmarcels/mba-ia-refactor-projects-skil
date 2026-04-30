================================
ARCHITECTURE AUDIT REPORT
================================
Project:       ecommerce-api-legacy
Stack:         JavaScript + Express ^4.18.2
Files:         3 analyzed | ~183 lines of code
Database:      SQLite (in-memory)
Domain:        LMS API (cursos, matriculas, pagamentos)

## Summary

| Severity | Count |
|---|---|
| CRITICAL | 3 |
| HIGH | 4 |
| MEDIUM | 3 |
| LOW | 3 |
| **Total** | **13** |

## Findings

### [CRITICAL] C1. Hardcoded Secrets / Credentials

- **File:** `src/utils.js:1-7`
- **Description:** The `config` object contains production credentials as string literals: `dbUser: "admin_master"`, `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"`, `smtpUser: "no-reply@fullcycle.com.br"`. Additionally, `src/AppManager.js:45` logs the credit card number and payment gateway key via `console.log`.
- **Impact:** Anyone with access to source code obtains production database credentials and payment gateway keys. The console.log leaks PCI-sensitive data (credit card numbers) to logs. Violates PCI-DSS requirements.
- **Recommendation:** Apply "Extract Config" transformation. Move all secrets to environment variables using `process.env`. Remove `console.log` statements that leak sensitive data.

### [CRITICAL] C3. God Class / God Method

- **File:** `src/AppManager.js:1-142`
- **Description:** The `AppManager` class (142 lines) handles ALL responsibilities: database initialization and schema creation (lines 10-23), ALL route definitions (lines 25-138), ALL business logic (checkout flow, payment processing, financial reporting, user deletion). The class named `*Manager` is a classic God Class signal. It contains `db.run`/`db.all`/`db.get` AND `app.get`/`app.post`/`app.delete` AND complex business calculations in a single file.
- **Impact:** Impossible to test any business logic in isolation. Any change to one feature risks breaking all others. Violates Single Responsibility Principle. Debugging is extremely difficult.
- **Recommendation:** Apply "Decompose God Class" transformation. Split into separate modules: `models/` (DB access), `controllers/` (business logic), `routes/` (endpoint definitions), `middlewares/` (error handling, auth).

### [CRITICAL] C4. Broken or Missing Authentication

- **File:** `src/AppManager.js:25-138`
- **Description:** No authentication middleware exists anywhere in the project. All endpoints are completely open: `POST /api/checkout` (line 28), `GET /api/admin/financial-report` (line 80), `DELETE /api/users/:id` (line 131). The admin financial report endpoint exposes revenue and student data to anyone. The DELETE endpoint allows anyone to delete any user.
- **Impact:** All endpoints are completely open. Destructive operations (DELETE, admin functions) accessible by anyone. User and financial data exposed without authorization.
- **Recommendation:** Apply "Add Auth Middleware" transformation. Implement JWT-based authentication with proper token validation middleware. Protect admin endpoints with role-based access control.

### [HIGH] H1. Insecure Password Storage

- **File:** `src/utils.js:17-23`
- **Description:** The `badCrypto()` function creates a "hash" by base64-encoding the password 10,000 times and truncating to 10 characters. This is trivially reversible (base64 is encoding, not encryption) and uses no salt. Additionally, `src/AppManager.js:68` defaults to password `"123456"` if none is provided: `badCrypto(p || "123456")`. No `bcrypt` or equivalent exists in dependencies.
- **Impact:** Database leak exposes all user passwords immediately. Base64 "hashing" can be reversed in milliseconds. Identical passwords produce identical hashes (no salt). Default password "123456" weakens security further.
- **Recommendation:** Apply "Secure Password Storage" transformation. Use `bcrypt` for password hashing with automatic salt generation. Remove the default password fallback.

### [HIGH] H2. Business Logic in Route Handlers

- **File:** `src/AppManager.js:28-78`
- **Description:** The checkout route handler (~50 lines) contains: user lookup/creation, payment processing simulation, enrollment creation, audit logging, AND response formatting — all in a single route callback. The financial report handler (lines 80-128, ~49 lines) contains complex nested iteration, revenue calculation, AND response building. No controllers or services exist.
- **Impact:** Cannot test business logic without the HTTP layer. Changes to business rules require modifying route code. Violates separation of concerns entirely.
- **Recommendation:** Apply "Extract Service Layer" transformation. Move business logic to dedicated controller/service classes: `CheckoutController`, `ReportController`, `UserController`.

### [HIGH] H3. Callback Hell / Pyramid of Doom

- **File:** `src/AppManager.js:37-77`
- **Description:** The checkout route has 5 levels of nested callbacks: `db.get` → `db.get` → `db.run` → `db.run` → `db.run`. The financial report (lines 83-128) has 4 levels: `db.all` → `db.all` → `db.get` → `db.get`. Error handling is repeated at each nesting level with `if (err) return res.status(500).send(...)`.
- **Impact:** Extremely difficult to read, maintain, and debug. Error handling inconsistent between nesting levels. High cognitive load. Classic "Pyramid of Doom" anti-pattern.
- **Recommendation:** Apply "Flatten Callback Nesting" transformation. Convert SQLite operations to Promise-based wrappers and use async/await.

### [HIGH] H4. Duplicated Code

- **File:** `src/AppManager.js:41-70`
- **Description:** The error handling pattern `if (err) return res.status(500).send("Erro ...")` is repeated 6 times throughout the file (lines 38, 41, 51, 55, 70, 84) with nearly identical structure but different generic error messages ("Erro DB", "Erro Matrícula", "Erro Pagamento", "Erro ao criar usuário").
- **Impact:** Bug fixes in one error handler don't reflect in others. Inconsistent error response format. No structured error logging.
- **Recommendation:** Apply "DRY Extract" and "Centralize Error Handling" transformations. Extract a centralized error handling middleware that returns consistent error responses and logs errors properly.

### [MEDIUM] M1. N+1 Query Pattern

- **File:** `src/AppManager.js:89-127`
- **Description:** The financial report endpoint iterates over all courses (line 89), then for each course queries enrollments (line 92), then for each enrollment queries users (line 104) AND payments (line 106) individually. For N courses with M enrollments total, this generates 1 + N + 2M queries instead of a single JOIN query.
- **Impact:** Performance degrades linearly with data volume. 10 courses with 100 enrollments = 211 queries instead of 1-2. Will become unusable at scale.
- **Recommendation:** Apply "Batch Query Optimization" transformation. Replace nested loops with a single SQL JOIN query: `SELECT courses.*, users.name, payments.amount, payments.status FROM courses LEFT JOIN enrollments ON ... LEFT JOIN users ON ... LEFT JOIN payments ON ...`.

### [MEDIUM] M2. Missing Input Validation

- **File:** `src/AppManager.js:29-35`
- **Description:** The checkout endpoint only checks for null/undefined values (`!u || !e || !cid || !cc`). No type validation (email format, card number format/length, course ID as integer), no sanitization, no schema validation library. The DELETE endpoint (line 131) accepts any `:id` parameter without validating it's a valid number. No `joi`, `zod`, or `express-validator` in dependencies.
- **Impact:** Invalid or malicious data enters the system. Malformed emails, non-numeric IDs, and garbage card numbers are accepted. Can cause data corruption.
- **Recommendation:** Apply "Add Input Validation" transformation. Add input validation middleware using `joi` or `express-validator`. Validate email format, card number length, course ID type, etc.

### [MEDIUM] M3. Dead Code / Unused Modules

- **File:** `src/utils.js:9-10`
- **Description:** `globalCache` object (line 9) is written to by `logAndCache()` but never read by any code — the cache serves no purpose. `totalRevenue` (line 10) is exported and imported in `AppManager.js` but never modified or read anywhere in the application.
- **Impact:** Misleading — suggests caching and revenue tracking functionality that doesn't actually exist. Wastes cognitive load and AI context tokens.
- **Recommendation:** Apply "Remove Dead Code" transformation. Remove `totalRevenue` completely. Either implement actual caching with reads, or remove `globalCache` and `logAndCache()`.

### [LOW] L1. Magic Numbers / Debug in Production

- **File:** `src/AppManager.js:45-46`
- **Description:** Line 45: `console.log` in production code leaking credit card number and payment key. Line 46: `cc.startsWith("4")` uses magic string `"4"` to determine payment success (presumably Visa card detection). No named constant explains the business rule.
- **Impact:** Debug logs leak sensitive financial data in production. Magic string makes payment logic opaque — no explanation of why "4" means success.
- **Recommendation:** Extract the card prefix check into a named constant or function (e.g., `isVisaCard()`). Remove or guard `console.log` statements behind an environment-aware logger.

### [LOW] L2. Poor Variable Naming

- **File:** `src/AppManager.js:29-33`
- **Description:** Variables in the checkout handler use single-letter or cryptic abbreviations: `u` (username), `e` (email), `p` (password), `cid` (courseId), `cc` (cardNumber). Similarly, `c` (line 89) for course, `enr` for enrollment, `enrId` for enrollment ID.
- **Impact:** Very low readability. Impossible to understand variable purpose without tracing usage. Increases onboarding time and bug risk.
- **Recommendation:** Rename to descriptive names: `username`, `email`, `password`, `courseId`, `cardNumber`, `course`, `enrollment`, `enrollmentId`.

### [LOW] L3. Unused Imports

- **File:** `src/AppManager.js:2`
- **Description:** `totalRevenue` is destructured from `require('./utils')` but is never used anywhere in AppManager.js. The variable serves no purpose in this file.
- **Impact:** Increases cognitive load when reading imports. Suggests dependency that doesn't exist.
- **Recommendation:** Remove `totalRevenue` from the destructured import.

================================
Total: 13 findings
================================

> **Note:** Deprecated API detection (DP) was checked via context7 for Express 4.18.x. No deprecated APIs from Express 3.x→4.x migration (`app.configure()`, `app.del()`, `req.accepted()`) were found in this project's code.
