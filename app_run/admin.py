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
        "speed",
        "created_at",
    )

    fields = (
        "athlete",
        "comment",
        "speed",
        "distance",
    )

    def get_fields(self, request, obj=None):
        if obj:
            return ["comment", "status", "speed", "distance"]
        return self.fields


@admin.register(models.Position)
class PositionAdmin(ModelAdmin):
    list_display = [
        "id",
        "run",
        "latitude",
        "longitude",
        "distance",
        "speed",
        "date_time",
    ]


@admin.register(models.Subscribe)
class SubscribeAdmin(ModelAdmin):
    list_display = [
        "id",
        "coach",
        "athlete"
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "coach":
            kwargs["queryset"] = models.User.objects.filter(is_staff=True).exclude(is_superuser=True)
        elif db_field.name == "athlete":
            kwargs["queryset"] = models.User.objects.filter(is_staff=False).exclude(is_superuser=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.Challenge)
class ChallengeAdmin(ModelAdmin):
    list_display = [
        "id",
        "full_name",
        "athlete",
    ]