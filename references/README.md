# Referências — Skills para Claude Code

Pesquisa sobre as referências do desafio de criação de Skills para refatoração arquitetural automatizada.

---

## Visão Geral

As quatro referências abaixo cobrem o espectro completo de conhecimento necessário para criar Skills no Claude Code: desde a visão geral da ferramenta até o guia detalhado de construção, passando pela documentação técnica oficial e o artigo conceitual sobre o design de Agent Skills.

---

## Referências

| # | Referência | Tipo | Arquivo |
|---|---|---|---|
| 1 | Claude Code: Skills | Documentação oficial | [claude-code-skills.md](claude-code-skills.md) |
| 2 | Claude Code: Overview | Documentação oficial | [claude-code-overview.md](claude-code-overview.md) |
| 3 | The Complete Guide to Building Skills for Claude | Guia completo (PDF) | [complete-guide-building-skills.md](complete-guide-building-skills.md) |
| 4 | Equipping Agents for the Real World with Agent Skills | Blog post técnico | [equipping-agents-with-agent-skills.md](equipping-agents-with-agent-skills.md) |

---

## Resumo por Referência

### 1. [Claude Code: Skills](claude-code-skills.md)

**Fonte:** https://docs.anthropic.com/en/docs/claude-code/skills

Documentação oficial sobre criação, gerenciamento e compartilhamento de Skills. Define a anatomia de uma Skill (SKILL.md + arquivos de suporte), o mecanismo de progressive disclosure em 3 níveis, convenções de nomenclatura, controle de ferramentas via `allowed-tools`, e patterns de teste/debug. Inclui exemplos práticos de Skills simples, com permissões e multi-arquivo.

**Conceitos-chave:** SKILL.md, YAML frontmatter, progressive disclosure, allowed-tools, personal/project/plugin skills

### 2. [Claude Code: Overview](claude-code-overview.md)

**Fonte:** https://docs.anthropic.com/en/docs/claude-code/overview

Visão geral do Claude Code como ferramenta agentic de coding no terminal. Apresenta as capacidades principais: build features, debug, navegação de codebase e automação. Destaca a filosofia Unix (composabilidade e scriptabilidade), integração com MCP para fontes externas, e o suporte nativo a Skills como mecanismo de extensão.

**Conceitos-chave:** Ferramenta agentic, terminal-first, MCP, composabilidade, enterprise-ready

### 3. [The Complete Guide to Building Skills for Claude](complete-guide-building-skills.md)

**Fonte:** https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf

Guia mais completo e detalhado sobre construção de Skills. Cobre 6 capítulos: Fundamentos (progressive disclosure, composability, portability), Planejamento e Design (casos de uso, categorias, critérios de sucesso), Teste e Iteração (triggering, funcional, performance), Distribuição (GitHub, API, padrão aberto), Patterns e Troubleshooting (5 patterns de design + troubleshooting), e Recursos. Inclui checklists de validação e exemplos completos.

**Conceitos-chave:** 5 patterns (sequential workflow, multi-MCP coordination, iterative refinement, context-aware tool selection, domain-specific intelligence), skill-creator, métricas de sucesso

### 4. [Equipping Agents for the Real World with Agent Skills](equipping-agents-with-agent-skills.md)

**Fonte:** https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills

Artigo conceitual dos engenheiros da Anthropic (Barry Zhang, Keith Lazuka, Mahesh Murag) que introduz Agent Skills. Explica a anatomia de um skill com exemplos visuais (PDF skill), a mecânica de progressive disclosure na context window, a relação entre skills e code execution, diretrizes de desenvolvimento e avaliação, considerações de segurança, e a visão de futuro (skills como padrão aberto, agentes criando seus próprios skills).

**Conceitos-chave:** Onboarding analogy, context window mechanics, code execution determinística, segurança, padrão aberto

---

## Conceitos Transversais

### Progressive Disclosure

Todas as referências convergem no princípio de progressive disclosure como design core:

1. **YAML frontmatter** → sempre no system prompt (descoberta)
2. **SKILL.md body** → carregado quando relevante (instruções)
3. **Arquivos linkados** → carregados sob demanda (detalhes)

Isso minimiza uso de tokens enquanto mantém expertise especializada disponível.

### Anatomia de um Skill

```
skill-name/
├── SKILL.md          # Obrigatório — frontmatter + instruções
├── scripts/          # Opcional — código executável
├── references/       # Opcional — documentação sob demanda
└── assets/           # Opcional — templates e recursos
```

### Categorias de Uso

| Categoria | Descrição | Exemplo |
|---|---|---|
| Document & Asset Creation | Output consistente e de alta qualidade | frontend-design |
| Workflow Automation | Processos multi-step com metodologia consistente | skill-creator |
| MCP Enhancement | Orientação de workflow sobre ferramentas MCP | sentry-code-review |

### Fluxo de Desenvolvimento Recomendado

1. **Identificar gaps** → Rodar o agente em tarefas representativas
2. **Definir casos de uso** → 2-3 cenários concretos
3. **Construir incrementalmente** → Skill mínima funcional primeiro
4. **Testar** → Triggering, funcional, performance
5. **Iterar** → Baseado em undertriggering, overtriggering, execution issues
6. **Distribuir** → GitHub + documentação

---

## Aplicação ao Desafio `refactor-arch`

A skill de refatoração arquitetural se alinha com:

- **Pattern 1 (Sequential Workflow)** da referência 3 — 3 fases sequenciais com validação
- **Progressive disclosure** — SKILL.md com fases + arquivos de referência sob demanda (anti-patterns catalog, MVC guidelines, refactor playbook)
- **Code execution** — Scripts de validação determinística na Fase 3
- **Critérios de sucesso** — Min 5 findings, stack detectada, app funcional após refatoração
- **Iteração** — Esperar 2-4 iterações para atingir qualidade nos 3 projetos

---

*Gerado em Abril/2026 a partir de pesquisa nas fontes originais.*
