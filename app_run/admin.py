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
        "run_time_seconds",
        "created_at",
    )

    fields = (
        "athlete",
        "comment",
    )

    def get_fields(self, request, obj=None):
        if obj:
            return ("comment", "status")
        return self.fields


@admin.register(models.Position)
class PositionAdmin(ModelAdmin):
    pass


