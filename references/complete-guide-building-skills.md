# The Complete Guide to Building Skills for Claude

- **URL:** https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf
- **Fonte:** Anthropic — Guia Oficial (PDF)
- **Tópico:** Guia completo sobre planejamento, design, teste e distribuição de Skills

---

## Resumo

Um skill é um conjunto de instruções — empacotado como uma pasta simples — que ensina o Claude a lidar com tarefas ou workflows específicos. Skills são uma das formas mais poderosas de customizar o Claude: em vez de re-explicar preferências, processos e expertise em cada conversa, você ensina o Claude uma vez e se beneficia todas as vezes.

Este guia cobre tudo sobre construção efetiva de skills — do planejamento e estrutura até teste e distribuição.

## Capítulo 1: Fundamentos

### O que é um Skill

Um skill é uma pasta contendo:

- **SKILL.md** (obrigatório): Instruções em Markdown com YAML frontmatter
- **scripts/** (opcional): Código executável (Python, Bash, etc.)
- **references/** (opcional): Documentação carregada conforme necessário
- **assets/** (opcional): Templates, fontes, ícones

### Princípios de Design Core

**Progressive Disclosure** — Sistema de três níveis:

1. **Primeiro nível** (YAML frontmatter): Sempre carregado no system prompt do Claude. Fornece informação suficiente para saber quando cada skill deve ser usado, sem carregar tudo no contexto.
2. **Segundo nível** (SKILL.md body): Carregado quando o Claude acha o skill relevante. Contém instruções completas e orientação.
3. **Terceiro nível** (Arquivos linkados): Arquivos adicionais dentro do diretório do skill que o Claude pode navegar e descobrir apenas quando necessário.

**Composability**: O Claude pode carregar múltiplos skills simultaneamente. Seu skill deve funcionar bem junto com outros.

**Portability**: Skills funcionam identicamente no Claude.ai, Claude Code e API.

### Skills + MCP

Para builders de MCP: Skills são a camada de conhecimento em cima da conectividade que o MCP fornece.

| MCP (Conectividade) | Skills (Conhecimento) |
|---|---|
| Conecta Claude ao seu serviço | Ensina Claude a usar seu serviço efetivamente |
| Fornece acesso a dados em tempo real | Captura workflows e melhores práticas |
| O que Claude pode fazer | Como Claude deve fazer |

## Capítulo 2: Planejamento e Design

### Comece com Casos de Uso

Antes de escrever código, identifique 2-3 casos de uso concretos. Pergunte-se:

- O que o usuário quer realizar?
- Que workflows multi-step isso requer?
- Quais ferramentas são necessárias?
- Que conhecimento de domínio deve ser embutido?

### Categorias de Uso

**Categoria 1: Criação de Documentos e Assets**
- Output consistente e de alta qualidade
- Exemplo: frontend-design skill
- Técnicas: Style guides embutidos, templates, checklists de qualidade

**Categoria 2: Automação de Workflows**
- Processos multi-step com metodologia consistente
- Exemplo: skill-creator skill
- Técnicas: Workflows passo-a-passo com gates de validação, templates, loops de refinamento

**Categoria 3: Melhoria de MCP**
- Orientação de workflow para potencializar o acesso a ferramentas de um MCP server
- Exemplo: sentry-code-review skill
- Técnicas: Coordenação de múltiplas chamadas MCP, expertise de domínio embutida

### Critérios de Sucesso

**Métricas quantitativas:**

- Skill dispara em 90%+ das queries relevantes
- Completa workflow em X tool calls (comparar com e sem skill)
- 0 chamadas de API falhas por workflow

**Métricas qualitativas:**

- Usuários não precisam instruir sobre próximos passos
- Workflows completam sem correção do usuário
- Resultados consistentes entre sessões

### Requisitos Técnicos

**Estrutura de arquivos:**

```
your-skill-name/
├── SKILL.md          # Obrigatório
├── scripts/          # Opcional
├── references/       # Opcional
└── assets/           # Opcional
```

**Regras críticas:**

- SKILL.md deve ser exatamente `SKILL.md` (case-sensitive)
- Pasta em kebab-case: `notion-project-setup` (não `Notion Project Setup`)
- Não incluir `README.md` dentro da pasta do skill

### YAML Frontmatter

Formato mínimo:

```yaml
---
name: your-skill-name
description: What it does. Use when user asks to [specific phrases].
---
```

**Campos:**

- `name` (obrigatório): kebab-case, sem espaços ou maiúsculas, deve coincidir com o nome da pasta
- `description` (obrigatório): DEVE incluir O QUE faz E QUANDO usar (trigger conditions), máx. 1024 caracteres, sem tags XML
- `license` (opcional): MIT, Apache-2.0, etc.
- `compatibility` (opcional): Requisitos de ambiente
- `metadata` (opcional): author, version, mcp-server, etc.

**Restrições de segurança:** Tags XML proibidas no frontmatter; skills com "claude" ou "anthropic" no nome são reservados.

### Escrevendo Instruções Efetivas

**Template recomendado:**

```markdown
---
name: your-skill
description: [what + when]
---

# Your Skill Name

## Instructions

## Step 1: [First Major Step]
Clear explanation + expected output

## Examples

## Troubleshooting
```

**Melhores práticas:**

- Ser específico e acionável (não vago)
- Incluir error handling
- Referenciar recursos bundled claramente
- Usar progressive disclosure (manter SKILL.md focado)

## Capítulo 3: Teste e Iteração

### Níveis de Teste

1. **Manual testing no Claude.ai**: Rápido, sem setup
2. **Scripted testing no Claude Code**: Validação repetível
3. **Programmatic testing via Skills API**: Suites de avaliação sistemáticas

### Abordagem Recomendada

**1. Triggering tests:** Garantir que o skill carrega nos momentos certos
- Deve disparar em tarefas óbvias e requests parafraseados
- Não deve disparar em tópicos não relacionados

**2. Functional tests:** Verificar outputs corretos
- Outputs válidos gerados
- Chamadas de API com sucesso
- Error handling funciona
- Edge cases cobertos

**3. Performance comparison:** Provar que o skill melhora resultados

| Métrica | Sem Skill | Com Skill |
|---|---|---|
| Instruções por conversa | Manual cada vez | Automático |
| Mensagens back-and-forth | 15 | 2 |
| API calls falhas | 3 | 0 |
| Tokens consumidos | 12.000 | 6.000 |

### skill-creator skill

Ferramenta integrada que ajuda a:

- Gerar skills a partir de descrições em linguagem natural
- Produzir SKILL.md formatado corretamente
- Revisar skills e identificar problemas
- Sugerir test cases

### Iteração Baseada em Feedback

**Undertriggering:** Skill não carrega quando deveria → Adicionar mais detalhe na description

**Overtriggering:** Skill carrega para queries não relacionadas → Adicionar negative triggers, ser mais específico

**Execution issues:** Resultados inconsistentes → Melhorar instruções, adicionar error handling

## Capítulo 4: Distribuição e Compartilhamento

### Modelo Atual

- Download da pasta → Upload via Settings > Capabilities > Skills
- Organization-level: Admins podem deploy workspace-wide
- Skills como padrão aberto: portáveis entre plataformas

### Skills via API

- Endpoint `/v1/skills` para listagem e gerenciamento
- Parâmetro `container.skills` no Messages API
- Works com Claude Agent SDK

### Abordagem Recomendada

1. Host no GitHub com README claro
2. Documentar no repo do MCP
3. Criar Installation Guide

## Capítulo 5: Patterns e Troubleshooting

### Pattern 1: Sequential Workflow Orchestration
- Steps explícitos em ordem
- Dependências entre steps
- Validação em cada estágio
- Instruções de rollback para falhas

### Pattern 2: Multi-MCP Coordination
- Separação clara de fases
- Passagem de dados entre MCPs
- Validação antes de avançar
- Error handling centralizado

### Pattern 3: Iterative Refinement
- Critérios de qualidade explícitos
- Loop de melhoria
- Scripts de validação
- Saber quando parar de iterar

### Pattern 4: Context-Aware Tool Selection
- Critérios de decisão claros
- Opções de fallback
- Transparência sobre escolhas

### Pattern 5: Domain-Specific Intelligence
- Expertise de domínio embutida na lógica
- Compliance antes de ação
- Documentação abrangente
- Governança clara

### Troubleshooting Comum

| Problema | Causa | Solução |
|---|---|---|
| Skill won't upload | Arquivo não nomeado SKILL.md | Renomear (case-sensitive) |
| Invalid frontmatter | YAML formatting | Verificar delimitadores `---` |
| Invalid skill name | Espaços ou maiúsculas | Usar kebab-case |
| Skill não dispara | Description vaga | Adicionar triggers específicos |
| Skills conflitam | Descrições parecidas | Usar termos distintos |

---

## Relevância para o Projeto

Este guia é a referência mais completa sobre construção de Skills. Para a skill `refactor-arch`, os insights mais relevantes são:

- **Progressive disclosure**: A skill deve ter 3 níveis — frontmatter (sempre carregado), SKILL.md body (quando relevante), referências (sob demanda)
- **Pattern 1 (Sequential Workflow)**: A skill `refactor-arch` segue este pattern com 3 fases sequenciais
- **Arquivos de referência**: Devem cobrir as 5 áreas de conhecimento (análise, anti-patterns, template, guidelines, playbook)
- **Critérios de sucesso**: Definir métricas claras (min 5 findings, stack detectada corretamente, app funciona após refatoração)
- **Iteração**: Esperar 2-4 iterações para atingir qualidade desejada

---

*Fonte original: [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)*
