# MVC Architecture Guidelines

This reference defines the target MVC architecture that Phase 3 refactoring should achieve.

---

## Layer Responsibilities

### Model Layer

**Directory:** `models/` or individual model files

**Responsibilities:**
- Data representation (schema definition, field types, relationships)
- Database access (queries, CRUD operations)
- Domain-level data validation (required fields, valid ranges, format constraints)
- Entity relationships (foreign keys, joins, associations)

**MUST NOT contain:**
- HTTP request handling or response formatting
- Business logic (calculations, workflows, orchestration)
- Direct use of `request` or `response` objects
- Route definitions or URL patterns

**Python/Flask example:**
```python
# models/user_model.py
import sqlite3
from config.database import get_db_connection

class UserModel:
    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        conn.close()
        return dict(user) if user else None

    @staticmethod
    def create(name, email, password_hash):
        conn = get_db_connection()
        cursor = conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
```

**Node.js/Express example:**
```javascript
// models/userModel.js
const db = require('../config/database');

class UserModel {
    static async getById(userId) {
        return new Promise((resolve, reject) => {
            db.get(
                "SELECT id, name, email FROM users WHERE id = ?",
                [userId],
                (err, row) => {
                    if (err) reject(err);
                    else resolve(row);
                }
            );
        });
    }

    static async create(name, email, passwordHash) {
        return new Promise((resolve, reject) => {
            db.run(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                [name, email, passwordHash],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.lastID);
                }
            );
        });
    }
}
```

---

### Route / View Layer

**Directory:** `routes/`

**Responsibilities:**
- Define HTTP endpoints (URL patterns and HTTP methods)
- Parse request parameters (body, query string, URL params)
- Delegate to the appropriate controller method
- Format and return HTTP responses (status codes, JSON structure)

**MUST NOT contain:**
- Business logic or calculations
- Direct database queries or SQL statements
- Data validation rules (delegate to models or services)
- Complex conditional logic beyond routing decisions

**Python/Flask example:**
```python
# routes/user_routes.py
from flask import Blueprint, request, jsonify
from controllers.user_controller import UserController

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
def list_users():
    users = UserController.get_all_users()
    return jsonify(users), 200

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    result, status = UserController.create_user(data)
    return jsonify(result), status
```

**Node.js/Express example:**
```javascript
// routes/userRoutes.js
const express = require('express');
const router = express.Router();
const UserController = require('../controllers/userController');

router.get('/users', async (req, res, next) => {
    try {
        const users = await UserController.getAllUsers();
        res.json(users);
    } catch (err) {
        next(err);
    }
});

router.post('/users', async (req, res, next) => {
    try {
        const result = await UserController.createUser(req.body);
        res.status(201).json(result);
    } catch (err) {
        next(err);
    }
});

module.exports = router;
```

---

### Controller Layer

**Directory:** `controllers/`

**Responsibilities:**
- Orchestrate request flow (receive parsed data from routes)
- Call models for data access
- Call services for business logic
- Handle business errors and convert to appropriate responses
- Assemble response data structures

**MUST NOT contain:**
- Direct SQL queries (delegate to models)
- HTTP parsing (routes handle this)
- Complex domain rules (delegate to services)
- Response formatting details (keep minimal, return data + status)

**Python/Flask example:**
```python
# controllers/user_controller.py
from models.user_model import UserModel
from utils.validators import validate_user_data
import bcrypt

class UserController:
    @staticmethod
    def get_all_users():
        users = UserModel.get_all()
        return users

    @staticmethod
    def create_user(data):
        validation_error = validate_user_data(data)
        if validation_error:
            return {"error": validation_error}, 400

        existing = UserModel.get_by_email(data['email'])
        if existing:
            return {"error": "Email already registered"}, 409

        password_hash = bcrypt.hashpw(
            data['password'].encode(), bcrypt.gensalt()
        )
        user_id = UserModel.create(
            data['name'], data['email'], password_hash
        )
        return {"id": user_id, "message": "User created"}, 201
```

