# Anti-Patterns Catalog

This reference contains the catalog of anti-patterns used for code auditing in Phase 2. Each anti-pattern includes specific detection signals, severity, and applicable stacks.

---

## Severity Scale

- **CRITICAL:** Security vulnerabilities, exposed credentials, complete architectural breakdown, or complete absence of authentication
- **HIGH:** Strong violations of MVC/SOLID, insecure data storage, significant maintainability issues
- **MEDIUM:** Performance bottlenecks, missing validation, dead code, inadequate error handling
- **LOW:** Readability issues, naming problems, minor code quality concerns

---

## CRITICAL Patterns

### C1. Hardcoded Secrets / Credentials

**Severity:** CRITICAL

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- Variable assignment with string literal containing `secret`, `password`, `key`, `token` in the name: `SECRET_KEY = "..."`, `API_KEY = "..."`, `dbPass = "..."`
- Hardcoded database passwords in connection strings
- Payment gateway keys, SMTP passwords, or API tokens as string literals
- Credentials appearing in `console.log()`, `print()`, or endpoint responses
- `.env` file committed to version control with real values

**Specific patterns to search for:**
- Python: `SECRET_KEY = '` or `SECRET_KEY = "` (not reading from `os.environ`)
- Python: `password = '` or `email_password = '`
- JavaScript: `password: "..."` or `key: "..."` in config objects
- JavaScript: `console.log(...)` containing credit card numbers, keys, or passwords

**Impact:** Anyone with access to source code or certain endpoints obtains production credentials. Violates security best practices and compliance requirements (PCI-DSS for payment data).

**Recommendation:** Apply "Extract Config" transformation. Move all secrets to environment variables using `os.environ.get()` (Python) or `process.env` (Node.js).

---

### C2. SQL Injection

**Severity:** CRITICAL

**Applicable stacks:** Python/Flask (with raw SQL), Node.js/Express (with raw sqlite3)

**Detection signals:**
- String concatenation in SQL queries: `"SELECT * FROM " + table_name`
- f-strings with variables in SQL: `f"SELECT * FROM users WHERE id = {user_id}"`
- Variable interpolation in SQL WHERE clauses: `"WHERE email = '" + email + "'"`
- Direct insertion of request parameters into SQL strings

**Specific patterns to search for:**
- Python: `"SELECT ... " + str(id)`, `f"SELECT ... {variable}"`, `"WHERE ... '" + input_var + "'"`
- JavaScript: `"SELECT ... " + id`, `` `SELECT ... ${variable}` ``

**Impact:** Any user input can execute arbitrary SQL on the database. Enables data exfiltration, data destruction, or privilege escalation.

**Recommendation:** Apply "Parameterize Queries" transformation. Replace all string concatenation with parameterized queries using `?` placeholders and separate parameter arguments.

---

### C3. God Class / God Method

**Severity:** CRITICAL

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- Single source file > 200 lines handling multiple domains (users, products, orders, etc.)
- A class/module responsible for: database initialization, schema creation, route handling, AND business logic
- Methods/functions > 50 lines with multiple levels of nesting
- File contains both `SELECT/INSERT` statements AND HTTP route definitions AND business logic

**Specific patterns to search for:**
- Python: A `.py` file with > 200 lines that has both `@app.route` or `app.add_url_rule` AND `cursor.execute` AND complex business logic
- JavaScript: A `.js` file with > 100 lines containing both `app.get`/`app.post` AND `db.run`/`db.all` AND business calculations
- A class named `*Manager` or `*Handler` that does everything

**Impact:** Impossible to test in isolation. Any change affects the entire file. Violates Single Responsibility Principle. Mixing concerns makes debugging extremely difficult.

**Recommendation:** Apply "Decompose God Class" transformation. Split into separate models, controllers, and routes by domain.

---

### C4. Broken or Missing Authentication

**Severity:** CRITICAL

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- No authentication middleware, decorator, or token validation
- Login endpoint returns fake tokens: `return 'fake-jwt-token-' + str(user.id)`
- Password comparison in plaintext: `"WHERE email = ... AND senha = ..."`
- Admin endpoints without any access control: `/admin/*` routes with no auth check
- Token exists but is never validated on subsequent requests

