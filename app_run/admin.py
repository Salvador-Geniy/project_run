from django.contrib import admin
from django.contrib.admin import ModelAdmin
from app_run import models


@admin.register(models.ClubData)
class ClubDataAdmin(ModelAdmin):
    pass


@admin.register(models.Run)
class RunAdmin(ModelAdmin):
    list_display = (
        "id",
        "athlete",
        "comment",
        "status",
        "distance",
        "created_at",
    )

    fields = (
        "athlete",
        "comment",
        "status",
    )

    def get_fields(self, request, obj=None):
        if obj:
            return ("comment", "status")
        return self.fields


