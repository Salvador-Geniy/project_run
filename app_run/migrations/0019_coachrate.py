# Generated by Django 5.0.2 on 2024-12-17 14:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0018_alter_athleteinfo_goals'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CoachRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.PositiveSmallIntegerField(default=None, null=True, verbose_name='рейтинг')),
                ('athlete', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='athlete_rate', to=settings.AUTH_USER_MODEL, verbose_name='бегун')),
                ('coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coach_rate', to=settings.AUTH_USER_MODEL, verbose_name='тренер')),
            ],
            options={
                'verbose_name': 'рейтинг тренера',
                'verbose_name_plural': 'рейтинги тренеров',
            },
        ),
    ]
