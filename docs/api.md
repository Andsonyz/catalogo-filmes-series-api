# API de cadastro de filmes e séries

## Execução

Na raiz do repositório, com o ambiente virtual instalado conforme o README:

```bash
venv/bin/python manage.py migrate --noinput
venv/bin/python manage.py check
venv/bin/python manage.py runserver 127.0.0.1:8000
```

Swagger: `http://127.0.0.1:8000/swagger/`. Schema: `/schema/`.

| Métodos | Rota | Operação |
| --- | --- | --- |
| GET, POST | `/api/generos/` | Listar/cadastrar gêneros |
| GET | `/api/generos/{id}/` | Consultar gênero |
| GET, POST | `/api/titulos/` | Listar/cadastrar títulos |
| GET, PUT, PATCH, DELETE | `/api/titulos/{id}/` | Consultar/atualizar/excluir título |

`Genero`: `id` somente leitura; `nome` obrigatório, até 100 caracteres.
`Titulo`: `id` somente leitura; `nome` obrigatório, até 200 caracteres; `tipo` igual a `filme` ou `serie`; `genero` é o ID de um gênero existente; `numero_temporadas` é anulável.

Filmes exigem temporadas nulas (campo também pode ser omitido no cadastro). Séries exigem um inteiro ≥ 1. No PUT/PATCH, campos opcionais omitidos conservam o valor persistido; `null` explícito limpa o valor, se a combinação final for válida. Assim, uma série com temporadas só muda para filme quando a mesma requisição envia `numero_temporadas: null`. Uma requisição inválida recebe 400 e não altera o registro. O PUT exige também os campos obrigatórios; o PATCH permite atualização parcial.

## Autenticação e permissões

A base aplica `AllowAny` em sua view de exemplo e não define permissão global restritiva. O catálogo mantém `AllowAny`, inclusive para escrita. As classes de autenticação herdadas aceitam Basic, Session e Token. Autenticação disponível não significa autenticação obrigatória. Os cenários registrados foram executados com Token; uma consulta anônima também foi confirmada.

Para reproduzir com um usuário descartável, abra outro terminal na raiz do projeto e crie uma conta comum, usando nome novo e senha escolhida localmente:

```bash
venv/bin/python manage.py shell -c 'from django.contrib.auth.models import User; from getpass import getpass; u = User.objects.create_user(username=input("Usuário temporário: "), password=getpass("Senha: ")); print("ID temporário:", u.pk)'
```

Guarde o ID desse usuário para limpeza. No Bash, obtenha o token sem registrá-lo em arquivos:

```bash
read -r -p 'Usuário temporário: ' CATALOGO_USUARIO
read -r -s -p 'Senha: ' CATALOGO_SENHA
CATALOGO_TOKEN=$(curl --fail --silent --show-error \
  --data-urlencode "username=$CATALOGO_USUARIO" \
  --data-urlencode "password=$CATALOGO_SENHA" \
  http://127.0.0.1:8000/api/token-auth/ \
  | venv/bin/python -c 'import json,sys; print(json.load(sys.stdin)["token"])')
unset CATALOGO_SENHA
```

O endpoint de token deve retornar 200. Nas próximas chamadas, `-i` mostra o código HTTP. Use somente IDs dos registros que você criar; não reutilize os IDs do log como se fossem fixos.

## Roteiro HTTP descartável

1. Consulte a lista inicial e anote sua contagem. Cadastre um gênero (201) e guarde o ID retornado em `CATALOGO_GENERO_ID`.

```bash
curl -i -H "Authorization: Token $CATALOGO_TOKEN" http://127.0.0.1:8000/api/titulos/
curl -i -H "Authorization: Token $CATALOGO_TOKEN" -H 'Content-Type: application/json' \
  -d '{"nome":"Gênero descartável API"}' http://127.0.0.1:8000/api/generos/
read -r -p 'ID do gênero recém-criado: ' CATALOGO_GENERO_ID
```

2. Crie um filme sem temporadas e uma série com duas temporadas (201 em ambos). Guarde os IDs retornados.

```bash
curl -i -H "Authorization: Token $CATALOGO_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"nome\":\"Filme descartável\",\"tipo\":\"filme\",\"genero\":$CATALOGO_GENERO_ID}" \
  http://127.0.0.1:8000/api/titulos/
read -r -p 'ID do filme recém-criado: ' CATALOGO_FILME_ID
curl -i -H "Authorization: Token $CATALOGO_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"nome\":\"Série descartável\",\"tipo\":\"serie\",\"genero\":$CATALOGO_GENERO_ID,\"numero_temporadas\":2}" \
  http://127.0.0.1:8000/api/titulos/
read -r -p 'ID da série recém-criada: ' CATALOGO_SERIE_ID
```

