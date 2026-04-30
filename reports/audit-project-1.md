================================
ARCHITECTURE AUDIT REPORT
================================
Project:       code-smells-project
Stack:         Python 3 + Flask 3.1.1 (flask-cors 5.0.1)
Files:         4 analyzed | ~780 lines of code (app.py 88, database.py 86, models.py 314, controllers.py 292)
Database:      SQLite file-based (loja.db), raw SQL via stdlib sqlite3, single global connection
Domain:        E-commerce API (produtos, usuarios, pedidos, itens_pedido)

> **Verificação de APIs depreciadas (padrão DP) — concluída via Context7 (Flask 3.1.1)**
> APIs verificadas: `before_first_request`, `before_app_first_request`, `request.json` (property), `JSON_AS_ASCII`, `JSON_SORT_KEYS`, `JSONIFY_MIMETYPE`, `JSONIFY_PRETTYPRINT_REGULAR`, `json_encoder`/`json_decoder`, `flask.json.JSONEncoder`/`JSONDecoder`/`htmlsafe_dump*`, `flask.ext.*`, `config.from_json`, `flask.safe_join`, `FLASK_ENV`/`app.env`, `_app_ctx_stack`/`_request_ctx_stack`, `session_cookie_name`, `send_file_max_age_default`, `use_x_sendfile`.
> **Resultado: nenhuma API depreciada encontrada.** O código já usa `request.get_json()` corretamente em todos os handlers. Nenhuma das config keys removidas no Flask 3.0 está presente. Total de findings permanece em 20.

## Summary

| Severity | Count |
|---|---|
| CRITICAL | 5 |
| HIGH     | 5 |
| MEDIUM   | 5 |
| LOW      | 5 |
| **Total** | **20** |

## Findings

### [CRITICAL] C1 — Hardcoded Secrets / Credentials

- **File:** `app.py:7-8`
- **Description:** `SECRET_KEY = "minha-chave-super-secreta-123"` e `DEBUG = True` declarados como literais no source, sem leitura de variável de ambiente.
- **Impact:** Qualquer pessoa com acesso ao repositório obtém a chave de sessão da aplicação. Compromete assinatura de cookies/JWTs e qualquer funcionalidade que dependa do segredo.
- **Recommendation:** Aplicar transformação **Extract Config** do playbook — mover para `os.environ.get("SECRET_KEY")` em módulo `config/` dedicado, com `.env.example` versionado.

### [CRITICAL] C1 — Secret exposto em endpoint público

- **File:** `controllers.py:285-289`
- **Description:** Endpoint `/health` devolve `"secret_key": "minha-chave-super-secreta-123"` e `"debug": True` no payload de resposta.
- **Impact:** Vazamento ativo de credencial pela rede para qualquer cliente HTTP. Pior do que um literal no source — é exposição em runtime sem autenticação.
- **Recommendation:** Remover campos sensíveis do `/health`. Health-check deve devolver apenas `status` e métricas não sensíveis.

### [CRITICAL] C2 — SQL Injection (toda a camada de dados)

- **File:** `models.py:28, 47-50, 57-61, 68, 92, 109-111, 126-129, 140, 148-151, 155, 157-161, 163-166, 174, 188, 192, 220, 224, 280-281, 289-297`
- **Description:** **Todas** as queries do `models.py` montam SQL via concatenação de strings com input do usuário. Exemplos: `"SELECT * FROM produtos WHERE id = " + str(id)` (linha 28), `"... WHERE email = '" + email + "' AND senha = '" + senha + "'"` (linhas 109-111), busca dinâmica com `LIKE '%" + termo + "%'` (linhas 289-297).
- **Impact:** Injeção SQL trivial em todo endpoint que aceita parâmetros. `/login` permite bypass com `' OR '1'='1`. Busca de produtos permite exfiltração de dados arbitrários. Crítico.
- **Recommendation:** Aplicar **Parameterize Queries** — substituir toda concatenação por `cursor.execute("... WHERE id = ?", (id,))`. Aplicar a 100% das funções de `models.py` antes de qualquer outra refatoração.

### [CRITICAL] C2 — Endpoint executa SQL arbitrário do cliente

- **File:** `app.py:59-78`
- **Description:** `/admin/query` aceita JSON `{"sql": "..."}` e executa diretamente via `cursor.execute(query)` — `SELECT`, `INSERT`, `UPDATE`, `DELETE` ou `DROP` à escolha do cliente, sem autenticação.
- **Impact:** Equivale a expor o banco em modo administrativo na internet pública. Permite drop de tabelas, leitura de senhas, manipulação total de estado.
- **Recommendation:** Remover o endpoint inteiramente. Se ferramentas de operação forem necessárias, expor apenas via CLI/admin tooling com auth forte e allow-list de comandos.

