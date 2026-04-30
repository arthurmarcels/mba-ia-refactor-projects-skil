# Refactoring Playbook

This reference contains transformation patterns for refactoring anti-patterns to MVC. Each transformation includes before/after code examples in both Python/Flask and Node.js/Express.

---

## Transformation Index

| # | Transformation | Resolves Anti-Pattern | Severity |
|---|---|---|---|
| 1 | Extract Config | C1. Hardcoded Secrets | CRITICAL |
| 2 | Parameterize Queries | C2. SQL Injection | CRITICAL |
| 3 | Decompose God Class | C3. God Class | CRITICAL |
| 4 | Add Auth Middleware | C4. Missing Auth | CRITICAL |
| 5 | Secure Password Storage | H1. Insecure Passwords | HIGH |
| 6 | Extract Service Layer | H2. Business Logic in Routes | HIGH |
| 7 | Flatten Callback Nesting | H3. Callback Hell | HIGH |
| 8 | DRY Extract | H4. Duplicated Code | HIGH |
| 9 | Batch Query Optimization | M1. N+1 Queries | MEDIUM |
| 10 | Add Input Validation | M2. Missing Validation | MEDIUM |
| 11 | Centralize Error Handling | M4. Bare Exceptions | MEDIUM |
| 12 | Remove Dead Code | M3. Dead Code | MEDIUM |

---

## 1. Extract Config

**Resolves:** C1. Hardcoded Secrets / Credentials

**Description:** Move all hardcoded configuration values (SECRET_KEY, database paths, API keys, passwords) to a dedicated config module that reads from environment variables.

### Python/Flask — Before

```python
# app.py
from flask import Flask

app = Flask(__name__)
SECRET_KEY = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True

# database.py
import sqlite3

def get_connection():
    return sqlite3.connect("loja.db")
```

### Python/Flask — After

```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database.db')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# config/database.py
import sqlite3
from config.settings import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# app.py
from flask import Flask
from config.settings import Config

app = Flask(__name__)
app.config.from_object(Config)
```

### Node.js/Express — Before

```javascript
// src/utils.js
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef"
};

// src/AppManager.js
const db = new sqlite3.Database(':memory:');
```

### Node.js/Express — After

```javascript
// config/settings.js
module.exports = {
    dbPath: process.env.DB_PATH || 'database.db',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    port: process.env.PORT || 3000,
    nodeEnv: process.env.NODE_ENV || 'development'
};

// config/database.js
const sqlite3 = require('sqlite3');
const settings = require('./settings');

function createDatabase() {
    return new sqlite3.Database(settings.dbPath);
}

module.exports = { createDatabase };
```

---

## 2. Parameterize Queries

**Resolves:** C2. SQL Injection

**Description:** Replace string concatenation and f-strings in SQL queries with parameterized queries using `?` placeholders.

### Python/Flask — Before

```python
# models.py
def get_produto(id):
    cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
    return cursor.fetchone()

def login(email, senha):
    cursor.execute(
        "SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"
    )
    return cursor.fetchone()
```

### Python/Flask — After

```python
# models/user_model.py
def get_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, name, email FROM usuarios WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return user

def get_by_email(email):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, name, email, password FROM usuarios WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()
    return user
```

### Node.js/Express — Before

```javascript
// src/AppManager.js
db.get("SELECT * FROM users WHERE id = " + req.params.id, (err, row) => {
    res.json(row);
});
```

### Node.js/Express — After

```javascript
// models/userModel.js
static async getById(userId) {
    return new Promise((resolve, reject) => {
        db.get(
            "SELECT id, name, email FROM users WHERE id = ?",
            [userId],
            (err, row) => err ? reject(err) : resolve(row)
        );
    });
}
```

---

## 3. Decompose God Class

**Resolves:** C3. God Class / God Method

**Description:** Split a monolithic file that handles DB, routes, and business logic into separate models, controllers, and routes by domain.

### Python/Flask — Before

