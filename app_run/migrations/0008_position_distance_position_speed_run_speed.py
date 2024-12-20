# Generated by Django 5.0.2 on 2024-10-30 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0007_position_date_time_run_run_time_seconds_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='position',
            name='distance',
            field=models.FloatField(default=0, verbose_name='пройденная дистанция'),
        ),
        migrations.AddField(
            model_name='position',
            name='speed',
            field=models.FloatField(default=0, verbose_name='скорость в м/с'),
        ),
        migrations.AddField(
            model_name='run',
            name='speed',
            field=models.FloatField(default=0, verbose_name='средняя скорость в м/с'),
        ),
    ]
