# Reaplicação da interface web para revisão

## Base e preservação

O PR #4 havia sido mesclado no GitHub, mas a branch padrão `main` foi posteriormente movida para `33dc79be6c6dc520836d3b037d112866dd831a78`, revisão sem a interface. A nova branch `feat/interface-catalogo-reaplicacao` parte dessa `main` atual. Não foi usado reset ou force push para alterar branches da equipe.

O commit funcional original `b5d9e9e` foi reaplicado por cherry-pick como `0b5c876`: página `/catalogo/`, templates, CSS/JS nativos e dois testes de página/CSRF. Os scripts de demonstração e verificação foram recuperados da implementação anterior. Mantidos os modelos, serializers, permissões, endpoints e dados da API. O `pytest.ini` passou a incluir `teste.py`, para descobrir os 15 testes da API existentes no arquivo da equipe, além dos dois da interface e do herdado.

## Uso e demonstração

Com as dependências do README instaladas:

```bash
venv/bin/python manage.py migrate --noinput
venv/bin/python manage.py runserver
```

Abra <http://127.0.0.1:8000/catalogo/>. Cadastre um gênero pela própria tela; adicione filme e série de duas temporadas; edite o nome da série e confira as temporadas; converta-a em filme e recarregue. Experimente cancelar e confirmar a exclusão.

A interface usa os endpoints reais, confirma sucesso somente após a resposta da API, preserva o formulário em erro e exibe erros junto ao campo. Filmes ocultam temporadas; séries exigem inteiro a partir de 1. O PATCH de nome omite temporadas; a conversão série → filme envia `tipo: filme` e `numero_temporadas: null` juntos. Fetch usa sessão de mesma origem e token CSRF do Django. `AllowAny` permanece conforme a base.

## Verificação real desta reaplicação

Para não usar os dados da equipe, foi executado um servidor com SQLite temporário:

```bash
venv/bin/python scripts/servir_interface_descartavel.py --port 8010
# Em outro terminal, na raiz:
CATALOGO_URL=http://127.0.0.1:8010 python3 scripts/verificar_interface.py
```

O script de navegador precisa de Playwright (versão usada 1.62.0) e Chromium (nesta execução `/usr/bin/chromium`). Opcionalmente, instale com `venv/bin/python -m pip install playwright==1.62.0` e `venv/bin/python -m playwright install chromium`, e use o Python desse ambiente para executar o script. Não são dependências para abrir a interface nem uma etapa de build. No PowerShell, substitua `venv/bin/python` por `.\venv\Scripts\python.exe` e defina `$env:CATALOGO_URL = 'http://127.0.0.1:8010'` antes de executar o script de navegador.

Resultado desta rodada:

- Página 200, catálogo vazio, cookie CSRF presente e link de salto acessível por teclado.
- Gênero, filme sem temporadas e série com duas temporadas: POST 201.
- Série com zero temporadas: validação nativa; ao contorná-la no roteiro, API 400 real, mensagem junto ao campo, sem gravação e sem perder preenchimento.
- PATCH apenas do nome: 200, payload somente `nome`, duas temporadas preservadas no banco.
- PATCH série → filme: 200, payload com tipo e null; GET e recarga confirmaram filme sem temporadas.
- Exclusão cancelada: registro preservado. Exclusão confirmada: DELETE 204 e GET 404.
- Falha de conexão e erro de carregamento simulados: preenchimento preservado, sem falso sucesso; botão de tentar novamente recuperou a lista.
- Desktop 1440×1060 e celular 390×844: sem overflow horizontal e sem erros JavaScript; capturas novas desta execução abaixo.

Comandos finais, registrados com saídas reais em [interface/comandos.log](interface/comandos.log):

```bash
venv/bin/python manage.py check
venv/bin/python manage.py makemigrations --check --dry-run
venv/bin/python -m pytest -v
node --check catalogo/static/catalogo/catalogo.js
git diff --check
```

Check sem problemas, nenhuma migração nova e sintaxe JS aprovada. **18 passed, 1 warning in 0.54s** na suíte completa: 15 testes da API da equipe, 1 herdado e 2 da página/CSRF. Os testes de sessão verificam 403 sem cabeçalho CSRF/nenhuma gravação e 201 com o token da página. O único aviso é a depreciação herdada do pytz, sem falha de teste.

Log dos cenários de navegador: [interface/cenarios-navegador.log](interface/cenarios-navegador.log). O SHA-256 do SQLite local preexistente permaneceu `6e4b87abfa1f50121cd3a63866e8026e0ee5e4ee7600badc5c51a380bade7c10`, sem entrar nos commits. Os dados do navegador foram criados somente no servidor descartável, cujo banco é removido ao encerrar.

Todos os cenários funcionais acima foram verificados nesta rodada. Não se afirma execução em Safari, Firefox ou Windows nem auditoria completa com leitor de tela. O novo PR contra `main` deverá ficar aberto para avaliação do solicitante, sem merge nesta etapa.

## Capturas desta execução

![Desktop](interface/desktop.png)

![Celular](interface/celular.png)
