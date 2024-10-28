from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer
from django.contrib.auth.models import User


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


class UserReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = User.objects.filter(is_superuser=False)
        type_filter = self.request.query_params.get("type")
        if type_filter:
            match type_filter:
                case "coach":
                    qs = qs.filter(is_staff=True)
                case "athlete":
                    qs = qs.filter(is_staff=False)
        return qs

    def filter_queryset(self, queryset):
        type_filter = self.request.query_params.get("type")
        if type_filter:
            match type_filter:
                case "coach":
                    queryset = queryset.filter(is_staff=True)
                case "athlete":
                    queryset = queryset.filter(is_staff=False)
        return queryset
