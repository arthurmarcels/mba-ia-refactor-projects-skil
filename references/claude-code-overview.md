# Claude Code: Overview — Visão Geral

- **URL:** https://docs.anthropic.com/en/docs/claude-code/overview
- **Fonte:** Anthropic — Documentação Oficial
- **Tópico:** Visão geral do Claude Code e suas capacidades

---

## Resumo

Claude Code é a ferramenta agentic de coding da Anthropic que opera no terminal. Permite construir features, debugar issues, navegar codebases e automatizar tarefas tediosas diretamente da linha de comando.

## Pontos-Chave

### Quick Start

**Pré-requisitos:**

- Node.js 18+
- Conta Claude.ai ou Anthropic Console

```bash
npm install -g @anthropic-ai/claude-code
cd your-awesome-project
claude
```

### O que o Claude Code faz

- **Build features from descriptions**: Descreva em linguagem natural; Claude planeja, escreve código e garante que funciona
- **Debug e fix issues**: Cole uma mensagem de erro; Claude analisa a codebase, identifica o problema e implementa a correção
- **Navigate any codebase**: Pergunte sobre qualquer codebase; Claude mantém consciência de toda a estrutura do projeto e pode buscar informações atualizadas da web e via MCP
- **Automate tedious tasks**: Corrigir lint issues, resolver merge conflicts, escrever release notes — em um único comando ou em CI

### Por que desenvolvedores preferem

- **Works in your terminal**: Não é outra janela de chat ou IDE — funciona onde você já trabalha
- **Takes action**: Edita arquivos diretamente, roda comandos, cria commits. Via MCP pode ler docs no Google Drive, atualizar tickets no Jira, etc.
- **Unix philosophy**: Componível e scriptável. Exemplo: `tail -f app.log | claude -p "Slack me if you see any anomalies"`
- **Enterprise-ready**: API da Anthropic ou hosting em AWS/GCP. Segurança, privacidade e compliance enterprise-grade

### Integração com MCP

O Model Context Protocol (MCP) permite ao Claude Code acessar fontes externas de dados:

- Google Drive, Figma, Slack e outros serviços
- Ferramentas customizadas de desenvolvimento
- Datasources externos para enriquecer o contexto

### Composabilidade com Skills

O Claude Code suporta Agent Skills — pastas organizadas com instruções, scripts e recursos que estendem as capacidades do Claude para domínios específicos. Skills são:

- Descobertas automaticamente pelo Claude
- Compartilháveis via git
- Componíveis (múltiplas Skills podem atuar juntas)

---

## Relevância para o Projeto

Esta referência fornece o contexto macro do Claude Code como plataforma. Entender que:

- O Claude Code é uma ferramenta agentic que opera no terminal com acesso a filesystem e execução de código
- Skills são um mecanismo nativo para estender capacidades do Claude
- MCP permite integração com ferramentas externas
- A filosofia Unix (composabilidade, scriptabilidade) se aplica ao design de Skills

Essa compreensão é fundamental para projetar a skill `refactor-arch` que precisa operar sobre codebases reais com acesso a arquivos, execução de comandos e validação.

---

*Fonte original: [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview)*