```python
# app.py (monolito — 300+ linhas)
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
conn = sqlite3.connect("loja.db")

@app.route('/produtos', methods=['GET'])
def get_produtos():
    cursor = conn.execute("SELECT * FROM produtos")
    produtos = [dict(row) for row in cursor.fetchall()]
    return jsonify(produtos)

@app.route('/pedidos', methods=['POST'])
def criar_pedido():
    data = request.json
    usuario_id = data['usuario_id']
    itens = data['itens']
    total = sum(item['preco'] * item['quantidade'] for item in itens)
    cursor = conn.execute(
        "INSERT INTO pedidos (usuario_id, total, status) VALUES (?, ?, 'pendente')",
        (usuario_id, total)
    )
    pedido_id = cursor.lastrowid
    for item in itens:
        conn.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco) VALUES (?, ?, ?, ?)",
            (pedido_id, item['produto_id'], item['quantidade'], item['preco'])
        )
    conn.commit()
    if total > 100:
        print("ENVIANDO EMAIL")
        print("ENVIANDO SMS")
    return jsonify({"id": pedido_id, "total": total}), 201
```

### Python/Flask — After

```python
# models/product_model.py
def get_all():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM produtos").fetchall()
    conn.close()
    return [dict(p) for p in products]

# models/order_model.py
def create(user_id, total):
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO pedidos (usuario_id, total, status) VALUES (?, ?, 'pendente')",
        (user_id, total)
    )
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

def add_item(order_id, product_id, quantity, price):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco) VALUES (?, ?, ?, ?)",
        (order_id, product_id, quantity, price)
    )
    conn.commit()
    conn.close()

# controllers/order_controller.py
from models.order_model import create as create_order, add_item
from services.notification_service import send_order_notification

def create_order_with_items(data):
    total = sum(item['preco'] * item['quantidade'] for item in data['itens'])
    order_id = create_order(data['usuario_id'], total)
    for item in data['itens']:
        add_item(order_id, item['produto_id'], item['quantidade'], item['preco'])
    send_order_notification(order_id, total)
    return {"id": order_id, "total": total}, 201

# routes/order_routes.py
order_bp = Blueprint('orders', __name__)

@order_bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    data = request.get_json()
    result, status = create_order_with_items(data)
    return jsonify(result), status
```

### Node.js/Express — Before

```javascript
// src/AppManager.js (141 lines — everything in one class)
class AppManager {
    constructor() {
        this.db = new sqlite3.Database(':memory:');
        this.initDB();
        this.app = express();
        this.setupRoutes();
    }

    initDB() {
        this.db.serialize(() => {
            this.db.run("CREATE TABLE courses (...)");
            this.db.run("CREATE TABLE users (...)");
            // ... seed data
        });
    }

    setupRoutes() {
        this.app.get('/api/courses', (req, res) => {
            this.db.all("SELECT * FROM courses", (err, rows) => {
                res.json(rows);
            });
        });

        this.app.post('/api/checkout', (req, res) => {
            // 50+ lines with 4 levels of callback nesting
        });
    }
}
```

### Node.js/Express — After

```javascript
// config/database.js — DB initialization
// models/courseModel.js — Course queries
// models/userModel.js — User queries
// controllers/checkoutController.js — Checkout logic
// routes/courseRoutes.js — Course endpoints
// routes/checkoutRoutes.js — Checkout endpoint
// app.js — Composition root

// app.js
const express = require('express');
const initDatabase = require('./config/database');
const courseRoutes = require('./routes/courseRoutes');
const checkoutRoutes = require('./routes/checkoutRoutes');
const errorHandler = require('./middlewares/errorHandler');

async function createApp() {
    const db = await initDatabase();
    const app = express();
    app.use(express.json());
    app.use('/api', courseRoutes(db));
    app.use('/api', checkoutRoutes(db));
    app.use(errorHandler);
    return app;
}

createApp().then(app => {
    app.listen(3000);
});
```

---

## 4. Add Auth Middleware

**Resolves:** C4. Broken or Missing Authentication

**Description:** Add JWT-based authentication middleware that validates tokens on protected routes.

### Python/Flask — Before

```python
# routes/user_routes.py
@user_bp.route('/login', methods=['POST'])
def login():
    user = UserModel.get_by_email(request.json['email'])
    if user and user['password'] == request.json['password']:
        return jsonify({"token": "fake-jwt-token-" + str(user['id'])})
    return jsonify({"error": "Invalid credentials"}), 401

@user_bp.route('/users', methods=['GET'])
def get_users():
    # No auth check — anyone can access
    return jsonify(UserModel.get_all())
```

