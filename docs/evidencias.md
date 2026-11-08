# Unidade 02 — evidências do Prompt 1

## Identificação e fontes

- Disciplina: PEX1277 — Manutenção de Software, UFERSA.
- Integrantes: Andrew Ferreira de Paiva Silva, Antonio Andson de Oliveira Rocha e Sophia Hellen Pires da Silveira.
- Tema escolhido na solicitação: **API de comandas de restaurante**. O trecho de filmes/séries do roteiro foi adaptado a esse tema, inclusive a branch equivalente.
- Enunciado: `Trabalho_Uni02_-_Manuteno.pdf`, lido integralmente com `pdftotext -layout`.
- SIGAA: equipe de até três integrantes; entrega em documento PDF único, contendo os nomes e o link do repositório; arquivo de até 10 MB; prazo exibido de 03/11/2026 às 00h00 até 10/11/2026 às 23h59. Horários transcritos da tela.
- Relatório do professor: máximo de três páginas, com entidades/endpoints, testes, duas métricas, uso de IA e dificuldades.
- Pontuação: Git/GitHub 2,0; API/manutenibilidade 3,5; testes 2,5; métricas 1,0; IA 1,0.
- Recebidos o PDF e a tela; o Prompt 1 foi fornecido depois em texto. Os Prompts 2–6 não foram recebidos nem executados.

## Origem, estado inicial e preservação

- Diretório inicial: `/workspace`, sem repositório Git e sem código de projeto prévio. Os arquivos anexados foram preservados.
- Destino existente e público: <https://github.com/Andsonyz/catalogo-filmes-series-api>. O nome do repositório foi mantido apesar da escolha de outro tema.
- `git ls-remote --symref ... HEAD 'refs/heads/*'` no destino retornou saída vazia e código 0: repositório sem commits/branches publicados. A API do GitHub informa branch padrão `main`.
- Base: <https://github.com/lisa-ufersa/django-quickproject>, branch `main`, commit `a59bd49d22f3a0987798cc84449797f5849b4d03` (`ssh-key test`).
- Cópia separada em `/workspace/catalogo-filmes-series-api`, criada com `git clone --origin upstream`, preservando o histórico da base.
- `origin`: repositório da equipe; `upstream`: professor, com URL de push local `DISABLED`. Nenhuma escrita no repositório do professor.
- Branch de trabalho: `feat/comandas-restaurante`, criada a partir da revisão acima. A `main` local permanece na revisão original; não foi realizado merge nesta etapa.
- Estado após clone e após verificações: `git status --short` vazio. Não havia alterações anteriores no checkout.
- SHA-256 de `db.sqlite3`, antes e depois das verificações: `ddb8f6692e1bc205e55c1407949ed18b71b1ac70f2615eb5e1ca52e9c6d96ad7`. O banco versionado permaneceu intacto.

## Comandos e resultados reais

Execução em 08/11/2026. O registro selecionado de comandos, saídas, horários UTC e códigos de retorno está em [registro-prompt1.log](registro-prompt1.log). O fuso de referência para a equipe nesta conversa é America/Fortaleza (UTC−3).

| Comando/verificação | Resultado observado |
| --- | --- |
| `git rev-parse --show-toplevel` em `/workspace` | Código 128: não é repositório; condição inicial, não falha do projeto |
| `git clone --origin upstream https://github.com/lisa-ufersa/django-quickproject.git /workspace/catalogo-filmes-series-api` | Código 0; histórico preservado |
| `git switch -c feat/comandas-restaurante` | Código 0 |
| `python3 --version` | Python 3.12.14 |
| `python3 -m venv venv` | Código 0; ambiente ignorado pelo Git |
| `venv/bin/python -m pip install -r requirements.txt` | Código 0; versões originais mantidas, incluindo Django 4.2.3, DRF 3.14.0, pytest 8.1.1 e pytest-django 4.8.0 |
| `venv/bin/python -m pip check` | Código 0: `No broken requirements found.` |
| `venv/bin/python manage.py migrate --noinput` | Código 0: `No migrations to apply.` |
| `venv/bin/python manage.py check` | Código 0: `System check identified no issues (0 silenced).` |
| `venv/bin/python -m pytest -v` | Código 0: **1 passed**; executor conforme `pytest.ini` e README da base |
| `venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload` | Servidor local iniciado para verificação HTTP |
| `curl` em `/swagger/`, `/schema/`, `/users/` | HTTP 200 nas três rotas; `/users/` retorna `[]` |
| `curl -X POST` com `{}` em `/api/token-auth/` | HTTP 400, informando usuário e senha obrigatórios; rota acessível |
| `curl` em `/users/999999/` | HTTP 404 para registro inexistente |
| `curl -X OPTIONS` em `/users/` | HTTP 405; base restringe os métodos a `get` e `put` |

