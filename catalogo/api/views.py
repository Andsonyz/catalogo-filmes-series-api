from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny

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


class TituloViewSet(viewsets.ModelViewSet):
    queryset = Titulo.objects.all()
    serializer_class = TituloSerializer
    permission_classes = [AllowAny]
