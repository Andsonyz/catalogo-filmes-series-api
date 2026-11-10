from rest_framework.renderers import BrowsableAPIRenderer


class CatalogoBrowsableAPIRenderer(BrowsableAPIRenderer):
    template = "catalogo/api.html"