### Limitações herdadas e verificação visual

- Não houve falha na instalação, nas migrações, no check ou na suíte existente.
- O único teste herdado é `users/tests.py::UserTestCase::test_user`, que compara `1 == 1`. Seu sucesso não comprova comportamento da API e não satisfaz os quatro testes exigidos para a entrega.
- A API de exemplo `/users/` oferece GET/PUT, não CRUD completo. Isso é uma limitação da base a considerar na próxima etapa.
- A tentativa de usar o navegador compartilhado retornou `Browser runtime unavailable`. A alternativa com Chromium/Playwright local funcionou: HTTP 200, título `Swagger`, operações `/api/token-auth/`, `/schema/`, `/users/` e `/users/{id}/` renderizadas; `page_errors: []`. Captura em [swagger-base.png](swagger-base.png). Isso não bloqueou a etapa nem exigiu novo acesso.

## Planejamento do domínio — ainda sem implementação

Proposta inicial para a etapa seguinte: manter a estrutura da base e adicionar um app `comandas` com duas entidades, sem introduzir catálogo de produtos ou pagamentos.

| Entidade | Campos planejados | Relação |
| --- | --- | --- |
| `Comanda` | `id`, `mesa` (inteiro ≥ 1), `status` (`aberta` por padrão ou `fechada`) | Uma comanda possui vários itens |
| `ItemComanda` | `id`, `comanda`, `descricao`, `quantidade` (inteiro ≥ 1), `preco_unitario` (decimal positivo, duas casas) | FK para `Comanda`, com exclusão protegida (`PROTECT`) |

**Regra de negócio proposta:** itens só podem ser cadastrados, atualizados ou excluídos em comandas abertas. Em PUT/PATCH, considerar o estado final combinado com os valores existentes; ao transferir um item, tanto a comanda de origem quanto a de destino devem estar abertas. Comanda fechada não pode ser reaberta ou alterada; comanda com itens não pode ser excluída. Violações devem retornar HTTP 400 com mensagem explicativa. Valores monetários serão decimais, sem ponto flutuante.

### Rotas planejadas

As rotas abaixo **não existem nesta etapa**. O CRUD completo será oferecido nas duas entidades; as regras restringem operações conforme o estado dos registros.

| Métodos | Rota | Finalidade |
| --- | --- | --- |
| GET, POST | `/api/comandas/` | Listar e abrir comandas |
| GET, PUT, PATCH, DELETE | `/api/comandas/{id}/` | Consultar, atualizar, fechar via `status` e excluir se aberta e vazia |
| GET, POST | `/api/itens/` | Listar e cadastrar itens |
| GET, PUT, PATCH, DELETE | `/api/itens/{id}/` | CRUD de itens, respeitando a situação das comandas |

### Exemplos planejados (não executados)

Abrir uma comanda — `POST /api/comandas/`:

```json
{"mesa": 4}
```

Resultado esperado: HTTP 201 com `id` gerado e `status: "aberta"`.

Adicionar item — `POST /api/itens/`, supondo comanda aberta de ID 1:

```json
{"comanda": 1, "descricao": "Suco de acerola", "quantidade": 2, "preco_unitario": "7.50"}
```

Resultado esperado: HTTP 201. Fechamento planejado: `PATCH /api/comandas/1/` com `{"status":"fechada"}`.

Requisição inválida — repetir o cadastro do item após fechar a comanda:

```json
{"comanda": 1, "descricao": "Café", "quantidade": 1, "preco_unitario": "4.00"}
```

Resultado esperado: HTTP 400, com mensagem como `Não é permitido adicionar itens a uma comanda fechada.` Estes exemplos substituem os exemplos audiovisuais do roteiro em função do tema solicitado.

## Pendências e limite desta etapa

- Aguardar o próximo prompt antes de implementar app, models, serializers, views, validações, migrations ou rotas do restaurante.
- Implementar e executar pelo menos quatro testes de comportamento (cadastro, consulta, atualização/exclusão e regra de negócio).
- Coletar duas métricas com resultados reais e analisar manutenibilidade.
- Registrar uma sugestão de melhoria/teste feita pela IA, sua resposta, decisão de uso e validação. O uso de IA para preparar esta etapa não substitui sozinho essa exigência.
- Realizar merge da funcionalidade em etapa apropriada e concluir README e relatório PDF de até três páginas com os três integrantes e link do repositório.
- Situação dos commits e publicação: complementar após executá-los.
