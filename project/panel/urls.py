from django.urls import path
from django.conf import settings
from .views import motivo_rechazo, rechazar_pedido, cambiar_estado_vehiculo, ver_info_vehiculo, ver_historial_pedidos, lista_usuarios_comunes, panel_control, inicio, registro, lista_vehiculos, ingresar_cliente, ingresar_conductor, editar_vehiculo, lista_usuarios, editar_usuario, eliminar_usuario, lista_conductores, registrar_vehiculo
from django.conf.urls.static import static

urlpatterns = [
    path('inicio/', inicio, name='panelinicio'),
    path('registro/', registro, name='registro'),
    path('registro/cliente/<int:user_id>/', ingresar_cliente, name='ingresar_cliente'),
    path('registro/conductor/<int:user_id>/', ingresar_conductor, name='ingresar_conductor'),
    path('usuarios/', lista_usuarios, name='lista_usuarios'),
    path('usuarios/editar/<int:user_id>/', editar_usuario, name='editar_usuario'),
    path('usuarios/eliminar/<int:user_id>/', eliminar_usuario, name='eliminar_usuario'),
    path('lista_conductores/', lista_conductores, name='lista_conductores'),
    path('registrar_vehiculo/<int:conductor_id>/', registrar_vehiculo, name='registrar_vehiculo'),
    path('editar_vehiculo/<int:vehiculo_id>/', editar_vehiculo, name='editar_vehiculo'),
    path('lista_vehiculos/', lista_vehiculos, name='lista_vehiculos'),
    path('panel/', panel_control, name='panel_control'),
    path('usuarios_comunes/', lista_usuarios_comunes, name='lista_usuarios_comunes'),
    path('historial_pedidos/<int:usuario_id>/', ver_historial_pedidos, name='ver_historial_pedidos'),
    path('vehiculo/<int:vehiculo_id>/', ver_info_vehiculo, name='ver_vehiculo'),
    path('vehiculo/<int:vehiculo_id>/cambiar_estado/', cambiar_estado_vehiculo, name='cambiar_estado_vehiculo'),
    path('rechazar_pedido/<int:pedido_id>/', rechazar_pedido, name='rechazar_pedido'),
    path('seleccionar_motivo/<int:pedido_id>/', motivo_rechazo, name='motivo_rechazo'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
