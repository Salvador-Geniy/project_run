import datetime

from django.contrib.auth.models import User
from app_run.models import Run, Position, Subscribe, Challenge, UnitLocation, UnitAthlete
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    CharField,
    IntegerField,
    ValidationError,
    FloatField,
    DateTimeField,
    PrimaryKeyRelatedField,
    Serializer,
    FileField,
)
from .services import get_distance_speed_from_last_position, check_unit_locations


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
    items = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "last_name",
            "first_name",
            "type",
            "runs_finished",
            "items",
        ]

    def get_type(self, instance) -> str:
        match instance.is_staff:
            case True:
                return "coach"
            case _:
                return "athlete"

    def get_items(self, obj):
        items = [uathlete.unit for uathlete in obj.uathlete.all()]
        return UnitLocationSerializer(items, many=True).data


class CoachSerializer(UserSerializer):
    athletes = SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = [
            *UserSerializer.Meta.fields,
            "athletes"
        ]

    def get_athletes(self, obj) -> list[int]:
        athletes = obj.coach_subscribe.all().values_list("athlete_id", flat=True)
        return athletes


class AthleteSerializer(UserSerializer):
    coach = IntegerField(source="athlete_subscribe.coach_id", read_only=True)

    class Meta(UserSerializer.Meta):
        fields = [
            *UserSerializer.Meta.fields,
            "coach"
        ]


class PositionSerializer(ModelSerializer):
    latitude = FloatField(min_value=-90.0, max_value=90.0)
    longitude = FloatField(min_value=-180.0, max_value=180.0)
    date_time = DateTimeField(format="%Y-%m-%dT%H:%M:%S.%f", required=False)
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
        date_time = validated_data.get("date_time")
        if not date_time:
            validated_data["date_time"] = datetime.datetime.now(datetime.timezone.utc)
        prev_position = self.context.get("prev_position")
        if prev_position:
            validated_data = get_distance_speed_from_last_position(prev_position, validated_data)
        new_position = super().create(validated_data)
        units_for_create = check_unit_locations(new_position)
        if units_for_create:
            athlete_id = validated_data["run"].athlete_id
            for unit in units_for_create:
                UnitAthlete.objects.create(athlete_id=athlete_id, unit_id=unit.id)
        return new_position


class SubscribeSerializer(ModelSerializer):
    coach = PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=True)
    )
    athlete = PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_staff=False)
    )

    class Meta:
        model = Subscribe
        fields = ["coach", "athlete"]

    def check_existing_suscribe(self, athlete) -> None:
        if Subscribe.objects.filter(athlete=athlete).exists():
            raise ValidationError("Subscribe already exists")

    def create(self, validated_data):
        athlete = validated_data.get("athlete")
        self.check_existing_suscribe(athlete)
        return super().create(validated_data)


class ChallengeSerializer(ModelSerializer):
    class Meta:
        model = Challenge
        fields = [
            "id",
            "full_name",
            "athlete",
        ]


class ChallengeAthleteSerializer(ModelSerializer):
    full_name = SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class ChallengesSummaryListSerializer(Serializer):
    name_to_display = CharField(source="full_name")
    athletes = ChallengeAthleteSerializer(many=True)


CITIES = [
    "New York",
    "Paris",
    "Maiami",
    "Toronto",
    "San Francisco",
    "Los Angeles",
    "Buenos Aires",
    "Tokio",
    "Kioto"
]


class UploadFileSerializer(Serializer):
    file = FileField()


class UnitLocationSerializer(ModelSerializer):
    class Meta:
        model = UnitLocation
        fields = [
            "id",
            "name",
            "uid",
            # "latitude",
            "longitude",
            "picture",
            "value"
        ]
