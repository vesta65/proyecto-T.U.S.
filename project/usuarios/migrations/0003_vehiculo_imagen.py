# Generated by Django 4.2.7 on 2024-08-11 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_customuser_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='vehiculos/'),
        ),
    ]
