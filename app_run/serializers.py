from django.contrib.auth.models import User

from app_run.models import Run
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField


class RunSerializer(ModelSerializer):
    status = CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Run
        fields = ["id", "athlete", "comment", "status", "created_at"]


class UserSerializer(ModelSerializer):
    type = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "last_name",
            "first_name",
            "type",
        ]

    def get_type(self, instance) -> str:
        match instance.is_staff:
            case True:
                return "coach"
            case _:
                return "athlete"
