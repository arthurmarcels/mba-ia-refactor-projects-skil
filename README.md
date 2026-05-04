# Criação de Skills — Refatoração Arquitetural Automatizada

Skill `refactor-arch` para Claude Code que analisa, audita e refatora projetos legados para o padrão MVC, de forma agnóstica de tecnologia. Testada com sucesso em 3 projetos (2× Python/Flask, 1× Node.js/Express), detectando 44 findings e corrigindo todos com validação automatizada.

**Ferramenta utilizada:** Claude Code  
**Skill:** `.claude/skills/refactor-arch/`  
**Projetos-alvo:** `code-smells-project/`, `ecommerce-api-legacy/`, `task-manager-api/`

---

## A) Análise Manual

Antes de criar a skill, cada projeto foi analisado manualmente para identificar problemas arquiteturais, de segurança e de qualidade. A análise completa está em [`Primeira-Analise.md`](Primeira-Analise.md).

### Sumário Geral

| Projeto | Stack | LOC | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|
| code-smells-project | Python/Flask 3.1.1 | 782 | 4 | 4 | 3 | 2 | 13 |
| ecommerce-api-legacy | Node.js/Express 4.18 | 180 | 3 | 5 | 2 | 2 | 12 |
| task-manager-api | Python/Flask 3.0.0 | 1.164 | 4 | 5 | 2 | 2 | 13 |
| **Total** | | **2.126** | **11** | **14** | **7** | **6** | **38** |

### Projeto 1 — code-smells-project (Python/Flask E-Commerce API)

**Arquitetura:** Monolítica — 4 arquivos sem separação real de camadas

| # | Severidade | Problema | Arquivo | Justificativa |
|---|---|---|---|---|
| 1 | CRITICAL | SQL Injection generalizado | `models.py:28, 48, 109, 289` | Todas as queries usam concatenação de strings. Login permite bypass com `' OR '1'='1`. |
| 2 | CRITICAL | Endpoint executa SQL arbitrário | `app.py:59-78` | `POST /admin/query` recebe SQL bruto e executa sem auth. Equivale a expor o banco publicamente. |
| 3 | CRITICAL | Credenciais hardcoded | `app.py:7`, `controllers.py:289` | SECRET_KEY como literal + exposta no `/health`. Senhas em plaintext no seed. |
| 4 | CRITICAL | Sem autenticação | `app.py` (inteiro) | Zero middleware de auth. Endpoints admin completamente abertos. |
| 5 | HIGH | Senhas em plaintext | `models.py:109`, `database.py:30` | Sem hashing. Login compara strings. API retorna campo senha. |
| 6 | HIGH | Conexão DB global não thread-safe | `database.py` | Conexão SQLite global com `check_same_thread=False`. |
| 7 | HIGH | Código duplicado em queries | `models.py:171-233` | Duas funções quase idênticas para listar pedidos, ambas com N+1. |
| 8 | HIGH | Notificações fake | `controllers.py:208-210` | `print("ENVIANDO EMAIL")` simula envio sem integração real. |
| 9 | MEDIUM | Registro de rotas inconsistente | `app.py` | Mistura `app.add_url_rule()` e `@app.route()` no mesmo arquivo. |
| 10 | MEDIUM | Validação na camada errada | `controllers.py` | Validação nos controllers, zero validação nos models. |
| 11 | MEDIUM | Lógica de negócio misturada | `controllers.py`, `models.py` | Controller contém notificações. Model contém cálculo de desconto. |
| 12 | LOW | Debug mode em produção | `app.py:88` | `app.run(debug=True)` hardcoded. |
| 13 | LOW | CORS sem restrição | `app.py:9` | `CORS(app)` aceita qualquer origem. |

### Projeto 2 — ecommerce-api-legacy (Node.js/Express LMS API)

**Arquitetura:** God Class — 1 classe (`AppManager`) faz tudo (DB + rotas + lógica)

