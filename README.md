# Cadastro de filmes e séries — Unidade 02

Trabalho da disciplina PEX1277 — Manutenção de Software, UFERSA.

**Equipe:** Andrew Ferreira de Paiva Silva, Antonio Andson de Oliveira Rocha e Sophia Hellen Pires da Silveira.

**Repositório:** <https://github.com/Andsonyz/catalogo-filmes-series-api>.

Aplicação com Django, Django REST Framework e SQLite para cadastrar gêneros e gerenciar filmes e séries. Possui página inicial, interface do catálogo e documentação interativa da API.

## Tutorial completo de execução local

Este é o roteiro de instalação e acesso do projeto atual. Escolha os comandos do seu sistema operacional e execute uma linha por vez. A página normal funciona **sem login**; o superusuário é opcional e serve para entrar no painel administrativo do Django.

### 1. Preparar os requisitos e abrir a pasta

Instale **Python 3.11**, com `pip` e o módulo `venv`, e Git se for clonar o repositório. As dependências estão fixadas em `requirements.txt`; este roteiro usa Python 3.11 para evitar incompatibilidades com versões mais recentes do Python.

Se ainda não baixou o projeto, execute:

```sh
git clone https://github.com/Andsonyz/catalogo-filmes-series-api.git
cd catalogo-filmes-series-api
```

Se o projeto já está baixado, abra um terminal na pasta que contém `manage.py` e `requirements.txt`. **Não clone novamente nem entre em outra subpasta.** No Windows deste ambiente, por exemplo:

```powershell
cd C:\Users\anton\catalogo-filmes-series-api
```

### 2. Instalar e iniciar — Windows (PowerShell)

Confira se o Python 3.11 está instalado:

```powershell
py -3.11 --version
```

Na raiz do projeto, crie o ambiente, instale as dependências, prepare o banco e inicie o servidor:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Não é necessário ativar o ambiente virtual: os comandos usam diretamente o Python de `venv`, evitando bloqueios de `Activate.ps1` no PowerShell. Se já existe um `venv` com Python 3.11, pule apenas a primeira linha de criação do ambiente.

### 2. Instalar e iniciar — Linux/macOS (Bash ou Zsh)

Use esta alternativa no lugar dos comandos de Windows. Confira primeiro:

```bash
python3.11 --version
```

Na raiz do projeto:

```bash
python3.11 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
./venv/bin/python manage.py migrate
./venv/bin/python manage.py check
./venv/bin/python manage.py runserver 127.0.0.1:8000
```

Também não é necessário ativar o ambiente. Se já existe um `venv` com Python 3.11, pule apenas a primeira linha de criação do ambiente.

### 3. Acessar a página normal

Ao final, `check` deve informar `System check identified no issues` e o servidor deve mostrar `Starting development server at http://127.0.0.1:8000/`. **Deixe esse terminal aberto** enquanto usa a aplicação. Se algum comando falhar, resolva o erro antes de executar o próximo.

Abra no navegador:

| Página | Endereço | Precisa de login? |
| --- | --- | --- |
| Página inicial | <http://127.0.0.1:8000/> | Não |
| Interface de filmes e séries | <http://127.0.0.1:8000/catalogo/> | Não |
| Área da cliente — O que assistir | <http://127.0.0.1:8000/assistir/> | Não |
| Documentação interativa (Swagger) | <http://127.0.0.1:8000/swagger/> | Não |
| Lista/cadastro de gêneros na API | <http://127.0.0.1:8000/api/generos/> | Não |
| Lista/cadastro de títulos na API | <http://127.0.0.1:8000/api/titulos/> | Não |
| Painel administrativo | <http://127.0.0.1:8000/admin/> | Sim, usuário com acesso administrativo |

Na página inicial, clique em **Gerenciar catálogo** ou vá diretamente a `/catalogo/`. Para usar a interface de gestão, mantenha o JavaScript habilitado:

1. Clique em **＋ Novo gênero**, informe um nome (por exemplo, Drama) e clique em **Criar gênero**.
2. Preencha nome, tipo e gênero de um título.
3. Para um filme, não informe temporadas. Para uma série, informe um inteiro maior ou igual a 1.
4. Clique em **Adicionar ao catálogo**. Use **Editar** ou **Excluir** no cartão para gerenciar o título.

Os registros ficam no arquivo local `db.sqlite3` e permanecem após reiniciar o servidor. Um banco novo começa sem gêneros e títulos; não há carga automática de exemplos.

#### Simular o acesso de uma cliente