**Specific patterns to search for:**
- Python: No `@login_required` decorator, no `jwt_required`, `fake-jwt-token` string
- Python: `SELECT ... WHERE email = ... AND senha = ...` (password in query)
- JavaScript: No auth middleware in route chain, fake token generation
- Endpoints named `/admin/*` with no middleware or authorization check

**Impact:** All endpoints are completely open. Destructive operations (DELETE, admin functions) accessible by anyone. User data exposed without authorization.

**Recommendation:** Apply "Add Auth Middleware" transformation. Implement JWT-based authentication with proper token validation middleware.

---

## HIGH Patterns

### H1. Insecure Password Storage

**Severity:** HIGH

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- Passwords stored in plaintext in the database
- MD5 hashing without salt: `hashlib.md5(password.encode())`
- Base64 encoding used as "encryption": `base64.b64encode(password.encode())`
- SHA1 without salt: `hashlib.sha1(password.encode())`
- Custom "encryption" functions that are trivially reversible
- bcrypt or argon2 NOT present in dependencies

**Specific patterns to search for:**
- Python: `hashlib.md5(`, `hashlib.sha1(`, `base64.b64encode(` used for passwords
- Python: Storing/comparing password as plaintext string
- JavaScript: Custom hash functions, simple encoding schemes
- No `bcrypt`, `argon2`, `werkzeug.security`, or equivalent in dependencies

**Impact:** Database leak exposes all user passwords. Weak hashing can be cracked via rainbow tables in seconds. Base64 is encoding, not encryption.

**Recommendation:** Apply "Secure Password Storage" transformation. Use bcrypt or argon2 for password hashing with automatic salt generation.

---

### H2. Business Logic in Route Handlers

**Severity:** HIGH

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- Route handler functions > 20 lines containing validation, computation, AND response formatting
- Route files that directly execute SQL queries instead of calling a model/service
- Validation rules (field length, allowed values) inside route handlers instead of models
- Complex if/else chains or calculations within route handlers
- Route files with the same or more lines than model files

**Specific patterns to search for:**
- Python: Route handler with `len(data['name']) >` validation, `cursor.execute()` calls, and response formatting all in the same function
- JavaScript: Route handler with validation checks, `db.run()` calls, and response building in the same callback
- Route files with > 100 lines

**Impact:** Cannot test business logic without HTTP layer. Changes to business rules require modifying route code. Violates separation of concerns.

**Recommendation:** Apply "Extract Service Layer" transformation. Move business logic to dedicated service/controller classes.

---

### H3. Callback Hell / Pyramid of Doom

**Severity:** HIGH

**Applicable stacks:** Node.js/Express (primarily)

**Detection signals:**
- 3+ levels of nested callbacks: `db.get(function(err, result1) { db.run(function(err, result2) { db.all(function(err, result3) { ... }) }) })`
- Closing brackets `})})})` stacked at the end of functions
- Error handling repeated at each nesting level
- Arrow functions or anonymous callbacks nested more than 3 levels deep

**Specific patterns to search for:**
- JavaScript: Count nesting levels of `function(err,` or `(err,` callbacks
- JavaScript: Multiple `});` stacked at function end (pyramid shape)
- Functions where the callback nesting exceeds the visible width

**Impact:** Extremely difficult to read, maintain, and debug. Error handling inconsistent between nesting levels. High cognitive load.

**Recommendation:** Apply "Flatten Callback Nesting" transformation. Convert to async/await or Promise chains.

---

### H4. Duplicated Code

**Severity:** HIGH

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- Two or more functions with > 5 nearly identical lines, differing only in variable names or WHERE clause
- Same SQL query pattern repeated in multiple functions
- Same serialization logic (dict construction) repeated across endpoints
- Copy-pasted validation blocks across route handlers
- Inline duplicate logic (e.g., overdue date checks) repeated 5+ times

**Specific patterns to search for:**
- Python: Two functions that differ only in `WHERE user_id = ?` vs no WHERE clause
- Python: Manual dict construction `{'id': t.id, 'title': t.title, ...}` repeated in multiple routes
- JavaScript: Similar `db.run` + `db.all` patterns in multiple handlers
- Overdue checks or status validation copied across files

**Impact:** Bug fixes in one copy don't reflect in others. Maintenance effort multiplied. Inconsistent behavior when copies drift.

**Recommendation:** Apply "DRY Extract" transformation. Extract common logic into shared functions or use existing model methods.

---

## MEDIUM Patterns

### M1. N+1 Query Pattern

