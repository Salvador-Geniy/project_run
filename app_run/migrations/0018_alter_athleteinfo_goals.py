# Generated by Django 5.0.2 on 2024-12-13 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0017_alter_athleteinfo_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='athleteinfo',
            name='goals',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='цели'),
        ),
    ]
