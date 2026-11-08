from django.db import models


class Genero(models.Model):
    nome = models.CharField(max_length=100)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.nome


class Titulo(models.Model):
    class Tipo(models.TextChoices):
        FILME = "filme", "Filme"
        SERIE = "serie", "Série"

    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=5, choices=Tipo.choices)
    genero = models.ForeignKey(
        Genero, on_delete=models.PROTECT, related_name="titulos"
    )
    numero_temporadas = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.nome
