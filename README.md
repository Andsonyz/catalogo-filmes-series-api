# Cadastro de filmes e séries — Unidade 02

API REST da disciplina PEX1277 — Manutenção de Software, UFERSA. O objetivo é cadastrar gêneros e manter um catálogo de filmes e séries, aplicando gerenciamento de configuração, testes e análise de manutenibilidade.

**Equipe:** Andrew Ferreira de Paiva Silva, Antonio Andson de Oliveira Rocha e Sophia Hellen Pires da Silveira.

**Repositório:** <https://github.com/Andsonyz/catalogo-filmes-series-api>. Base Django Quick Project: <https://github.com/lisa-ufersa/django-quickproject>, com histórico preservado. Django REST Framework e SQLite; sem serviços externos de banco.

## Entidades e regra

- `Genero`: `id` e `nome`.
- `Titulo`: `id`, `nome`, `tipo` (`filme` ou `serie`), `genero` (chave estrangeira obrigatória) e `numero_temporadas` (anulável). Um gênero possui vários títulos; a FK usa `PROTECT`.

Filmes devem ter temporadas nulas; o campo pode ser omitido no cadastro. Séries exigem inteiro maior ou igual a 1. O serializer centraliza a validação da API em POST, PUT e PATCH. Valores inválidos retornam **400**, antes de salvar.

No PATCH, omitir um campo conserva o valor persistido, enquanto `null` explícito tenta limpá-lo. Assim, uma série de duas temporadas só pode virar filme se a mesma requisição enviar `{"tipo":"filme","numero_temporadas":null}`. Enviar apenas `{"tipo":"filme"}` retorna 400 e preserva o registro. Um filme não vira série sem informar temporadas válidas. Escritas diretas pelo ORM não passam pelo serializer.

## Instalação, migrações e inicialização

Requisito recomendado e verificado: **Python 3.12**, Git e acesso ao PyPI. Execute na raiz do clone. Não é necessário ativar o ambiente virtual.

Linux/macOS (verificado em Linux):

```bash
git clone https://github.com/Andsonyz/catalogo-filmes-series-api.git
cd catalogo-filmes-series-api
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python manage.py migrate --noinput
venv/bin/python manage.py check
venv/bin/python manage.py runserver 127.0.0.1:8000
```

Windows/PowerShell:

```powershell
git clone https://github.com/Andsonyz/catalogo-filmes-series-api.git
Set-Location catalogo-filmes-series-api
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate --noinput
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Pare o servidor com Ctrl+C. O SQLite é criado/aplicado pelas migrações; a base contém um `db.sqlite3` versionado, que pode ser reaproveitado. Os testes usam banco separado e descartável. Não exclua o banco local de uma equipe que já possui dados.

## Autenticação e rotas

O catálogo mantém a permissão **AllowAny** da base, inclusive para escrita. Basic, Session e Token são aceitos, mas login não é obrigatório. Para autenticação por token, crie seu próprio usuário com `venv/bin/python manage.py createsuperuser` (PowerShell: `.\venv\Scripts\python.exe manage.py createsuperuser`), envie usuário e senha por POST a `/api/token-auth/` e use `Authorization: Token <token_recebido>`. Não dependa de credenciais herdadas. A reprodução autenticada com usuário descartável está em [docs/api.md](docs/api.md).

| Métodos | URL | Operação |
| --- | --- | --- |
| GET, POST | `/api/generos/` | Listar/cadastrar gêneros |
| GET | `/api/generos/{id}/` | Consultar gênero |
| GET, POST | `/api/titulos/` | Listar/cadastrar títulos |
| GET, PUT, PATCH, DELETE | `/api/titulos/{id}/` | Consultar/atualizar/excluir título |
| POST | `/api/token-auth/` | Obter token com credenciais próprias |
| GET | `/swagger/` e `/schema/` | Documentação e OpenAPI |

## Exemplo de sucesso e rejeição

Com o servidor ativo, em outro terminal Bash, crie um gênero e utilize o ID retornado:

```bash
CATALOGO_GENERO_ID=$(curl --fail --silent -H 'Content-Type: application/json' \
  -d '{"nome":"Ficção científica"}' http://127.0.0.1:8000/api/generos/ \
  | venv/bin/python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
curl -i -H 'Content-Type: application/json' \
  -d "{\"nome\":\"Interestelar\",\"tipo\":\"filme\",\"genero\":$CATALOGO_GENERO_ID}" \
  http://127.0.0.1:8000/api/titulos/
curl -i -H 'Content-Type: application/json' \
  -d "{\"nome\":\"Filme inválido\",\"tipo\":\"filme\",\"genero\":$CATALOGO_GENERO_ID,\"numero_temporadas\":2}" \
  http://127.0.0.1:8000/api/titulos/
```

A primeira criação de título retorna **201**, com `numero_temporadas: null`. A segunda retorna **400**, com `{"numero_temporadas":["Filmes devem ficar sem número de temporadas (null)."]}`, sem gravar outro título.

PowerShell usa `Invoke-RestMethod` para evitar diferenças do alias `curl`:

```powershell
$genero = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/generos/ -ContentType 'application/json' -Body '{"nome":"Drama"}'
$filme = @{ nome = 'Interestelar'; tipo = 'filme'; genero = $genero.id } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/titulos/ -ContentType 'application/json' -Body $filme
$invalido = @{ nome = 'Filme inválido'; tipo = 'filme'; genero = $genero.id; numero_temporadas = 2 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/titulos/ -ContentType 'application/json' -Body $invalido
```

A última chamada gera um erro HTTP 400 esperado no PowerShell. Estes exemplos criam registros: use uma cópia descartável para experimentar ou remova somente os IDs que você criou.

## Testes automatizados

`APITestCase` do DRF, integrado ao pytest-django. Arquivo da equipe: `catalogo/teste.py`, descoberto explicitamente pelo padrão em `pytest.ini`. São 15 testes da equipe e 1 teste demonstrativo herdado de `users`, total de 16. As verificações incluem HTTP 400, mensagem, ausência de gravação, `refresh_from_db()` após PATCH rejeitado e conversão válida com null.

```bash
venv/bin/python -m pytest catalogo/teste.py -v
venv/bin/python -m pytest -v
venv/bin/python -m pytest catalogo/teste.py::CatalogoAPITests::test_patch_rejeita_conversao_para_serie_sem_informar_temporadas -v
```

No PowerShell, substitua `venv/bin/python` por `.\venv\Scripts\python.exe` nos três comandos. O aviso de depreciação do `pytz` herdado no Python 3.12 não é uma falha de teste.

## Reprodução das duas métricas

Instale ferramentas adicionais fixadas em `requirements-metricas.txt`. A cobertura é de **linhas** do código de produção do app `catalogo`. `.coveragerc` exclui testes e migrações; `config`, `users`, dependências e ambiente virtual ficam fora do escopo. Não é cobertura de branches.

```bash
venv/bin/python -m pip install -r requirements-metricas.txt
venv/bin/python -m coverage --version
venv/bin/python -m radon --version
venv/bin/python -m coverage erase
venv/bin/python -m coverage run -m pytest -v
venv/bin/python -m coverage report -m
venv/bin/python -m radon cc catalogo -s -j -e 'catalogo/test*.py,catalogo/*test*.py,catalogo/migrations/*'
```

Windows/PowerShell:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-metricas.txt
.\venv\Scripts\python.exe -m coverage --version
.\venv\Scripts\python.exe -m radon --version
.\venv\Scripts\python.exe -m coverage erase
.\venv\Scripts\python.exe -m coverage run -m pytest -v
.\venv\Scripts\python.exe -m coverage report -m
.\venv\Scripts\python.exe -m radon cc catalogo -s -j -e 'catalogo/test*.py,catalogo/*test*.py,catalogo/migrations/*'
```

No JSON do Radon, `complexity` é a complexidade ciclomática por bloco; compare métodos/funções e identifique o máximo. Não está sendo coletado índice de manutenibilidade, quantidade de linhas ou outra métrica. Resultados medidos, versões, revisão, limitações e interpretação estão em [docs/evidencias.md](docs/evidencias.md).

As instruções foram verificadas em clone separado, ambiente virtual novo e SQLite novo em Linux. Os comandos PowerShell correspondem aos executáveis e APIs nativos do Windows; a execução nativa no Windows não foi verificada neste ambiente Linux. O relatório final ainda não foi redigido.
