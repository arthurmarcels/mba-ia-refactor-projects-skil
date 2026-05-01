================================
REFACTORING REPORT
================================
Project:       task-manager-api
Stack:         Python 3 + Flask 3.0.0 (flask-sqlalchemy 3.1.1, flask-cors 4.0.0, PyJWT 2.8.0)
Pattern:       MVC com camadas de controller e middleware
Data:          2026-04-30

## New Project Structure

```
task-manager-api/
├── app.py                          # composition root (create_app factory)
├── config.py                       # Config lê SECRET_KEY/DB_URI/SMTP/CORS de env
├── database.py                     # instância SQLAlchemy
├── requirements.txt                # flask, flask-sqlalchemy, flask-cors, PyJWT, python-dotenv
├── seed.py                         # dados iniciais (senhas com werkzeug hash)
├── README.md
├── controllers/
│   ├── __init__.py
│   ├── task_controller.py          # CRUD + search + stats, joinedload para N+1
│   ├── user_controller.py          # CRUD + login com JWT real
│   └── report_controller.py        # summary, user_report + CategoryController
├── middlewares/
│   ├── __init__.py
│   ├── auth.py                     # @token_required com JWT decode + HS256
│   └── error_handler.py            # 400/404/409/500 + Exception centralizados
├── models/
│   ├── __init__.py
│   ├── task.py                     # to_dict + to_dict_with_relations + is_overdue
│   ├── user.py                     # werkzeug password hash, sem password em to_dict
│   └── category.py
├── routes/
│   ├── __init__.py
│   ├── task_routes.py              # 300→55 LOC (delega para TaskController)
│   ├── user_routes.py              # 212→57 LOC (delega para UserController)
│   └── report_routes.py            # 224→48 LOC (delega para ReportController)
├── services/
│   ├── __init__.py
│   └── notification_service.py     # SMTP via Config (sem credenciais hardcoded)
└── utils/
    ├── __init__.py
    └── helpers.py                  # dead code removido, apenas funções utilizadas
```

LOC total: ~950 (vs. ~1170 antes — código redistribuído de 3 rotas monolíticas para 23 módulos coesos).

## Transformations Applied

| # | Transformação                | Anti-pattern alvo               | Onde foi aplicada                                                                 |
|---|------------------------------|---------------------------------|-----------------------------------------------------------------------------------|
| 1 | Extract Config               | C1. Hardcoded Secrets           | `config.py` lê SECRET_KEY/DB_URI/SMTP_*/CORS_ORIGINS de `os.environ` via dotenv  |
| 4 | Add Auth Middleware          | C4. Missing Auth                | `middlewares/auth.py` — JWT + decorator `@token_required`                        |
| — | Remove Password Leak         | C1. Password Leak in API        | `models/user.py:to_dict()` não inclui mais campo `password`                       |
| 5 | Secure Password Storage      | H1. Insecure Passwords          | `werkzeug.security.generate_password_hash` em `models/user.py`                   |
| 6 | Extract Service Layer        | H2. Business Logic in Routes    | `controllers/task_controller.py`, `user_controller.py`, `report_controller.py`   |
| 8 | DRY Extract                  | H4. Duplicated Code             | `task.is_overdue()` + `to_dict()` substituem 6 blocos duplicados                  |
| 9 | Batch Query Optimization     | M1. N+1 Queries                 | `joinedload(Task.user, Task.category)` em `TaskController.get_all_tasks()`       |
| 12| Remove Dead Code             | M3. Dead Code                   | `notification_service` limpo; helpers reduzido; deps `marshmallow`/`requests` removidas |
| 11| Centralize Error Handling    | M4. Bare Exceptions             | `middlewares/error_handler.py` substitui 9 bare excepts                           |
| — | Fix Debug/CORS/Logging       | L1. Debug & Open CORS           | `Config.DEBUG` de env; `CORS(app, origins=...)` configurável; `logging` stdlib   |
| — | Remove Unused Imports        | L3. Unused Imports              | `os, sys, json, time, hashlib` removidos de routes e app.py                       |

> Transformações 2 (Parameterize Queries) e 7 (Flatten Callback Nesting) não se aplicam — projeto usa SQLAlchemy ORM (sem SQL raw) e Python (sem callbacks).

## Findings → Resolução