**Severity:** MEDIUM

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- A `for` loop containing a database query: `for item in items: cursor.execute("SELECT ...")`
- ORM lazy loading inside a loop: `for order in orders: order.items.all()`
- Individual queries per iteration instead of a single JOIN or batch query
- Fetching related data one-by-one inside iteration

**Specific patterns to search for:**
- Python: `for ... in ...:` followed by `cursor.execute(` or `db.session.query(`
- JavaScript: `for (const item of items)` followed by `db.get(` or `db.all(`
- Any loop with a SQL query or ORM call inside the loop body

**Impact:** Performance degrades linearly with data volume. A list of 100 items generates 100+ queries instead of 1-2.

**Recommendation:** Apply "Batch Query Optimization" transformation. Replace loops with JOINs or eager loading.

---

### M2. Missing Input Validation

**Severity:** MEDIUM

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- Route handler accepts request data without checking required fields
- No type validation on input (string length, number range, allowed values)
- Request body parsed and used directly without sanitization
- No schema validation library in dependencies (e.g., no `marshmallow`, `joi`, `zod`)
- Input used in database operations or business logic without checks

**Specific patterns to search for:**
- Python: `request.json['field']` accessed without `if 'field' in request.json` or try/except
- JavaScript: `req.body.field` used without checking existence or type
- No validation middleware or schema definition before route handlers
- String fields used in SQL without length checks

**Impact:** Invalid or malicious data enters the system. Can cause crashes, data corruption, or security vulnerabilities when combined with SQL injection.

**Recommendation:** Apply "Add Input Validation" transformation. Add validation middleware or schema checks before processing.

---

### M3. Dead Code / Unused Modules

**Severity:** MEDIUM

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- Imported modules never used in the file: `import json` with no `json.` usage
- Service/utility files that are never imported by any other file
- Variables declared and exported but never modified or referenced
- Functions defined but never called from any route or other function
- Entire files in directories like `services/` with no importers

**Specific patterns to search for:**
- Python: `from X import Y` where `Y` is never used in the file
- Python: A service class file with no other file containing `from services.x import`
- JavaScript: `let totalRevenue = 0` exported but never modified
- JavaScript: `const helper = require('./utils')` in files where `helper` is unused
- `require()` or `import` statements for modules never referenced

**Impact:** Increases codebase size without value. Misleading — suggests functionality that doesn't exist. Wastes tokens in AI context.

**Recommendation:** Apply "Remove Dead Code" transformation. Remove unused imports, functions, and modules. If the functionality is needed, connect it to the application flow.

---

### M4. Bare Exception Handling

**Severity:** MEDIUM

**Applicable stacks:** Python/Flask (primarily)

**Detection signals:**
- `except:` without a specific exception type: `except: pass`, `except: return ...`
- `except Exception:` catching all exceptions generically
- `try/except` blocks that silently swallow errors: `except: return jsonify({"error": "erro"})`
- Multiple `try/except` blocks with the same generic handler in different files
- No logging of caught exceptions

**Specific patterns to search for:**
- Python: `except:` (bare except, no exception type)
- Python: `except Exception as e:` followed by `pass` or generic error response without `str(e)`
- JavaScript: `catch(err)` with only `res.status(500).send("Error")` without logging `err`
- Error handlers that return vague messages like "Erro DB", "Erro Matricula"

**Impact:** Errors are silently swallowed. Impossible to debug production issues. Exceptions from bugs or infrastructure issues are hidden.

**Recommendation:** Apply "Centralize Error Handling" transformation. Replace bare excepts with specific exception types and a global error handler middleware.

---

## LOW Patterns

### L1. Magic Numbers / Debug in Production

**Severity:** LOW

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- `app.run(debug=True)` hardcoded in production code
- `app.config["DEBUG"] = True` set unconditionally
- Magic numbers without named constants: `if stock < 5`, `discount = 0.1`
- CORS configured to accept all origins: `CORS(app)` without parameters
- Debug print statements left in production code

**Specific patterns to search for:**
- Python: `app.run(debug=True)`, `app.config["DEBUG"] = True`
- Python: `CORS(app)` with no `origins` parameter
- Python: `print(` statements in non-debug code
- JavaScript: `console.log(` with sensitive or unnecessary data in production routes
- Unexplained numeric literals in business logic