### Python/Flask — After

```python
# middlewares/auth.py
from functools import wraps
from flask import request, jsonify
import jwt
from config.settings import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# routes/user_routes.py
from middlewares.auth import token_required

@user_bp.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    return jsonify(UserModel.get_all())

@user_bp.route('/login', methods=['POST'])
def login():
    user = UserModel.get_by_email(request.json['email'])
    if user and bcrypt.checkpw(
        request.json['password'].encode(), user['password'].encode()
    ):
        token = jwt.encode(
            {"user_id": user['id'], "exp": datetime.utcnow() + timedelta(hours=24)},
            Config.SECRET_KEY,
            algorithm='HS256'
        )
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401
```

### Node.js/Express — Before

```javascript
// No middleware — all routes unprotected
app.get('/api/courses', (req, res) => { ... });
app.delete('/api/users/:id', (req, res) => { ... });
```

### Node.js/Express — After

```javascript
// middlewares/auth.js
const jwt = require('jsonwebtoken');
const settings = require('../config/settings');

function authMiddleware(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) {
        return res.status(401).json({ error: 'Token is missing' });
    }
    try {
        const decoded = jwt.verify(token, settings.secretKey);
        req.userId = decoded.userId;
        next();
    } catch (err) {
        return res.status(401).json({ error: 'Invalid or expired token' });
    }
}

module.exports = authMiddleware;

// routes/userRoutes.js
const authMiddleware = require('../middlewares/auth');

router.delete('/api/users/:id', authMiddleware, async (req, res, next) => {
    // Protected route
});
```

---

## 5. Secure Password Storage

**Resolves:** H1. Insecure Password Storage

**Description:** Replace plaintext passwords, MD5, or weak hashing with bcrypt.

### Python/Flask — Before

```python
import hashlib

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(password, hash):
    return hash_password(password) == hash
```

### Python/Flask — After

```python
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode(), password_hash.encode())
```

### Node.js/Express — Before

```javascript
// utils.js
function badCrypto(password) {
    let hash = Buffer.from(password).toString('base64');
    for (let i = 0; i < 10000; i++) {
        hash = Buffer.from(hash).toString('base64');
    }
    return hash.substring(0, 10);
}
```

### Node.js/Express — After

```javascript
// utils/password.js
const bcrypt = require('bcrypt');

async function hashPassword(password) {
    return await bcrypt.hash(password, 10);
}

async function verifyPassword(password, hash) {
    return await bcrypt.compare(password, hash);
}

module.exports = { hashPassword, verifyPassword };
```

---

## 6. Extract Service Layer

**Resolves:** H2. Business Logic in Route Handlers

**Description:** Move business logic from route handlers into dedicated service/controller classes.

### Python/Flask — Before

```python
@order_bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    data = request.get_json()
    if not data.get('usuario_id') or not data.get('itens'):
        return jsonify({"error": "Missing fields"}), 400
    if len(data.get('itens', [])) == 0:
        return jsonify({"error": "No items"}), 400
    total = sum(item['preco'] * item['quantidade'] for item in data['itens'])
    if total > 500:
        total = total * 0.9
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO pedidos (usuario_id, total, status) VALUES (?, ?, ?)",
        (data['usuario_id'], total, 'pendente')
    )
    # ... 20 more lines of logic
```

### Python/Flask — After

```python
# services/order_service.py
class OrderService:
    @staticmethod
    def create_order(data):
        OrderService._validate_order(data)
        total = OrderService._calculate_total(data['itens'])
        order_id = OrderModel.create(data['usuario_id'], total)
        OrderService._add_items(order_id, data['itens'])
        NotificationService.send_order_confirmation(order_id, total)
        return order_id, total

    @staticmethod
    def _validate_order(data):
        if not data.get('usuario_id') or not data.get('itens'):
            raise ValueError("Missing required fields")
        if len(data['itens']) == 0:
            raise ValueError("Order must have items")

    @staticmethod
    def _calculate_total(items):
        total = sum(item['preco'] * item['quantidade'] for item in items)
        if total > 500:
            total *= 0.9
        return total

# routes/order_routes.py
@order_bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    data = request.get_json()
    try:
        order_id, total = OrderService.create_order(data)
        return jsonify({"id": order_id, "total": total}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
```

