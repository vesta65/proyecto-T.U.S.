from django.shortcuts import render, redirect
from .forms import PedidoForm
from usuarios.models import TipoServicio, Vehiculo, Cliente
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from usuarios.models import Pedido, Conductor, Cliente, Vehiculo
from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages


@login_required
def detailpedidos(request, pedido_id):
    # Obtiene el pedido específico o muestra una página 404 si no existe
    pedido = get_object_or_404(Pedido, id=pedido_id)

    # Verifica si el usuario está autorizado a ver el pedido (opcional)
    if pedido.cliente.user != request.user:
        return render(request, '403.html', status=403)  # Página de acceso denegado

    context = {
        'pedido': pedido,
    }
    return render(request, 'detailpedidos.html', context)
@login_required
def pedidos_usuario(request):
    try:
        # Obtiene el cliente relacionado con el usuario en sesión
        cliente = Cliente.objects.get(user=request.user)
        # Filtra los pedidos relacionados con el cliente y ordénalos de más reciente a más antiguo
        pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_hora_inicio')
    except Cliente.DoesNotExist:
        # Si el usuario no es un cliente, no tiene pedidos
        pedidos = []

    context = {
        'pedidos': pedidos,
    }
    return render(request, 'pedidos_usuario.html', context)
@login_required
def pedidos_conductor(request):
    user = request.user

    # Verifica si el usuario es un conductor
    if not hasattr(user, 'conductor'):
        return redirect('inicio')  # Redirige a otra página si el usuario no es un conductor

    # Obtiene el conductor del usuario logueado
    conductor = Conductor.objects.get(user=user)

    # Obtiene los pedidos asignados al conductor con estado "en progreso"
    pedidos = Pedido.objects.filter(conductor=conductor, estado='En Progreso')

    return render(request, 'pedidos_conductor.html', {'pedidos': pedidos})

def marcar_pedido_completado(request, pedido_id):
    try:
        # Obtener el pedido o lanzar 404 si no existe
        pedido = get_object_or_404(Pedido, id=pedido_id)

        # Verificar que el conductor del pedido sea el usuario actual
        if pedido.conductor.user == request.user:
            # Cambiar el estado del pedido a "Completado"
            pedido.estado = 'Completado'
            pedido.fecha_hora_fin = timezone.now()
            pedido.save()

            # Cambiar el estado del vehículo del conductor a "activo"
            vehiculo = get_object_or_404(Vehiculo, conductor=pedido.conductor)
            vehiculo.estado = 'activo'
            vehiculo.save()

            # Redirigir a la página de pedidos asignados
            return redirect('pedidos_conductor')
        else:
            return HttpResponseForbidden("No tienes permiso para completar este pedido.")
    except Pedido.DoesNotExist:
        return HttpResponseNotFound("Pedido no encontrado.")

def crear_pedido(request):
    if request.method == 'POST':
        form = PedidoForm(request.POST, user=request.user)
        if form.is_valid():
            pedido = form.save()
            return redirect('estado_pedido', pedido_id=pedido.id)
    else:
        form = PedidoForm(user=request.user)
        
    servicios = TipoServicio.objects.all()
    return render(request, 'add_pedido.html', {'form': form, 'servicios': servicios})

def pedido_exito(request):
    ultimo_pedido = Pedido.objects.latest('fecha_hora_inicio')
    return render(request, 'pedido_exito.html', {'pedido': ultimo_pedido})

def inicio(request):
    return render(request, 'inicio.html')
@login_required

def pedidos_completados(request):
    user = request.user

    # Verifica si el usuario es un conductor
    if not hasattr(user, 'conductor'):
        return redirect('inicio')  # Redirige a otra página si el usuario no es un conductor

    # Obtiene el conductor del usuario logueado
    conductor = Conductor.objects.get(user=user)

    # Obtiene los pedidos asignados al conductor con estado "Completado" o "Cancelado"
    pedidos = Pedido.objects.filter(conductor=conductor, estado__in=['Completado', 'Cancelado'])

    return render(request, 'pedidos_completados.html', {'pedidos': pedidos})

