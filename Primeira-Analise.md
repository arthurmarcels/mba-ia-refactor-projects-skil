# Primeira Análise Manual — Anti-Patterns e Code Smells

Análise manual dos 3 projetos legados para identificação de problemas arquiteturais, de segurança e de qualidade de código. Esta análise serve como insumo para a construção do catálogo de anti-patterns da skill `refactor-arch`.

---

## Sumário por Projeto

| Projeto | Stack | LOC | Endpoints | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|---|
| code-smells-project | Python/Flask | 782 | 18 | 4 | 4 | 3 | 2 | 13 |
| ecommerce-api-legacy | Node.js/Express | 180 | 3 | 3 | 5 | 2 | 2 | 12 |
| task-manager-api | Python/Flask | 1.164 | 22 | 4 | 5 | 2 | 2 | 13 |

---

## Projeto 1 — code-smells-project (Python/Flask E-Commerce API)

**Stack:** Python 3 + Flask 3.1.1 + SQLite (raw SQL)
**Arquitetura:** Monolítica — 4 arquivos sem separação real de camadas
**Domínio:** API de E-commerce (produtos, usuários, pedidos, relatórios)

### [CRITICAL-1] SQL Injection — Generalizado

- **Arquivo:** `models.py` (linhas 28, 48-49, 109-110, 289-297)
- **Descrição:** Todas as queries SQL usam concatenação de strings em vez de queries parametrizadas. Exemplo em `models.py:28`: `"SELECT * FROM produtos WHERE id = " + str(id)`. O login (`models.py:109-110`) concatena email e senha diretamente na query.
- **Impacto:** Qualquer input do usuário pode executar SQL arbitrário no banco. Vulnerabilidade clássica de segurança.
- **Severidade:** CRITICAL

### [CRITICAL-2] Endpoint de Execução Arbitrária de SQL

- **Arquivo:** `app.py` (linhas 59-78)
- **Descrição:** O endpoint `POST /admin/query` recebe SQL bruto no body da requisição e executa diretamente no banco. Sem autenticação, sem autorização, sem validação.
- **Impacto:** Qualquer pessoa pode DROP TABLE, ler dados sensíveis, ou modificar o banco remotamente.
- **Severidade:** CRITICAL

### [CRITICAL-3] Credenciais Hardcoded

- **Arquivo:** `app.py:7` — `SECRET_KEY = "minha-chave-super-secreta-123"`
- **Arquivo:** `controllers.py:289` — Secret key exposta no endpoint `/health`
- **Arquivo:** `database.py` (seed data) — Senhas em plaintext: `admin123`, `123456`, `senha123`
- **Descrição:** Chave secreta do Flask hardcoded como string literal. Senhas de usuários armazenadas em plaintext no banco. A chave secreta é retornada no endpoint de health check.
- **Impacto:** Qualquer pessoa com acesso ao código ou ao endpoint `/health` obtém a SECRET_KEY. Senhas podem ser lidas diretamente do banco.
- **Severidade:** CRITICAL

### [CRITICAL-4] Sem Autenticação/Autorização

- **Arquivo:** `app.py` (inteiro)
- **Descrição:** Não existe middleware de autenticação, JWT, sessão, ou qualquer controle de acesso. Todos os endpoints estão completamente abertos, incluindo os endpoints admin (`/admin/reset-db`, `/admin/query`).
- **Impacto:** Endpoints destrutivos e sensíveis são acessíveis por qualquer cliente HTTP.
- **Severidade:** CRITICAL

### [HIGH-1] Conexão DB Global Não Thread-Safe

- **Arquivo:** `database.py` — `db_connection` global com `check_same_thread=False`
- **Descrição:** Conexão SQLite única e global compartilhada entre todas as threads do Flask. SQLite não é thread-safe por padrão.
- **Impacto:** Condições de corrida sob carga concorrente. Dados corrompidos ou crashes.
- **Severidade:** HIGH

### [HIGH-2] Senhas em Plaintext — Sem Hashing

- **Arquivo:** `models.py:109-110` (login), `database.py` (seed)
- **Descrição:** Senhas armazenadas e comparadas em plaintext. O login faz `SELECT * FROM usuarios WHERE email = ... AND senha = ...` com concatenação direta.
- **Impacto:** Vazamento do banco expõe todas as senhas diretamente.
- **Severidade:** HIGH