### [CRITICAL] C3 — God Class em `models.py` e `controllers.py`

- **File:** `models.py:1-314`, `controllers.py:1-292`
- **Description:** `models.py` (314 linhas) acumula data-access para 4 domínios (produtos, usuários, pedidos, itens), orquestração transacional (`criar_pedido` lê produto, valida estoque, insere pedido, insere itens, atualiza estoque) e regras de negócio (`relatorio_vendas` calcula tiers de desconto). `controllers.py` (292 linhas) mistura parsing de request, validação, regras de negócio (categorias permitidas, tamanhos), efeitos colaterais simulados (`print("ENVIANDO EMAIL")`) e formatação de resposta para 4 domínios.
- **Impact:** Impossível testar regras isoladamente. Mudança em uma rota afeta arquivo gigante. Múltiplas responsabilidades por arquivo violam SRP. Acoplamento total entre HTTP, regras e persistência.
- **Recommendation:** Aplicar **Decompose God Class** — quebrar por domínio (`models/produto.py`, `models/usuario.py`, `models/pedido.py`), extrair `services/pedido_service.py` para orquestração de pedidos, `services/relatorio_service.py` para regras de relatório, e `controllers/produto_controller.py` etc. Rotas em `routes/`.

### [CRITICAL] C4 — Autenticação inexistente

- **File:** `app.py:11-30, 47-78`, `controllers.py:167-186`, `models.py:105-120`
- **Description:** Nenhuma rota possui middleware de autenticação. `/login` (`controllers.py:167`) compara senha em plaintext via SQL e retorna o objeto do usuário — não emite nem valida token. Endpoints destrutivos `/admin/reset-db`, `/admin/query`, `DELETE /produtos/<id>`, `PUT /pedidos/<id>/status` aceitam qualquer requisição. `requirements.txt` não inclui `flask-jwt-extended` nem similar.
- **Impact:** Toda a API é pública. Qualquer cliente pode dropar produtos, alterar status de pedidos arbitrários, executar SQL e listar usuários (com senhas — ver H1).
- **Recommendation:** Aplicar **Add Auth Middleware** — adicionar `flask-jwt-extended`, criar middleware/decorator `@auth_required`, emitir JWT no login (somente após validação de senha hasheada), proteger todas as rotas de mutação e admin. Endpoints `/admin/*` devem exigir role `admin`.

### [HIGH] H1 — Senhas em plaintext (storage + retorno + seed)

- **File:** `database.py:30-35, 75-83`, `models.py:81-86, 99-103, 105-131`
- **Description:** Schema `usuarios.senha TEXT` armazena plaintext. Seed insere `("Admin", "admin@loja.com", "admin123", "admin")`. `criar_usuario` insere senha exatamente como recebida. `get_todos_usuarios` e `get_usuario_por_id` **retornam o campo senha** no payload (`controllers.py:128-144` repassa direto). `login_usuario` faz comparação por igualdade de string em SQL.
- **Impact:** Vazamento do banco expõe credenciais em texto puro. Listar `/usuarios` devolve senhas. Sem `bcrypt`/`argon2`/`werkzeug.security` em `requirements.txt`.
- **Recommendation:** Aplicar **Secure Password Storage** — adicionar `werkzeug.security` (já vem com Flask) ou `bcrypt` em `requirements.txt`, hash com salt em `criar_usuario`, comparação via `check_password_hash` em `login_usuario`, e **omitir o campo senha** em qualquer serialização para API.

### [HIGH] H2 — Lógica de negócio nos controllers

- **File:** `controllers.py:24-62, 64-96, 188-220, 237-255`
- **Description:** `criar_produto` (38 linhas) e `atualizar_produto` misturam parsing, 8 regras de validação inline (preço ≥ 0, estoque ≥ 0, len(nome) ∈ [2, 200], categoria ∈ allow-list), chamada de DB e formatação de resposta. `criar_pedido` chama o model e em seguida emite "notificações" via `print(...)`. `atualizar_status_pedido` valida transição e emite efeitos colaterais.
- **Impact:** Regras de negócio inacessíveis sem subir HTTP. Difícil reuso (mesma validação repetida em criar/atualizar). Notificações acopladas a rota.
- **Recommendation:** Aplicar **Extract Service Layer** — mover validações para `models/produto.py` (ou `services/produto_service.py`), criar `services/notification_service.py` para emails/SMS/push (mesmo que stub), controllers ficam com ≤ 10 linhas por handler.

### [HIGH] H2 — Lógica de negócio dentro do módulo de dados