### Node.js/Express — Before

```javascript
app.post('/api/checkout', (req, res) => {
    const { name, email, courseId, cardNumber } = req.body;
    // 50 lines of validation, DB calls, payment logic, notifications
    db.get("SELECT * FROM courses WHERE id = ?", [courseId], (err, course) => {
        if (!course) return res.status(404).json({ error: "Course not found" });
        db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
            if (!user) {
                db.run("INSERT INTO users ...", (err) => {
                    // ... more nesting
                });
            }
        });
    });
});
```

### Node.js/Express — After

```javascript
// services/checkoutService.js
class CheckoutService {
    static async processCheckout(data) {
        const course = await CourseModel.getById(data.courseId);
        if (!course) throw new NotFoundError('Course not found');

        let user = await UserModel.getByEmail(data.email);
        if (!user) {
            user = await UserModel.create(data.name, data.email, data.password);
        }

        const payment = await PaymentService.process(
            data.cardNumber, course.price
        );

        await EnrollmentModel.create(user.id, course.id, payment.id);
        await AuditLogModel.create(user.id, course.id, 'enrollment');

        return { user, course, payment };
    }
}

// routes/checkoutRoutes.js
router.post('/api/checkout', async (req, res, next) => {
    try {
        const result = await CheckoutService.processCheckout(req.body);
        res.status(201).json(result);
    } catch (err) {
        next(err);
    }
});
```

---

## 7. Flatten Callback Nesting

**Resolves:** H3. Callback Hell / Pyramid of Doom

**Description:** Convert nested callbacks to async/await for flat, readable code.

### Node.js/Express — Before

```javascript
app.post('/api/checkout', (req, res) => {
    const { courseId, email } = req.body;

    db.get("SELECT * FROM courses WHERE id = ?", [courseId], (err, course) => {
        if (err) return res.status(500).json({ error: "Erro DB" });
        if (!course) return res.status(404).json({ error: "Curso nao encontrado" });

        db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
            if (err) return res.status(500).json({ error: "Erro DB" });

            if (!user) {
                db.run("INSERT INTO users (name, email) VALUES (?, ?)",
                    [req.body.name, email], function(err) {
                        if (err) return res.status(500).json({ error: "Erro ao criar usuario" });
                        const userId = this.lastID;

                        db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
                            [userId, courseId], (err) => {
                                if (err) return res.status(500).json({ error: "Erro Matricula" });

                                db.run("INSERT INTO payments (user_id, course_id, amount) VALUES (?, ?, ?)",
                                    [userId, courseId, course.price], (err) => {
                                        if (err) return res.status(500).json({ error: "Erro Pagamento" });
                                        res.json({ status: "approved" });
                                    });
                            });
                    });
            } else {
                // Similar nesting for existing user...
            }
        });
    });
});
```

### Node.js/Express — After

```javascript
// Using async/await with promisified db
// models/courseModel.js
static async getById(id) {
    return new Promise((resolve, reject) => {
        db.get("SELECT * FROM courses WHERE id = ?", [id], (err, row) => {
            if (err) reject(err);
            else resolve(row);
        });
    });
}

// controllers/checkoutController.js
static async processCheckout(data) {
    const course = await CourseModel.getById(data.courseId);
    if (!course) throw new NotFoundError('Course not found');

    let user = await UserModel.getByEmail(data.email);
    if (!user) {
        user = await UserModel.create(data.name, data.email);
    }

    const enrollment = await EnrollmentModel.create(user.id, course.id);
    const payment = await PaymentModel.create(user.id, course.id, course.price);

    return { enrollment, payment };
}

// routes/checkoutRoutes.js
router.post('/api/checkout', async (req, res, next) => {
    try {
        const result = await CheckoutController.processCheckout(req.body);
        res.status(201).json(result);
    } catch (err) {
        next(err);
    }
});
```

### Python/Flask Note

Python does not have callback hell issues. This transformation is specific to Node.js projects. For Python, skip this transformation and focus on the service layer extraction instead.

