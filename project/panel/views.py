from django.shortcuts import render, redirect, get_object_or_404
from .forms import RechazoForm, RegistroForm, VehiculoForm, ClienteForm, ConductorForm, CustomUserForm
from usuarios.models import Pedido, CustomUser, Cliente, Rol, Conductor, Vehiculo
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import IntegrityError
from django.contrib import messages



def rechazar_pedido(request, pedido_id):
    """Redirige a la página para seleccionar motivo de cancelación."""
    return redirect('motivo_rechazo', pedido_id=pedido_id)

def motivo_rechazo(request, pedido_id):
    """Vista para seleccionar el motivo del rechazo de un pedido."""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        form = RechazoForm(request.POST)
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            descripcion_otros = form.cleaned_data['descripcion_otros']

            # Almacena el motivo de rechazo en el pedido
            if motivo == 'otros' and descripcion_otros:
                pedido.motivo_rechazo = descripcion_otros
            else:
                pedido.motivo_rechazo = dict(form.fields['motivo'].choices)[motivo]

            pedido.estado = 'Rechazado'
            pedido.save()
            
            messages.success(request, 'El pedido ha sido cancelado con éxito.')
            return redirect('pedidos_con_conductor')
    else:
        form = RechazoForm()

    return render(request, 'cliente/motivo_rechazo.html', {'form': form, 'pedido': pedido})

def inicio(request):
    return render(request, 'panel/inicio.html')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, request.FILES)  # Incluir request.FILES para manejar archivos
        if form.is_valid():
            # Guardar el usuario utilizando el método save del formulario
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Establecer la contraseña cifrada
            user.save()

            # Redirigir según el rol seleccionado
            rol = form.cleaned_data['rol']
            if rol.nombre == 'comun':
                return redirect('ingresar_cliente', user_id=user.id)
            elif rol.nombre == 'conductor':
                return redirect('ingresar_conductor', user_id=user.id)
            else:
                return redirect('home')  # Ajustar con la URL correcta

    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro2.html', {'form': form})

def ingresar_cliente(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            ci = form.cleaned_data['ci']
            cliente = Cliente.objects.create(user=user, ci=ci)
            return redirect('lista_usuarios_comunes')  # Reemplazar 'home' con la URL de la página de inicio del cliente
    else:
        form = ClienteForm()

    return render(request, 'cliente/ingresar_cliente.html', {'form': form})

def ingresar_conductor(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = ConductorForm(request.POST)
        if form.is_valid():
            num_lice = form.cleaned_data['num_lice']
            categoria = form.cleaned_data['categoria']
            conductor = Conductor.objects.create(user=user, num_lice=num_lice, categoria=categoria)
            return redirect('lista_conductores')  # Redirigir a la página de inicio o a otra URL deseada
    else:
        form = ConductorForm()

    return render(request, 'conductor/ingresar_conductor.html', {'form': form})

def lista_usuarios_comunes(request):
    query = request.GET.get('q', '')
    usuarios_comunes = CustomUser.objects.select_related('id_rol')

    # Filtrar usuarios comunes por nombre de usuario o email si se proporciona un término de búsqueda
    if query:
        usuarios_comunes = usuarios_comunes.filter(
   
            Q(username__icontains=query) | Q(email__icontains=query)
        )
    else:
        usuarios_comunes = usuarios_comunes.filter(id_rol__nombre='comun')

    # Pasar la lista de usuarios comunes y el término de búsqueda al contexto
    return render(request, 'panel/usuarios_comunes.html', {
        'usuarios': usuarios_comunes,
        'query': query
    })

def lista_usuarios(request):
    query = request.GET.get('q')  # Parámetro para la búsqueda por nombre o email
    rol_filter = request.GET.get('rol')  # Parámetro para el filtro por rol

    # Filtramos usuarios por búsqueda y por rol
    usuarios = CustomUser.objects.select_related('id_rol', 'cliente', 'conductor')

    if query:
        # Si hay un término de búsqueda, filtramos los usuarios por username o email
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )
    
    if rol_filter:
        # Si hay un rol seleccionado, filtramos los usuarios por rol
        usuarios = usuarios.filter(id_rol__nombre=rol_filter)

    context = {
        'usuarios': usuarios,
        'query': query,
        'rol_filter': rol_filter  # Pasamos el rol seleccionado al template
    }

    return render(request, 'panel/lista.html', context)

def editar_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    
    # Determinar el tipo de usuario y seleccionar el formulario apropiado
    if usuario.id_rol.nombre == 'admin':
        detalles_instance = None
        detalles_form_class = None
    elif usuario.id_rol.nombre == 'comun':
        detalles_instance = usuario.cliente if hasattr(usuario, 'cliente') else None
        detalles_form_class = ClienteForm
    elif usuario.id_rol.nombre == 'conductor':
        detalles_instance = usuario.conductor if hasattr(usuario, 'conductor') else None
        detalles_form_class = ConductorForm
    else:
        # Redirigir a la vista de error si el rol no es válido
        return redirect(reverse('eliminar_usuario', args=[user_id]))

    if request.method == 'POST':
        form = CustomUserForm(request.POST, request.FILES, instance=usuario)
        if detalles_form_class:
            detalles_form = detalles_form_class(request.POST, instance=detalles_instance)
        else:
            detalles_form = None
        
        if form.is_valid() and (detalles_form is None or detalles_form.is_valid()):
            try:
                form.save()
                if detalles_form:
                    detalles_instance = detalles_form.save(commit=False)
                    detalles_instance.user = usuario  # Asegúrate de asociar el usuario
                    detalles_instance.save()
                # Redirigir a la lista de usuarios u otra página después de editar
                return redirect('lista_usuarios')  # Ajusta 'lista_usuarios' con el nombre de tu URL
            except IntegrityError:
                # Manejar la excepción de integridad si ocurre un error al guardar
                return redirect(reverse('eliminar_usuario', args=[user_id]))
    else:
        form = CustomUserForm(instance=usuario)
        detalles_form = detalles_form_class(instance=detalles_instance) if detalles_form_class else None
    
    return render(request, 'usuarios/editar_usuario.html', {'form': form, 'detalles_form': detalles_form, 'usuario': usuario})

def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        usuario.delete()
        return redirect('lista_usuarios')  # Redirigir a la lista de usuarios después de eliminar
    
    return render(request, 'usuarios/eliminar_usuario.html', {'usuario': usuario})

def lista_conductores(request):
    query = request.GET.get('q')
    conductores = Conductor.objects.select_related('user')
    
    # Filtrar conductores por nombre de usuario si se proporciona un término de búsqueda
    if query:
        conductores = conductores.filter(Q(user__username__icontains=query))
    
    conductores_sin_vehiculo = [conductor for conductor in conductores if not Vehiculo.objects.filter(conductor=conductor).exists()]

    return render(request, 'panel/lista_conductores.html', {
        'conductores': conductores,
        'conductores_sin_vehiculo': conductores_sin_vehiculo,
        'query': query  # Pasar la consulta al contexto para mantener el valor del campo de búsqueda
    })

def registrar_vehiculo(request, conductor_id):
    conductor = get_object_or_404(Conductor, id=conductor_id)

    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES)  # Incluir request.FILES para manejar archivos
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.conductor = conductor
            vehiculo.save()
            return redirect('lista_conductores')  # Redirige a la lista de conductores después de guardar
    else:
        form = VehiculoForm()

    return render(request, 'usuarios/registrar_vehiculo.html', {'form': form, 'conductor': conductor})