**Node.js/Express example:**
```javascript
// controllers/userController.js
const UserModel = require('../models/userModel');
const bcrypt = require('bcrypt');
const { validateUserData } = require('../utils/validators');

class UserController {
    static async getAllUsers() {
        return await UserModel.getAll();
    }

    static async createUser(data) {
        const validationError = validateUserData(data);
        if (validationError) {
            throw new ValidationError(validationError);
        }

        const existing = await UserModel.getByEmail(data.email);
        if (existing) {
            throw new ConflictError('Email already registered');
        }

        const passwordHash = await bcrypt.hash(data.password, 10);
        const userId = await UserModel.create(
            data.name, data.email, passwordHash
        );
        return { id: userId, message: 'User created' };
    }
}
```

---

## Configuration Module

**Directory:** `config/` or `config.py` / `config.js`

**Rules:**
- All credentials and secrets MUST be read from environment variables
- NEVER hardcode values like SECRET_KEY, database paths, or API keys
- Provide sensible defaults for development only (not production secrets)
- Use a dedicated config module imported by other modules

**Python/Flask config example:**
```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database.db')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
```

**Node.js/Express config example:**
```javascript
// config/settings.js
module.exports = {
    secretKey: process.env.SECRET_KEY || 'dev-key-change-in-production',
    dbPath: process.env.DATABASE_PATH || 'database.db',
    port: process.env.PORT || 3000,
    nodeEnv: process.env.NODE_ENV || 'development'
};
```

---

## Error Handling

**Strategy:** Centralized error handling via middleware, not scattered try/catch blocks.

### Python/Flask

```python
# middlewares/error_handler.py
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
```

### Node.js/Express

```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    console.error(`[${new Date().toISOString()}] Error:`, err.message);

    const statusCode = err.statusCode || 500;
    const message = statusCode === 500
        ? 'Internal server error'
        : err.message;

    res.status(statusCode).json({ error: message });
}

module.exports = errorHandler;
```

---

## Entry Point as Composition Root

The entry point (`app.py` or `app.js`/`index.js`) acts as the composition root. It is responsible ONLY for wiring the application together.

### Python/Flask

```python
# app.py
from flask import Flask
from flask_cors import CORS
from config.settings import Config
from routes.user_routes import user_bp
from routes.product_routes import product_bp
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)

    register_error_handlers(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG)
```

### Node.js/Express

```javascript
// app.js
const express = require('express');
const cors = require('cors');
const config = require('./config/settings');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();

app.use(cors());
app.use(express.json());

app.use(userRoutes);

app.use(errorHandler);

if (require.main === module) {
    app.listen(config.port, () => {
        console.log(`Server running on port ${config.port}`);
    });
}

module.exports = app;
```

---

## Standard Directory Structure

### Python/Flask

```
project/
├── app.py                    # Entry point (composition root)
├── config/
│   ├── __init__.py
│   ├── settings.py           # Config from env vars
│   └── database.py           # DB connection management
├── models/
│   ├── __init__.py
│   ├── user_model.py
│   ├── product_model.py
│   └── order_model.py
├── routes/
│   ├── __init__.py
│   ├── user_routes.py
│   ├── product_routes.py
│   └── order_routes.py
├── controllers/
│   ├── __init__.py
│   ├── user_controller.py
│   ├── product_controller.py
│   └── order_controller.py
├── middlewares/
│   ├── __init__.py
│   ├── error_handler.py
│   └── auth.py
├── services/                 # Optional — for complex business logic
│   ├── __init__.py
│   └── notification_service.py
├── requirements.txt
└── .env                      # Environment variables (not committed)
```

### Node.js/Express

```
project/
├── app.js                    # Entry point (composition root)
├── config/
│   ├── settings.js           # Config from env vars
│   └── database.js           # DB connection management
├── models/
│   ├── userModel.js
│   ├── courseModel.js
│   └── enrollmentModel.js
├── routes/
│   ├── userRoutes.js
│   ├── courseRoutes.js
│   └── enrollmentRoutes.js
├── controllers/
│   ├── userController.js
│   ├── courseController.js
│   └── enrollmentController.js
├── middlewares/
│   ├── errorHandler.js
│   └── auth.js
├── services/                 # Optional — for complex business logic
│   └── paymentService.js
├── package.json
└── .env                      # Environment variables (not committed)
```