3. Liste e consulte (200). Renomeie a série (200) e consulte novamente: temporadas devem continuar em 2.

```bash
curl -i -H "Authorization: Token $CATALOGO_TOKEN" http://127.0.0.1:8000/api/titulos/
curl -i -H "Authorization: Token $CATALOGO_TOKEN" "http://127.0.0.1:8000/api/titulos/$CATALOGO_SERIE_ID/"
curl -i -X PATCH -H "Authorization: Token $CATALOGO_TOKEN" -H 'Content-Type: application/json' \
  -d '{"nome":"Série renomeada"}' "http://127.0.0.1:8000/api/titulos/$CATALOGO_SERIE_ID/"
curl -i -H "Authorization: Token $CATALOGO_TOKEN" "http://127.0.0.1:8000/api/titulos/$CATALOGO_SERIE_ID/"
```

4. Tente cadastrar filme com temporadas (400), liste e confira que a contagem ainda é a inicial + 2.

```bash
curl -i -H "Authorization: Token $CATALOGO_TOKEN" -H 'Content-Type: application/json' \
  -d "{\"nome\":\"Filme inválido\",\"tipo\":\"filme\",\"genero\":$CATALOGO_GENERO_ID,\"numero_temporadas\":2}" \
  http://127.0.0.1:8000/api/titulos/
curl -i -H "Authorization: Token $CATALOGO_TOKEN" http://127.0.0.1:8000/api/titulos/
```

5. Mude apenas o tipo (400), consulte e confira a preservação da série. Depois limpe temporadas na mesma requisição (200).

```bash
curl -i -X PATCH -H "Authorization: Token $CATALOGO_TOKEN" -H 'Content-Type: application/json' \
  -d '{"tipo":"filme"}' "http://127.0.0.1:8000/api/titulos/$CATALOGO_SERIE_ID/"
curl -i -H "Authorization: Token $CATALOGO_TOKEN" "http://127.0.0.1:8000/api/titulos/$CATALOGO_SERIE_ID/"
curl -i -X PATCH -H "Authorization: Token $CATALOGO_TOKEN" -H 'Content-Type: application/json' \
  -d '{"tipo":"filme","numero_temporadas":null}' "http://127.0.0.1:8000/api/titulos/$CATALOGO_SERIE_ID/"
```

6. Exclua os dois títulos descartáveis (204), consulte cada um (404) e confirme que a lista voltou à contagem inicial.

```bash
curl -i -X DELETE -H "Authorization: Token $CATALOGO_TOKEN" "http://127.0.0.1:8000/api/titulos/$CATALOGO_SERIE_ID/"
curl -i -H "Authorization: Token $CATALOGO_TOKEN" "http://127.0.0.1:8000/api/titulos/$CATALOGO_SERIE_ID/"
curl -i -X DELETE -H "Authorization: Token $CATALOGO_TOKEN" "http://127.0.0.1:8000/api/titulos/$CATALOGO_FILME_ID/"
curl -i -H "Authorization: Token $CATALOGO_TOKEN" "http://127.0.0.1:8000/api/titulos/$CATALOGO_FILME_ID/"
curl -i -H "Authorization: Token $CATALOGO_TOKEN" http://127.0.0.1:8000/api/titulos/
unset CATALOGO_TOKEN
```

Como a API só cadastra/consulta gêneros, remova o gênero descartável pelo shell do Django após excluir seus títulos. Use somente os IDs anotados na sua execução. O usuário descartável pode ser removido pelo mesmo shell; seu token será removido em cascata:

```bash
venv/bin/python manage.py shell
```

```python
from catalogo.models import Genero
from django.contrib.auth.models import User
genero_id = int(input("ID do gênero descartável criado nesta execução: "))
Genero.objects.get(pk=genero_id).delete()
usuario_id = int(input("ID do usuário descartável criado nesta execução: "))
User.objects.get(pk=usuario_id).delete()
```

O registro [cenarios-api.log](cenarios-api.log) também contém requisições de PUT e outros casos inválidos com seus corpos e respostas reais. Este roteiro HTTP não substitui a etapa posterior de testes automatizados.
