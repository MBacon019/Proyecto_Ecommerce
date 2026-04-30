"""
URL configuration for moto_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings            # Importa settings
from django.conf.urls.static import static  # Importa static helper
from store import views as store_views      # Importa la vista home desde store

urlpatterns = [
    path('admin/', admin.site.urls),
    # --- Ruta para la página de inicio ---
    path('', store_views.home_views, name='home'),
    # --- Incluye las URLs de tu app 'store' bajo el prefijo 'tienda/' ---
    # Puedes quitar el prefijo 'tienda/' si quieres que las URLs de store
    # (como /productos/, /categoria/...) cuelguen directamente de la raíz
    path('', include('store.urls')),

    # --- URLs para autenticación (si las implementas) ---
    # path('accounts/', include('django.contrib.auth.urls')), # Incluye login, logout, etc.
    # path('registro/', user_views.signup, name='signup'), # Ejemplo si tienes vista de registro
]

# --- Servir archivos estáticos y multimedia durante el DESARROLLO ---
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Aunque STATIC_ROOT es para prod, esto a veces ayuda
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)