### [HIGH-3] Duplicação de Código — Queries de Pedidos

- **Arquivo:** `models.py:171-201` (`get_pedidos_usuario`) vs `models.py:203-233` (`get_todos_pedidos`)
- **Descrição:** Duas funções quase idênticas que diferem apenas na cláusula WHERE. Ambas contêm padrão N+1 (loop interno com cursor novo para cada item).
- **Impacto:** Manutenção duplicada. Bug fix em um não reflete no outro.
- **Severidade:** HIGH

### [HIGH-4] Notificações Fakes

- **Arquivo:** `controllers.py:208-210`
- **Descrição:** Lógica de notificação é apenas `print("ENVIANDO EMAIL")`, `print("ENVIANDO SMS")`, `print("ENVIANDO PUSH")`. Simula envio sem integração real.
- **Impacto:** Notificações nunca são enviadas. Código enganoso que parece funcional.
- **Severidade:** HIGH

### [MEDIUM-1] Registro de Rotas Inconsistente

- **Arquivo:** `app.py`
- **Descrição:** A maioria das rotas usa `app.add_url_rule()`, mas `/` e `/admin/*` usam `@app.route()`. Dois padrões diferentes no mesmo arquivo.
- **Impacto:** Confusão na manutenção. Não segue convenção única.
- **Severidade:** MEDIUM

### [MEDIUM-2] Validação na Camada Errada

- **Arquivo:** `controllers.py` (várias funções)
- **Descrição:** Validação de input (tamanho de nome, categorias válidas, etc.) está nos controllers, não nos models. A camada de models tem zero validação.
- **Impacto:** Models podem receber dados inválidos se chamados diretamente. Violação do princípio de que cada camada deve validar seu domínio.
- **Severidade:** MEDIUM

### [MEDIUM-3] Lógica de Negócio Misturada com Controllers

- **Arquivo:** `controllers.py` (função `criar_pedido`), `models.py` (função `relatorio_vendas`)
- **Descrição:** Controller de pedido contém orquestração de notificações. Model de relatório contém lógica de cálculo de desconto. Responsabilidades misturadas entre camadas.
- **Impacto:** Difícil testar isoladamente. Mudança na regra de negócio requer alteração em controller.
- **Severidade:** MEDIUM

### [LOW-1] Debug Mode Habilitado em Produção

- **Arquivo:** `app.py` — `app.run(debug=True)` e `app.config["DEBUG"] = True`
- **Descrição:** Debug mode habilitado como padrão. Em produção, expõe traceback interativo.
- **Severidade:** LOW

### [LOW-2] CORS Sem Restrição

- **Arquivo:** `app.py` — `CORS(app)` sem parâmetros
- **Descrição:** CORS configurado para aceitar requisições de qualquer origem.
- **Severidade:** LOW

---

## Projeto 2 — ecommerce-api-legacy (Node.js/Express LMS API)

**Stack:** Node.js + Express 4.18 + SQLite (in-memory, raw sqlite3)
**Arquitetura:** God Class — 1 classe faz tudo (DB init + schema + seed + rotas + lógica)
**Domínio:** API de LMS com fluxo de checkout (cursos, matrículas, pagamentos)

### [CRITICAL-1] Credenciais Hardcoded em Plaintext

- **Arquivo:** `src/utils.js:3` — `dbPass: "senha_super_secreta_prod_123"`
- **Arquivo:** `src/utils.js:4` — `paymentGatewayKey: "pk_live_1234567890abcdef"`
- **Arquivo:** `src/AppManager.js:45` — Número do cartão de crédito logado no console: `console.log('Processando cartão ${cc} na chave ${config.paymentGatewayKey}')`
- **Descrição:** Senha de banco, chave de gateway de pagamento e número do cartão expostos como strings literais e em logs.
- **Impacto:** Violação de PCI-DSS. Dados de cartão em logs. Credenciais de produção no código-fonte.
- **Severidade:** CRITICAL

### [CRITICAL-2] Lógica de Pagamento Fake e Insegura

