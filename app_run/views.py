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
from .services import get_distance, get_run_time_seconds
from django_filters.rest_framework import DjangoFilterBackend


@api_view(["GET"])
def get_club_data(request):
    return Response({
        "company_name": "My company",
        "slogan": "My slogan",
        "contacts": "My company contacts",
    })


class RunViewSet(ModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    filterset_fields = ["status"]
    ordering_fields = ["created_at"]


class UserReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ["first_name", "last_name"]

    def get_queryset(self):
        qs = (
            User.objects.filter(is_superuser=False)
            .prefetch_related("user_run")
            .annotate(runs_finished=Count("user_run", filter=Q(user_run__status=3)))
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
        self.update_run_fields(run, dist_total, run_time_seconds)

        return Response({"Detail": "Run stopped"}, 200)

    def get_positions(self, run):
        return Position.objects.filter(run=run)

    def update_run_fields(self, run: Run, dist_total: int, run_time_seconds: int) -> None:
        run.distance = dist_total
        run.status = "finished"
        run.run_time_seconds = run_time_seconds
        run.save(update_fields=["distance", "status", "run_time_seconds"])


class PositionViewSet(ModelViewSet):
    queryset = Position.objects.select_related("run")
    serializer_class = PositionSerializer
    lookup_url_kwarg = "run"

    def filter_queryset(self, queryset):
        run_id = self.request.query_params.get(self.lookup_url_kwarg)
        if run_id:
            return queryset.filter(run=run_id)
        return queryset
