from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from usuarios.models import CustomUser, Cliente, Rol, Conductor, Vehiculo
from django import forms


class RechazoForm(forms.Form):
    MOTIVO_CHOICES = [
        ('cliente_no_contactable', 'Cliente no contactable'),
        ('conductor_no_disponible', 'Conductor no disponible'),
        ('demora', 'Demora en el servicio'),
        ('otros', 'Otros (Especificar)'),
    ]

    motivo = forms.ChoiceField(choices=MOTIVO_CHOICES, widget=forms.RadioSelect)
    descripcion_otros = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Especificar motivo si eligió "Otros"'}))


class RegistroForm(forms.ModelForm):
    rol = forms.ModelChoiceField(queryset=Rol.objects.all(), empty_label="Seleccione un rol")
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)
    email = forms.EmailField(label='Correo electrónico')
    profile_image = forms.ImageField(label='Imagen de perfil', required=False)  # Campo para la imagen

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'telf', 'edad', 'rol', 'profile_image']

    def clean_confirm_password(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        return password2

    def save(self, commit=True):
        user = super(RegistroForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        rol = self.cleaned_data['rol']
        user.id_rol = rol
        if commit:
            user.set_password(self.cleaned_data['password'])
            user.save()
        return user

    
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['ci']  # Lista los campos que quieres incluir en el formulario

    def __init__(self, *args, **kwargs):
        super(ClienteForm, self).__init__(*args, **kwargs)
        self.fields['ci'].label = 'Cédula de Identidad'  # Personaliza la etiqueta del campo si es necesario
        self.fields['ci'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingrese su CI'})  # Añade clases CSS y atributos HTML si es necesario

class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = ['num_lice', 'categoria']  # Lista los campos que quieres incluir en el formulario

    def __init__(self, *args, **kwargs):
        super(ConductorForm, self).__init__(*args, **kwargs)
        self.fields['num_lice'].label = 'Número de Licencia'  # Personaliza la etiqueta del campo si es necesario
        self.fields['num_lice'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingrese su número de licencia'})  # Añade clases CSS y atributos HTML si es necesario

        self.fields['categoria'].label = 'Categoría'  # Personaliza la etiqueta del campo si es necesario
        self.fields['categoria'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Ingrese la categoría de licencia'})  # Añade clases CSS y atributos HTML si es necesario

class CustomUserForm(forms.ModelForm):
    profile_image = forms.ImageField(required=False, label='Imagen de Perfil')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'id_rol', 'first_name', 'last_name',  'telf', 'edad', 'profile_image']

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['ci']

class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = ['num_lice', 'categoria']

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['estado', 'placa', 'modelo', 'color', 'anio', 'tipo_vehiculo', 'imagen']