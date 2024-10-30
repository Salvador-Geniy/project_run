from geopy.distance import geodesic
from .models import Position


def get_distance(positions: list[Position]) -> float:
    distance_total = 0
    if len(positions) >= 2:
        for i in range(len(positions) - 1):
            distance_total += geodesic(
                (positions[i].latitude, positions[i].longitude),
                (positions[i+1].latitude, positions[i+1].longitude)
            ).km
    return distance_total
