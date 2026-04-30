# Equipping Agents for the Real World with Agent Skills

- **URL:** https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills
- **Fonte:** Anthropic — Blog Oficial (Claude Blog)
- **Autores:** Barry Zhang, Keith Lazuka, Mahesh Murag
- **Data:** 16 de Outubro de 2025
- **Tópico:** Visão conceitual e técnica sobre Agent Skills — design, funcionamento e boas práticas

---

## Resumo

Agent Skills são pastas organizadas de instruções, scripts e recursos que agentes descobrem e carregam dinamicamente para performar melhor em tarefas específicas. Skills transformam agentes de propósito geral em agentes especializados, empacotando expertise em recursos componíveis. Building a skill for an agent é como montar um guia de onboarding para um novo contratado.

---

## A Anatomia de um Skill

### Níveis de Progressive Disclosure

**Primeiro nível** — YAML frontmatter (`name` e `description`):

- Pré-carregado no system prompt no startup
- Informação suficiente para o Claude saber QUANDO usar cada skill
- Sem carregar tudo no contexto

**Segundo nível** — Body do SKILL.md:

- Carregado quando o Claude avalia que o skill é relevante para a tarefa atual
- Instruções completas e orientação

**Terceiro nível e além** — Arquivos linkados:

- Arquivos adicionais dentro do diretório do skill
- Claude navega e descobre apenas quando necessário
- Contexto efetivamente ilimitado

### Exemplo: PDF Skill

O PDF skill demonstra o pattern completo:

- `SKILL.md`: Instruções core (leitura, extração de texto)
- `reference.md`: Referência detalhada da API
- `forms.md`: Instruções específicas para preenchimento de formulários

Ao mover instruções de forms para um arquivo separado, o autor mantém o core enxuto — o Claude lê `forms.md` apenas quando precisa preencher um formulário.

### Skills e a Context Window

Sequência de operações quando um skill é acionado:

1. Context window tem system prompt core + metadata de todos skills instalados + mensagem do usuário
2. Claude avalia relevância e lê o SKILL.md completo (segundo nível)
3. Claude pode ler arquivos adicionais bundled (terceiro nível)
4. Claude prossegue com a tarefa com as instruções carregadas

### Skills e Code Execution

Skills podem incluir código para o Claude executar a seu critério. Exemplo: o PDF skill inclui um script Python que lê um PDF e extrai todos os form fields. O Claude roda o script sem carregar nem o script nem o PDF no contexto.

**Vantagens de código em Skills:**

- Operações determinísticas são mais confiáveis que geração de tokens
- Eficiência: sort via código vs. via token generation
- Consistência e repetibilidade

## Desenvolvimento e Avaliação de Skills

### Diretrizes para Autoria e Teste

1. **Comece com avaliação**: Identifique gaps nas capacidades dos agentes rodando tarefas representativas. Observe onde eles lutam ou precisam de contexto adicional. Construa skills incrementalmente para endereçar esses gaps.

2. **Estruture para escala**: Quando SKILL.md fica grande demais, divida em arquivos separados e referencie-os. Contextos mutuamente exclusivos devem ter caminhos separados. Código pode servir como ferramenta executável e como documentação.

3. **Pense da perspectiva do Claude**: Monitore como o Claude usa seu skill em cenários reais e itere. Preste atenção especial ao `name` e `description` — o Claude os usa para decidir se dispara o skill.

4. **Itere com o Claude**: Peça ao Claude para capturar abordagens bem-sucedidas e erros comuns em context reutilizável dentro de um skill. Se ele sai do caminho, peça auto-reflexão sobre o que deu errado.

### Considerações de Segurança

Skills dão ao Claude novas capacidades através de instruções e código. Isso significa que skills maliciosos podem:

- Introduzir vulnerabilidades no ambiente
- Direcionar o Claude a exfiltrar dados
- Provocar ações não intencionadas

**Recomendações:**

- Instalar skills apenas de fontes confiáveis
- Auditar skills de fontes menos confiáveis
- Ler conteúdo dos arquivos bundled
- Atenção a dependências de código e recursos bundled
- Atenção a instruções que conectam a fontes de rede não confiáveis

## O Futuro dos Skills

Skills são suportados no Claude.ai, Claude Code, Claude Agent SDK e Claude Developer Platform.

Roadmap:

- Features para o ciclo completo: criar, editar, descobrir, compartilhar e usar Skills
- Skills complementando MCP servers com workflows mais complexos
- Agentes criando, editando e avaliando Skills por conta própria

### Skills como Padrão Aberto

Agent Skills foram publicados como padrão aberto para portabilidade cross-platform (assim como MCP). O mesmo skill deve funcionar em Claude ou outras plataformas de IA.

---

## Relevância para o Projeto

Este artigo fornece a fundamentação conceitual por trás dos Agent Skills. Para a skill `refactor-arch`:

- **Progressive disclosure é o design principle central**: A skill deve ter frontmatter descritivo, SKILL.md com instruções core, e arquivos de referência carregados sob demanda
- **Pensar da perspectiva do Claude**: Monitorar como a skill se comporta nos 3 projetos e iterar
- **Iterar com o Claude**: Pedir ao Claude para capturar padrões bem-sucedidos e erros comuns
- **Código como ferramenta**: Scripts de validação podem garantir determinismo na Fase 3
- **Security**: A skill lê código-fonte e reescreve arquivos — validar que não introduz vulnerabilidades

---

*Fonte original: [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills)*
