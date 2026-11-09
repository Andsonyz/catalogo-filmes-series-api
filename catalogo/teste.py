from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from catalogo.models import Genero, Titulo


class CatalogoAPITests(APITestCase):
    def setUp(self):
        self.genero = Genero.objects.create(nome="Ficção científica")
        usuario = User.objects.create_user(username="usuario_do_teste")
        token = Token.objects.create(user=usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.titulos_url = reverse("titulos-list")

    def criar_serie(self, nome="Série do teste"):
        return Titulo.objects.create(
            nome=nome, tipo="serie", genero=self.genero, numero_temporadas=2
        )

    def conferir_cadastro_rejeitado(self, dados, mensagem):
        existente = self.criar_serie()
        quantidade_anterior = Titulo.objects.count()

        response = self.client.post(self.titulos_url, dados, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("numero_temporadas", response.data)
        self.assertIn(mensagem, str(response.data["numero_temporadas"][0]))
        self.assertEqual(Titulo.objects.count(), quantidade_anterior)
        self.assertFalse(Titulo.objects.filter(nome=dados["nome"]).exists())
        self.assertTrue(Titulo.objects.filter(pk=existente.pk).exists())

    def test_cadastra_genero(self):
        response = self.client.post(
            reverse("generos-list"), {"nome": "Comédia"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Genero.objects.get(pk=response.data["id"]).nome, "Comédia")

    def test_consulta_genero(self):
        response = self.client.get(reverse("generos-detail", args=[self.genero.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"id": self.genero.pk, "nome": self.genero.nome})

    def test_cadastra_filme_sem_temporadas(self):
        response = self.client.post(
            self.titulos_url,
            {"nome": "Filme do teste", "tipo": "filme", "genero": self.genero.pk},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Titulo.objects.count(), 1)
        titulo = Titulo.objects.get(pk=response.data["id"])
        self.assertEqual(titulo.nome, "Filme do teste")
        self.assertEqual(titulo.tipo, "filme")
        self.assertEqual(titulo.genero_id, self.genero.pk)
        self.assertIsNone(titulo.numero_temporadas)
        self.assertIsNone(response.data["numero_temporadas"])

    def test_cadastra_serie_com_duas_temporadas(self):
        response = self.client.post(
            self.titulos_url,
            {
                "nome": "Série cadastrada",
                "tipo": "serie",
                "genero": self.genero.pk,
                "numero_temporadas": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Titulo.objects.count(), 1)
        titulo = Titulo.objects.get(pk=response.data["id"])
        self.assertEqual(titulo.nome, "Série cadastrada")
        self.assertEqual(titulo.tipo, "serie")
        self.assertEqual(titulo.genero_id, self.genero.pk)
        self.assertEqual(titulo.numero_temporadas, 2)

    def test_lista_titulos(self):
        serie = self.criar_serie()
        filme = Titulo.objects.create(nome="Filme", tipo="filme", genero=self.genero)

        response = self.client.get(self.titulos_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({item["id"] for item in response.data}, {serie.pk, filme.pk})
        self.assertEqual(len(response.data), 2)

    def test_consulta_titulo(self):
        titulo = self.criar_serie()

        response = self.client.get(reverse("titulos-detail", args=[titulo.pk]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": titulo.pk,
                "nome": "Série do teste",
                "tipo": "serie",
                "genero": self.genero.pk,
                "numero_temporadas": 2,
            },
        )

    def test_patch_nome_preserva_temporadas_omitidas(self):
        titulo = self.criar_serie()

        response = self.client.patch(
            reverse("titulos-detail", args=[titulo.pk]),
            {"nome": "Série renomeada"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titulo.refresh_from_db()
        self.assertEqual(titulo.nome, "Série renomeada")
        self.assertEqual(titulo.tipo, "serie")
        self.assertEqual(titulo.numero_temporadas, 2)
        self.assertEqual(titulo.genero_id, self.genero.pk)
        self.assertEqual(response.data["numero_temporadas"], 2)

    def test_exclui_titulo(self):
        titulo = self.criar_serie()
        outro = self.criar_serie(nome="Outra série")
        url = reverse("titulos-detail", args=[titulo.pk])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Titulo.objects.filter(pk=titulo.pk).exists())
        self.assertTrue(Titulo.objects.filter(pk=outro.pk).exists())
        self.assertEqual(Titulo.objects.count(), 1)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_rejeita_cadastro_filme_com_temporadas(self):
        self.conferir_cadastro_rejeitado(
            {
                "nome": "Filme inválido",
                "tipo": "filme",
                "genero": self.genero.pk,
                "numero_temporadas": 2,
            },
            "Filmes devem ficar sem número de temporadas",
        )

    def test_rejeita_cadastro_serie_com_zero_temporadas(self):
        self.conferir_cadastro_rejeitado(
            {
                "nome": "Série com zero",
                "tipo": "serie",
                "genero": self.genero.pk,
                "numero_temporadas": 0,
            },
            "maior ou igual a 1",
        )

    def test_rejeita_cadastro_serie_sem_campo_temporadas(self):
        self.conferir_cadastro_rejeitado(
            {"nome": "Série sem temporadas", "tipo": "serie", "genero": self.genero.pk},
            "Séries exigem um número inteiro de temporadas maior ou igual a 1",
        )

    def test_patch_rejeita_conversao_para_filme_sem_limpar_temporadas(self):
        titulo = self.criar_serie()

        response = self.client.patch(
            reverse("titulos-detail", args=[titulo.pk]),
            {"tipo": "filme", "nome": "Não deve persistir"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Filmes devem ficar sem", str(response.data["numero_temporadas"][0]))
        titulo.refresh_from_db()
        self.assertEqual(titulo.tipo, "serie")
        self.assertEqual(titulo.numero_temporadas, 2)
        self.assertEqual(titulo.nome, "Série do teste")
        self.assertEqual(Titulo.objects.count(), 1)

    def test_patch_converte_serie_para_filme_com_temporadas_null(self):
        titulo = self.criar_serie()

        response = self.client.patch(
            reverse("titulos-detail", args=[titulo.pk]),
            {"tipo": "filme", "numero_temporadas": None},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titulo.refresh_from_db()
        self.assertEqual(titulo.tipo, "filme")
        self.assertIsNone(titulo.numero_temporadas)
        self.assertEqual(titulo.nome, "Série do teste")
        self.assertEqual(response.data["tipo"], "filme")
        self.assertIsNone(response.data["numero_temporadas"])
        self.assertEqual(Titulo.objects.count(), 1)

    def test_patch_rejeita_temporadas_null_mantendo_serie(self):
        titulo = self.criar_serie()

        response = self.client.patch(
            reverse("titulos-detail", args=[titulo.pk]),
            {"numero_temporadas": None},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Séries exigem", str(response.data["numero_temporadas"][0]))
        titulo.refresh_from_db()
        self.assertEqual(titulo.tipo, "serie")
        self.assertEqual(titulo.numero_temporadas, 2)


    def test_patch_rejeita_conversao_para_serie_sem_informar_temporadas(self):
        titulo = Titulo.objects.create(
            nome="Filme do teste", tipo="filme", genero=self.genero
        )

        response = self.client.patch(
            reverse("titulos-detail", args=[titulo.pk]),
            {"tipo": "serie"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("numero_temporadas", response.data)
        self.assertIn(
            "Séries exigem um número inteiro de temporadas maior ou igual a 1",
            str(response.data["numero_temporadas"][0]),
        )
        titulo.refresh_from_db()
        self.assertEqual(titulo.tipo, "filme")
        self.assertIsNone(titulo.numero_temporadas)
        self.assertEqual(titulo.nome, "Filme do teste")
        self.assertEqual(titulo.genero_id, self.genero.pk)
        self.assertEqual(Titulo.objects.count(), 1)