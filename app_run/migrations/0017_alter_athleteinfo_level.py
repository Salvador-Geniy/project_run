# Generated by Django 5.0.2 on 2024-12-12 11:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0016_athleteinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athleteinfo',
            name='level',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='уровень'),
        ),
    ]