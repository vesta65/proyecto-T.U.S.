from django.urls import path
from .views import limpiar_pedidos, ver_archivo, listar_archivos, exportar_pedidos, Pedidoreport, pedidos_conductor_asignado, pedidos_list, pedidos_json, atender_pedido, asignar_vehiculo

urlpatterns = [
    path('pedidos-list/', pedidos_list, name='pedidos_list'),
    path('pedidos-json/', pedidos_json, name='pedidos_json'),
    path('atender-pedido/<int:pedido_id>/', atender_pedido, name='atender_pedido'),
    path('asignar-vehiculo/<int:vehiculo_id>/pedido/<int:pedido_id>/', asignar_vehiculo, name='asignar_vehiculo'),
    path('pedidos-con-conductor/', pedidos_conductor_asignado, name='pedidos_con_conductor'),
    path('pedidos/', Pedidoreport.as_view(), name='pedidoreport'),
    path('exportar_pedidos/', exportar_pedidos, name='exportar_pedidos'),
    path('listar_archivos/', listar_archivos, name='listar_archivos'),
    path('ver_archivo/<str:nombre_archivo>/', ver_archivo, name='ver_archivo'),
    path('limpiar_pedidos/', limpiar_pedidos, name='limpiar_pedidos'),
    
]


