# Generated by Django 4.2.7 on 2024-08-12 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0005_alter_pedido_conductor_alter_pedido_origen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='estado',
            field=models.CharField(default='pendiente', max_length=100),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='estado',
            field=models.CharField(default='fuera de servicio', max_length=100),
        ),
    ]
