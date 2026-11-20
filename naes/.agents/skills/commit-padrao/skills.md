
---
name: commit-padrao
description: Use ao criar, revisar ou sugerir mensagens de commit para alterações no projeto NAES, seguindo o padrão Conventional Commits.
---

# Skill — Padrão de Commits

Utilize o padrão Conventional Commits para escrever mensagens de commit claras, objetivas e consistentes.

## 1. Estrutura

Toda mensagem deve seguir o formato:

`tipo(escopo): descrição`

- **tipo:** categoria da alteração realizada.
- **escopo:** módulo ou área afetada, quando aplicável.
- **descrição:** resumo curto e objetivo da alteração.

O escopo é opcional quando não acrescentar clareza.

## 2. Tipos de commit

Utilize os seguintes tipos:

| Tipo | Utilização |
|---|---|
| feat | Adição de uma nova funcionalidade. |
| fix | Correção de um erro ou comportamento incorreto. |
| docs | Alterações na documentação. |
| style | Alterações de formatação sem modificar a lógica. |
| refactor | Reestruturação do código sem alterar o comportamento. |
| perf | Melhorias de desempenho. |
| test | Criação ou alteração de testes. |
| build | Alterações em dependências ou ferramentas de build. |
| ci | Alterações em processos de integração contínua. |
| chore | Tarefas de manutenção que não se encaixam nos demais tipos. |
| revert | Reversão de um commit anterior. |

## 3. Regras para escrever mensagens

1. Utilize letras minúsculas no tipo, escopo e descrição.
2. Escreva a descrição de forma objetiva.
3. Utilize verbos no imperativo, como adicionar, corrigir, atualizar, remover e implementar.
4. Não finalize a descrição com ponto.
5. Evite mensagens genéricas.
6. Não misture alterações sem relação em uma única mensagem.
7. Utilize o escopo para identificar a área afetada quando isso ajudar na compreensão.
8. Não utilize emojis.
9. Não inclua informações que não correspondam às alterações realizadas.

## 4. Exemplos de mensagens boas

- `feat(ufc): adicionar cadastro de eventos`
- `fix(ufc): corrigir filtro de lutadores`
- `docs(agents): documentar instruções do projeto`
- `refactor(views): otimizar consultas de eventos`
- `test(ufc): adicionar testes para cadastro de lutadores`
- `chore(deps): atualizar dependências do projeto`
- `feat(ia): implementar integração com modelo de linguagem`

## 5. Exemplos de mensagens ruins

Evite mensagens genéricas ou fora do padrão:

- `atualizações`
- `corrigindo bugs`
- `mudanças no projeto`
- `novo código`
- `finalizado`
- `feat: fiz algumas alterações`

Essas mensagens não deixam claro o que foi modificado.

## 6. Processo para sugerir um commit

Antes de sugerir uma mensagem:

1. Analise as alterações realizadas.
2. Identifique a principal finalidade da mudança.
3. Escolha o tipo de commit adequado.
4. Defina um escopo coerente, quando necessário.
5. Escreva uma descrição objetiva.
6. Confira se a mensagem segue todas as regras desta skill.

Se houver alterações de naturezas diferentes, sugira separar os commits.

Nunca invente alterações ou sugira uma mensagem que não represente o conteúdo efetivamente modificado.
