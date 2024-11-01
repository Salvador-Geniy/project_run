from django.db.models import Count, Q
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from app_run.models import Run, Position
from app_run.serializers import RunSerializer, UserSerializer, PositionSerializer
from django.contrib.auth.models import User
from rest_framework.filters import SearchFilter, OrderingFilter
from .services import get_distance, get_run_time_seconds, get_average_speed
from django_filters.rest_framework import DjangoFilterBackend


@api_view(["GET"])
def get_club_data(request):
    return Response({
        "company_name": "My company",
        "slogan": "My slogan",
        "contacts": "My company contacts",
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
            .annotate(runs_finished=Count("user_run", filter=Q(user_run__status="finished")))
        )
        type_filter = self.request.query_params.get("type")
        if type_filter:
            match type_filter:
                case "coach":
                    qs = qs.filter(is_staff=True)
                case "athlete":
                    qs = qs.filter(is_staff=False)
        return qs


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

        return Response({"Detail": "Run stopped"}, 200)

    def get_positions(self, run):
        return Position.objects.filter(run=run)

    def update_run_fields(self, run: Run, dist_total: float, run_time_seconds: int, avg_speed: float) -> None:
        run.distance = dist_total
        run.status = "finished"
        run.run_time_seconds = run_time_seconds
        run.speed = avg_speed
        run.save(update_fields=["distance", "status", "run_time_seconds", "speed"])


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
