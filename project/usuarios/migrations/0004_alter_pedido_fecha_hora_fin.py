# Generated by Django 4.2.7 on 2024-08-12 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_vehiculo_imagen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='fecha_hora_fin',
            field=models.DateTimeField(null=True),
        ),
    ]
