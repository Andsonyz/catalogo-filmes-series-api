from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer

from catalogo.api.renderers import CatalogoBrowsableAPIRenderer
from catalogo.api.serializers import GeneroSerializer, TituloSerializer
from catalogo.models import Genero, Titulo


class GeneroViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer, CatalogoBrowsableAPIRenderer]


class TituloViewSet(viewsets.ModelViewSet):
    queryset = Titulo.objects.all()
    serializer_class = TituloSerializer
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer, CatalogoBrowsableAPIRenderer]