| ID  | Severidade | Anti-pattern                          | Status | Local da correção                                                                  |
|-----|------------|---------------------------------------|--------|------------------------------------------------------------------------------------|
| C1  | CRITICAL   | Hardcoded SECRET_KEY e DB URI         | ✅ Fixed | `config.py` lê de `os.environ.get()` com defaults seguros                         |
| C1  | CRITICAL   | Credenciais SMTP hardcoded            | ✅ Fixed | `services/notification_service.py` lê de `Config.SMTP_*`                          |
| C1  | CRITICAL   | Password hash vazado via API          | ✅ Fixed | `models/user.py:to_dict()` não inclui campo `password`                            |
| C4  | CRITICAL   | Fake JWT token na autenticação        | ✅ Fixed | `controllers/user_controller.py:login()` gera JWT real com `PyJWT`                |
| C4  | CRITICAL   | Nenhum endpoint protegido             | ✅ Fixed | `middlewares/auth.py:@token_required` aplicado em mutações e endpoints sensíveis  |
| H1  | HIGH       | Senhas com MD5 sem salt               | ✅ Fixed | `werkzeug.security.generate_password_hash` (PBKDF2+salt) em `models/user.py`     |
| H2  | HIGH       | Lógica de negócio nas rotas (736 LOC) | ✅ Fixed | Extraída para `controllers/` (task, user, report); rotas reduzidas de 736→160 LOC |
| H4  | HIGH       | Overdue check duplicado 6 vezes       | ✅ Fixed | `task.is_overdue()` + `to_dict()` com `overdue` embutido                          |
| H4  | HIGH       | Serialização manual duplicada         | ✅ Fixed | `task.to_dict()` e `to_dict_with_relations()` usados em todos os endpoints        |
| M1  | MEDIUM     | N+1 query no GET /tasks               | ✅ Fixed | `joinedload(Task.user, Task.category)` em `TaskController.get_all_tasks()`        |
| M3  | MEDIUM     | notification_service nunca importado  | ✅ Fixed | Módulo limpo e credenciais via Config; disponível para integração futura           |
| M3  | MEDIUM     | Helpers mortos (6 funções + constantes)| ✅ Fixed | `utils/helpers.py` reduzido para apenas funções efetivamente usadas               |
| M3  | MEDIUM     | Deps não utilizadas (marshmallow, requests) | ✅ Fixed | Removidas do `requirements.txt`                                                  |
| M4  | MEDIUM     | 9 bare excepts sem logging            | ✅ Fixed | `middlewares/error_handler.py` com `@app.errorhandler` + `logger.error`           |
| L1  | LOW        | `debug=True` hardcoded                | ✅ Fixed | `Config.DEBUG` lê de `FLASK_DEBUG` env var                                        |
| L1  | LOW        | CORS wildcard sem restrição           | ✅ Fixed | `CORS(app, origins=Config.CORS_ORIGINS)` configurável via env                     |
| L1  | LOW        | `print()` como logging                | ✅ Fixed | Substituído por `logging` stdlib em controllers e services                        |
| L3  | LOW        | Imports não utilizados                | ✅ Fixed | `os, sys, json, time, hashlib` removidos de routes/app                            |

Total: 18 findings endereçados (11 do audit original + findings implícitos resolvidos durante refactoring).

## Endpoints Preserved

| Método | Rota                              | Auth                                |
|--------|-----------------------------------|-------------------------------------|
| GET    | /                                 | público                             |
| GET    | /health                           | público                             |
| GET    | /tasks                            | público                             |
| GET    | /tasks/<id>                       | público                             |
| GET    | /tasks/search                     | público                             |
| GET    | /tasks/stats                      | público                             |
| POST   | /tasks                            | autenticado (@token_required)       |
| PUT    | /tasks/<id>                       | autenticado (@token_required)       |
| DELETE | /tasks/<id>                       | autenticado (@token_required)       |
| GET    | /users                            | autenticado (@token_required)       |
| GET    | /users/<id>                       | autenticado (@token_required)       |
| POST   | /users                            | público (signup)                    |
| PUT    | /users/<id>                       | autenticado (@token_required)       |
| DELETE | /users/<id>                       | autenticado (@token_required)       |
| GET    | /users/<id>/tasks                 | autenticado (@token_required)       |
| POST   | /login                            | público                             |
| GET    | /reports/summary                  | autenticado (@token_required)       |
| GET    | /reports/user/<id>                | autenticado (@token_required)       |
| GET    | /categories                       | público                             |
| POST   | /categories                       | autenticado (@token_required)       |
| PUT    | /categories/<id>                  | autenticado (@token_required)       |
| DELETE | /categories/<id>                  | autenticado (@token_required)       |

