from django.contrib.auth.models import User
from app_run.models import Run, Position
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    CharField,
    IntegerField,
    ValidationError,
    FloatField,
    DateTimeField,
)
from .services import get_distance_speed_from_last_position


class UserDataSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "last_name",
            "first_name",
        ]


class RunSerializer(ModelSerializer):
    status = CharField(source="get_status_display", read_only=True)
    distance = FloatField(read_only=True)
    run_time_seconds = IntegerField(read_only=True)
    speed = FloatField(read_only=True)
    athlete_data = UserDataSerializer(source="athlete", read_only=True)

    class Meta:
        model = Run
        fields = [
            "id",
            "athlete",
            "comment",
            "status",
            "created_at",
            "distance",
            "run_time_seconds",
            "speed",
            "athlete_data",
        ]


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
    date_time = DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f")
    speed = FloatField(read_only=True)
    distance = FloatField(read_only=True)

    class Meta:
        model = Position
        fields = [
            "id",
            "run",
            "latitude",
            "longitude",
            "date_time",
            "speed",
            "distance",
        ]

    def validate_run(self, run):
        if run.status != "in_progress":
            raise ValidationError("Run must have status 'in_progress'")
        return run

    def create(self, validated_data):
        prev_position = self.context.get("prev_position")
        if prev_position:
            validated_data = get_distance_speed_from_last_position(prev_position, validated_data)
        return super().create(validated_data)

    # def compare_times(self, run, date_time) -> None:
    #     if run.created_at > date_time:
    #         raise ValidationError("Position date_time can't be less than the run start time")
    #
    # def create(self, validated_data):
    #     run = validated_data.get("run")
    #     date_time = validated_data.get("date_time")
    #     self.compare_times(run, date_time)
    #     return super().create(validated_data)
    #
    # def update(self, instance, validated_data):
    #     run = validated_data.get("run") or instance.run
    #     date_time = validated_data.get("date_time") or instance.date_time
    #     self.compare_times(run, date_time)
    #     return super().update(instance, validated_data)
