from django.db.models import Count, Q, Sum, Avg, Prefetch
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404, CreateAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from app_run.models import (
    Run,
    Position,
    Challenge,
    Subscribe,
    UnitLocation,
    UnitAthleteRelation,
    AthleteInfo,
    CoachRate
)
from app_run.serializers import (
    RunSerializer,
    UserSerializer,
    PositionSerializer,
    SubscribeSerializer,
    CoachSerializer,
    AthleteSerializer,
    ChallengeSerializer,
    ChallengesSummaryListSerializer,
    UploadFileSerializer,
    UnitLocationSerializer,
    AthleteInfoSerializer,
    CoachRateSerializer,
)
from django.contrib.auth.models import User
from rest_framework.filters import SearchFilter, OrderingFilter
from .services import get_distance, get_run_time_seconds, get_average_speed
from django_filters.rest_framework import DjangoFilterBackend
import openpyxl
import re

@api_view(["GET"])
def get_club_data(request):
    return Response({
        "company_name": "Der company",
        "slogan": "Der slogan",
        "contacts": "Der company contacts",
    })


class RunViewSet(ModelViewSet):
    queryset = Run.objects.select_related("athlete")
    serializer_class = RunSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = ["status", "id"]
    ordering_fields = ["created_at"]


class UserReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        qs = (
            User.objects.filter(is_superuser=False)
            .prefetch_related("user_run")
            .prefetch_related(
                Prefetch(
                    "uathlete",
                    queryset=UnitAthleteRelation.objects.select_related("unit")
                )
            )
            .annotate(runs_finished=Count("user_run", filter=Q(user_run__status="finished")))
            .annotate(avg_rating=Avg("coach__rating"))
        )
        type_filter = self.request.query_params.get("type")
        if type_filter:
            match type_filter:
                case "coach":
                    qs = qs.filter(is_staff=True).prefetch_related("coach_subscribe", "coach")
                case "athlete":
                    qs = qs.filter(is_staff=False).select_related("athlete_subscribe", "athlete")
        return qs

    def get_serializer_class(self, is_coach: bool):
        match self.action:
            case "retrieve":
                match is_coach:
                    case True:
                        return CoachSerializer
                    case _:
                        return AthleteSerializer
            case "list":
                return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        if self.action == "list":
            serializer_class = self.serializer_class
        else:
            is_coach = args[0].is_staff
            serializer_class = self.get_serializer_class(is_coach)
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)


