from geopy.distance import geodesic
from .models import Position
from django.db.models import Min, Max, QuerySet


def get_distance(positions: list[Position]) -> float:
    distance_total = 0
    if len(positions) >= 2:
        for i in range(len(positions) - 1):
            distance_total += geodesic(
                (positions[i].latitude, positions[i].longitude),
                (positions[i+1].latitude, positions[i+1].longitude)
            ).km
    return distance_total


def get_run_time_seconds(positions: QuerySet["Position"]) -> int:
    border_positions_time = positions.aggregate(
        first_time=Min("date_time"),
        last_time=Max("date_time")
    )
    first_time = border_positions_time.get("first_time")
    last_time = border_positions_time.get("last_time")
    if first_time and last_time:
        return (last_time - first_time).seconds
    return 0
