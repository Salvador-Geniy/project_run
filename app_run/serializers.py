from app_run.models import Run
from rest_framework.serializers import ModelSerializer


class RunSerializer(ModelSerializer):
    class Meta:
        model = Run
        fields = ["id", "athlete", "comment", "created_at"]
