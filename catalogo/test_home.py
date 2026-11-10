from django.test import SimpleTestCase


class HomePageTests(SimpleTestCase):
    def test_home_page_links_to_catalog_and_documentation(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Catálogo de filmes e séries")
        self.assertContains(response, 'href="/api/generos/"')
        self.assertContains(response, 'href="/api/titulos/"')
        self.assertContains(response, 'href="/swagger/"')
        self.assertContains(response, 'href="/catalogo/"')
        self.assertContains(response, 'href="/assistir/"')
