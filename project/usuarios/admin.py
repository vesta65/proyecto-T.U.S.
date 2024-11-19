from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Rol, Cliente, Conductor, TipoVehiculo, Vehiculo, TipoServicio, Pedido

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'id_rol', 'telf', 'edad')
    search_fields = ('username', 'email', 'id_rol__nombre', 'telf')
    list_filter = ('id_rol',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('id_rol', 'telf', 'edad')}),
    )

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'ci')
    search_fields = ('user__username', 'ci')

@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'num_lice', 'categoria')
    search_fields = ('user__username', 'num_lice', 'categoria')

@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('id', 'estado', 'placa', 'modelo', 'color', 'anio', 'conductor', 'tipo_vehiculo')
    search_fields = ('placa', 'modelo', 'color', 'conductor__user__username', 'tipo_vehiculo__nombre')
    list_filter = ('estado', 'anio', 'tipo_vehiculo')

@admin.register(TipoServicio)
class TipoServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'conductor', 'servicio', 'fecha_hora_inicio', 'fecha_hora_fin', 'estado', 'origen')
    search_fields = ('cliente__user__username', 'conductor__user__username', 'servicio__nombre', 'estado')
    list_filter = ('estado', 'fecha_hora_inicio', 'fecha_hora_fin')