| # | Severidade | Problema | Arquivo | Justificativa |
|---|---|---|---|---|
| 1 | CRITICAL | Credenciais hardcoded + PCI | `utils.js:3-4`, `AppManager.js:45` | Senha DB, chave de pagamento e número de cartão logados no console. Viola PCI-DSS. |
| 2 | CRITICAL | Pagamento fake e inseguro | `AppManager.js:45` | Aprovação baseada em prefixo "4" (Visa). Sem gateway real. |
| 3 | CRITICAL | Criptografia inútil (badCrypto) | `utils.js:17-23` | Base64 encode 10k vezes, truncado para 10 chars. Trivialmente reversível. |
| 4 | HIGH | God Class | `AppManager.js` (142 linhas) | Uma classe com DB init, schema, seed, rotas e lógica de negócio. |
| 5 | HIGH | Callback Hell | `AppManager.js:37-77` | 5 níveis de nesting no checkout. Error handling repetido em cada nível. |
| 6 | HIGH | Banco in-memory | `AppManager.js` | `sqlite3.Database(':memory:')`. Dados perdidos a cada restart. |
| 7 | HIGH | Estado global mutável | `utils.js` | `globalCache` sem limite + `totalRevenue` nunca atualizado (dead code). |
| 8 | HIGH | Dados órfãos ao deletar usuário | `AppManager.js` | DELETE não faz cascade em matrículas e pagamentos. |
| 9 | MEDIUM | Erros sem estrutura | `AppManager.js` | Mensagens genéricas ("Erro DB") sem status codes diferenciados. |
| 10 | MEDIUM | Sem validação de input | `AppManager.js:29-35` | Só null checks, sem validação de tipo, formato ou sanitização. |
| 11 | LOW | Nomes de variáveis ofuscados | `AppManager.js:29-33` | `u`, `e`, `p`, `cid`, `cc` em vez de nomes descritivos. |
| 12 | LOW | Dead code — totalRevenue | `utils.js` | Declarado e exportado mas nunca modificado. |

### Projeto 3 — task-manager-api (Python/Flask Task Manager)

**Arquitetura:** Parcialmente organizada (`models/`, `routes/`, `services/`, `utils/`) mas sem separação real de responsabilidades

| # | Severidade | Problema | Arquivo | Justificativa |
|---|---|---|---|---|
| 1 | CRITICAL | Credenciais hardcoded | `app.py:13`, `notification_service.py:9-10` | SECRET_KEY e credenciais SMTP como literals. |
| 2 | CRITICAL | MD5 para hash de senhas | `models/user.py:29` | MD5 sem salt. Quebrado via rainbow tables em segundos. |
| 3 | CRITICAL | Autenticação JWT fake | `user_routes.py:210` | Retorna `'fake-jwt-token-' + str(user.id)`. Nenhuma rota valida token. |
| 4 | CRITICAL | Senha exposta na API | `models/user.py:21` | `to_dict()` inclui campo `password`. Hash MD5 exposto em GET/POST. |
| 5 | HIGH | Rotas atuam como controllers | `task_routes.py` (299 LOC) | 3 arquivos de rotas com CRUD, validação e lógica inline. 736 LOC no total. |
| 6 | HIGH | Overdue check duplicado 7× | 7 locais diferentes | Mesma lógica reimplementada. `Task.is_overdue()` existe mas nunca é chamado. |
| 7 | HIGH | Serialização duplicada | `task_routes.py`, `user_routes.py` | Constrói dicts manuais em vez de usar `Task.to_dict()`. |
| 8 | HIGH | NotificationService é dead code | `notification_service.py` (48 LOC) | Nunca importado por nenhum módulo. |
| 9 | HIGH | CRUD de categorias no blueprint errado | `report_routes.py` | Endpoints de Category vivem no blueprint de relatórios. |
| 10 | MEDIUM | Bare except clauses | 8 locais em routes/ | `except:` sem tipo, sem logging. Erros engolidos silenciosamente. |
| 11 | MEDIUM | N+1 queries | `task_routes.py:42-57` | Queries individuais por task para User e Category. |
| 12 | LOW | Imports não utilizados | Múltiplos arquivos | `json`, `os`, `sys`, `time`, `hashlib` importados sem uso. |
| 13 | LOW | `datetime.utcnow` como default | `models/task.py`, `user.py` | Deveria usar `func.now()` para consistência do banco. |

### Matriz de Cobertura Cross-Projeto