- **File:** `models.py:133-169, 235-273`
- **Description:** `criar_pedido` no `models.py` faz orquestração transacional (validação de estoque + cálculo de total + 3 INSERTs + UPDATE de estoque) — fluxo de domínio dentro do "model". `relatorio_vendas` calcula tiers de desconto (`> 10000 → 10%`, `> 5000 → 5%`, `> 1000 → 2%`) misturados com queries.
- **Impact:** "Models" deveriam encapsular apenas acesso a dados. Hoje carregam regras de domínio que não podem ser substituídas/testadas separadamente.
- **Recommendation:** Aplicar **Extract Service Layer** — mover orquestração para `services/pedido_service.py` e regras de relatório para `services/relatorio_service.py`. Models expõem apenas CRUD e queries específicas.

### [HIGH] H4 — Código duplicado: serialização e validação

- **File:** `models.py:12-21, 31-40, 304-313` (serialização produto 3x); `models.py:79-86, 95-102` (usuário 2x); `models.py:178-185, 211-218` (pedido 2x); `models.py:187-200, 219-232` (loop de itens de pedido 2x); `controllers.py:24-62 vs 64-96` (bloco de validação de produto)
- **Description:** Construção manual de dicts repetida em todas as funções "get". Bloco de validação de `criar_produto` e `atualizar_produto` é quase idêntico (parsing + 7 validações). Loops aninhados para popular itens de pedido replicados em `get_pedidos_usuario` e `get_todos_pedidos`.
- **Impact:** Mudança de schema obriga editar N pontos. Drift entre cópias é inevitável (e.g., `atualizar_produto` já não valida `categoria` enquanto `criar_produto` valida).
- **Recommendation:** Aplicar **DRY Extract** — função `_row_to_produto(row)` (e equivalentes) para serialização; helper `_validate_produto_payload(data)` para validações.

### [HIGH] H4 — Wildcard de exception handler repetido

- **File:** `controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292`
- **Description:** Bloco `except Exception as e: return jsonify({"erro": str(e)}), 500` (variantes com/sem `print`) replicado em 16 handlers.
- **Impact:** 16 cópias de error-handling para manter; mensagens de exceção interna vazam para o cliente; padrão de logging inconsistente.
- **Recommendation:** Aplicar **Centralize Error Handling** — usar `@app.errorhandler(Exception)` em middleware único, retornando mensagem genérica e logando o stack trace.

### [MEDIUM] M1 — N+1 em criação de pedido

- **File:** `models.py:139-146, 154-167`
- **Description:** `criar_pedido` itera `itens` duas vezes: o primeiro loop faz 1 `SELECT` por produto para validar estoque (já lendo o `preco`), e o segundo loop refaz **outro** `SELECT preco` por produto, mais 1 `INSERT` em `itens_pedido` e 1 `UPDATE` em `produtos`. Total: ~4 queries por item.
- **Impact:** Pedido com 50 itens dispara ~200 queries. Latência cresce linearmente. O segundo loop é redundante — o `preco` já foi lido no primeiro.
- **Recommendation:** Aplicar **Batch Query Optimization** — `SELECT id, preco, estoque, nome FROM produtos WHERE id IN (...)` uma vez, reaproveitar o resultado para validação e inserção, e usar `executemany` para inserir os itens em batch.

### [MEDIUM] M1 — N+1 ao listar pedidos

- **File:** `models.py:177-200, 209-232`
- **Description:** `get_pedidos_usuario` e `get_todos_pedidos` iteram pedidos e, para cada pedido, executam um `SELECT * FROM itens_pedido WHERE pedido_id = ...`. Para cada item desse, mais um `SELECT nome FROM produtos`. Padrão N+M.
- **Impact:** Listar 100 pedidos com 5 itens cada = 1 + 100 + 500 = 601 queries.
- **Recommendation:** Substituir por um único `SELECT` com `JOIN`: `pedidos JOIN itens_pedido JOIN produtos`, agrupando em Python por `pedido_id`.

### [MEDIUM] M2 — Validação de input ausente

- **File:** `controllers.py:64-96, 146-165, 188-220, 237-245`
- **Description:** `atualizar_produto` não valida `categoria` (que `criar_produto` valida). `criar_usuario` não valida formato de e-mail, força de senha nem duplicidade. `criar_pedido` não valida formato de `itens` (`produto_id` inteiro, `quantidade` > 0). `atualizar_status_pedido` não verifica se o pedido existe antes do `UPDATE`. Sem `marshmallow`/`pydantic` no `requirements.txt`.
- **Impact:** Dados inválidos chegam ao banco; combinado com C2 amplia superfície de ataque; pedidos com payload mal formado quebram em runtime com 500.
- **Recommendation:** Aplicar **Add Input Validation** — adotar `pydantic` ou `marshmallow` para schemas por endpoint, ou no mínimo extrair `_validate_produto_payload`/`_validate_usuario_payload`/`_validate_pedido_payload` consistentes.

