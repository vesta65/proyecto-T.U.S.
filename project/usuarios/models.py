from django.contrib.auth.models import AbstractUser
from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class CustomUser(AbstractUser):
    id_rol = models.ForeignKey(Rol, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    telf = models.CharField(max_length=15, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)  # Campo de imagen opcional    
    
    def save(self, *args, **kwargs):
        # Verifica si el número de teléfono no está vacío
        if self.telf:
            # Elimina espacios en blanco y el signo '+' si existe
            self.telf = self.telf.replace(" ", "").replace("+", "")
            # Si el número no comienza con '591', añade el prefijo
            if not self.telf.startswith("591"):
                self.telf = "+591" + self.telf
        # Llama al método save de la clase base para guardar el objeto
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

class Cliente(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    ci = models.CharField(max_length=20)

    def __str__(self):
        return f"Cliente: {self.user.username}"

class Conductor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    num_lice = models.CharField(max_length=20)
    categoria = models.CharField(max_length=10)

    def __str__(self):
        return f"Conductor: {self.user.username}"

class TipoVehiculo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    estado = models.CharField(max_length=100, default='fuera de servicio')
    placa = models.CharField(max_length=20)
    modelo = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    anio = models.PositiveIntegerField()
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE)
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='vehiculos/', null=True, blank=True)  # Añade este campo
    

    def __str__(self):
        return f"Vehículo {self.placa} - Modelo: {self.modelo}"

class TipoServicio(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    conductor = models.ForeignKey(Conductor, null=True, on_delete=models.CASCADE)
    servicio = models.ForeignKey(TipoServicio, on_delete=models.CASCADE)
    fecha_hora_inicio = models.DateTimeField()
    fecha_hora_fin = models.DateTimeField(null=True)
    estado = models.CharField(max_length=100, default='pendiente')  # Valor por defecto
    origen = models.URLField(null=True)
    motivo_rechazo = models.CharField(max_length=255, null=True, blank=True)  # Añade este campo

    def __str__(self):
        return f"Pedido {self.id} - Cliente: {self.cliente.user.username} - Conductor: {self.conductor.user.username}"



