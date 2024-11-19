from twilio.rest import Client
from django.conf import settings

def enviar_sms_conductor(pedido):
    # Inicializa el cliente de Twilio
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    # Extrae el número de teléfono del conductor asignado
    conductor = pedido.conductor
    numero_conductor = conductor.user.telf

    # Construye el mensaje
    mensaje = f"""
    Nuevo Pedido Asignado:
    Cliente: {pedido.cliente.user.username}
    Servicio: {pedido.servicio.nombre}
    Fecha y Hora de Inicio: {pedido.fecha_hora_inicio}
    Ubicación: {pedido.origen}
    """

    # Envía el mensaje
    message = client.messages.create(
        body=mensaje,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=numero_conductor
    )
    return message.sid