1. Cadastre um gênero e um filme pela área de gestão acima.
2. Volte à página inicial e clique em **O que assistir**, ou abra <http://127.0.0.1:8000/assistir/>. Não é necessário login.
3. Digite o nome completo ou parte do nome do filme, selecione seu gênero e, se quiser, escolha o tipo **Filme**. A busca ignora diferenças entre maiúsculas e minúsculas, inclusive nas letras acentuadas.
4. Clique em **Pesquisar catálogo**. Os filtros são combinados: o filme só aparece se corresponder ao nome, gênero e tipo escolhidos.
5. O cartão informa **Disponível no catálogo**. Se não houver correspondência, a página informa **Nenhum título encontrado**. Use **Limpar filtros** para consultar todo o acervo.

Também é possível pesquisar somente por gênero ou tipo, sem preencher o nome. A pesquisa funciona sem JavaScript e o endereço com os filtros pode ser copiado. A área da cliente consulta os registros reais e não oferece edição ou exclusão; não há reprodução de vídeo, pois o projeto armazena os dados dos títulos. As permissões existentes da API continuam iguais.

O link **Voltar à página inicial** está disponível na gestão, no diálogo de novo gênero e nas páginas HTML da API de acervo e gêneros.

### 4. Criar e acessar o superusuário (opcional)

Este passo é necessário somente para usar `/admin/`. A instalação não cria uma conta padrão: **não há login e senha garantidos como `admin/adminadmin`**.

No terminal do servidor, pressione **Ctrl+C**. Na mesma pasta, execute o comando do seu sistema:

**Windows (PowerShell):**

```powershell
.\venv\Scripts\python.exe manage.py createsuperuser
```

**Linux/macOS:**

```bash
./venv/bin/python manage.py createsuperuser
```

Responda aos campos `Username`, `Email address` (pode ficar vazio) e `Password`. Escolha um nome disponível e uma senha própria; confirme a senha. **A senha não aparece enquanto você digita, nem como asteriscos.** Se o Django apontar que ela é fraca, escolha outra. Aguarde a mensagem `Superuser created successfully`.

Reinicie o servidor:

**Windows (PowerShell):**

```powershell
.\venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

**Linux/macOS:**

```bash
./venv/bin/python manage.py runserver 127.0.0.1:8000
```

Abra <http://127.0.0.1:8000/admin/> e entre com o **nome de usuário e a senha que acabou de criar**. O painel permite administrar usuários e grupos. Os modelos do catálogo não estão registrados nesse painel; gerencie gêneros, filmes e séries em `/catalogo/` ou pela API.

Se você já criou um superusuário, basta usar essa conta. Para trocar uma senha esquecida, use o comando abaixo e substitua `SEU_USUARIO` pelo nome cadastrado:

**Windows (PowerShell):**

```powershell
.\venv\Scripts\python.exe manage.py changepassword SEU_USUARIO
```

**Linux/macOS:**

```bash
./venv/bin/python manage.py changepassword SEU_USUARIO
```

### 5. Parar e executar novamente

Para parar, pressione **Ctrl+C** no terminal do servidor. Nos próximos acessos, abra o terminal na raiz do projeto e execute apenas o `runserver` do seu sistema, mostrado acima. Não é necessário recriar o ambiente ou o superusuário a cada execução.

Depois de atualizar o código, com o servidor parado, repita `-m pip install -r requirements.txt`, `manage.py migrate` e `manage.py check` usando o Python de `venv`, antes de iniciar novamente. As migrações já estão no repositório; não é necessário executar `makemigrations` para instalar o projeto.

### Solução de problemas

| Problema | Como resolver |
| --- | --- |
| `py` não é reconhecido ou Python 3.11 não foi encontrado | Instale Python 3.11 com o launcher no Windows e reabra o terminal. Se `python --version` indicar 3.11, pode usar `python -m venv venv` para criar o ambiente. |
| `python3.11` não encontrado ou erro de `ensurepip`/`venv` no Linux/macOS | Instale Python 3.11 e o suporte a `venv`/`pip` do seu sistema antes de criar o ambiente. |
| O caminho `venv\Scripts\python.exe` ou `venv/bin/python` não existe | Confira a pasta atual e crie o ambiente com o comando do seu sistema. Não reutilize um ambiente virtual copiado de outra máquina ou sistema operacional. |
| `No module named django`, `rest_framework` ou `drf_spectacular` | Reexecute a instalação de `requirements.txt` com o Python de `venv`. Evite `pip` ou `python` soltos, que podem apontar para outra instalação. |
| Instalação falha ao compilar uma dependência | Confira a versão do Python do ambiente. Use um ambiente criado com Python 3.11 para estas dependências fixadas. |
| `No module named catalogo.views` ou `TemplateDoesNotExist` | Use os arquivos corrigidos deste projeto: `catalogo/views.py` e templates em `catalogo/templates/catalogo/`. Reinicie o servidor após atualizar. |
| `no such table` ou aviso de migrações pendentes | Pare o servidor e execute `manage.py migrate` com o Python de `venv`. Não apague `db.sqlite3` para resolver: ele contém seus dados. |
| A página não abre / conexão recusada | Confira se `runserver` continua aberto e sem erro; use `http://127.0.0.1:8000/`, com HTTP. Não abra o HTML diretamente pelo explorador de arquivos. |
| Porta 8000 ocupada | Troque `127.0.0.1:8000` por `127.0.0.1:8001` no comando `runserver` e use a porta 8001 em todos os endereços do navegador. |
| Login administrativo recusado | Use a conta criada com `createsuperuser`; ela é independente da página normal. Se necessário, use `changepassword`. |
| Erro 403/CSRF ao salvar após entrar no admin | Recarregue `/catalogo/` para obter um token atualizado. Mantenha o mesmo endereço (`127.0.0.1`) durante a navegação. |