**Impact:** Debug mode exposes interactive traceback in production. CORS wildcard allows requests from any origin. Magic numbers make code harder to understand.

**Recommendation:** Read debug flag from environment variable. Define named constants for magic numbers. Configure CORS with specific allowed origins.

---

### L2. Poor Variable Naming

**Severity:** LOW

**Applicable stacks:** Node.js/Express (primarily), Python/Flask

**Detection signals:**
- Single-letter variable names in business logic: `u`, `e`, `p` instead of `user`, `enrollment`, `payment`
- Cryptic abbreviations: `cid` instead of `courseId`, `cc` instead of `cardNumber`
- Variables named `data`, `result`, `info` without descriptive context
- Callback parameters with names that don't indicate their content

**Specific patterns to search for:**
- JavaScript: `const u = ...`, `const e = ...`, `const p = ...` in business logic
- JavaScript: Variables named `cc`, `cid`, `uid` in checkout or order flows
- Python: `d = {}`, `l = []`, `r = requests.get()` (single letter in non-trivial scope)

**Impact:** Very low readability. Difficult to understand what each variable represents without tracing the code. Increases onboarding time.

**Recommendation:** Rename to descriptive names that indicate purpose: `user` instead of `u`, `enrollment` instead of `e`, `cardNumber` instead of `cc`.

---

### L3. Unused Imports

**Severity:** LOW

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- `import json` in a file with no `json.` usage
- `import os` in a file that doesn't use `os.environ` or `os.path`
- `import sys`, `import time`, `import math` with no usage of those modules
- `require('path')` or `require('fs')` with no usage
- Import statements for modules that aren't referenced anywhere in the file

**Specific patterns to search for:**
- Python: `import X` at the top of a file where `X.` never appears in the file body
- JavaScript: `const X = require('Y')` where `X` is never used

**Impact:** Increases cognitive load when reading imports. Suggests dependencies that don't exist. Minor increase in memory footprint.

**Recommendation:** Remove unused import statements. If the import was intended for future use, add a comment or implement the functionality.

---

## Special Pattern

### DP. Deprecated API Usage

**Severity:** HIGH (when detected)

**Applicable stacks:** Python/Flask, Node.js/Express

**Detection signals:**
- Framework version detected in Phase 1
- APIs or methods that were deprecated in the detected version

**How to detect:**
This pattern requires dynamic detection using context7:

1. Call `resolve-library-id` with the framework name (e.g., `Flask` or `Express`)
2. Call `query-docs` with the library ID, asking: "What APIs, methods, or patterns are deprecated in [framework] [version]? List each deprecated item with its modern replacement."
3. Cross-reference the project's source code against the deprecated APIs listed
4. For each deprecated API found in the code, create a finding

**If context7 is unavailable:**
- Skip this pattern
- Add a note in the report: "Deprecated API detection skipped — context7 unavailable"
- The remaining patterns provide sufficient coverage for the minimum finding count

**Finding format:**
- **Description:** State the deprecated API and the version it was deprecated in
- **Impact:** Deprecated APIs may be removed in future versions, breaking the application
- **Recommendation:** State the modern replacement API and link to migration docs if available

---

## Coverage Matrix

| Pattern | ID | Severity | Python/Flask | Node.js/Express |
|---|---|---|---|---|
| Hardcoded Secrets | C1 | CRITICAL | X | X |
| SQL Injection | C2 | CRITICAL | X | X |
| God Class / God Method | C3 | CRITICAL | X | X |
| Broken/Missing Auth | C4 | CRITICAL | X | X |
| Insecure Password Storage | H1 | HIGH | X | X |
| Business Logic in Routes | H2 | HIGH | X | X |
| Callback Hell | H3 | HIGH | - | X |
| Duplicated Code | H4 | HIGH | X | X |
| N+1 Queries | M1 | MEDIUM | X | X |
| Missing Validation | M2 | MEDIUM | X | X |
| Dead Code | M3 | MEDIUM | X | X |
| Bare Exception Handling | M4 | MEDIUM | X | - |
| Magic Numbers / Debug | L1 | LOW | X | X |
| Poor Naming | L2 | LOW | - | X |
| Unused Imports | L3 | LOW | X | X |
| Deprecated API Usage | DP | HIGH | X | X |

**Total:** 15 patterns (4 CRITICAL + 4 HIGH + 4 MEDIUM + 3 LOW + 1 special)