| Anti-Pattern | P1 | P2 | P3 | Severidade |
|---|:---:|:---:|:---:|---|
| Hardcoded Secrets/Credentials | ✓ | ✓ | ✓ | CRITICAL |
| SQL Injection | ✓ | | | CRITICAL |
| God Class / God Method | ✓ | ✓ | | CRITICAL |
| Autenticação Ausente ou Fake | ✓ | ✓ | ✓ | CRITICAL |
| Senhas Plaintext / Hash Fraco | ✓ | ✓ | ✓ | HIGH |
| Business Logic em Route Handler | ✓ | | ✓ | HIGH |
| Callback Hell | | ✓ | | HIGH |
| Código Duplicado | ✓ | | ✓ | HIGH |
| Dead Code / Módulos Não Usados | | ✓ | ✓ | MEDIUM |
| N+1 Query Pattern | ✓ | | ✓ | MEDIUM |
| Validação de Input Ausente | ✓ | ✓ | ✓ | MEDIUM |
| Error Handling Inadequado | | ✓ | ✓ | MEDIUM |
| Nomes de Variáveis Ruins | | ✓ | | LOW |
| Magic Numbers / Debug em Produção | ✓ | | ✓ | LOW |

**14 anti-patterns identificados** cobrindo 4 níveis de severidade em todos os 3 projetos.

---

## B) Construção da Skill

### Estrutura da Skill

```
.claude/skills/refactor-arch/
├── SKILL.md                        # Orquestrador (3 fases + integração com tools)
├── project-analysis.md             # Heurísticas de análise (Fase 1)
├── anti-patterns-catalog.md        # Catálogo com 23 anti-patterns (Fase 2)
├── audit-report-template.md        # Template padronizado de relatório (Fase 2)
├── mvc-guidelines.md               # Regras do padrão MVC alvo (Fase 3)
└── refactoring-playbook.md         # 12 transformações com before/after (Fase 3)
```

### Decisões de Design

**D1 — Arquivos separados por área de conhecimento:** Cada arquivo de referência cobre exatamente uma das 5 áreas obrigatórias. O SKILL.md carrega instruções do workflow; os arquivos de referência são consultados sob demanda por fase. Isso evita desperdiçar tokens carregando todo o conhecimento de uma vez (progressive disclosure — padrão Anthropic).

**D2 — Integração com `sequential-thinking`:** O SKILL.md instrui o agente a usar sequential-thinking como motor de raciocínio em cada fase. Isso força análise passo a passo: na Fase 1, heurísticas são verificadas uma a uma; na Fase 2, cada anti-pattern é cruzado contra cada arquivo; na Fase 3, transformações são planejadas antes de executar.

**D3 — Integração com `context7` para APIs deprecated:** Em vez de hardcodar "Flask 2.x deprecated X" (o que tornaria a skill frágil), a Fase 2 usa context7 para resolver a lib detectada na Fase 1 e consultar dinamicamente a documentação sobre APIs deprecated daquela versão específica.

**D4 — Playbook dual-stack:** Cada transformação no playbook inclui exemplos before/after em **ambas** as stacks (Python/Flask e Node.js/Express). Isso garante que o agente tenha referências concretas independente do projeto alvo, em vez de tentar "traduzir" exemplos de uma linguagem para outra.

**D5 — Catálogo expandido:** O catálogo contém **23 anti-patterns** (vs. 8 mínimo exigido) distribuídos nos 4 níveis de severidade. A expansão garante cobertura cross-projeto — cada projeto tem problemas diferentes, e um catálogo maior aumenta a probabilidade de detecção.

### Anti-patterns incluídos no catálogo

O catálogo cobre 23 anti-patterns organizados por severidade:

| Código | Anti-Pattern | Severidade | Por que incluído |
|---|---|---|---|
| C1 | Hardcoded Secrets/Credentials | CRITICAL | Presente em todos os 3 projetos |
| C2 | SQL Injection | CRITICAL | Generalizado no P1, ausente nos demais |
| C3 | God Class / God Method | CRITICAL | P1 (models.py) e P2 (AppManager.js) |
| C4 | Broken/Missing Authentication | CRITICAL | Presente em todos os 3 projetos |
| H1 | Insecure Password Storage | HIGH | Plaintext (P1), badCrypto (P2), MD5 (P3) |
| H2 | Business Logic in Route Handlers | HIGH | P1 e P3 — controllers/rotas com regras |
| H3 | Callback Hell / Pyramid of Doom | HIGH | Específico do P2 (Node.js) |
| H4 | Duplicated Code | HIGH | P1 (queries) e P3 (overdue 7×) |
| H5 | Tight Coupling / No DI | HIGH | Cross-projeto |
| M1 | N+1 Query Pattern | MEDIUM | P1 e P3 |
| M2 | Missing Input Validation | MEDIUM | Presente em todos os 3 projetos |
| M3 | Dead Code / Unused Modules | MEDIUM | P2 (totalRevenue) e P3 (notification) |
| M4 | Bare Exception Handling | MEDIUM | P1 (16×) e P3 (9×) |
| DP | Deprecated API Usage | HIGH | Detecção dinâmica via context7 |
| L1-L4 | Magic Numbers, Poor Naming, etc. | LOW | Problemas de legibilidade |

### Como a agnosticidade foi garantida

1. **Zero referência a projeto específico no SKILL.md** — a skill não menciona nomes de arquivos, pastas ou frameworks fixos. Tudo é detectado dinamicamente na Fase 1.
2. **Heurísticas de detecção por sinais** — `project-analysis.md` usa sinais como presença de `requirements.txt` (Python), `package.json` (Node.js), imports de `flask`/`express` para determinar a stack.
3. **Playbook dual-stack** — cada transformação tem exemplos concretos em Python/Flask E Node.js/Express.
4. **Catálogo baseado em conceitos, não syntax** — anti-patterns como "God Class" ou "Hardcoded Secrets" são definidos por sinais comportamentais, não por syntax específica.
5. **context7 para deprecated APIs** — consulta dinâmica por versão detectada, não lista estática.
6. **Testada em 3 projetos diferentes** — 2 stacks (Python/Flask, Node.js/Express) com 3 níveis de organização (monolito, god class, MVC parcial).

### Desafios encontrados e soluções

| Desafio | Solução |
|---|---|
| P3 já tem estrutura MVC parcial — skill poderia achar que "está ok" | Heurísticas verificam qualidade do código DENTRO das pastas, não apenas existência de diretórios |
| Token limit — SKILL.md + 5 referências é muito conteúdo | Progressive disclosure: SKILL.md contém apenas o workflow, referências são carregadas por fase |
| Playbook dual-stack dobra o tamanho | Trade-off aceito: necessário para agnosticidade real |
| context7 pode não ter docs para todas as versões | Fallback: se context7 não retorna, skill documenta que não foi possível verificar |

---

## C) Resultados

### Resumo dos Relatórios de Auditoria

Os relatórios completos estão em `reports/audit-project-{1,2,3}.md`.

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total | Relatório |
|---|---|---|---|---|---|---|
| code-smells-project | 5 | 5 | 5 | 5 | **20** | [`audit-project-1.md`](reports/audit-project-1.md) |
| ecommerce-api-legacy | 3 | 4 | 3 | 3 | **13** | [`audit-project-2.md`](reports/audit-project-2.md) |
| task-manager-api | 3 | 3 | 3 | 2 | **11** | [`audit-project-3.md`](reports/audit-project-3.md) |
| **Total** | **11** | **12** | **11** | **10** | **44** | |

> A skill encontrou **mais findings** que a análise manual (44 vs 38) porque cruzou sistematicamente os 23 anti-patterns do catálogo contra cada arquivo, detectando instâncias que a revisão manual não cobriu.

### Comparação Antes/Depois

#### Projeto 1 — code-smells-project

```
ANTES (4 arquivos monolíticos)          DEPOIS (25 módulos MVC)
app.py         (88 LOC)                config/settings.py, database.py, logging.py
models.py      (314 LOC)               models/produto_model.py, usuario_model.py, pedido_model.py
controllers.py (292 LOC)               controllers/{produto,usuario,pedido,auth,relatorio,system,admin}_controller.py
database.py    (86 LOC)                services/{pedido,relatorio,notification}_service.py
                                        routes/{produto,usuario,auth,pedido,relatorio,system,admin}_routes.py
                                        middlewares/auth.py, error_handler.py
                                        utils/validators.py, migrations/, seeds/

780 LOC em 4 arquivos                  1170 LOC em 25 módulos coesos
```

