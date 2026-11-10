from django import forms

from catalogo.models import Genero, Titulo


class BuscaCatalogoForm(forms.Form):
    q = forms.CharField(
        label="Nome do filme ou série", required=False, max_length=200,
        widget=forms.TextInput(attrs={"type": "search", "placeholder": "Qual história você procura?"}),
    )
    genero = forms.ModelChoiceField(
        label="Gênero", queryset=Genero.objects.order_by("nome", "id"),
        required=False, empty_label="Todos os gêneros",
        error_messages={"invalid_choice": "Escolha um gênero disponível na lista."},
    )
    tipo = forms.ChoiceField(
        label="Tipo", required=False,
        choices=[("", "Filmes e séries"), *Titulo.Tipo.choices],
        error_messages={"invalid_choice": "Escolha filme, série ou todos os tipos."},
    )
