from re import escape
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET

from catalogo.forms import BuscaCatalogoForm
from catalogo.models import Titulo


@require_GET
@ensure_csrf_cookie
def pagina_catalogo(request):
    return render(request, "catalogo/catalogo.html")


@require_GET
def pagina_assistir(request):
    form = BuscaCatalogoForm(request.GET)
    titulos = Titulo.objects.select_related("genero").order_by("nome", "id")
    filtros = {}
    if form.is_valid():
        busca = form.cleaned_data
        if busca["q"]:
            # SQLite LIKE ignores case only for ASCII; regex handles Unicode.
            titulos = titulos.filter(nome__iregex=escape(busca["q"]))
            filtros["q"] = busca["q"]
        if busca["genero"]:
            titulos = titulos.filter(genero=busca["genero"])
            filtros["genero"] = busca["genero"].pk
        if busca["tipo"]:
            titulos = titulos.filter(tipo=busca["tipo"])
            filtros["tipo"] = busca["tipo"]
    else:
        titulos = titulos.none()
        for name in form.errors:
            form.fields[name].widget.attrs.update({
                "aria-invalid": "true", "aria-describedby": f"{name}-errors",
            })

    page = Paginator(titulos, 12).get_page(request.GET.get("page"))
    return render(request, "catalogo/assistir.html", {
        "form": form,
        "titulos": page.object_list,
        "page_obj": page,
        "total_catalogo": Titulo.objects.count(),
        "filtros_query": urlencode(filtros),
    })
