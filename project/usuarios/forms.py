from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from usuarios.models import CustomUser, Rol

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Rol, Cliente

class CustomUserCreationForm(UserCreationForm):
    # Añadimos un campo para la cédula de identidad
    ci = forms.CharField(max_length=20, required=False, label='Cédula de Identidad')

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'telf', 'edad']

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Asignar el rol por defecto al nuevo usuario
        rol_comun = Rol.objects.get(nombre='comun')  # Asegúrate de que el nombre del rol sea correcto
        user.id_rol = rol_comun
        
        if commit:
            user.save()

        # Si el usuario es común, asignar el campo CI en el modelo Cliente
        if user.id_rol.nombre == 'comun' and self.cleaned_data.get('ci'):
            # Crear el cliente con la cédula de identidad proporcionada
            Cliente.objects.create(user=user, ci=self.cleaned_data['ci'])
        
        return user


class CustomUserLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