#### Projeto 2 — ecommerce-api-legacy

```
ANTES (3 arquivos god class)            DEPOIS (18 módulos MVC)
src/app.js         (10 LOC)            src/app.js (composition root)
src/AppManager.js  (142 LOC)           src/config/settings.js, database.js
src/utils.js       (23 LOC)            src/models/{user,course,enrollment,payment,auditLog}Model.js
                                        src/controllers/{checkout,report,user}Controller.js
                                        src/routes/{checkout,report,user}Routes.js
                                        src/middlewares/auth.js, errorHandler.js
                                        src/utils/password.js, errors.js

183 LOC em 3 arquivos                  ~350 LOC em 18 módulos coesos
```

#### Projeto 3 — task-manager-api

```
ANTES (MVC parcial, lógica nas rotas)   DEPOIS (MVC completo com controllers)
routes/task_routes.py   (299 LOC)       routes/task_routes.py    (55 LOC) → delega
routes/user_routes.py   (212 LOC)       routes/user_routes.py    (57 LOC) → delega
routes/report_routes.py (224 LOC)       routes/report_routes.py  (48 LOC) → delega
services/notification   (dead code)     controllers/task_controller.py (novo)
                                        controllers/user_controller.py (novo)
                                        controllers/report_controller.py (novo)
                                        middlewares/auth.py, error_handler.py (novos)
                                        config.py (extraído de app.py)

~1170 LOC em 15 arquivos               ~950 LOC em 23 módulos coesos
```

### Checklist de Validação

#### Projeto 1 — code-smells-project ✅

- [x] **Fase 1:** Python detectado, Flask 3.1.1 detectado, domínio E-commerce descrito, 4 arquivos analisados
- [x] **Fase 2:** 20 findings (5C, 5H, 5M, 5L), template seguido, arquivo:linha exatos, CRITICAL→LOW
- [x] **Fase 2:** APIs deprecated verificadas via context7 (nenhuma encontrada)
- [x] **Fase 2:** Skill pausou e pediu confirmação antes da Fase 3
- [x] **Fase 3:** Estrutura MVC com config/, models/, controllers/, routes/, services/, middlewares/
- [x] **Fase 3:** Config extraída (SECRET_KEY, DB, DEBUG, CORS → env vars)
- [x] **Fase 3:** Auth JWT real implementado (werkzeug + PyJWT)
- [x] **Fase 3:** Error handling centralizado em `middlewares/error_handler.py`
- [x] **Fase 3:** App inicia sem erros — **27/27 smoke tests passando**

#### Projeto 2 — ecommerce-api-legacy ✅

- [x] **Fase 1:** JavaScript detectado, Express 4.18.2 detectado, domínio LMS descrito, 3 arquivos analisados
- [x] **Fase 2:** 13 findings (3C, 4H, 3M, 3L), template seguido, arquivo:linha exatos
- [x] **Fase 2:** APIs deprecated verificadas via context7 (nenhuma encontrada)
- [x] **Fase 2:** Skill pausou e pediu confirmação antes da Fase 3
- [x] **Fase 3:** Estrutura MVC com config/, models/, controllers/, routes/, middlewares/, utils/
- [x] **Fase 3:** Callback hell eliminado (5 níveis → flat async/await)
- [x] **Fase 3:** `badCrypto` substituído por `bcrypt` (10 salt rounds)
- [x] **Fase 3:** Dead code removido (globalCache, totalRevenue, logAndCache)
- [x] **Fase 3:** App inicia sem erros — **7/7 smoke tests passando**

#### Projeto 3 — task-manager-api ✅