## Validation Results

  ✓ App inicia sem erros (`from app import app` + `app.run()`)
  ✓ Schema é criado automaticamente via `db.create_all()` no app factory
  ✓ Seed roda com sucesso (3 usuários, 4 categorias, 10 tasks)
  ✓ 22 endpoints originais respondem corretamente (23/23 smoke tests, incluindo casos de erro)
  ✓ JWT auth real funciona: 401 sem token ("Token is missing"), 200/201 com token válido
  ✓ Senhas armazenadas com `werkzeug.security.generate_password_hash` (PBKDF2+salt) — MD5 eliminado
  ✓ Password hash nunca retornado pela API (`to_dict()` não inclui campo `password`)
  ✓ Zero credenciais hardcoded (SECRET_KEY, DB_URI, SMTP_PASSWORD, CORS → env vars com defaults seguros)
  ✓ N+1 eliminado: `joinedload` no GET /tasks carrega User e Category em uma query
  ✓ Duplicação removida: overdue check (6x) → `task.is_overdue()`, serialização → `to_dict()`
  ✓ 9 bare excepts substituídos por `@app.errorhandler` centralizado com logging
  ✓ `print()` substituído por `logging` stdlib em controllers e services
  ✓ Dependências mortas removidas (marshmallow, requests)

## Smoke Test (23/23)

  OK  GET    /                                                got=200 want=200  -- index
  OK  GET    /health                                          got=200 want=200  -- health
  OK  POST   /login                                           got=200 want=200  -- login_ok (retorna JWT real)
  OK  GET    /tasks                                           got=200 want=200  -- listar_tasks (10 tasks)
  OK  GET    /tasks/1                                         got=200 want=200  -- buscar_task_ok
  OK  GET    /tasks/search?q=login                            got=200 want=200  -- buscar_tasks (1 resultado)
  OK  GET    /tasks/stats                                     got=200 want=200  -- stats_tasks
  OK  GET    /categories                                      got=200 want=200  -- listar_categorias (4 categorias)
  OK  GET    /users                                           got=200 want=200  -- listar_usuarios (auth, 3 users, sem password)
  OK  GET    /users/1                                         got=200 want=200  -- buscar_usuario_ok (auth, sem password)
  OK  POST   /tasks                                           got=201 want=201  -- criar_task (auth)
  OK  PUT    /tasks/1                                         got=200 want=200  -- atualizar_task (auth)
  OK  GET    /users/1/tasks                                   got=200 want=200  -- tasks_do_usuario (auth)
  OK  GET    /reports/summary                                 got=200 want=200  -- relatorio_summary (auth)
  OK  GET    /reports/user/1                                  got=200 want=200  -- relatorio_usuario (auth)
  OK  POST   /users                                           got=201 want=201  -- criar_usuario (público, sem password no retorno)
  OK  POST   /categories                                      got=201 want=201  -- criar_categoria (auth)
  OK  PUT    /categories/1                                    got=200 want=200  -- atualizar_categoria (auth)
  OK  DELETE /tasks/11                                        got=200 want=200  -- deletar_task (auth)
  OK  DELETE /categories/5                                    got=200 want=200  -- deletar_categoria (auth)
  OK  PUT    /users/4                                         got=200 want=200  -- atualizar_usuario (auth)
  OK  DELETE /users/4                                         got=200 want=200  -- deletar_usuario (auth)
  OK  GET    /users                                           got=401 want=401  -- unauth_request (sem token)

## How to Run

```bash
cd task-manager-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py   # popular banco com dados iniciais
python app.py
```

Para configurar variáveis de ambiente em produção:
```bash
export SECRET_KEY="sua-chave-forte-aqui"
export DATABASE_URI="sqlite:///prod-tasks.db"
export FLASK_DEBUG=false
export CORS_ORIGINS="https://seu-frontend.com"
export SMTP_USER="email@real.com"
export SMTP_PASSWORD="senha-real"
```

================================
Refactor concluído — 18 findings endereçados, 23/23 smoke tests passando
================================
