"""Verificação por navegador. Execute apenas contra um banco descartável.

Requer Playwright e Chromium; veja docs/interface.md. Não usa pytest nem muda
configurações da API. Só exclui títulos que esta execução criou.
"""
import json
import os
from pathlib import Path
import shutil

from playwright.sync_api import expect, sync_playwright

BASE = os.environ.get('CATALOGO_URL', 'http://127.0.0.1:8000').rstrip('/')
OUT = Path(os.environ.get('CATALOGO_CAPTURAS', 'docs/interface'))
OUT.mkdir(parents=True, exist_ok=True)


def report(scenario, **result):
    print(json.dumps({'cenario': scenario, **result}, ensure_ascii=False), flush=True)


with sync_playwright() as p:
    chromium = os.environ.get('CATALOGO_CHROMIUM') or shutil.which('chromium')
    browser = p.chromium.launch(**({'executable_path': chromium} if chromium else {}), headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1440, 'height': 1060}, reduced_motion='reduce')
    if os.environ.get('CATALOGO_SESSAO'):
        context.add_cookies(json.loads(Path(os.environ['CATALOGO_SESSAO']).read_text()))
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    created = []
    try:
        response = page.goto(BASE + '/catalogo/')
        assert response.status == 200
        expect(page.locator('#total-titulos')).not_to_have_text('—')
        initial = context.request.get(BASE + '/api/titulos/').json()
        assert initial == [], 'Use um banco vazio e descartável para esta demonstração.'
        expect(page.locator('#catalogo-vazio')).to_be_visible()
        assert any(cookie['name'] == 'csrftoken' for cookie in context.cookies())
        page.keyboard.press('Tab')
        expect(page.get_by_role('link', name='Ir para o catálogo', exact=True)).to_be_focused()
        report('Página e catálogo vazio', http=200, total=0, csrf_cookie=True)

        page.get_by_role('button', name='＋ Novo gênero').click()
        page.get_by_label('Nome do gênero', exact=True).fill('Ficção científica')
        with page.expect_response(lambda r: r.url.endswith('/api/generos/') and r.request.method == 'POST') as result:
            page.get_by_role('button', name='Criar gênero', exact=True).click()
        assert result.value.status == 201
        assert result.value.request.headers.get('x-csrftoken')
        genre = result.value.json()
        expect(page.locator('#genero-dialog')).not_to_be_visible()
        expect(page.locator('#genero')).to_have_value(str(genre['id']))
        report('Cadastro de gênero pela tela', http=201, id=genre['id'], csrf_header=True, sessao=bool(os.environ.get('CATALOGO_SESSAO')))

        page.get_by_label('Nome da obra').fill('Interestelar')
        with page.expect_response(lambda r: r.url.endswith('/api/titulos/') and r.request.method == 'POST') as result:
            page.locator('#salvar-titulo').click()
        assert result.value.status == 201
        film = result.value.json(); created.append(film['id'])
        assert film['numero_temporadas'] is None
        expect(page.locator('#total-titulos')).to_have_text('1')
        report('Cadastro de filme', http=201, numero_temporadas=None)

        page.get_by_label('Nome da obra').fill('Dark')
        page.get_by_label('Tipo').select_option('serie')
        expect(page.get_by_label('Número de temporadas')).to_be_visible()
        page.get_by_label('Número de temporadas').fill('0')
        page.locator('#genero').select_option(str(genre['id']))
        assert page.locator('#numero_temporadas').evaluate('(input) => !input.checkValidity()')
        report('Validação nativa de temporadas', zero_invalido=True, min=1, step=1)
        # Bypass only the HTML min to exercise a real 400 from the API.
        page.locator('#numero_temporadas').evaluate('(input) => input.removeAttribute("min")')
        with page.expect_response(lambda r: r.url.endswith('/api/titulos/') and r.request.method == 'POST') as result:
            page.locator('#salvar-titulo').click()
        assert result.value.status == 400
        expect(page.locator('#erro-numero_temporadas')).to_contain_text('maior ou igual a 1')
        expect(page.locator('#nome')).to_have_value('Dark')
        expect(page.locator('#numero_temporadas')).to_have_value('0')
        expect(page.locator('#genero')).to_have_value(str(genre['id']))
        assert len(context.request.get(BASE + '/api/titulos/').json()) == 1
        report('Erro real da API junto ao campo, sem perder preenchimento', http=400, total=1)
        page.locator('#numero_temporadas').evaluate('(input) => input.min = "1"')
        page.get_by_label('Número de temporadas').fill('2')
        with page.expect_response(lambda r: r.url.endswith('/api/titulos/') and r.request.method == 'POST') as result:
            page.locator('#salvar-titulo').click()
        assert result.value.status == 201
        series = result.value.json(); created.append(series['id'])
        assert series['numero_temporadas'] == 2
        expect(page.locator('#total-titulos')).to_have_text('2')
        report('Cadastro de série', http=201, numero_temporadas=2)

        page.get_by_role('button', name='Editar Dark', exact=True).click()
        page.get_by_label('Nome da obra').fill('Dark: entre tempos')
        with page.expect_response(lambda r: r.url.endswith(f"/api/titulos/{series['id']}/") and r.request.method == 'PATCH') as result:
            page.locator('#salvar-titulo').click()
        assert result.value.status == 200
        assert result.value.request.post_data_json == {'nome': 'Dark: entre tempos'}
        saved = context.request.get(BASE + f"/api/titulos/{series['id']}/").json()
        assert saved['numero_temporadas'] == 2
        report('Edição somente do nome', http=200, payload=result.value.request.post_data_json, temporadas_persistidas=2)
        page.reload()
        expect(page.get_by_role('heading', name='Dark: entre tempos', exact=True)).to_be_visible()
        page.get_by_role('button', name='Editar Dark: entre tempos', exact=True).click()
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path=str(OUT / 'desktop.png'), full_page=True)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        page.set_viewport_size({'width': 390, 'height': 844})
        page.evaluate('window.scrollTo(0, 0)')
        page.screenshot(path=str(OUT / 'celular.png'), full_page=True)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
        report('Desktop e celular', desktop='1440x1060', celular='390x844', overflow_horizontal=False, erros_js=errors)

        page.get_by_label('Tipo').select_option('filme')
        expect(page.locator('#campo-temporadas')).not_to_be_visible()
        with page.expect_response(lambda r: r.url.endswith(f"/api/titulos/{series['id']}/") and r.request.method == 'PATCH') as result:
            page.locator('#salvar-titulo').click()
        assert result.value.status == 200
        assert result.value.request.post_data_json == {'tipo': 'filme', 'numero_temporadas': None}
        page.reload()
        expect(page.locator('#total-filmes')).to_have_text('2')
        saved = context.request.get(BASE + f"/api/titulos/{series['id']}/").json()
        assert saved['tipo'] == 'filme' and saved['numero_temporadas'] is None
        report('Conversão série → filme e recarga', http=200, payload=result.value.request.post_data_json, tipo_persistido=saved['tipo'], temporadas_persistidas=None)

        page.once('dialog', lambda dialog: dialog.dismiss())
        page.get_by_role('button', name='Excluir Interestelar', exact=True).click()
        assert context.request.get(BASE + f"/api/titulos/{film['id']}/").status == 200
        expect(page.locator(f'li[data-id="{film["id"]}"]')).to_be_visible()
        report('Cancelamento da exclusão', registro_preservado=True)
        page.once('dialog', lambda dialog: dialog.accept())
        with page.expect_response(lambda r: r.url.endswith(f"/api/titulos/{film['id']}/") and r.request.method == 'DELETE') as result:
            page.get_by_role('button', name='Excluir Interestelar', exact=True).click()
        assert result.value.status == 204
        expect(page.locator('#total-titulos')).to_have_text('1')
        assert context.request.get(BASE + f"/api/titulos/{film['id']}/").status == 404
        report('Confirmação da exclusão', http=204, consulta_posterior=404)

        page.locator('#nome').fill('Rascunho preservado')
        page.locator('#genero').select_option(str(genre['id']))
        context.set_offline(True)
        page.locator('#salvar-titulo').click()
        expect(page.locator('#erro-formulario')).to_contain_text('conectar ao servidor')
        expect(page.locator('#nome')).to_have_value('Rascunho preservado')
        expect(page.locator('#mensagem')).not_to_be_visible()
        context.set_offline(False)
        report('Falha de conexão no envio', preenchimento_preservado=True, falso_sucesso=False)

        page.route('**/api/titulos/', lambda route: route.abort())
        page.reload()
        expect(page.locator('#falha-carregamento')).to_be_visible()
        page.unroute('**/api/titulos/')
        page.locator('#tentar-novamente').click()
        expect(page.locator('#total-titulos')).to_have_text('1')
        expect(page.locator('#falha-carregamento')).not_to_be_visible()
        report('Falha de carregamento e tentar novamente', recuperacao=True)
        assert not errors, errors
    finally:
        context.set_offline(False)
        for pk in created:
            context.request.delete(BASE + f'/api/titulos/{pk}/', headers={'X-CSRFToken': next((cookie['value'] for cookie in context.cookies() if cookie['name'] == 'csrftoken'), '')})
        browser.close()