- [x] **Fase 1:** Python detectado, Flask 3.0.0 detectado, domínio Task Manager descrito, 15 arquivos analisados
- [x] **Fase 2:** 11 findings (3C, 3H, 3M, 2L), template seguido, arquivo:linha exatos
- [x] **Fase 2:** APIs deprecated verificadas via context7 (nenhuma encontrada)
- [x] **Fase 2:** Skill pausou e pediu confirmação antes da Fase 3
- [x] **Fase 3:** Controllers criados — rotas reduziram de 736→160 LOC
- [x] **Fase 3:** MD5 substituído por werkzeug PBKDF2+salt; password removido de to_dict()
- [x] **Fase 3:** JWT fake substituído por JWT real com PyJWT
- [x] **Fase 3:** App inicia sem erros — **23/23 smoke tests passando**

### Evidências de Funcionamento

Cada projeto foi validado com smoke tests automatizados executados pela skill na Fase 3. Os relatórios completos de refatoração estão em `reports/refactor-project-{1,2,3}.md`.

**Projeto 1 (27/27 testes):** Todos os 18 endpoints originais respondem. JWT auth funciona (401 sem token, 403 com role errada, 200 com admin). SQL injection neutralizada. Senhas com PBKDF2+salt.

**Projeto 2 (7/7 testes):** Os 3 endpoints originais mantidos. Checkout com Visa 200, non-Visa 400. Admin report protegido por JWT (401→200 com token). Delete com cascade.

**Projeto 3 (23/23 testes):** Todos os 22 endpoints originais respondem. JWT real funciona (401 sem token, 200 com token). Password nunca retornado na API. N+1 eliminado com joinedload.

### Comportamento da Skill em Stacks Diferentes

| Aspecto | Python/Flask (P1, P3) | Node.js/Express (P2) |
|---|---|---|
| Detecção de stack | ✅ Correto | ✅ Correto |
| Anti-patterns detectados | SQL Injection, God Class | Callback Hell, God Class |
| Transformação exclusiva | Parameterize Queries | Flatten Callback Nesting |
| Transformação não aplicável | Flatten Callbacks (sem callbacks) | Parameterize Queries (já usava `?`) |
| Auth implementado | werkzeug + PyJWT | bcrypt + jsonwebtoken |
| Adaptação ao contexto | P3 já tinha models/ → skill melhorou sem recriar | AppManager decomposto do zero |

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado ([docs](https://docs.anthropic.com/en/docs/claude-code/overview))
- **Node.js** ≥ 18 (para o Projeto 2)
- **Python** ≥ 3.10 (para os Projetos 1 e 3)
- A skill já está instalada em `.claude/skills/refactor-arch/` nos 3 projetos

### Executar a Skill

```bash
# Projeto 1 — code-smells-project (Python/Flask)
cd code-smells-project
claude "/refactor-arch"

# Projeto 2 — ecommerce-api-legacy (Node.js/Express)
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — task-manager-api (Python/Flask)
cd ../task-manager-api
claude "/refactor-arch"
```

A skill executa em 3 fases:
1. **Fase 1 (Análise):** Detecta stack, mapeia arquitetura, imprime resumo
2. **Fase 2 (Auditoria):** Cruza código contra catálogo, gera relatório, **pede confirmação**
3. **Fase 3 (Refatoração):** Reestrutura para MVC, valida boot + endpoints

Salve os relatórios da Fase 2 em `reports/audit-project-{1,2,3}.md`.

### Validar que a Refatoração Funcionou

#### Projeto 1

```bash
cd code-smells-project
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
# Em outro terminal: curl http://localhost:5000/health
```

#### Projeto 2

```bash
cd ecommerce-api-legacy
npm install
npm start
# Em outro terminal: curl http://localhost:3000/api/admin/financial-report
```

#### Projeto 3

```bash
cd task-manager-api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py
python app.py
# Em outro terminal: curl http://localhost:5000/health
```

### Critérios de Aceite — Resultado Final

| Critério | P1 | P2 | P3 |
|---|:---:|:---:|:---:|
| Fase 1 detecta stack corretamente | ✅ | ✅ | ✅ |
| Fase 2 encontra ≥ 5 findings | ✅ (20) | ✅ (13) | ✅ (11) |
| Fase 2 inclui ≥ 1 CRITICAL ou HIGH | ✅ (10) | ✅ (7) | ✅ (6) |
| Fase 3 aplicação funciona | ✅ 27/27 | ✅ 7/7 | ✅ 23/23 |