---

## 8. DRY Extract

**Resolves:** H4. Duplicated Code

**Description:** Extract duplicated code blocks into shared functions or use existing model methods.

### Python/Flask — Before

```python
# routes/task_routes.py
def get_tasks():
    tasks = TaskModel.get_all()
    result = []
    for t in tasks:
        overdue = t['due_date'] < datetime.utcnow() and t['status'] not in ['done', 'cancelled']
        result.append({
            'id': t['id'],
            'title': t['title'],
            'status': t['status'],
            'overdue': overdue
        })
    return jsonify(result)

def get_user_tasks(user_id):
    tasks = TaskModel.get_by_user(user_id)
    result = []
    for t in tasks:
        overdue = t['due_date'] < datetime.utcnow() and t['status'] not in ['done', 'cancelled']
        result.append({
            'id': t['id'],
            'title': t['title'],
            'status': t['status'],
            'overdue': overdue
        })
    return jsonify(result)
```

### Python/Flask — After

```python
# models/task_model.py — already has to_dict() and is_overdue()
def to_dict(task):
    return {
        'id': task['id'],
        'title': task['title'],
        'description': task.get('description', ''),
        'status': task['status'],
        'due_date': task['due_date'],
        'overdue': is_overdue(task)
    }

def is_overdue(task):
    return (
        task['due_date'] and
        task['due_date'] < datetime.utcnow() and
        task['status'] not in ['done', 'cancelled']
    )

# routes/task_routes.py
def get_tasks():
    tasks = TaskModel.get_all()
    return jsonify([TaskModel.to_dict(t) for t in tasks])

def get_user_tasks(user_id):
    tasks = TaskModel.get_by_user(user_id)
    return jsonify([TaskModel.to_dict(t) for t in tasks])
```

### Node.js/Express — Before

```javascript
// Same validation and error handling repeated in every handler
app.post('/api/courses', (req, res) => {
    const { name, description, price } = req.body;
    if (!name || !price) {
        return res.status(400).json({ error: "Missing required fields" });
    }
    db.run("INSERT INTO courses ...", [name, description, price], function(err) {
        if (err) return res.status(500).json({ error: "Erro DB" });
        res.status(201).json({ id: this.lastID });
    });
});

app.put('/api/courses/:id', (req, res) => {
    const { name, description, price } = req.body;
    if (!name || !price) {
        return res.status(400).json({ error: "Missing required fields" });
    }
    db.run("UPDATE courses SET ...", [name, description, price, req.params.id], (err) => {
        if (err) return res.status(500).json({ error: "Erro DB" });
        res.json({ updated: true });
    });
});
```

### Node.js/Express — After

```javascript
// utils/validators.js
function validateCourse(data) {
    if (!data.name || !data.price) {
        throw new ValidationError('Name and price are required');
    }
}

// controllers/courseController.js
class CourseController {
    static async create(data) {
        validateCourse(data);
        return await CourseModel.create(data.name, data.description, data.price);
    }

    static async update(id, data) {
        validateCourse(data);
        return await CourseModel.update(id, data.name, data.description, data.price);
    }
}
```

---

## 9. Batch Query Optimization

**Resolves:** M1. N+1 Query Pattern

**Description:** Replace loops containing individual queries with single batch queries using JOINs or WHERE IN.

### Python/Flask — Before

```python
def get_pedidos_usuario(usuario_id):
    conn = get_db_connection()
    pedidos = conn.execute(
        "SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)
    ).fetchall()

    result = []
    for pedido in pedidos:
        itens = conn.execute(
            "SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido['id'],)
        ).fetchall()
        pedido_dict = dict(pedido)
        pedido_dict['itens'] = [dict(i) for i in itens]
        result.append(pedido_dict)
    return result
```

### Python/Flask — After

```python
def get_pedidos_usuario(usuario_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT p.*, ip.produto_id, ip.quantidade, ip.preco
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
        WHERE p.usuario_id = ?
        ORDER BY p.id
    """, (usuario_id,)).fetchall()
    conn.close()

    pedidos = {}
    for row in rows:
        pid = row['id']
        if pid not in pedidos:
            pedidos[pid] = {
                'id': row['id'],
                'total': row['total'],
                'status': row['status'],
                'itens': []
            }
        if row['produto_id']:
            pedidos[pid]['itens'].append({
                'produto_id': row['produto_id'],
                'quantidade': row['quantidade'],
                'preco': row['preco']
            })
    return list(pedidos.values())
```