class RunStartView(APIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        run_id = kwargs.get("run_id")
        run = get_object_or_404(Run, pk=run_id)
        if run.status != "init":
            return Response({"Detail": "Wrong run status"}, 400)
        run.status = "in_progress"
        run.save()
        return Response({"Detail": "Run started"}, 200)


class RunStopView(APIView):
    serializer_class = None

    def post(self, request, *args, **kwargs):
        run_id = kwargs.get("run_id")
        run = get_object_or_404(Run, pk=run_id)
        if run.status != "in_progress":
            return Response({"Detail": "Wrong run status"}, 400)

        positions = self.get_positions(run)
        dist_total = get_distance(positions)
        run_time_seconds = get_run_time_seconds(positions)
        avg_speed = get_average_speed(positions)
        self.update_run_fields(run, dist_total, run_time_seconds, avg_speed)
        self.check_run_count(run.athlete)
        self.check_total_distance(run.athlete)
        self.check_run_speed(run)
        return Response({"Detail": "Run stopped"}, 200)

    def check_run_speed(self, run):
        if run.run_time_seconds < 600 and run.distance >= 2.0:
            Challenge.objects.get_or_create(full_name="Пробеги 2 километра меньше чем за 10 минут!", athlete=run.athlete)

    def check_total_distance(self, athlete):
        total_distance = (
            Run.objects
            .filter(athlete=athlete, status="finished")
            .aggregate(total_distance=Sum("distance"))
            .get("total_distance")
        )
        if total_distance > 50.0:
            Challenge.objects.get_or_create(full_name="Пробеги 50 километров!", athlete=athlete)

    def get_positions(self, run):
        return Position.objects.filter(run=run)

    def update_run_fields(self, run: Run, dist_total: float, run_time_seconds: int, avg_speed: float) -> None:
        run.distance = dist_total
        run.status = "finished"
        run.run_time_seconds = run_time_seconds
        run.speed = avg_speed
        run.save(update_fields=["distance", "status", "run_time_seconds", "speed"])

    @staticmethod
    def check_run_count(athlete):
        finished_run_count = Run.objects.filter(athlete=athlete, status="finished").count()
        if finished_run_count == 10:
            Challenge.objects.get_or_create(full_name="Сделай 10 Забегов!", athlete=athlete)


class PositionViewSet(ModelViewSet):
    queryset = Position.objects.select_related("run")
    serializer_class = PositionSerializer
    lookup_url_kwarg = "run"

    def filter_queryset(self, queryset):
        run_id = self.request.query_params.get(self.lookup_url_kwarg)
        if run_id:
            return queryset.filter(run=run_id)
        return queryset

    def get_serializer_context(self):
        run_id = self.request.data.get("run")
        prev_position = self.get_prev_position(run_id)
        context = super().get_serializer_context()
        context |= {"prev_position": prev_position}
        return context

    def get_prev_position(self, run_id: int) -> Position | None:
        return Position.objects.filter(run_id=run_id).order_by("-id").first()


class SubscribeView(CreateAPIView):
    serializer_class = SubscribeSerializer

    def create(self, request, *args, **kwargs):
        coach_id = kwargs.get("id")
        coach = get_object_or_404(User, pk=coach_id)

        data = request.data
        data["coach"] = coach.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class ChallengeListView(ListAPIView):
    queryset = Challenge.objects.select_related("athlete")
    serializer_class = ChallengeSerializer
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_fields = ["athlete"]


class ChallengesSummaryListView(ListAPIView):
    serializer_class = ChallengesSummaryListSerializer

    def get_queryset(self):
        queryset = Challenge.objects.values("full_name").distinct()
        res = []
        for obj in queryset:
            obj["athletes"] = User.objects.filter(user_challenge__full_name=obj.get("full_name"))
            res.append(obj)
        return queryset


class ChallengesSummary2(APIView):

    def get(self, request, *args, **kwargs):
        challenge_names = Challenge.objects.values_list("full_name", flat=True).distinct()
        data_map = {name: set() for name in challenge_names}
        users = User.objects.prefetch_related("user_challenge").filter(is_staff=False)
        for user in users:
            for ch in user.user_challenge.all():
                if ch.full_name in data_map:
                    data_map[ch.full_name].add(user)

        data = [{"name_to_display": key, "athletes": [
            {"id": user.id, "full_name": f"{user.first_name} {user.last_name}", "username": user.username} for user in value
        ]} for key, value in data_map.items()]

        return Response(data=data, status=200)


class CoachAnalytics(APIView):
    def get(self, request, coach_id, *args, **kwargs):
        athletes = list(Subscribe.objects.filter(coach_id=coach_id).values_list("athlete_id", flat=True))
        if not athletes:
            return Response(status=404)
        data = dict()
        longest_run = Run.objects.filter(athlete__in=athletes).order_by("-distance").first()
        data["longest_run_user"] = longest_run.athlete_id
        data["longest_run_value"] = longest_run.distance

        users = (
            User.objects
            .filter(pk__in=athletes)
            .prefetch_related("user_run")
            .annotate(total_dist=Sum("user_run__distance"))
            .annotate(avg_speed=Avg("user_run__speed", default=0))
        )

        longest_total_distance = users.order_by("-total_dist").first()
        data["total_run_user"] = longest_total_distance.id
        data["total_run_value"] = longest_total_distance.total_dist

        avg_speed = users.order_by("-avg_speed").first()
        data["speed_avg_user"] = avg_speed.id
        data["speed_avg_value"] = avg_speed.avg_speed

        return JsonResponse(data, status=200)


class UploadFileView(APIView):
    parser_classes = [MultiPartParser]
    serializer_class = UploadFileSerializer

    def post(self, request, *args, **kwargs):
        wrong_rows = []
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            file = validated_data["file"]
            content_type = validated_data["file"].content_type
            if content_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                return Response("Wrong content type", 400)

            wrong_rows = self.get_rows(file)
        return Response(wrong_rows, status=status.HTTP_200_OK)

    def get_rows(self, file):
        wrong_rows = []
        sheet = openpyxl.load_workbook(file)
        sheet = sheet.active
        for i, row in enumerate(sheet.iter_rows(values_only=True)):
            if i == 0:
                continue
            wrong_row = self.get_unit(row)
            if wrong_row:
                wrong_rows.append(list(wrong_row))
        return wrong_rows

    def check_position(self, lat, lon) -> bool:
        try:
            lat = float(lat)
            lon = float(lon)
            return (-90.0 <= lat <= 90.0) and (-180.0 <= lon <= 180.0)
        except Exception:
            return False

    def check_level(self, level):
        try:
            int(level)
            return True
        except Exception:
            return False

    def check_name(self, name):
        if not name or not isinstance(name, str):
            return False
        return True

    def get_unit(self, row):
        try:
            if not self.check_url(row[5]) or not self.check_position(row[3], row[4]) or not self.check_level(row[2]) or not self.check_name(row[0]):
                raise ValueError
            UnitLocation.objects.create(
                name=row[0],
                uid=row[1],
                latitude=row[3],
                longitude=row[4],
                picture=row[5],
                value=row[2]
            )
        except ValueError:
            return row

    @staticmethod
    def check_url(url: str) -> bool:
        pattern = r"^(https?):\/\/([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/[^\s]*)?$"
        if re.match(pattern, url):
            return True
        return False


class UnitLocationListView(ListAPIView):
    queryset = UnitLocation.objects.all()
    serializer_class = UnitLocationSerializer


class AthleteInfoView(ModelViewSet):
    queryset = AthleteInfo.objects.all()
    serializer_class = AthleteInfoSerializer
    http_method_names = ["get", "put"]
    lookup_field = "user_id"

    def get_object(self):
        user = get_object_or_404(User, pk=self.kwargs.get(self.lookup_field))
        obj, _ = AthleteInfo.objects.get_or_create(user_id=user.id)
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CoachRateView(APIView):
    def post(self, request, coach_id, *args, **kwargs):
        coach = get_object_or_404(User, id=coach_id)
        athlete_id = request.data.get("athlete")
        if not athlete_id:
            return Response("Athlete is required field", 400)
        if not User.objects.filter(is_staff=False, pk=athlete_id).exists():
            return Response("No", 400)
        athlete = get_object_or_404(User.objects.select_related("athlete_subscribe"), is_staff=False, pk=athlete_id)
        subscribe = Subscribe.objects.filter(coach=coach, athlete=athlete).first()
        if not subscribe:
            return Response("Can't rate", 400)
        if athlete.athlete_subscribe and athlete.athlete_subscribe.coach_id != coach_id:
            return Response("Athlete doesn't can rate this coach", 400)
        rate_obj, _ = CoachRate.objects.get_or_create(coach_id=coach_id, athlete_id=athlete_id)
        serializer = CoachRateSerializer(data=request.data, instance=rate_obj)
        if not serializer.is_valid():
            return Response(serializer.errors, 400)
        serializer.save()
        return Response(serializer.data, 200)