- **Arquivo:** `src/AppManager.js` (função de checkout, ~linha 45)
- **Descrição:** Aprovação de cartão baseada em se o número começa com "4" (prefixo Visa). Número do cartão é aceito integralmente e impresso no console. Não há integração com gateway de pagamento real.
- **Impacto:** Qualquer cartão começando com "4" é aprovado. Números de cartão ficam em logs.
- **Severidade:** CRITICAL

### [CRITICAL-3] Criptografia Inútil (badCrypto)

- **Arquivo:** `src/utils.js:17-23` — função `badCrypto()`
- **Descrição:** A função faz base64 encode 10.000 vezes e trunca para 10 caracteres. Não é hashing criptográfico — é trivialmente reversível.
- **Impacto:** Senhas "hasheadas" podem ser revertidas. Segurança falsa que engana revisores.
- **Severidade:** CRITICAL

### [HIGH-1] God Class / God Method

- **Arquivo:** `src/AppManager.js` (141 linhas — arquivo inteiro)
- **Descrição:** Classe `AppManager` é dona de: inicialização do DB, criação de schema, seed de dados, definição de TODAS as rotas, e lógica de negócio inline. O handler `/api/checkout` tem ~50 linhas com 4 níveis de nesting.
- **Impacto:** Impossível testar em isolamento. Mudança em qualquer aspecto afeta o arquivo inteiro.
- **Severidade:** HIGH

### [HIGH-2] Callback Hell (Pyramid of Doom)

- **Arquivo:** `src/AppManager.js` (função de checkout)
- **Descrição:** O fluxo de checkout aninha callbacks 4+ níveis: course lookup → user lookup → create user → insert enrollment → insert payment → insert audit log. Cada nível com seu próprio error handling.
- **Impacto:** Difícil de ler, manter e debugar. Error handling inconsistente entre níveis.
- **Severidade:** HIGH

### [HIGH-3] Banco de Dados In-Memory

- **Arquivo:** `src/AppManager.js` — `new sqlite3.Database(':memory:')`
- **Descrição:** Banco SQLite em memória. Todos os dados são perdidos a cada restart do servidor.
- **Impacto:** Aplicação não persiste estado. Inviável para qualquer uso real.
- **Severidade:** HIGH

### [HIGH-4] Estado Global Mutável

- **Arquivo:** `src/utils.js` — `globalCache = {}` e `totalRevenue = 0`
- **Descrição:** Variáveis module-level mutáveis compartilhadas entre todas as requisições. `totalRevenue` é declarado mas nunca atualizado. `logAndCache()` armazena dados em objeto in-memory sem limite.
- **Impacto:** Memory leak potencial. Dados de uma requisição contaminam outra. `totalRevenue` é dead code.
- **Severidade:** HIGH

### [HIGH-5] Dados Órfãos ao Deletar Usuário

- **Arquivo:** `src/AppManager.js` — endpoint `DELETE /api/users/:id`
- **Descrição:** Ao deletar um usuário, matrículas e pagamentos permanecem no banco. O código literalmente responde "as matrículas e pagamentos ficaram sujos no banco".
- **Impacto:** Integridade referencial violada. Dados órfãos acumulam.
- **Severidade:** HIGH

### [MEDIUM-1] Erros Sem Estrutura

- **Arquivo:** `src/AppManager.js` (múltiplos catch blocks)
- **Descrição:** Mensagens de erro genéricas como "Erro DB", "Erro Matrícula", "Erro Pagamento" sem status codes, sem tipo, sem detalhe.
- **Impacto:** Impossível debugar por logs. Cliente não sabe o que aconteceu.
- **Severidade:** MEDIUM

### [MEDIUM-2] Sem Validação de Input

- **Arquivo:** `src/AppManager.js` (função de checkout)
- **Descrição:** O endpoint verifica presença de campos mas não valida tipos, tamanhos ou sanitiza valores. Qualquer valor passa diretamente para o banco.
- **Impacto:** Dados inválidos ou maliciosos são aceitos sem restrição.
- **Severidade:** MEDIUM

### [LOW-1] Nomes de Variáveis Ofuscados

- **Arquivo:** `src/AppManager.js` (função de checkout)
- **Descrição:** Variáveis como `u`, `e`, `p`, `cid`, `cc` em vez de `name`, `email`, `password`, `courseId`, `cardNumber`.
- **Impacto:** Legibilidade muito baixa. Difícil entender o que cada variável representa.
- **Severidade:** LOW