### Node.js/Express — Before

```javascript
// For each user, query their enrollments separately
db.all("SELECT * FROM users", (err, users) => {
    users.forEach(user => {
        db.all(
            "SELECT * FROM enrollments WHERE user_id = ?",
            [user.id],
            (err, enrollments) => {
                user.enrollments = enrollments;
            }
        );
    });
});
```

### Node.js/Express — After

```javascript
// Single query with LEFT JOIN
const rows = await new Promise((resolve, reject) => {
    db.all(`
        SELECT u.*, e.course_id, e.enrolled_at
        FROM users u
        LEFT JOIN enrollments e ON u.id = e.user_id
    `, (err, rows) => err ? reject(err) : resolve(rows));
});

const users = {};
rows.forEach(row => {
    if (!users[row.id]) {
        users[row.id] = { id: row.id, name: row.name, enrollments: [] };
    }
    if (row.course_id) {
        users[row.id].enrollments.push({
            courseId: row.course_id, enrolledAt: row.enrolled_at
        });
    }
});
```

---

## 10. Add Input Validation

**Resolves:** M2. Missing Input Validation

**Description:** Add validation middleware or schema checks before processing request data.

### Python/Flask — Before

```python
@product_bp.route('/produtos', methods=['POST'])
def create_produto():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO produtos (nome, preco, categoria) VALUES (?, ?, ?)",
        (data['nome'], data['preco'], data['categoria'])
    )
    conn.commit()
    return jsonify({"message": "Produto criado"}), 201
```

### Python/Flask — After

```python
# utils/validators.py
def validate_product(data):
    if not data:
        raise ValueError("Request body is required")
    if not data.get('nome') or len(data['nome'].strip()) < 2:
        raise ValueError("Product name must be at least 2 characters")
    if not isinstance(data.get('preco'), (int, float)) or data['preco'] <= 0:
        raise ValueError("Price must be a positive number")
    valid_categories = ['eletronicos', 'roupas', 'alimentos', 'livros']
    if data.get('categoria') and data['categoria'] not in valid_categories:
        raise ValueError(f"Category must be one of: {valid_categories}")

# routes/product_routes.py
@product_bp.route('/produtos', methods=['POST'])
def create_produto():
    data = request.get_json()
    try:
        validate_product(data)
        result, status = ProductController.create(data)
        return jsonify(result), status
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
```

### Node.js/Express — Before

```javascript
app.post('/api/checkout', (req, res) => {
    const { name, email, courseId, cardNumber } = req.body;
    // No validation — directly used in DB queries
    db.get("SELECT * FROM courses WHERE id = ?", [courseId], ...);
});
```

### Node.js/Express — After

```javascript
// utils/validators.js
function validateCheckout(data) {
    if (!data.name || data.name.trim().length < 2) {
        throw new ValidationError('Name must be at least 2 characters');
    }
    if (!data.email || !data.email.includes('@')) {
        throw new ValidationError('Valid email is required');
    }
    if (!data.courseId || isNaN(parseInt(data.courseId))) {
        throw new ValidationError('Valid course ID is required');
    }
    if (!data.cardNumber || data.cardNumber.length < 13) {
        throw new ValidationError('Valid card number is required');
    }
}

// routes/checkoutRoutes.js
router.post('/api/checkout', async (req, res, next) => {
    try {
        validateCheckout(req.body);
        const result = await CheckoutController.processCheckout(req.body);
        res.status(201).json(result);
    } catch (err) {
        next(err);
    }
});
```

---

## 11. Centralize Error Handling

**Resolves:** M4. Bare Exception Handling

**Description:** Replace scattered bare except/catch blocks with a centralized error handler middleware.

### Python/Flask — Before

