# Área da cliente e navegação — Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Permitir voltar ao início e consultar quais filmes e séries de um gênero estão cadastrados.

**Architecture:** Manter Django e o banco atual. A página pública `/assistir/` renderiza consultas GET por nome, gênero e tipo no servidor, sem depender de JavaScript. A interface de gestão continua em `/catalogo/`; uma extensão do template da API fornece navegação de retorno no acervo e em gêneros, preservando JSON.

**Tech Stack:** Django 4.2, templates, SQLite, HTML/CSS e pytest existentes.

**Spec:** Pedido do usuário nesta conversa: retorno das telas de acervo e cadastro de gêneros e simulação da cliente que busca filmes de determinado gênero.

## Global Constraints

- Português e layout responsivo; reutilizar o visual da interface existente.
- Consultar dados reais; não inserir exemplos no banco do usuário.
- Área da cliente sem edição; consulta de disponibilidade no catálogo, pois não há vídeos cadastrados no modelo.
- Manter as permissões existentes da API e as alterações anteriores da conversa.

## Review Focus

- Busca combinada não deve mostrar títulos de outros gêneros/tipos.
- Filtros inválidos devem mostrar orientação, sem erro 500 ou lista não filtrada.
- Catálogo vazio e pesquisa sem resultados devem ser compreensíveis.
- Valores de busca devem ser escapados e preservados no formulário.
- Links de retorno devem aparecer nas páginas HTML da API sem alterar JSON.

### Task 1: Navegação de retorno

**Files:** `catalogo/templates/rest_framework/api.html`, `catalogo/templates/catalogo/catalogo.html`, `catalogo/test_interface.py`, `catalogo/test_home.py`.

- [x] Escrever e executar testes de links no HTML de acervo, gêneros, gestão e diálogo de gênero.
- [x] Adicionar links explícitos para início e área da cliente, preservando os endpoints existentes.
- [x] Verificar os testes de navegação e o JSON da API.

### Task 2: Consulta pública

**Files:** `catalogo/views.py`, `config/urls.py`, `catalogo/forms.py`, `catalogo/templates/catalogo/assistir.html`, `catalogo/static/catalogo/assistir.css`, `catalogo/test_assistir.py`, `catalogo/templates/catalogo/home.html`, `README.md`.

**Interfaces:** View `pagina_assistir(request)` na rota nomeada `assistir`; GET `q`, `genero`, `tipo`; formulário `BuscaCatalogoForm` valida os filtros; contexto `form`, `titulos`, `total_catalogo` e paginação com filtros preservados.

- [x] Escrever e executar testes de busca, combinação de filtros, validação, vazio, escape e paginação.
- [x] Implementar formulário, view, rota e página de consulta com cartões de disponibilidade, limpeza de filtros e retorno ao início.
- [x] Integrar a entrada “O que assistir” à página inicial e à gestão; documentar a simulação no README.
- [x] Rodar pytest completo, check e verificação de migrações; inspeção visual tentada, mas bloqueada pela ferramenta por não conseguir identificar com segurança a URL do navegador.

## Decisões e verificação

- A implementação continua na pasta atual para integrar as correções ainda não commitadas da conversa anterior; o banco alterado pelo usuário foi preservado.
- O template da API é selecionado por um renderer próprio dos dois viewsets do catálogo, pois o carregamento de templates prioriza o app rest_framework na configuração atual. JSON e permissões foram preservados.
- A revisão independente identificou um falso negativo na busca Unicode do SQLite. Um teste reproduziu a falha; `iregex` com o texto escapado mantém a busca literal e ignora caixa em letras acentuadas.
- Testes de banco usam o banco de testes; as verificações HTTP na aplicação existente são somente de leitura.
