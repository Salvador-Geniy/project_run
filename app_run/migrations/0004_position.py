# Generated by Django 5.0.2 on 2024-10-29 22:11

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0003_run_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)], verbose_name='широта')),
                ('longitude', models.FloatField(validators=[django.core.validators.MinValueValidator(-180.0), django.core.validators.MaxValueValidator(180.0)], verbose_name='долгота')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_run.run', verbose_name='забег')),
            ],
            options={
                'verbose_name': 'координаты забега',
                'verbose_name_plural': 'координаты забегов',
            },
        ),
    ]
