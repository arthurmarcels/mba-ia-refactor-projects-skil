# Project Analysis Heuristics

This reference provides heuristics for detecting a project's technology stack, architecture, and domain during Phase 1.

---

## 1. Language Detection

### Python

**Detection signals:**
- `requirements.txt` file present in root
- `.py` source files present
- `setup.py` or `pyproject.toml` present
- Lines starting with `import ` or `from ... import` in source files
- `if __name__ == "__main__":` pattern
- `venv/`, `.venv/` directories present

**How to confirm:** Read `requirements.txt` and check for Python-specific packages. Look at first few lines of main source file for Python imports.

### JavaScript / Node.js

**Detection signals:**
- `package.json` file present in root
- `.js` source files present (especially in `src/` directory)
- `node_modules/` directory present
- Lines with `const `, `let `, `var `, `require(`, or `import ` syntax
- `module.exports =` pattern

**How to confirm:** Read `package.json` and check the `dependencies` and `devDependencies` fields. Look at the `main` or `scripts.start` field for entry point.

---

## 2. Framework Detection

### Flask (Python)

**Detection signals:**
- `flask` listed in `requirements.txt`
- Source file contains `from flask import Flask` or `from flask import ...`
- Source file contains `Flask(__name__)` or `app = Flask(`
- Source file contains `@app.route(` or `app.add_url_rule(`
- Source file contains `app.run(debug=` or `app.run(host=`
- `flask-cors`, `flask-sqlalchemy`, `flask-jwt-extended` in requirements.txt

**Version extraction:** Parse `requirements.txt` for the line containing `flask` — version may appear as `flask==3.1.1`, `flask>=3.0`, or `Flask==3.1.1`.

**How to confirm:** Find the Flask app instance creation and at least one route definition.

### Express (Node.js)

**Detection signals:**
- `express` listed in `package.json` dependencies
- Source file contains `require('express')` or `require("express")`
- Source file contains `const app = express()` or `express()`
- Source file contains `app.get(`, `app.post(`, `app.put(`, `app.delete(`
- Source file contains `app.listen(`
- `body-parser`, `cors`, `express-session` in package.json

**Version extraction:** Parse `package.json` for `dependencies.express` — version appears as `"express": "^4.18.0"` or similar.

**How to confirm:** Find the Express app creation and at least one route definition.

---

## 3. Database Detection

### SQLite

**Detection signals (Python):**
- `import sqlite3` in source files
- `sqlite3.connect(` with a file path (e.g., `'loja.db'`, `'database.db'`) → file-based SQLite
- `sqlite3.connect(':memory:')` → in-memory SQLite
- `.db` or `.sqlite` files present in the project directory

**Detection signals (Node.js):**
- `require('sqlite3')` or `require('better-sqlite3')` in source files
- `new sqlite3.Database(` with a file path → file-based SQLite
- `new sqlite3.Database(':memory:')` → in-memory SQLite
- `better-sqlite3` in package.json

**How to distinguish file-based vs in-memory:**
- File-based: connection string is a filename (e.g., `'loja.db'`)
- In-memory: connection string is `':memory:'`

### ORM vs Raw SQL

**Raw SQL detection:**
- `cursor.execute("SELECT ...")` with inline SQL strings
- `db.run("INSERT ...")` with inline SQL strings
- `db.all("SELECT ...")` with inline SQL strings
- SQL keywords in string literals: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE TABLE`

**ORM detection:**
- `from flask_sqlalchemy import SQLAlchemy` or `db = SQLAlchemy(app)` → SQLAlchemy (Python)
- `db.Model`, `db.Column`, `db.relationship` → SQLAlchemy models
- `require('mongoose')` or `require('prisma')` → ORM for Node.js

---

## 4. Architecture Mapping

### Monolithic

**Signals:**
- 2-4 source files in the project root with no subdirectories for layers
- Single file contains routes, database access, and business logic
- No `models/`, `routes/`, `controllers/`, `services/` directories
- All imports are between 2-4 files in the same directory

**Classification label:** `Monolitica — sem separacao de camadas`

### God Class

**Signals:**
- 1 dominant file (often > 100 lines) that handles everything
- That single file contains: database initialization, schema creation, route definitions, and business logic
- Other files in the project are utilities or configuration only
- The class/file has methods spanning multiple concerns (DB + routes + logic)

**Classification label:** `God Class — 1 classe/arquivo domina tudo`

### Partially Organized

**Signals:**
- Directories like `models/`, `routes/`, `services/`, `utils/` exist
- BUT routes contain business logic inline (validation, computation, DB queries)
- OR services exist but are never imported/used (dead code)
- Models may lack validation or contain logic that belongs in controllers
- Routes act as both routes AND controllers simultaneously

**Classification label:** `Parcialmente organizada — rotas atuam como controllers`

### MVC (Proper)

**Signals:**
- Clear directory structure: `config/`, `models/`, `routes/`, `controllers/`, `middlewares/`
- Models contain only data representation and DB access
- Routes contain only endpoint definitions and delegate to controllers
- Controllers contain orchestration logic
- Configuration is in a dedicated module reading from env vars
- Error handling is centralized in middleware

**Classification label:** `MVC — separacao adequada de responsabilidades`

---

## 5. Domain Detection

### E-commerce

**Signals:**
- Tables/models named: `produtos`, `produtos`, `usuarios`, `pedidos`, `itens_pedido`, `orders`, `products`, `users`, `customers`
- Endpoints like: `/produtos`, `/pedidos`, `/carrinho`, `/products`, `/orders`, `/checkout`
- Concepts: products, orders, cart, payments, customers, inventory

**Classification label:** `E-commerce API (produtos, pedidos, usuarios)`

### LMS (Learning Management System)

**Signals:**
- Tables/models named: `courses`, `enrollments`, `users`, `payments`, `audit_log`
- Endpoints like: `/courses`, `/enrollments`, `/checkout`, `/users`
- Concepts: courses, enrollments, students, payments, certificates, lessons

**Classification label:** `LMS API (cursos, matriculas, pagamentos)`

### Task Manager

**Signals:**
- Tables/models named: `tasks`, `users`, `categories`, `comments`, `labels`
- Endpoints like: `/tasks`, `/users`, `/categories`, `/reports`, `/comments`
- Concepts: tasks, assignments, due dates, categories, priorities, reports, status tracking

**Classification label:** `Task Manager API (tarefas, usuarios, categorias)`

### Generic API

If the domain doesn't match any known pattern, describe it based on the model names and endpoints found:

**Classification label:** `API (list the main entities found)`

---

## Detection Procedure

1. **Start with files:** List files in root directory. Look for `package.json`, `requirements.txt`, `setup.py`, `pyproject.toml`
2. **Confirm language:** Read the relevant config file and source files
3. **Identify framework:** Search for framework-specific imports in source files
4. **Detect database:** Search for database imports and connection patterns
5. **Map architecture:** List all source files and directories, count lines per file, classify
6. **Identify domain:** Read model definitions and route endpoint names
7. **Synthesize:** Use sequential-thinking to reason through each heuristic before concluding
