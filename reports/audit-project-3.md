================================
ARCHITECTURE AUDIT REPORT
================================
Project:       task-manager-api
Stack:         Python + Flask 3.0.0
Files:         15 analyzed | ~1170 lines of code
Database:      SQLite (file-based: tasks.db) via SQLAlchemy ORM
Domain:        Task Manager API (tarefas, usuarios, categorias)

## Summary

| Severity | Count |
|---|---|
| CRITICAL | 3 |
| HIGH | 3 |
| MEDIUM | 3 |
| LOW | 2 |
| **Total** | **11** |

## Findings

### [CRITICAL] C1 — Hardcoded Secrets / Credentials

- **File:** `app.py:13`
- **Description:** `SECRET_KEY` está hardcoded como `'super-secret-key-123'`. A URI do banco de dados também está hardcoded em `app.py:11` (`sqlite:///tasks.db`). Adicionalmente, `services/notification_service.py:9-10` contém credenciais SMTP hardcoded (`email_user = 'taskmanager@gmail.com'`, `email_password = 'senha123'`).
- **Impact:** Qualquer pessoa com acesso ao código-fonte obtém credenciais de produção. A SECRET_KEY exposta permite forjar cookies de sessão. Credenciais SMTP permitem envio de email não autorizado.
- **Recommendation:** Aplicar transformação "Extract Config". Mover todos os segredos para variáveis de ambiente usando `os.environ.get()`. Utilizar `python-dotenv` (já nas dependências mas não utilizado) para carregar `.env`.

---

### [CRITICAL] C4 — Broken / Missing Authentication

- **File:** `routes/user_routes.py:210`
- **Description:** O endpoint `/login` retorna um token falso: `'fake-jwt-token-' + str(user.id)`. Nenhuma rota possui middleware de autenticação — todos os endpoints (incluindo DELETE, PUT e endpoints de admin) são acessíveis publicamente sem qualquer verificação de token.
- **Impact:** Todas as operações destrutivas (DELETE `/users/{id}`, DELETE `/tasks/{id}`, PUT) estão completamente abertas. Qualquer pessoa pode deletar dados, modificar usuários e acessar relatórios sem autenticação.
- **Recommendation:** Aplicar transformação "Add Auth Middleware". Implementar autenticação JWT real com `flask-jwt-extended` e decorator `@jwt_required` nos endpoints protegidos.

---

### [CRITICAL] C1 — Password Leak in API Response

- **File:** `models/user.py:22`
- **Description:** O método `to_dict()` do modelo `User` inclui o hash da senha na resposta: `'password': self.password`. Os endpoints GET `/users`, GET `/users/{id}` e POST `/login` retornam o hash MD5 da senha na resposta JSON.
- **Impact:** Hash de senhas exposto via API permite ataques de rainbow table para reverter senhas MD5. Combinado com o uso de MD5 sem salt, as senhas podem ser quebradas em segundos.
- **Recommendation:** Remover o campo `password` do método `to_dict()`. Nunca expor hashes de senha em respostas de API.

---

### [HIGH] H1 — Insecure Password Storage (MD5)

- **File:** `models/user.py:29,32`
- **Description:** Senhas são armazenadas usando MD5 sem salt: `hashlib.md5(pwd.encode()).hexdigest()`. MD5 é um algoritmo de hash criptográfico obsoleto, extremamente rápido e vulnerável a rainbow tables. Não há nenhuma dependência de bcrypt, argon2 ou werkzeug.security no projeto.
- **Impact:** Em caso de vazamento do banco de dados, todas as senhas dos usuários podem ser revertidas em segundos usando rainbow tables públicas. MD5 sem salt é considerado completamente inseguro para armazenamento de senhas.
- **Recommendation:** Aplicar transformação "Secure Password Storage". Substituir MD5 por `werkzeug.security.generate_password_hash()` e `check_password_hash()` (já incluído como dependência do Flask).

---

### [HIGH] H2 — Business Logic in Route Handlers

- **File:** `routes/task_routes.py:1-300`, `routes/user_routes.py:1-212`, `routes/report_routes.py:1-224`
- **Description:** Todos os 3 arquivos de rotas contêm lógica de negócio inline: validação de campos, consultas ao banco de dados, serialização de objetos e cálculos de relatórios. Exemplos: `task_routes.py` faz validação de status, prioridade e título inline (linhas 92-114); `report_routes.py` calcula estatísticas de produtividade diretamente no handler (linhas 54-68); `user_routes.py` faz validação de email e senha inline (linhas 54-72). As rotas somam 736 linhas atuando como controllers.
- **Impact:** Impossível testar lógica de negócio sem camada HTTP. Mudanças em regras de negócio exigem modificação do código de roteamento. Viola separação de responsabilidades. Não existe diretório `controllers/`.
- **Recommendation:** Aplicar transformação "Extract Service Layer". Criar controllers dedicados em `controllers/` e mover toda lógica de validação, consulta e cálculos para os controllers. Rotas devem apenas definir endpoints e delegar para controllers.

---

### [HIGH] H4 — Duplicated Code

