
# AGENTS.md

# Projeto NAES — UFC Manager

## 1. Contexto do projeto

O NAES é um sistema web desenvolvido com Django para gerenciamento de informações relacionadas ao universo do UFC.

O projeto utiliza:
- Python 3.12
- Django 5.2
- PostgreSQL
- HTML, CSS e JavaScript
- Bootstrap
- jQuery e DataTables

O sistema possui funcionalidades de gerenciamento de lutadores, eventos, categorias, países e rankings.

## 2. Estrutura do projeto

- `naes/`: configurações principais do Django.
- `ufc/`: aplicação responsável pelas funcionalidades relacionadas ao UFC.
- `templates/`: templates HTML compartilhados.
- `static/`: arquivos estáticos do projeto.
- `media/`: arquivos enviados pelos usuários.
- `ia/`: funcionalidades relacionadas à integração com inteligência artificial.
- `manage.py`: ponto de entrada dos comandos administrativos do Django.

Antes de criar novos arquivos ou funcionalidades, verifique a estrutura existente para evitar duplicações.

## 3. Padrões de desenvolvimento

- Utilize os padrões e recursos nativos do Django sempre que possível.
- Mantenha a arquitetura atual do projeto.
- Utilize Class-Based Views quando a funcionalidade já seguir esse padrão.
- Separe responsabilidades entre models, views, forms, templates e demais módulos.
- Utilize nomes de classes, funções e variáveis claros e coerentes com o restante do código.
- Evite duplicação de código.
- Não remova funcionalidades existentes sem necessidade.
- Prefira alterações pequenas e compatíveis com a estrutura atual.

## 4. Banco de dados

- O banco de dados principal é PostgreSQL.
- As configurações de conexão devem utilizar variáveis de ambiente.
- Nunca coloque credenciais ou senhas diretamente no código.
- Toda alteração na estrutura dos models deve ser acompanhada das migrations necessárias.
- Não exclua ou altere dados existentes sem autorização.
- Utilize transações quando uma operação envolver alterações relacionadas em múltiplos registros.

## 5. Segurança e permissões

- Respeite o sistema de autenticação e autorização existente.
- Verifique as permissões do usuário antes de permitir operações de criação, edição ou exclusão.
- Preserve as restrições de acesso aos registros de propriedade dos usuários.
- Usuários administradores devem respeitar as regras especiais de acesso já implementadas.
- Não exponha informações sensíveis nas respostas, logs ou templates.
- Nunca versione arquivos `.env`, tokens, senhas ou chaves de API.

## 6. Views e consultas

- Evite consultas desnecessárias ao banco de dados.
- Utilize `select_related()` e `prefetch_related()` quando apropriado.
- Utilize paginação nas listagens que apresentam muitos registros.
- Preserve os filtros e parâmetros de busca durante a navegação entre páginas.
- Utilize mensagens do Django para informar o resultado das operações ao usuário.

## 7. Templates e interface

- Utilize os templates base existentes sempre que possível.
- Mantenha a identidade visual e os padrões de interface já adotados.
- Priorize componentes Bootstrap já utilizados no projeto.
- Preserve a responsividade das páginas.
- Evite duplicar estruturas HTML compartilhadas.
- Mantenha compatibilidade com os recursos JavaScript existentes, incluindo jQuery e DataTables.

## 8. Inteligência artificial

- Centralize as integrações com provedores de IA nos módulos responsáveis por essa funcionalidade.
- Utilize variáveis de ambiente para armazenar chaves de API.
- Trate erros de comunicação com os serviços externos.
- Evite chamadas desnecessárias aos modelos de IA.
- Não exponha chaves, prompts internos ou dados sensíveis dos usuários.

## 9. Testes e validação

Antes de considerar uma alteração concluída:

1. Verifique se o código não possui erros de sintaxe.
2. Execute `python manage.py check`.
3. Execute os testes existentes com `python manage.py test`.
4. Caso tenha alterado models, verifique as migrations com `python manage.py makemigrations --check --dry-run`.
5. Corrija os problemas encontrados antes de finalizar.

Não informe que os testes passaram sem realmente executá-los.

## 10. Commits

- Para escrever a mensagem de um commit, use a skill `commit-padrao`.

## 11. Orientações gerais

- Analise o código existente antes de implementar alterações.
- Não invente funcionalidades ou estruturas que não foram solicitadas.
- Explique alterações relevantes realizadas.
- Não substitua arquivos inteiros quando uma alteração pontual for suficiente.
- Preserve compatibilidade com as funcionalidades já existentes.
- Em caso de dúvida sobre uma regra de negócio, solicite esclarecimento antes de tomar decisões que possam alterar o comportamento do sistema.
