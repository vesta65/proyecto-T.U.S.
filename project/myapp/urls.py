# urls.py
from django.urls import path
from .views import  estadomovil, perfil_usuario, ultimo_pedido, pedidos_usuario, detailpedidos, cancelar_pedido, pedido_detalle, verificar_estado_pedido, estado_pedido, pedidos_completados, marcar_pedido_completado, inicio, crear_pedido, pedido_exito, pedidos_conductor
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('add_pedido/', crear_pedido, name='add_pedido'),
    path('pedido_exito/', pedido_exito, name='pedido_exito'),  # Añadir esta línea
    path('appmovil/', inicio, name='inicio'),
    path('pedidos-conductor/', pedidos_conductor, name='pedidos_conductor'),
    path('pedidos/completar/<int:pedido_id>/', marcar_pedido_completado, name='marcar_pedido_completado'),
    path('pedidos_completados/', pedidos_completados, name='pedidos_completados'),
    path('estado_pedido/<int:pedido_id>/', estado_pedido, name='estado_pedido'),
    path('verificar_estado_pedido/<int:pedido_id>/', verificar_estado_pedido, name='verificar_estado_pedido'),
    path('pedido/<int:pedido_id>/', pedido_detalle, name='pedido_detalle'),
    path('cancelar_pedido/<int:pedido_id>/', cancelar_pedido, name='cancelar_pedido'),
    path('mis_pedidos/', pedidos_usuario, name='pedidos_usuario'),
    path('pedidos/<int:pedido_id>/', detailpedidos, name='detailpedidos'),  # Ejemplo para la vista de detalle
    path('ultimo_pedido/', ultimo_pedido, name='ultimo_pedido'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('mvehiculo/<int:vehiculo_id>/cambiar_estado/', estadomovil, name='estadomovil'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

