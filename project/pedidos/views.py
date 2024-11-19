from django.shortcuts import render, redirect, get_object_or_404
from usuarios.models import Pedido, Vehiculo
from django.http import JsonResponse
from django.conf import settings
from twilio.rest import Client 
from django.shortcuts import render
from django.views.generic import ListView
from usuarios.models import Pedido, TipoServicio
from django.utils.timezone import now
from django.db.models import Q
import csv
from django.http import HttpResponse
import os
import pandas as pd
from datetime import datetime
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages


def limpiar_pedidos(request):
    if request.method == 'POST':
        Pedido.objects.all().delete()  # Eliminar todos los pedidos
        messages.success(request, 'Todos los pedidos han sido eliminados.')
        return redirect('panelinicio')  # Cambia esto al nombre de tu vista principal

    return render(request, 'lista/confirmar_limpiar_pedidos.html')  # Plantilla para confirmar la eliminación

def listar_archivos(request):
    ruta_csv = os.path.join(settings.MEDIA_ROOT, 'csv_files')
    
    if not os.path.exists(ruta_csv):
        return render(request, 'error.html', {'mensaje': 'La carpeta de archivos CSV no existe.'})

    archivos = [f for f in os.listdir(ruta_csv) if f.endswith('.csv')]
    
    context = {
        'archivos': archivos,
    }
    return render(request, 'lista/listar_archivos.html', context)

def ver_archivo(request, nombre_archivo):
    ruta_archivo = os.path.join(settings.MEDIA_ROOT, 'csv_files', nombre_archivo)
    
    if not os.path.isfile(ruta_archivo):
        return render(request, 'error.html', {'mensaje': 'El archivo no existe.'})

    df = pd.read_csv(ruta_archivo)
    
    datos = df.to_html(classes='table table-striped', index=False)
    
    context = {
        'nombre_archivo': nombre_archivo,
        'datos': datos,
    }
    return render(request, 'lista/ver_archivo.html', context)


def exportar_pedidos(request):
    # Crea la carpeta media/csv_files si no existe
    csv_folder = os.path.join(settings.MEDIA_ROOT, 'csv_files')
    os.makedirs(csv_folder, exist_ok=True)  # Crea la carpeta si no existe

    # Obtiene la fecha y hora actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # Formato: YYYY-MM-DD_HH-MM-SS
    nombre_archivo = f'pedidos_backup_{fecha_actual}.csv'  # Nombre del archivo con la fecha actual
    archivo_path = os.path.join(csv_folder, nombre_archivo)  # Ruta completa del archivo

    # Escribe el archivo CSV en la ruta especificada
    with open(archivo_path, mode='w', newline='') as archivo_csv:
        writer = csv.writer(archivo_csv)
        writer.writerow(['ID', 'Cliente', 'Conductor', 'Servicio', 'Fecha Inicio', 'Fecha Fin', 'Estado'])

        pedidos = Pedido.objects.all()
        for pedido in pedidos:
            writer.writerow([
                pedido.id,
                pedido.cliente.user.username,
                pedido.conductor.user.username if pedido.conductor else 'Sin asignar',
                pedido.servicio.nombre,
                pedido.fecha_hora_inicio,
                pedido.fecha_hora_fin,
                pedido.estado,
            ])

    # Opcional: Puedes devolver un mensaje de éxito o redirigir a otra vista
    return HttpResponse(f'Archivo guardado como: {nombre_archivo} en {csv_folder}')

