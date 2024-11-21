from geopy.distance import geodesic
from .models import Position
from django.db.models import Min, Max, QuerySet, Avg
import geopandas as gpd
from shapely.geometry import Point


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
    try:
        time = (cur_time - prev_time).seconds
        return round(distance * 1000 / time, 2)
    except ZeroDivisionError:
        return 0


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
    if not positions:
        return 0
    avg_speed = positions.aggregate(avg_speed=Avg("speed")).get("avg_speed")
    return round(avg_speed, 2)


def get_cities_for_positions(positions):
    result = []
    cities_file = "ne_10m_populated_places/ne_10m_populated_places.shp"
    try:
        # Загружаем файл с городами
        cities = gpd.read_file(cities_file)
        # Проверяем текущую систему координат
        if cities.crs is None:
            raise ValueError("CRS не определена в файле .shp. Проверьте файл.")
        for position in positions:
            latitude, longitude = position.latitude, position.longitude

            # Создаем точку из координат
            point = gpd.GeoSeries([Point(float(longitude), float(latitude))], crs="EPSG:4326")

            # Преобразуем обе геометрии в проекционную систему координат
            cities = cities.to_crs(epsg=3857)  # Преобразуем в метрическую систему
            point = point.to_crs(epsg=3857)

            # Вычисляем расстояние от точки до всех городов
            cities["distance"] = cities.geometry.distance(point.iloc[0], align=False)

            # Находим ближайший город
            nearest_city = cities.sort_values("distance").iloc[0]

            # Получаем название города
            city_name = nearest_city.get("NAME", None)

            if city_name:
                result.append(city_name)

    except Exception:
        pass

    return result