- **File:** `routes/task_routes.py:30-39,71-80,283-287`, `routes/user_routes.py:171-180`, `routes/report_routes.py:34-43,132-135`
- **Description:** A verificação de overdue (tarefa atrasada) está duplicada em **6 locais** diferentes com a mesma lógica: verificar `due_date`, comparar com `datetime.utcnow()`, verificar se status não é `done`/`cancelled`. O modelo `Task` já possui o método `is_overdue()` (linhas 50-60) que implementa a mesma lógica, mas **nenhuma rota o utiliza**. Além disso, a serialização de tarefas é feita manualmente em `task_routes.py:17-28` e `user_routes.py:162-169` em vez de usar `task.to_dict()`.
- **Impact:** Correções de bugs em uma cópia não se refletem nas outras. Comportamento inconsistente quando as cópias divergem. Manutenção multiplicada.
- **Recommendation:** Aplicar transformação "DRY Extract". Usar `task.is_overdue()` e `task.to_dict()` em todas as rotas. Centralizar a lógica de overdue no modelo.

---

### [MEDIUM] M1 — N+1 Query Pattern

- **File:** `routes/task_routes.py:42-57`
- **Description:** No endpoint GET `/tasks`, dentro de um loop iterando todas as tasks, são feitas queries individuais para `User.query.get(t.user_id)` e `Category.query.get(t.category_id)` para cada task. Com 100 tasks, isso gera 200+ queries adicionais ao invés de usar JOIN ou eager loading.
- **Impact:** Performance degrada linearmente com o volume de dados. Uma lista de 100 tasks gera 200+ queries ao banco em vez de 1-2 queries com JOIN.
- **Recommendation:** Aplicar transformação "Batch Query Optimization". Usar eager loading do SQLAlchemy: `Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()`.

---

### [MEDIUM] M3 — Dead Code / Unused Modules

- **File:** `services/notification_service.py:1-49`, `utils/helpers.py:57-108`
- **Description:** O arquivo `notification_service.py` **nunca é importado** por nenhum outro módulo do projeto — é completamente inativo. Em `utils/helpers.py`, as funções `process_task_data()`, `validate_email()`, `sanitize_string()`, `generate_id()`, `log_action()`, `is_valid_color()` e as constantes `VALID_STATUSES`, `VALID_ROLES`, etc. são definidas mas **nunca chamadas** (exceto `format_date` e `calculate_percentage` usados em `report_routes.py`). Nas dependências, `marshmallow==3.20.1`, `requests==2.31.0` e `python-dotenv==1.0.0` estão listados mas nunca importados no código.
- **Impact:** Aumenta o tamanho do codebase sem valor. Confunde leitura — sugere funcionalidade que não existe. Dependências não utilizadas aumentam superfície de ataque e tempo de instalação.
- **Recommendation:** Aplicar transformação "Remove Dead Code". Remover ou integrar o `notification_service.py` ao fluxo da aplicação. Utilizar as funções helper já existentes nas rotas ao invés de duplicar lógica. Remover dependências não utilizadas ou integrá-las.

---

### [MEDIUM] M4 — Bare Exception Handling

- **File:** `routes/task_routes.py:62,137,204,236`, `routes/user_routes.py:130,149`, `routes/report_routes.py:186,207,222`
- **Description:** Existem **9 blocos** `except:` (bare except sem tipo de exceção) espalhados pelos arquivos de rotas. Exemplos: `task_routes.py:62` captura qualquer exceção e retorna `{'error': 'Erro interno'}` sem logging; `task_routes.py:137` captura exceção na criação de task sem diferenciar tipo de erro. Nenhum bare except faz logging da exceção real.
- **Impact:** Erros são silenciosamente engolidos. Impossível debugar problemas em produção. Exceções de bugs ou infraestrutura ficam ocultas atrás de mensagens genéricas.
- **Recommendation:** Aplicar transformação "Centralize Error Handling". Substituir bare excepts por tipos específicos de exceção. Implementar middleware global de error handling com Flask `@app.errorhandler()`.

---

### [LOW] L1 — Debug Mode & Open CORS in Production

- **File:** `app.py:15,34`
- **Description:** `app.run(debug=True)` hardcoded na linha 34 — ativa debugger interativo em produção. `CORS(app)` na linha 15 sem parâmetro `origins` — aceita requisições de qualquer origem. Múltiplas instruções `print()` espalhadas pelo código para logging (task_routes:149,153,219,234; user_routes:83,89,147).
- **Impact:** Debug mode expõe traceback interativo em produção, permitindo execução remota de código. CORS wildcard permite requisições cross-origin de qualquer domínio. Print statements não são adequados para logging em produção.
- **Recommendation:** Ler flag de debug de variável de ambiente. Configurar CORS com origens específicas permitidas. Substituir `print()` pelo módulo `logging` do Python.

---

### [LOW] L3 — Unused Imports

- **File:** `app.py:7`, `routes/task_routes.py:7`
- **Description:** `app.py:7` importa `os, sys, json, datetime` — `os`, `sys` e `json` não são usados no arquivo. `task_routes.py:7` importa `json, os, sys, time` — nenhum destes módulos é utilizado no arquivo. `user_routes.py:6` importa `hashlib, json` — `hashlib` e `json` não são utilizados.
- **Impact:** Aumenta carga cognitiva na leitura dos imports. Sugere dependências inexistentes.
- **Recommendation:** Remover imports não utilizados.

---

================================
Total: 11 findings (3 CRITICAL, 3 HIGH, 3 MEDIUM, 2 LOW)
================================

> **Nota:** Verificação de APIs deprecadas via context7 para Flask 3.0.0 não retornou resultados específicos de deprecação. As APIs utilizadas no projeto são compatíveis com Flask 3.0.0.
