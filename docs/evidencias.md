# Unidade 02 — evidências

## Identificação e fontes

- Disciplina: PEX1277 — Manutenção de Software, UFERSA.
- Integrantes: Andrew Ferreira de Paiva Silva, Antonio Andson de Oliveira Rocha e Sophia Hellen Pires da Silveira.
- Tema definitivo, corrigido pelo solicitante: **Cadastro de filmes e séries**. Título previsto para o relatório de entrega: **Cadastro de filmes e séries — Unidade 02**.
- Enunciado: `Trabalho_Uni02_-_Manuteno.pdf`, lido integralmente com `pdftotext -layout`.
- SIGAA: equipe de até três integrantes; entrega em documento PDF único, contendo os nomes e o link do repositório; arquivo de até 10 MB; prazo exibido de 03/11/2026 às 00h00 até 10/11/2026 às 23h59. Horários transcritos da tela.
- Relatório do professor: máximo de três páginas, com entidades/endpoints, testes, duas métricas, uso de IA e dificuldades.
- Pontuação: Git/GitHub 2,0; API/manutenibilidade 3,5; testes 2,5; métricas 1,0; IA 1,0.
- Na preparação inicial, foram recebidos o PDF e a tela; o Prompt 1 foi fornecido depois em texto. As etapas seguintes dependem das instruções posteriores do solicitante.

## Origem, estado inicial e preservação

- Diretório inicial: `/workspace`, sem repositório Git e sem código de projeto prévio. Os arquivos anexados foram preservados.
- Destino existente e público: <https://github.com/Andsonyz/catalogo-filmes-series-api>. O repositório existente foi reutilizado para o tema definitivo.
- Na primeira execução, `git ls-remote --symref ... HEAD 'refs/heads/*'` no destino retornou saída vazia e código 0: repositório sem commits/branches publicados. A API do GitHub informa branch padrão `main`.
- Base: <https://github.com/lisa-ufersa/django-quickproject>, branch `main`, commit `a59bd49d22f3a0987798cc84449797f5849b4d03` (`ssh-key test`).
- Cópia separada em `/workspace/catalogo-filmes-series-api`, criada com `git clone --origin upstream`, preservando o histórico da base.
- `origin`: repositório da equipe; `upstream`: professor, com URL de push local `DISABLED`. Nenhuma escrita no repositório do professor.
- Branch da primeira execução: `feat/comandas-restaurante`, criada a partir da revisão acima. Naquela execução, a `main` permaneceu na revisão original e o agente não realizou merge. O estado atual e a branch corrigida estão registrados abaixo.
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
| `venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload` | Servidor local iniciado e verificado; encerrado intencionalmente ao final por SIGTERM (retorno −15), não por falha da aplicação |
| `curl` em `/swagger/`, `/schema/`, `/users/` | HTTP 200 nas três rotas; `/users/` retorna `[]` |
| `curl -X POST` com `{}` em `/api/token-auth/` | HTTP 400, informando usuário e senha obrigatórios; rota acessível |
| `curl` em `/users/999999/` | HTTP 404 para registro inexistente |
| `curl -X OPTIONS` em `/users/` | HTTP 405; base restringe os métodos a `get` e `put` |

### Limitações herdadas e verificação visual

- Não houve falha na instalação, nas migrações, no check ou na suíte existente.
- O único teste herdado é `users/tests.py::UserTestCase::test_user`, que compara `1 == 1`. Seu sucesso não comprova comportamento da API e não satisfaz os quatro testes exigidos para a entrega.
- A API de exemplo `/users/` oferece GET/PUT, não CRUD completo. Isso é uma limitação da base a considerar na próxima etapa.
- A tentativa de usar o navegador compartilhado retornou `Browser runtime unavailable`. A alternativa com Chromium/Playwright local funcionou: HTTP 200, título `Swagger`, operações `/api/token-auth/`, `/schema/`, `/users/` e `/users/{id}/` renderizadas; `page_errors: []`. Captura em [swagger-base.png](swagger-base.png). Isso não bloqueou a etapa nem exigiu novo acesso.

## Planejamento do domínio no Prompt 1 (histórico)

Manter a estrutura Django REST Framework e SQLite da base e planejar um app `catalogo` com duas entidades.

| Entidade | Campos planejados | Relação |
| --- | --- | --- |
| `Genero` | `id`, `nome` | Um gênero classifica vários títulos |
| `Titulo` | `id`, `nome`, `tipo` (`filme` ou `serie`), `genero`, `numero_temporadas` (inteiro anulável) | FK obrigatória para o gênero principal, com exclusão protegida (`PROTECT`) |