```python
# Scattered across multiple route files
@app.route('/produtos/<int:id>')
def get_produto(id):
    try:
        produto = ProductModel.get_by_id(id)
        return jsonify(produto)
    except:
        return jsonify({"error": "erro"}), 500

@app.route('/pedidos')
def get_pedidos():
    try:
        pedidos = OrderModel.get_all()
        return jsonify(pedidos)
    except:
        return jsonify({"error": "erro"}), 500
```

### Python/Flask — After

```python
# middlewares/error_handler.py
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

class AppError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({"error": e.message}), e.status_code

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# routes/product_routes.py — no try/except needed
@product_bp.route('/produtos/<int:id>')
def get_produto(id):
    produto = ProductModel.get_by_id(id)
    if not produto:
        raise AppError("Product not found", 404)
    return jsonify(produto)
```

### Node.js/Express — Before

```javascript
// Scattered catch blocks with vague messages
db.get("SELECT ...", (err, row) => {
    if (err) return res.status(500).json({ error: "Erro DB" });
});

db.run("INSERT ...", (err) => {
    if (err) return res.status(500).json({ error: "Erro Matricula" });
});
```

### Node.js/Express — After

```javascript
// middlewares/errorHandler.js
class AppError extends Error {
    constructor(message, statusCode = 400) {
        super(message);
        this.statusCode = statusCode;
    }
}

function errorHandler(err, req, res, next) {
    console.error(`[${new Date().toISOString()}] ${err.message}`);

    const statusCode = err.statusCode || 500;
    const message = statusCode === 500
        ? 'Internal server error'
        : err.message;

    res.status(statusCode).json({ error: message });
}

module.exports = { AppError, errorHandler };

// In route handlers — throw errors instead of catching
router.get('/api/courses/:id', async (req, res, next) => {
    try {
        const course = await CourseModel.getById(req.params.id);
        if (!course) throw new AppError('Course not found', 404);
        res.json(course);
    } catch (err) {
        next(err);
    }
});
```

---

## 12. Remove Dead Code

**Resolves:** M3. Dead Code / Unused Modules

**Description:** Identify and remove unused imports, functions, and modules. If the functionality is needed, connect it to the application flow.

### Python/Flask — Before

```python
# services/notification_service.py — never imported anywhere
import smtplib

class NotificationService:
    email_address = "noreply@example.com"
    email_password = "senha123"

    @staticmethod
    def send_email(to, subject, body):
        print("ENVIANDO EMAIL")

    @staticmethod
    def send_sms(phone, message):
        print("ENVIANDO SMS")
```

### Python/Flask — After

```python
# Option A: Remove the file entirely if notifications aren't needed

# Option B: Connect to the application if the functionality is needed
# services/notification_service.py
import os
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_email(to, subject, body):
        smtp_host = os.environ.get('SMTP_HOST')
        if smtp_host:
            logger.info(f"Sending email to {to}: {subject}")
        else:
            logger.warning(f"SMTP not configured. Email to {to} skipped: {subject}")

# controllers/order_controller.py
from services.notification_service import NotificationService

def create_order(data):
    order_id = OrderModel.create(data)
    NotificationService.send_email(
        data['email'],
        "Order Confirmation",
        f"Order #{order_id} created"
    )
    return order_id
```

### Node.js/Express — Before

```javascript
// utils.js
let totalRevenue = 0;  // Never modified anywhere
let globalCache = {};   // Unbounded memory leak

function logAndCache(message) {
    console.log(message);
    globalCache[Date.now()] = message;  // Never read
}

module.exports = { totalRevenue, globalCache, logAndCache };
```

### Node.js/Express — After

```javascript
// utils/logger.js — Clean, focused utility
const logger = {
    info(message) {
        console.log(`[INFO] ${new Date().toISOString()} ${message}`);
    },
    error(message) {
        console.error(`[ERROR] ${new Date().toISOString()} ${message}`);
    }
};

module.exports = logger;
```

---

## Applying Transformations

When applying transformations during Phase 3:

1. **Start with Extract Config** — removes credentials first, reduces risk
2. **Then Decompose God Class** — establishes MVC structure
3. **Then fix security issues** — parameterize queries, secure passwords, add auth
4. **Then clean architecture** — extract services, DRY, centralize errors
5. **Finally optimize** — batch queries, add validation, remove dead code
6. **Validate after each group** — ensure the app still boots and endpoints respond
