# Generated manually to keep the database history aligned with the hotel form.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotelghino', '0005_alter_alojamiento_fecha_creacion_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alojamiento',
            name='tipo',
            field=models.CharField(choices=[('HT', 'Hotel'), ('HS', 'Hostel'), ('CA', 'Casa'), ('DP', 'Departamento'), ('CB', 'Cabana')], default='HT', max_length=20),
        ),
        migrations.AlterField(
            model_name='alojamiento',
            name='calle',
            field=models.CharField(max_length=50),
        ),
    ]
