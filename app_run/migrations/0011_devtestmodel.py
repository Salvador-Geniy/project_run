# Generated by Django 5.0.2 on 2025-01-03 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_run', '0010_challenge'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevTestModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('count', models.PositiveSmallIntegerField()),
            ],
        ),
    ]