### [MEDIUM] M3 — Conexão global e schema-init no `get_db`

- **File:** `database.py:4-86`
- **Description:** Variável global `db_connection` reusada em todas as requests com `check_same_thread=False`. `get_db()` mistura abrir conexão, criar 4 tabelas, e popular seed data — toda lógica num único módulo "database".
- **Impact:** Não é dead code, mas é um anti-pattern adjacente: o módulo combina connection management, migrations e seeds. Conexão global é problemática sob concorrência.
- **Recommendation:** Separar em `config/database.py` (conexão por request via `g` do Flask), `migrations/init_schema.py` (DDL) e `seeds/initial_data.py` (dados de exemplo).

### [MEDIUM] M3 — Imports não usados

- **File:** `models.py:2`, `database.py:2`
- **Description:** `import sqlite3` em `models.py` (módulo nunca chama `sqlite3.*` — usa apenas `get_db()`). `import os` em `database.py` (não há usos).
- **Impact:** Ruído e sugestão enganosa de dependências. Já antecipa que após a refatoração `os` deve ser usado para ler `os.environ`.
- **Recommendation:** Aplicar **Remove Dead Code** — remover imports e reintroduzir `os` apenas no novo módulo `config/`.

### [MEDIUM] M4 — Bare exception handling com vazamento de detalhes

- **File:** `controllers.py:10-12, 60-62, 95-96, 108-109, 125-126, 164-165, 185-186, 218-220, 254-255, 261-262, 291-292`, `app.py:77-78`
- **Description:** Padrão `except Exception as e: return jsonify({"erro": str(e)}), 500` retorna a string da exceção (incluindo detalhes do SQLite, paths, stack info parcial) ao cliente. `print("ERRO: " + str(e))` é o único "log".
- **Impact:** Information disclosure (mensagens internas viram superfície de reconhecimento). Difícil debugar — sem stack trace estruturado nem nível de log.
- **Recommendation:** Aplicar **Centralize Error Handling** — `@app.errorhandler(Exception)` único; logar via `logging.exception(...)`; resposta ao cliente com mensagem genérica e id de correlação.

### [LOW] L1 — Debug habilitado em produção

- **File:** `app.py:8, 88`
- **Description:** `app.config["DEBUG"] = True` e `app.run(..., debug=True)` fixos no código.
- **Impact:** Werkzeug expõe console interativo de debug em caso de erro — execução remota de Python via browser se a aplicação for exposta.
- **Recommendation:** Ler `DEBUG` de `os.environ.get("FLASK_DEBUG", "0") == "1"`. Default seguro em produção.

### [LOW] L1 — CORS aberto a qualquer origem

- **File:** `app.py:9`
- **Description:** `CORS(app)` sem parâmetro `origins` — permite qualquer origem.
- **Impact:** Browsers maliciosos podem chamar a API a partir de qualquer site logado do usuário.
- **Recommendation:** `CORS(app, resources={r"/*": {"origins": os.environ.get("ALLOWED_ORIGINS", "").split(",")}})`.

### [LOW] L1 — Magic numbers em regras de desconto

- **File:** `models.py:256-262`, `controllers.py:47-50`
- **Description:** Tiers de desconto com literais `10000, 5000, 1000` e `0.1, 0.05, 0.02`. Validações de tamanho de nome com `2` e `200`.
- **Impact:** Intenção opaca; mudança de regra exige edição em código sem rastreabilidade.
- **Recommendation:** Constantes nomeadas em `services/relatorio_service.py` (e.g., `DISCOUNT_TIERS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]`) e em `models/produto.py` (`MIN_NOME_LEN = 2`, `MAX_NOME_LEN = 200`).

### [LOW] L1 — `print` como mecanismo de log

- **File:** `controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250`, `app.py:56, 83-86`
- **Description:** Código de produção usa `print(...)` para logging, incluindo simulação de envio de e-mail/SMS/push e mensagens de erro.
- **Impact:** Sem nível, sem timestamp, sem destino configurável. Não distingue stdout de log estruturado.
- **Recommendation:** Migrar para `logging` stdlib configurado em `config/logging.py`. Notificações em `services/notification_service.py`.

### [LOW] L3 — Imports não utilizados

- **File:** `models.py:2`, `database.py:2`
- **Description:** Mesma listagem do M3 — repetida aqui pois o catálogo classifica `Unused Imports` como LOW (L3) e `Dead Code` como MEDIUM (M3).
- **Impact:** Ver M3.
- **Recommendation:** Remover imports.

================================
Total: 20 findings
================================
