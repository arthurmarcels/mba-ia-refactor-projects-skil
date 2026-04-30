# Claude Code: Agent Skills — Documentação Oficial

- **URL:** https://docs.anthropic.com/en/docs/claude-code/skills
- **Fonte:** Anthropic — Claude Code Docs
- **Tópico:** Criação, gerenciamento e compartilhamento de Skills no Claude Code

---

## Resumo

Skills são capacidades modulares que estendem a funcionalidade do Claude através de pastas organizadas contendo instruções, scripts e recursos. Cada Skill consiste em um arquivo `SKILL.md` com instruções que o Claude lê quando relevante, além de arquivos opcionais de suporte como scripts e templates.

## Pontos-Chave

### O que são Agent Skills

Skills empacotam expertise em capacidades descobríveis. O Claude decide autonomamente quando usá-las com base na requisição do usuário e na descrição da Skill (model-invoked), diferente de slash commands que são user-invoked.

**Benefícios:**

- Estendem as capacidades do Claude para workflows específicos
- Compartilham expertise via git
- Reduzem prompting repetitivo
- Composição de múltiplas Skills para tarefas complexas

### Criação de Skills

**Personal Skills** (`~/.claude/skills/`): Disponíveis em todos os projetos, para workflows individuais e experimentação.

**Project Skills** (`.claude/skills/`): Compartilhadas com o time via git, para convenções e workflows do projeto.

**Plugin Skills**: Vêm de plugins do Claude Code, funcionam igual às demais.

### Estrutura do SKILL.md

```markdown
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---

# Your Skill Name

## Instructions
Provide clear, step-by-step guidance for Claude.

## Examples
Show concrete examples of using this Skill.
```

**Campos obrigatórios:**

- `name`: Apenas letras minúsculas, números e hífens (máx. 64 caracteres)
- `description`: O que a Skill faz e quando usá-la (máx. 1024 caracteres)

### Arquivos de Suporte

```
my-skill/
├── SKILL.md (obrigatório)
├── reference.md (documentação opcional)
├── examples.md (exemplos opcionais)
├── scripts/
│   └── helper.py (utilitário opcional)
└── templates/
    └── template.txt (template opcional)
```

O Claude lê arquivos adicionais apenas quando necessário (progressive disclosure).

### Controle de Ferramentas

O campo `allowed-tools` no frontmatter limita quais ferramentas o Claude pode usar:

```yaml
allowed-tools: Read, Grep, Glob
```

Casos de uso: Skills read-only, escopo limitado, workflows sensíveis à segurança.

### Teste e Debug

Se o Claude não usa a Skill:

1. **Descrição específica**: Incluir o que faz E quando usar
2. **Verificar caminho**: `~/.claude/skills/skill-name/SKILL.md` ou `.claude/skills/skill-name/SKILL.md`
3. **Sintaxe YAML**: `---` na linha 1, `---` antes do conteúdo, sem tabs

### Compartilhamento via Git

```bash
git add .claude/skills/
git commit -m "Add team Skill for PDF processing"
git push
```

Team members recebem Skills automaticamente ao fazer `git pull`.

### Melhores Práticas

- **Foco**: Uma Skill = uma capacidade
- **Descrições claras**: Incluir triggers específicos
- **Testar com o time**: Coletar feedback sobre ativação e instruções
- **Documentar versões**: Incluir seção de version history no SKILL.md

### Exemplos

**Skill simples** (commit-helper): Gera mensagens de commit a partir de diffs.

**Skill com permissões** (code-reviewer): Review de código com apenas ferramentas de leitura.

**Skill multi-arquivo** (pdf-processing): Extração de texto, preenchimento de formulários, merge de PDFs com scripts e referências adicionais.

---

## Relevância para o Projeto

Esta referência é a documentação oficial que define como criar e estruturar Skills no Claude Code. Ela estabelece:

- A anatomia de uma Skill (SKILL.md + arquivos de suporte)
- O mecanismo de progressive disclosure (3 níveis)
- Convenções de nomenclatura e estrutura de diretórios
- O campo `allowed-tools` para controle de permissões
- Patterns de teste e debug

É a base técnica para implementar a skill `refactor-arch` no desafio.

---

*Fonte original: [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills)*
