from rest_framework import serializers

from catalogo.models import Genero, Titulo


class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ["id", "nome"]


class TituloSerializer(serializers.ModelSerializer):
    numero_temporadas = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        error_messages={
            "invalid": "O número de temporadas deve ser um inteiro.",
            "min_value": "O número de temporadas deve ser maior ou igual a 1.",
        },
    )

    class Meta:
        model = Titulo
        fields = ["id", "nome", "tipo", "genero", "numero_temporadas"]
        extra_kwargs = {
            "tipo": {"error_messages": {"invalid_choice": "O tipo deve ser filme ou serie."}}
        }

    def validate(self, attrs):
        # get() preserves explicit None; only omitted fields use persisted values.
        tipo = attrs.get("tipo", getattr(self.instance, "tipo", None))
        temporadas = attrs.get(
            "numero_temporadas", getattr(self.instance, "numero_temporadas", None)
        )
        if tipo == Titulo.Tipo.FILME and temporadas is not None:
            raise serializers.ValidationError(
                {"numero_temporadas": "Filmes devem ficar sem número de temporadas (null)."}
            )
        if tipo == Titulo.Tipo.SERIE and temporadas is None:
            raise serializers.ValidationError(
                {"numero_temporadas": "Séries exigem um número inteiro de temporadas maior ou igual a 1."}
            )
        return attrs