### [LOW-2] Dead Code — `totalRevenue`

- **Arquivo:** `src/utils.js` — `totalRevenue = 0`
- **Descrição:** Variável declarada e exportada mas nunca modificada em nenhuma parte do código.
- **Impacto:** Código morto que sugere funcionalidade inexistente.
- **Severidade:** LOW

---

## Projeto 3 — task-manager-api (Python/Flask Task Manager)

**Stack:** Python 3 + Flask 3.0 + Flask-SQLAlchemy + SQLite
**Arquitetura:** Parcialmente organizada (models/, routes/, services/, utils/) mas sem separação real de responsabilidades
**Domínio:** API de Task Manager (tarefas, usuários, categorias, relatórios)

### [CRITICAL-1] Credenciais Hardcoded

- **Arquivo:** `app.py:13` — `SECRET_KEY = 'super-secret-key-123'`
- **Arquivo:** `services/notification_service.py:9-10` — Credenciais SMTP hardcoded: `email_password = 'senha123'`
- **Descrição:** Secret key do Flask e senha de email hardcoded como strings literais no código-fonte.
- **Impacto:** Qualquer pessoa com acesso ao código obtém as credenciais de produção.
- **Severidade:** CRITICAL

### [CRITICAL-2] MD5 para Hash de Senhas

- **Arquivo:** `models/user.py:29` — `hashlib.md5()`
- **Descrição:** Senhas hasheadas com MD5 sem salt. MD5 é criptograficamente quebrado e inadequado para senhas.
- **Impacto:** Senhas podem ser quebradas via rainbow tables em segundos.
- **Severidade:** CRITICAL

### [CRITICAL-3] Autenticação JWT Fake

- **Arquivo:** `routes/user_routes.py:210` — `'fake-jwt-token-' + str(user.id)`
- **Descrição:** Login retorna um token fake (`fake-jwt-token-<user_id>`). Não há verificação real de JWT, middleware de autenticação, ou rotas protegidas. Nenhum endpoint valida o token.
- **Impacto:** Sistema de autenticação completamente ineficaz. Todos os endpoints são abertos.
- **Severidade:** CRITICAL

### [CRITICAL-4] Senha Exposta na Resposta da API

- **Arquivo:** `models/user.py:21` — `User.to_dict()` inclui campo `password`
- **Descrição:** O hash da senha é retornado em TODAS as respostas da API de usuários (GET /users, GET /users/:id, POST /login).
- **Impacto:** Hash de senhas exposto publicamente. Com MD5 fraco, é equivalente a expor a senha.
- **Severidade:** CRITICAL

### [HIGH-1] Arquivos de Rota como Controllers — Sem Separação

- **Arquivo:** `routes/task_routes.py` (299 linhas), `routes/user_routes.py` (211 linhas), `routes/report_routes.py` (223 linhas)
- **Descrição:** Cada arquivo de rotas contém CRUD completo, validação, serialização e lógica de negócio inline. Routes são simultaneamente routes, controllers e services. Apesar de existir `services/`, o único service (NotificationService) é dead code.
- **Impacto:** Arquivos de rota inchados. Impossível testar lógica de negócio sem HTTP. Mudança em regra de negócio requer alteração em route handler.
- **Severidade:** HIGH

### [HIGH-2] Lógica Overdue Duplicada 7x

- **Arquivo:** `routes/task_routes.py` (linhas 30-39, 71-80, 282-287), `routes/user_routes.py` (linhas 171-180), `routes/report_routes.py` (linhas 33-43, 132-135), `models/task.py` (linhas 50-59)
- **Descrição:** A verificação de tarefa atrasada (`if t.due_date < datetime.utcnow() and status not in ['done','cancelled']`) é reimplementada inline em 7 locais diferentes. O método `Task.is_overdue()` existe no model mas **nunca é chamado**.
- **Impacto:** Se a regra mudar, 7 locais precisam ser atualizados inconsistentemente. Bug em potencial.
- **Severidade:** HIGH

### [HIGH-3] Serialização Duplicada

