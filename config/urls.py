"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from rest_framework.routers import SimpleRouter
from rest_framework.authtoken import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.api.views import UserProfileExampleViewSet
from catalogo.api.views import GeneroViewSet, TituloViewSet
from catalogo.views import pagina_assistir, pagina_catalogo

router = SimpleRouter()

router.register("users", UserProfileExampleViewSet, basename="users")
router.register("api/generos", GeneroViewSet, basename="generos")
router.register("api/titulos", TituloViewSet, basename="titulos")

urlpatterns = [
    path("", TemplateView.as_view(template_name="catalogo/home.html"), name="home"),
    path("catalogo/", pagina_catalogo, name="catalogo"),
    path("assistir/", pagina_assistir, name="assistir"),
    path("admin/", admin.site.urls),
    path("api/token-auth/", views.obtain_auth_token),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]+router.urls
