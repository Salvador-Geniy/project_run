"""
URL configuration for project_run project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from app_run.views import (
    get_club_data,
    RunViewSet,
    UserReadOnlyViewSet,
    RunStartView,
    RunStopView,
    PositionViewSet,
    SubscribeView,
    ChallengeListView,
    ChallengesSummaryListView,
    ChallengesSummary2,
    CoachAnalytics,
    TestPositionView,
)

from rest_framework.routers import SimpleRouter
router = SimpleRouter()

router.register(r"api/runs", RunViewSet, basename="runs")
router.register(r"api/users", UserReadOnlyViewSet, basename="users")
router.register(r"api/positions", PositionViewSet, basename="positions")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/company_details/', get_club_data, name='company-details'),
    path("api/runs/<int:run_id>/start/", RunStartView.as_view(), name="run-start"),
    path("api/runs/<int:run_id>/stop/", RunStopView.as_view(), name="run-start"),
    path("api/subscribe_to_coach/<int:id>/", SubscribeView.as_view(), name="subscribe-to-coach"),
    path("api/challenges/", ChallengeListView.as_view(), name="challenge-list"),
    path("api/challenges_summary/", ChallengesSummary2.as_view(), name="challenges-summary"),
    path("api/analytics_for_coach/<int:coach_id>/", CoachAnalytics.as_view(), name="coach-analitics"),
    path("api/test-position/", TestPositionView.as_view(), name="test-position"),
    path("", include(router.urls)),
]