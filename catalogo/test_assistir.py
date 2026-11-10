from django.test import TestCase
from django.urls import reverse

from catalogo.models import Genero, Titulo


class AreaClienteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.drama = Genero.objects.create(nome="Drama")
        cls.comedia = Genero.objects.create(nome="Comédia")
        cls.filme = Titulo.objects.create(nome="Uma boa história", tipo="filme", genero=cls.drama)
        cls.serie = Titulo.objects.create(nome="Uma boa série", tipo="serie", genero=cls.drama, numero_temporadas=2)
        cls.outro = Titulo.objects.create(nome="Uma boa comédia", tipo="filme", genero=cls.comedia)

    def buscar(self, **params):
        return self.client.get(reverse("assistir"), params)

    def test_cliente_anonima_consulta_catalogo_sem_controles_de_edicao(self):
        response = self.buscar()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Uma boa história")
        self.assertContains(response, "Uma boa série")
        self.assertContains(response, "Disponível no catálogo", count=3)
        self.assertNotContains(response, "Editar")
        self.assertNotContains(response, "Excluir")
        self.assertContains(response, 'href="/">Voltar à página inicial</a>')

    def test_combina_nome_genero_e_tipo(self):
        response = self.buscar(q="  BOA  ", genero=self.drama.pk, tipo="filme")
        self.assertEqual(list(response.context["titulos"]), [self.filme])
        self.assertNotContains(response, "Uma boa série")
        self.assertNotContains(response, "Uma boa comédia")
        self.assertEqual(response.context["form"].cleaned_data["q"], "BOA")

    def test_filtro_de_genero_e_tipo_funcionam_sozinhos(self):
        self.assertEqual(list(self.buscar(genero=self.comedia.pk).context["titulos"]), [self.outro])
        self.assertEqual(list(self.buscar(tipo="serie").context["titulos"]), [self.serie])

    def test_nome_filtra_sem_depender_dos_outros_campos(self):
        self.assertEqual(list(self.buscar(q="história").context["titulos"]), [self.filme])

    def test_busca_ignora_maiusculas_tambem_em_letras_acentuadas(self):
        self.assertEqual(list(self.buscar(q="HISTÓRIA").context["titulos"]), [self.filme])

    def test_caracteres_especiais_sao_pesquisados_como_texto_literal(self):
        response = self.buscar(q=".*")
        self.assertContains(response, "Nenhum título encontrado")

    def test_mostra_quando_filme_nao_esta_no_genero_escolhido(self):
        response = self.buscar(q="história", genero=self.comedia.pk)
        self.assertContains(response, "Nenhum título encontrado")
        self.assertNotContains(response, "Disponível no catálogo")
        self.assertContains(response, "Limpar filtros")

    def test_catalogo_vazio_tem_orientacao_propria(self):
        Titulo.objects.all().delete()
        response = self.buscar()
        self.assertContains(response, "O catálogo ainda está vazio")

    def test_filtros_invalidos_nao_retornam_todos_os_titulos(self):
        for params in ({"genero": "abc"}, {"genero": "999999"}, {"tipo": "invalido"}, {"q": "x" * 201}):
            with self.subTest(params=params):
                response = self.buscar(**params)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Confira os filtros")
                self.assertNotContains(response, "Disponível no catálogo")

    def test_busca_e_escapada_e_preservada(self):
        response = self.buscar(q='<script>alert("teste")</script>')
        self.assertNotContains(response, '<script>alert("teste")</script>')
        self.assertContains(response, "&lt;script&gt;")

    def test_paginacao_preserva_filtros_e_nao_repete_resultados(self):
        for n in range(13):
            Titulo.objects.create(nome=f"Busca {n:02}", tipo="filme", genero=self.drama)
        params = {"q": "Busca", "genero": self.drama.pk, "tipo": "filme"}
        first = self.buscar(**params)
        self.assertEqual(len(first.context["titulos"]), 12)
        self.assertContains(first, f'q=Busca&amp;genero={self.drama.pk}&amp;tipo=filme&amp;page=2')
        second = self.buscar(**params, page=2)
        self.assertEqual(len(second.context["titulos"]), 1)
        self.assertTrue(set(first.context["titulos"]).isdisjoint(second.context["titulos"]))

    def test_consulta_rejeita_escrita(self):
        response = self.client.post(reverse("assistir"), {"nome": "Intruso"})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Titulo.objects.count(), 3)
