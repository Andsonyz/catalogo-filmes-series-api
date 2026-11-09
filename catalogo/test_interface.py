import json

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from catalogo.models import Genero


class PaginaCatalogoTests(TestCase):
    def test_pagina_renderiza_e_prepara_csrf_para_o_javascript(self):
        response = self.client.get(reverse("catalogo"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalogo/catalogo.html")
        self.assertContains(response, 'lang="pt-BR"')
        self.assertContains(response, f'data-titulos-url="{reverse("titulos-list")}"')
        self.assertIn("csrftoken", response.cookies)

    def test_sessao_autenticada_requer_csrf_e_aceita_o_token_da_pagina(self):
        client = Client(enforce_csrf_checks=True)
        user = User.objects.create_user(username="sessao_da_interface")
        client.force_login(user)
        client.get(reverse("catalogo"))
        csrf = client.cookies["csrftoken"].value
        payload = json.dumps({"nome": "Gênero via sessão"})

        rejected = client.post(
            reverse("generos-list"), payload, content_type="application/json"
        )
        self.assertEqual(rejected.status_code, 403)
        self.assertEqual(Genero.objects.count(), 0)

        accepted = client.post(
            reverse("generos-list"), payload, content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(accepted.status_code, 201)
        self.assertEqual(Genero.objects.get().nome, "Gênero via sessão")