**Regra de negócio:** filme deve ter `numero_temporadas` nulo (ou omitido no cadastro, resultando em nulo); série exige um número inteiro maior ou igual a 1. A validação deve ocorrer no cadastro e em PUT/PATCH, considerando os valores finais do registro: campos recebidos combinados com os campos existentes. Requisições inválidas retornam HTTP 400 com mensagem explicativa, sem persistir alterações parciais.

Em PATCH, trocar uma série por filme exige enviar também `numero_temporadas: null` se havia temporadas. Trocar um filme por série exige informar um inteiro ≥ 1. Alterar somente o nome de uma série mantém suas temporadas e deve continuar válido. Não descartar silenciosamente um número de temporadas incompatível com o tipo.

### Rotas planejadas

No Prompt 1, as rotas abaixo ainda não existiam. Foram implementadas na etapa registrada ao final deste documento.

| Métodos | Rota | Finalidade |
| --- | --- | --- |
| GET, POST | `/api/generos/` | Listar e cadastrar gêneros |
| GET | `/api/generos/{id}/` | Consultar um gênero |
| GET, POST | `/api/titulos/` | Listar e cadastrar títulos |
| GET, PUT, PATCH, DELETE | `/api/titulos/{id}/` | Consultar, atualizar integral/parcialmente e excluir títulos |

### Exemplos planejados (não executados)

Cadastrar um gênero — `POST /api/generos/`:

```json
{"nome": "Ficção científica"}
```

Resultado esperado: HTTP 201. Os próximos exemplos pressupõem um gênero existente com ID 1.

Filme — `POST /api/titulos/`:

```json
{"nome": "Interestelar", "tipo": "filme", "genero": 1, "numero_temporadas": null}
```

Resultado esperado: HTTP 201. Omitir `numero_temporadas` no cadastro de filme também será válido.

Série — `POST /api/titulos/`:

```json
{"nome": "Dark", "tipo": "serie", "genero": 1, "numero_temporadas": 3}
```

Resultado esperado: HTTP 201.

Requisição inválida — `POST /api/titulos/`:

```json
{"nome": "Série inválida", "tipo": "serie", "genero": 1, "numero_temporadas": 0}
```

Resultado esperado: HTTP 400, com mensagem como `Séries exigem um número inteiro de temporadas maior ou igual a 1.` Filme com temporadas não nulas também será inválido.

Exemplo de atualização: em uma série com três temporadas, `PATCH /api/titulos/{id}/` com `{"tipo":"filme"}` deve retornar 400; com `{"tipo":"filme","numero_temporadas":null}` deve retornar 200.

## Pendências ao fim do Prompt 1 (histórico)

- Aguardar o próximo prompt antes de implementar app, models, serializers, views, validações, migrations ou rotas do catálogo.
- Implementar e executar pelo menos quatro testes de comportamento (cadastro, consulta, atualização/exclusão e regra de negócio).
- Coletar duas métricas com resultados reais e analisar manutenibilidade.
- Registrar uma sugestão de melhoria/teste feita pela IA, sua resposta, decisão de uso e validação. O uso de IA para preparar esta etapa não substitui sozinho essa exigência.
- Realizar merge da funcionalidade do catálogo em etapa apropriada e concluir README e relatório PDF de até três páginas, com título **Cadastro de filmes e séries — Unidade 02**, os três integrantes e link do repositório.

## Registro Git da primeira execução (histórico)

- Commit de preparação: `51cb8d482fa219ae8021c418fefe6dd936d36a25` — `docs: registra preparação da base e planejamento de comandas`.
- `git push --set-upstream origin main feat/comandas-restaurante`: código 0; as duas branches foram publicadas sem sobrescrever histórico existente.
- `git ls-remote --symref origin HEAD refs/heads/main refs/heads/feat/comandas-restaurante`: confirmou branch padrão `main` apontando para a revisão original do professor e a funcionalidade apontando para o commit de preparação.
- `git merge-base --is-ancestor a59bd49d22f3a0987798cc84449797f5849b4d03 HEAD`: código 0, confirmando ancestralidade da base.
- `git diff --name-only a59bd49d22f3a0987798cc84449797f5849b4d03 -- '*.py' requirements.txt pytest.ini db.sqlite3`: saída vazia, código 0; nenhum código, dependência, teste ou banco da base foi alterado.
- `git diff --cached --check`: código 0 antes do commit. `git status --short --branch` após a primeira publicação: branch sincronizada e checkout limpo.
- O fechamento recebeu o commit documental `12f8f3f`. O agente não fez merge naquela execução. Nenhuma pendência de acesso permaneceu.

