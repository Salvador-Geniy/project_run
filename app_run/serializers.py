from django.contrib.auth.models import User
from app_run.models import Run, Position
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    CharField,
    IntegerField,
    ValidationError,
    FloatField,
)


class RunSerializer(ModelSerializer):
    status = CharField(source="get_status_display", read_only=True)
    distance = FloatField(read_only=True)

    class Meta:
        model = Run
        fields = ["id", "athlete", "comment", "status", "created_at", "distance"]


class UserSerializer(ModelSerializer):
    type = SerializerMethodField()
    runs_finished = IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "last_name",
            "first_name",
            "type",
            "runs_finished",
        ]

    def get_type(self, instance) -> str:
        match instance.is_staff:
            case True:
                return "coach"
            case _:
                return "athlete"


class PositionSerializer(ModelSerializer):
    latitude = FloatField(min_value=-90.0, max_value=90.0)
    longitude = FloatField(min_value=-180.0, max_value=180.0)

    class Meta:
        model = Position
        fields = [
            "id",
            "run",
            "latitude",
            "longitude",
        ]

    def validate_run(self, run):
        if run.status != "in_progress":
            raise ValidationError("Run must have status 'in_progress'")
        return run