## Verificação e testes

Com as dependências instaladas, na raiz do projeto:

**Windows (PowerShell):**

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe -m pytest -v
```

**Linux/macOS:**

```bash
./venv/bin/python manage.py check
./venv/bin/python manage.py makemigrations --check --dry-run
./venv/bin/python -m pytest -v
```

Os testes usam um banco separado do banco local. Eles verificam a API, a renderização das páginas e o CSRF da interface em sessões autenticadas.

O roteiro de instalação foi validado com Python 3.11.9 no Windows/PowerShell em ambiente e banco novos, incluindo migrações, acesso HTTP e login administrativo com conta temporária. A suíte atual tem 33 testes, incluindo navegação, pesquisa da cliente, filtros combinados, paginação e validação. Os comandos de Linux/macOS não foram executados neste ambiente. A inspeção visual da área da cliente foi bloqueada pela ferramenta de navegador; a verificação funcional foi feita por testes e HTTP local.

## Entrega acadêmica e métricas

A verificação de 10/11/2026 com Python 3.11.9 no Windows executou **33 testes**. A cobertura de linhas do código Python de produção do app `catalogo` foi **99,01%** (100 de 101 linhas). A maior complexidade ciclomática entre funções e métodos foi **6** (B), na função `pagina_assistir`; `TituloSerializer.validate` teve complexidade **5** (A). Cobertura de linhas não significa cobertura de todos os caminhos e não inclui JavaScript, HTML ou CSS; a complexidade indica pontos que merecem revisão, não uma avaliação completa da qualidade do projeto.

O escopo e a análise, os resultados brutos, as medições históricas e a identificação do código local medido estão em [evidências e métricas](docs/evidencias.md#estado-atual--10112026). O [registro de uso de IA](docs/uso-ia.md) apresenta o prompt, a resposta, a sugestão aceita e sua validação. O [relatório final em PDF](output/pdf/Cadastro_filmes_series_Unidade02.pdf) contém três páginas, com integrantes, contexto, entidades e endpoints, testes, métricas, uso de IA e dificuldades. Foi formatado integralmente em Times New Roman tamanho 12, com texto preto e parágrafos justificados, e revisado por renderização e inspeção das três páginas.

Para reproduzir, use o ambiente virtual preparado acima. O arquivo [.coveragerc](.coveragerc) inclui o código Python de `catalogo` e exclui testes e migrações. As ferramentas ficam em dependências opcionais, separadas de `requirements.txt`.

**Windows (PowerShell):**

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-metricas.txt
.\venv\Scripts\python.exe -m coverage run -m pytest -v
.\venv\Scripts\python.exe -m coverage report -m
.\venv\Scripts\python.exe -m radon cc catalogo -s -e 'catalogo/test*.py,catalogo/*test*.py,catalogo/migrations/*'
```

**Linux/macOS:**

```bash
./venv/bin/python -m pip install -r requirements-metricas.txt
./venv/bin/python -m coverage run -m pytest -v
./venv/bin/python -m coverage report -m
./venv/bin/python -m radon cc catalogo -s -e 'catalogo/test*.py,catalogo/*test*.py,catalogo/migrations/*'
```

O arquivo local `.coverage` gerado pela reprodução é ignorado pelo Git. Os números podem mudar conforme a revisão do código e dos testes. Os comandos de métricas foram executados em Windows; os equivalentes Linux/macOS ainda não foram validados nesta etapa.

## API e escopo

`Genero` e `Titulo` são relacionados por chave estrangeira. A aplicação oferece cadastro e consulta de gêneros e CRUD completo de títulos. Filmes têm `numero_temporadas` nulo; séries exigem um inteiro maior ou igual a 1, tanto no cadastro quanto na atualização.

O catálogo usa `AllowAny`, inclusive para escrita: o superusuário não é necessário para cadastrar pela interface ou pela API. A base aceita autenticação Basic, Session e Token; o endpoint `/api/token-auth/` recebe credenciais de uma conta existente. O schema OpenAPI está em `/schema/` e há um endpoint de exemplo em `/users/`.

Este roteiro é para desenvolvimento local. Consulte [rotas, autenticação e cenários HTTP](docs/api.md) e [evidências e pendências](docs/evidencias.md) para os detalhes técnicos e registros da entrega.