def editar_vehiculo(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)

    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES, instance=vehiculo)
        if form.is_valid():
            form.save()
            return redirect('lista_conductores')
    else:
        form = VehiculoForm(instance=vehiculo)

    return render(request, 'panel/editar_vehiculo.html', {'form': form})

def lista_vehiculos(request):
    vehiculos = Vehiculo.objects.select_related('conductor__user').all()
    return render(request, 'usuarios/lista_vehiculos.html', {'vehiculos': vehiculos})

def panel_control(request):
    context = {
        'user_name': request.user.get_full_name(),  # Obtén el nombre completo del usuario autenticado
        'user_image': 'ruta_a_imagen_usuario',  # Coloca la ruta a la imagen del usuario
    }
    return render(request, 'panel/base.html', context)

def ver_historial_pedidos(request, usuario_id):
    cliente = get_object_or_404(Cliente, user_id=usuario_id)
    pedidos = Pedido.objects.filter(cliente=cliente).order_by('-fecha_hora_inicio')  # Ordenar desde el más reciente
    
    return render(request, 'panel/historial_pedidos.html', {
        'pedidos': pedidos,
        'cliente': cliente,
    })

def ver_info_vehiculo(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)

    if request.method == 'POST':
        # Cambiar el estado del vehículo
        if vehiculo.estado == 'ocupado':
            vehiculo.estado = 'activo'
            messages.success(request, 'El estado del vehículo ha sido cambiado a activo.')
        elif vehiculo.estado == 'activo':
            vehiculo.estado = 'inactivo'
            messages.success(request, 'El estado del vehículo ha sido cambiado a inactivo.')
        elif vehiculo.estado == 'inactivo':
            vehiculo.estado = 'activo'
            messages.success(request, 'El estado del vehículo ha sido cambiado a activo.')
        
        vehiculo.save()
        return redirect('ver_vehiculo', vehiculo_id=vehiculo.id)  # Redirigir de nuevo a la misma vista

    context = {
        'vehiculo': vehiculo,
    }

    return render(request, 'panel/ver_vehiculo.html', context)

def cambiar_estado_vehiculo(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in ['activo', 'inactivo']:
            vehiculo.estado = nuevo_estado
            vehiculo.save()
            messages.success(request, f"El estado del vehículo ha sido cambiado a {nuevo_estado}.")
        else:
            messages.error(request, "Estado inválido.")
    
    return redirect('ver_vehiculo', conductor_id=vehiculo.conductor.id)
from django.http import JsonResponse

