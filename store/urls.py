from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Página principal - Solo una ruta para 'home'
    path('', views.home_views, name='home'),  # Usamos home_views que parece la página principal con destacados

    # Productos y categorías
    path('productos/', views.product_list_view, name='product_list'),
    path('categoria/<slug:category_slug>/', views.product_list_view, name='product_list_by_category'),
    path('producto/<slug:product_slug>/', views.product_detail_view, name='product_detail'),

    # Perfil
    path('profile/', views.profile, name='profile'),

    # Autenticación personalizada
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('agregar/<int:product_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),  # Solo una ruta para agregar
    path('eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),

    # Checkout y ordenes
    path('checkout/', views.checkout, name='checkout'),
    path('confirmar-orden/', views.confirmar_orden, name='confirmar_orden'),
    path('orden-confirmada/<int:orden_id>/', views.orden_confirmada, name='orden_confirmada'),
    path('ordenes/historial/', views.historial_ordenes, name='historial_ordenes'),
    path('ordenes/admin/', views.historial_ordenes_admin, name='historial_ordenes_admin'),
    path('ordenes/<int:orden_id>/cambiar-estado/', views.cambiar_estado_orden, name='cambiar_estado_orden'),


    # Nota de venta (factura)
    path('nota-venta/<int:orden_id>/', views.nota_venta, name='nota_venta'),
    path('notas-venta/', views.lista_notas_venta, name='lista_notas_venta'),


    # Edición de stock (admin o bodega)
    path('editar-stock/', views.editar_stock, name='editar_stock'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
