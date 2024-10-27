from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def get_club_data(request):
    return Response({
        "company_name": "My company",
        "slogan": "My slogan",
        "contacts": "My company contacts",
    }, 200)

