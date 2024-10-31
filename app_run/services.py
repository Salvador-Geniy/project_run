from geopy.distance import geodesic
from .models import Position
from django.db.models import Min, Max, QuerySet, Avg


def get_distance(positions: list[Position]) -> float:
    distance_total = 0
    if len(positions) >= 2:
        for i in range(len(positions) - 1):
            distance_total += geodesic(
                (positions[i].latitude, positions[i].longitude),
                (positions[i+1].latitude, positions[i+1].longitude)
            ).km
    return round(distance_total, 2)


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


def _get_current_distance(prev_latitude, prev_longitude, cur_latitude, cur_longitude) -> float:
    distance = geodesic((prev_latitude, prev_longitude), (cur_latitude, cur_longitude)).km
    return round(distance, 2)


def _get_current_speed(prev_time, cur_time, distance) -> float:
    time = (cur_time - prev_time).seconds
    return round(distance * 1000 / time, 2)


def get_distance_speed_from_last_position(prev_position, validated_data) -> dict[str, [str | int | float]]:
    cur_latitude = validated_data.get("latitude")
    cur_longitude = validated_data.get("longitude")
    cur_time = validated_data.get("date_time")
    distance = _get_current_distance(
        prev_position.latitude,
        prev_position.longitude,
        cur_latitude,
        cur_longitude
    )
    speed = _get_current_speed(prev_position.date_time, cur_time, distance)
    validated_data["distance"] = prev_position.distance + distance
    validated_data["speed"] = speed
    return validated_data


def get_average_speed(positions: QuerySet["Position"]) -> float:
    avg_speed = positions.aggregate(avg_speed=Avg("speed")).get("avg_speed")
    return round(avg_speed, 2)