- **Arquivo:** `routes/task_routes.py` (get_tasks), `routes/user_routes.py` (get_user_tasks)
- **Descrição:** `get_tasks` constrói dicts manualmente campo a campo em vez de usar `Task.to_dict()`. O mesmo padrão se repete em `get_user_tasks`.
- **Impacto:** Se o model mudar, serializações manuais quebram silenciosamente.
- **Severidade:** HIGH

### [HIGH-4] NotificationService é Dead Code

- **Arquivo:** `services/notification_service.py` (48 linhas inteiras)
- **Descrição:** Service completo definido com configuração SMTP, métodos de envio, mas **nunca importado ou chamado** em nenhum outro arquivo do projeto.
- **Impacto:** 48 linhas mortas. Funcionalidade de notificação não existe na prática.
- **Severidade:** HIGH

### [HIGH-5] CRUD de Categorias no Blueprint Errado

- **Arquivo:** `routes/report_routes.py` — endpoints de Category (POST, PUT, DELETE)
- **Descrição:** Operações CRUD de categorias vivem no blueprint de relatórios em vez de ter seu próprio blueprint ou arquivo de rotas dedicado.
- **Impacto:** Violação de responsabilidade única. Relatórios e categorias são domínios diferentes misturados.
- **Severidade:** HIGH

### [MEDIUM-1] Bare Except Clauses

- **Arquivo:** `routes/task_routes.py` (linhas 62, 137, 204), `routes/user_routes.py` (linhas 130, 149), `routes/report_routes.py` (linhas 186, 208, 221)
- **Descrição:** Múltiplos blocos `except:` que capturam todas as exceções silenciosamente, sem logar ou classificar o erro.
- **Impacto:** Erros são engolidos. Impossível debugar falhas em produção.
- **Severidade:** MEDIUM

### [MEDIUM-2] N+1 Queries em Relatórios

- **Arquivo:** `routes/report_routes.py` (summary_report, user_report)
- **Descrição:** Relatórios iteram sobre todas as tarefas/usuários com queries individuais em vez de usar queries de agregação (COUNT, AVG, GROUP BY).
- **Impacto:** Performance degradada conforme volume de dados cresce.
- **Severidade:** MEDIUM

### [LOW-1] Imports Não Utilizados

- **Arquivo:** Múltiplos arquivos importam módulos nunca usados (`json`, `os`, `sys`, `time`, `math`, `hashlib` em contextos desnecessários)
- **Descrição:** Imports mortos que aumentam o footprint sem motivo.
- **Severidade:** LOW

### [LOW-2] `datetime.utcnow` como Default

- **Arquivo:** `models/task.py`, `models/user.py`
- **Descrição:** Usa `datetime.utcnow` como default do SQLAlchemy em vez de `func.now()` para defaults a nível de banco.
- **Impacto:** Timestamps dependem do horário do servidor em vez do horário do banco. Menor consistência em deployments distribuídos.
- **Severidade:** LOW

---

## Matriz de Cobertura Cross-Projeto

| Anti-Pattern | P1 | P2 | P3 | Severidade |
|---|:---:|:---:|:---:|---|
| Hardcoded Secrets/Credentials | X | X | X | CRITICAL |
| SQL Injection | X | | | CRITICAL |
| God Class / God Method | X | X | | CRITICAL |
| Autenticação Ausente ou Fake | X | X | X | CRITICAL |
| Senhas em Plaintext / Hash Fraco | X | X | X | HIGH |
| Business Logic em Route Handler | X | | X | HIGH |
| Callback Hell / Pyramid of Doom | | X | | HIGH |
| Código Duplicado | X | | X | HIGH |
| Dead Code / Módulos Não Usados | | X | X | MEDIUM |
| N+1 Query Pattern | X | | X | MEDIUM |
| Validação de Input Ausente | X | X | X | MEDIUM |
| Error Handling Inadequado | | X | X | MEDIUM |
| Nomes de Variáveis Ruins | | X | | LOW |
| Magic Numbers / Debug em Produção | X | | X | LOW |

**Cobertura:** 14 anti-patterns identificados, distribuídos em 4 níveis de severidade, com cobertura em todos os 3 projetos.

---

*Análise realizada manualmente antes da criação da skill, conforme Requisito 1 do desafio.*