## Correção do tema — somente complemento do Prompt 1

- O solicitante corrigiu o tema de restaurante/comandas para **Cadastro de filmes e séries**. O planejamento anterior foi substituído por `Genero` e `Titulo`, com cadastro/consulta de gêneros, CRUD de títulos e validação de temporadas no cadastro e na atualização.
- A inspeção inicial encontrou checkout limpo na revisão `12f8f3f`. `git fetch origin` revelou que a equipe já havia integrado a preparação na `main`: commit `963f6b704c30e119d84641123a6fcd1ea14f2a8d` (`Merge pull request #1 from Andsonyz/feat/comandas-restaurante`). A árvore desse merge era idêntica à do checkout anterior.
- Reutilizados o repositório `Andsonyz/catalogo-filmes-series-api`, o remoto `origin`, o ambiente `venv` e o histórico do Django Quick Project. O remoto do professor segue com push desabilitado.
- Não existia branch `feat/catalogo-audiovisual`, local ou remota. Criada com `git switch -c feat/catalogo-audiovisual origin/main`, a partir do merge da equipe, preservando os commits anteriores e a branch antiga.
- Corrigidos o README, as entidades, as rotas, as regras, os exemplos e o título previsto para o relatório. Nenhum model, endpoint ou teste de domínio foi implementado.
- Mantidos os resultados reais da primeira execução, o arquivo `registro-prompt1.log` e a captura `swagger-base.png` sem alteração. Referências ao tema antigo nesses registros e nesta explicação são históricas, não fazem parte do escopo vigente.
- A revisão documental desta correção e as verificações do estado Git estão em [registro-correcao-tema.log](registro-correcao-tema.log). As verificações de execução da base acima pertencem à primeira execução; não foram apresentadas como novas execuções nesta correção documental.
- A correção será registrada em novo commit descritivo, sem reescrever commits nem realizar merge da nova branch. O hash final e a publicação são informados no fechamento da conversa.

## Implementação da API — etapa atual

Branch `feat/catalogo-audiovisual`, iniciada nesta etapa em `983f5e9`, com checkout limpo. Reutilizado o remoto `origin` da equipe. Implementados o app `catalogo`, models `Genero` e `Titulo`, FK com `PROTECT`, migration `0001_initial`, serializers e viewsets registrados no `SimpleRouter` da base. Nenhuma interface adicional foi criada.

A validação de entrada está centralizada em `TituloSerializer`: `tipo` aceita `filme`/`serie`; o campo de temporadas valida inteiro ≥ 1 quando não nulo; `validate()` verifica a combinação de tipo e temporadas para POST, PUT e PATCH. Campos omitidos utilizam o estado persistido; `null` explícito é mantido. A validação ocorre antes de salvar. Essa regra é da API; escritas diretas pelo ORM não passam pelo serializer.

Permissões verificadas: `users` usa `AllowAny`; não há `DEFAULT_PERMISSION_CLASSES` restritiva. Mantido `AllowAny` no catálogo, com Basic/Session/Token herdados. A consulta anônima retornou 200. Os cenários de escrita e leitura foram realizados com Token obtido em `/api/token-auth/` usando usuário descartável. Usuário, senha e token não foram registrados em texto aberto. Reprodução: [api.md](api.md).

### Verificações executadas

| Comando | Resultado real |
| --- | --- |
| `venv/bin/python manage.py makemigrations catalogo` | Criada `catalogo/migrations/0001_initial.py` |
| `venv/bin/python manage.py migrate --noinput` | `Applying catalogo.0001_initial... OK` |
| `venv/bin/python manage.py check` | `System check identified no issues (0 silenced).` |
| `venv/bin/python manage.py makemigrations --check --dry-run` | `No changes detected` |
| `venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload` | Servidor iniciado; usado pelos cenários HTTP reais e encerrado ao final com Ctrl+C |
| `venv/bin/python manage.py spectacular --validate --file /workspace/scratch/catalogo-schema.yaml` | Código 0, schema OpenAPI válido |
| `git diff --check` | Código 0 |

