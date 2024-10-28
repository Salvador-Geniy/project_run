from django.contrib import admin
from django.contrib.admin import ModelAdmin
from app_run import models


@admin.register(models.ClubData)
class ClubDataAdmin(ModelAdmin):
    pass


@admin.register(models.Run)
class RunAdmin(ModelAdmin):
    pass