def verificar_estado_pedido(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        response_data = {
            'estado': pedido.estado,
        }
        if pedido.estado == 'Rechazado':
            response_data['motivo'] = pedido.motivo_rechazo  # Asegúrate de que el modelo `Pedido` tiene este campo
        return JsonResponse(response_data)
    except Pedido.DoesNotExist:
        return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
   
def estado_pedido(request, pedido_id):
    return render(request, 'estado_pedido.html', {'pedido_id': pedido_id})

def pedido_detalle(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'pedido_detalle.html', {'pedido': pedido})

@require_POST
def cancelar_pedido(request, pedido_id):
    try:
        # Obtener el pedido correspondiente
        pedido = Pedido.objects.get(id=pedido_id)

        # Cambiar el estado del pedido a 'Cancelado'
        pedido.estado = 'Cancelado'
        pedido.fecha_hora_fin = timezone.now()

        # Cambiar el estado del vehículo a 'activo' si hay un conductor asignado
        if pedido.conductor:  # Verifica que el pedido tiene un conductor asignado
            vehiculo = pedido.conductor.vehiculo  # Accede directamente al vehículo del conductor
            
            if vehiculo.estado == 'ocupado':  # Verifica que el vehículo esté ocupado
                vehiculo.estado = 'activo'  # Cambia el estado del vehículo a 'activo'
                vehiculo.save()  # Guarda los cambios del vehículo

        # Guarda los cambios del pedido
        pedido.save()
        return JsonResponse({'success': True})
    except Pedido.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pedido no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
    
def ultimo_pedido(request):
    # Obtener el último pedido
    ultimo_pedido = Pedido.objects.latest('fecha_hora_inicio')
    
    if request.method == 'POST':
        # Cancelar el pedido si el estado es "En progreso"
        if ultimo_pedido.estado.lower() == 'en progreso':
            ultimo_pedido.estado = 'Cancelado'
            ultimo_pedido.fecha_hora_fin = timezone.now()  # Establecer la hora de finalización
            ultimo_pedido.save()
            messages.success(request, 'El pedido ha sido cancelado exitosamente.')
            return redirect('ultimo_pedido')

    return render(request, 'ultimo_pedido.html', {'pedido': ultimo_pedido})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def perfil_usuario(request):
    user = request.user  # Usuario actualmente autenticado

    # Verificar si el usuario tiene información adicional en un modelo relacionado
    try:
        if hasattr(user, 'cliente'):
            perfil = user.cliente
        elif hasattr(user, 'conductor'):
            perfil = user.conductor
        elif hasattr(user, 'comun'):
            perfil = user.comun
        else:
            perfil = None
    except Exception:
        perfil = None

    if request.method == 'POST':
        # Cambiar imagen de perfil
        nueva_imagen = request.FILES.get('profile_image')
        nuevo_ci = request.POST.get('ci')

        # Actualizar imagen de perfil
        if nueva_imagen:
            user.profile_image = nueva_imagen  # Actualizar el campo 'profile_image'
            user.save()
            messages.success(request, 'Imagen de perfil actualizada exitosamente.')

        # Agregar CI si está vacío
        if perfil and not perfil.ci and nuevo_ci:
            perfil.ci = nuevo_ci
            perfil.save()
            messages.success(request, 'CI agregado exitosamente.')
        elif not nuevo_ci and perfil and not perfil.ci:
            messages.warning(request, 'Por favor, proporciona un valor para el CI.')

        return redirect('perfil_usuario')  # Redirigir a la misma página después de guardar cambios

    context = {
        'user': user,
        'perfil': perfil,
    }

    return render(request, 'perfil.html', context)

    user = request.user  # El usuario actualmente autenticado

    # Si tienes información adicional en modelos relacionados, puedes obtenerla así
    try:
        if hasattr(user, 'cliente'):
            perfil = user.cliente
        elif hasattr(user, 'conductor'):
            perfil = user.conductor
        else:
            perfil = None
    except:
        perfil = None
    
    context = {
        'user': user,
        'perfil': perfil,
    }
    
    return render(request, 'perfil.html', context)

from django.views.decorators.csrf import csrf_exempt

def estadomovil(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        vehiculo.estado = nuevo_estado
        vehiculo.save()
    return redirect(request.META.get('HTTP_REFERER'))