Logs: [registro-implementacao.log](registro-implementacao.log) e [cenarios-api.log](cenarios-api.log). As chamadas HTTP foram feitas por um script temporário em `/workspace/scratch/exercitar_catalogo_http.py`, fora da suíte de testes. Nenhum teste automatizado de Django/pytest foi criado ou executado nesta etapa, conforme o limite solicitado.

### Resultados HTTP observados

Todas as URLs abaixo usam `http://127.0.0.1:8000`. IDs 1 e 2 foram gerados nesta execução e os respectivos registros já foram removidos.

| Método e URL | HTTP | Resultado |
| --- | --- | --- |
| GET `/api/titulos/`, anônimo | 200 | Lista inicial vazia; contagem 0 |
| POST `/api/token-auth/` | 200 | Token válido para o usuário descartável |
| POST `/api/generos/` | 201 | Gênero descartável, ID 1 |
| GET `/api/generos/` e `/api/generos/1/` | 200 | Listagem e consulta do gênero criado |
| POST `/api/titulos/`, filme com temporadas omitidas | 201 | ID 1, temporadas nulas |
| POST `/api/titulos/`, série com duas temporadas | 201 | ID 2, temporadas 2 |
| GET `/api/titulos/` e `/api/titulos/2/` | 200 | Dois títulos; detalhe da série correto |
| PATCH `/api/titulos/2/`, apenas nome | 200 | Nome alterado; temporadas continuam 2, confirmado por GET |
| POST `/api/titulos/`, filme com temporadas 2 | 400 | Mensagem sobre temporadas nulas; contagem permaneceu 2 |
| PATCH `/api/titulos/2/`, apenas tipo filme | 400 | Estado anterior preservado, confirmado por GET |
| PATCH `/api/titulos/2/`, temporadas null mantendo série | 400 | Registro preservado |
| PATCH `/api/titulos/2/`, temporadas 0, −1 ou 1.5 | 400 | Validação de inteiro positivo; registro preservado |
| PATCH `/api/titulos/2/`, tipo documentario | 400 | Tipo inválido; registro preservado |
| PATCH `/api/titulos/2/`, tipo filme e temporadas null | 200 | Conversão válida, confirmada por GET |
| PATCH `/api/titulos/2/`, apenas tipo série após conversão | 400 | Filme com temporadas nulas preservado |
| PUT `/api/titulos/2/`, série completa com temporadas 2 | 200 | Atualização integral válida |
| PUT `/api/titulos/2/`, filme omitindo temporadas ainda persistidas | 400 | Registro preservado, inclusive nome |
| DELETE `/api/titulos/2/` e `/api/titulos/1/` | 204 | Ambos os títulos descartáveis excluídos |
| GET de cada título excluído | 404 | Exclusão confirmada |
| GET `/api/titulos/` ao final | 200 | Lista vazia; contagem voltou a 0 |

### Preservação e dificuldades

Antes das migrações foi criada uma cópia SQLite de segurança em `/workspace/scratch/catalogo-antes-api.sqlite3`. A conferência final comparou todas as linhas das tabelas preexistentes. O usuário e o token originais foram preservados. As únicas adições permanentes foram a migration do catálogo, dois content types e oito permissões padrão do Django; sequências SQLite também avançaram com os registros descartáveis.

A primeira versão do verificador de preservação falhou ao exigir igualdade total em `django_content_type`, sem considerar metadados criados por `migrate`. A inspeção mostrou zero linhas antigas removidas/alteradas e somente os dois content types e oito permissões esperados. O verificador foi ajustado para permitir exatamente essas adições, preservando a comparação de todas as linhas anteriores; a nova execução terminou com código 0. Essa falha foi do verificador auxiliar, não da API, e permanece no log.

Os títulos foram excluídos pela API. O gênero e o usuário/token temporários foram removidos pelo ORM, limitados aos IDs criados nesta execução; não há endpoint de exclusão de gêneros no escopo. As tabelas do catálogo terminaram vazias. O banco local permanece migrado e, por já ser versionado na base, aparece como modificado no checkout; não será incluído nos commits de código/documentação. Novos checkouts aplicam a migration normalmente.

### Commits e pendências

- `14f0c61` — `feat: modela gêneros e títulos com persistência SQLite`.
- `a6693cd` — `feat: expõe catálogo REST com validação de temporadas em criação e atualização`.
- Evidências e instruções de reprodução recebem commit documental separado.
- Parar antes da etapa de testes automatizados. Continuam pendentes testes, métricas, análise acadêmica de uso de IA, merge e relatório final. O teste demonstrativo herdado continua no projeto; seu resultado antigo não representa validação automatizada da nova API.