class Pedidoreport(ListView):
    model = Pedido
    template_name = 'lista/pedido_report.html'  # Nombre del template
    context_object_name = 'pedidos'  # El nombre que se utilizará en el template
    ordering = ['-fecha_hora_fin']  # Ordenado por la fecha de fin en orden descendente

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por fecha
        fecha_fin = self.request.GET.get('fecha_fin')
        mes = self.request.GET.get('mes')
        tipo_servicio = self.request.GET.get('tipo_servicio')
        busqueda = self.request.GET.get('busqueda')

        # Filtrar por fecha de fin
        if fecha_fin:
            queryset = queryset.filter(fecha_hora_fin__date=fecha_fin)

        # Filtrar por mes
        if mes:
            queryset = queryset.filter(fecha_hora_fin__month=mes)

        # Filtrar por tipo de servicio
        if tipo_servicio:
            queryset = queryset.filter(servicio__id=tipo_servicio)

        # Búsqueda general (puedes buscar por cliente, conductor, etc.)
        if busqueda:
            queryset = queryset.filter(
                Q(cliente__user__username__icontains=busqueda) |
                Q(conductor__user__username__icontains=busqueda) |
                Q(servicio__nombre__icontains=busqueda)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir los tipos de servicios para el filtro
        context['tipos_servicio'] = TipoServicio.objects.all()

        # Agregar una lista de meses para el filtro
        context['meses'] = [
            {"numero": 1, "nombre": "Enero"},
            {"numero": 2, "nombre": "Febrero"},
            {"numero": 3, "nombre": "Marzo"},
            {"numero": 4, "nombre": "Abril"},
            {"numero": 5, "nombre": "Mayo"},
            {"numero": 6, "nombre": "Junio"},
            {"numero": 7, "nombre": "Julio"},
            {"numero": 8, "nombre": "Agosto"},
            {"numero": 9, "nombre": "Septiembre"},
            {"numero": 10, "nombre": "Octubre"},
            {"numero": 11, "nombre": "Noviembre"},
            {"numero": 12, "nombre": "Diciembre"},
        ]
        return context




def pedidos_list(request):
    pedidos = Pedido.objects.all()  # Obtiene todos los pedidos
    return render(request, 'lista/pedidos_list.html', {'pedidos': pedidos})

def pedidos_json(request):
    pedidos = Pedido.objects.all()
    data = list(pedidos.values(
        'id', 'cliente__user__username', 'conductor__user__username', 
        'servicio__nombre', 'fecha_hora_inicio', 'fecha_hora_fin', 
        'estado', 'origen'
    ))
    return JsonResponse({'pedidos': data})

def atender_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)

    if request.method == 'POST':
        vehiculo_id = request.POST.get('vehiculo')
        vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
        
        # Asignar el vehículo al pedido
        pedido.conductor = vehiculo.conductor
        pedido.save()
        
        return redirect('pedidos_list')

    vehiculos = Vehiculo.objects.filter(estado='activo')
    return render(request, 'lista/atender_pedido.html', {'pedido': pedido, 'vehiculos': vehiculos})


def asignar_vehiculo(request, vehiculo_id, pedido_id):
    # Obtener el vehículo y el pedido
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Cambiar el estado del vehículo a "ocupado"
    vehiculo.estado = 'ocupado'
    vehiculo.save()

    # Asignar el vehículo y el conductor al pedido
    pedido.conductor = vehiculo.conductor
    pedido.estado = 'En Progreso'  # Cambiar el estado a "En Progreso"
    pedido.vehiculo_asignado = vehiculo  # Asegúrate de que este campo exista en el modelo Pedido
    pedido.save()

    # Enviar mensaje al conductor (descomentar si deseas enviar el mensaje)
    # enviar_mensaje_conductor(pedido)

    # Mensaje de éxito para el usuario
    messages.success(request, f"El vehículo {vehiculo.placa} ha sido asignado al pedido {pedido.id}.")

    return redirect('pedidos_list')  # Ajusta la redirección según sea necesario


#def enviar_mensaje_conductor(pedido):
    # Obtener el conductor del pedido
    conductor = pedido.conductor
    mensaje = (
        f"Nuevo Pedido Asignado:\n"
        f"Cliente: {pedido.cliente.user.username}\n"
        f"Servicio: {pedido.servicio.nombre}\n"
        f"Fecha y Hora de Inicio: {pedido.fecha_hora_inicio}\n"
        f"Fecha y Hora de Fin: {pedido.fecha_hora_fin}\n"
        f"Estado: {pedido.estado}\n"
        f"Ubicación de Origen: {pedido.origen}\n"
    )

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    client.messages.create(
        body=mensaje,
        #from_=f'whatsapp:{settings.TWILIO_WHATSAPP_PHONE_NUMBER}',  # Número de WhatsApp de Twilio
        from_=settings.TWILIO_PHONE_NUMBER,
        #to=f'whatsapp:{conductor.user.telf}'  # Número de WhatsApp del conductor, en formato `whatsapp:+<número>`
        to=conductor.user.telf
    )

def pedidos_conductor_asignado(request):
    # Filtra los pedidos que tienen uno de los estados específicos
    estados_permitidos = ['Cancelado', 'Rechazado', 'Completado', 'En Progreso']
    pedidos = Pedido.objects.filter(estado__in=estados_permitidos).order_by('-fecha_hora_inicio')

    return render(request, 'lista/pedidos_conductor_asignado.html', {'pedidos': pedidos})