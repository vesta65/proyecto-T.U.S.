from django import forms
from usuarios.models import Pedido
from django.utils import timezone

class PedidoForm(forms.ModelForm):
    origen = forms.URLField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Introduce la URL de Google Maps'})
    )

    class Meta:
        model = Pedido
        fields = ['servicio', 'origen']  # Excluye 'fecha_hora_fin' y 'conductor'

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Usuario logueado
        super().__init__(*args, **kwargs)
        if self.user:
            self.instance.cliente = self.user.cliente  # Asume que hay una relación uno a uno

    def save(self, commit=True):
        pedido = super().save(commit=False)
        if commit:
            pedido.fecha_hora_inicio = timezone.now()  # Establece la hora actual
            if commit:
                pedido.save()
        return pedido
