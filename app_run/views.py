from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from app_run.models import Run
from app_run.serializers import RunSerializer


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
