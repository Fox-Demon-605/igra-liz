import heapq
import math

from .config import (
    MAP_COLS,
    MAP_ROWS,
    MOUNTAIN_TYPES,
    SEED,
    WATER_TYPES,
)


def clamp(value, minimum=0.0, maximum=1.0):
    return max(minimum, min(maximum, value))


def smoothstep(value):
    value = clamp(value)
    return value * value * (3 - 2 * value)


def hash_noise(x, y, seed):
    number = (
        x * 374761393
        + y * 668265263
        + seed * 1442695041
    ) & 0xFFFFFFFF

    number ^= number >> 13
    number = (number * 1274126177) & 0xFFFFFFFF
    number ^= number >> 16

    return number / 0xFFFFFFFF


def smooth_noise(x, y, scale, seed):
    x /= scale
    y /= scale

    x0 = math.floor(x)
    y0 = math.floor(y)

    fx = smoothstep(x - x0)
    fy = smoothstep(y - y0)

    a = hash_noise(x0, y0, seed)
    b = hash_noise(x0 + 1, y0, seed)
    c = hash_noise(x0, y0 + 1, seed)
    d = hash_noise(x0 + 1, y0 + 1, seed)

    top = a + (b - a) * fx
    bottom = c + (d - c) * fx

    return top + (bottom - top) * fy


def layered_noise(x, y, seed):
    return (
        smooth_noise(x, y, 25, seed) * 0.52
        + smooth_noise(x, y, 11, seed + 31) * 0.29
        + smooth_noise(x, y, 5, seed + 67) * 0.14
        + smooth_noise(x, y, 2, seed + 101) * 0.05
    )


def distance_to_segment(px, py, ax, ay, bx, by):
    vx = bx - ax
    vy = by - ay

    length_squared = vx * vx + vy * vy

    if length_squared == 0:
        return math.hypot(px - ax, py - ay)

    t = clamp(
        ((px - ax) * vx + (py - ay) * vy) / length_squared
    )

    nearest_x = ax + t * vx
    nearest_y = ay + t * vy

    return math.hypot(px - nearest_x, py - nearest_y)


def make_world():
    elevations = []
    moisture_values = []

    for y in range(MAP_ROWS):
        elevation_row = []
        moisture_row = []

        for x in range(MAP_COLS):
            nx = (x - MAP_COLS * 0.49) / (MAP_COLS * 0.52)
            ny = (y - MAP_ROWS * 0.53) / (MAP_ROWS * 0.58)

            distance = math.sqrt(
                (nx * 0.93) ** 2 + (ny * 1.08) ** 2
            )

            continent = 0.83 - distance * 0.68

            west_peninsula = max(
                0.0,
                0.18 - math.hypot(
                    (x - MAP_COLS * 0.22) / 23,
                    (y - MAP_ROWS * 0.40) / 15,
                ) * 0.16,
            )

            southeast = max(
                0.0,
                0.13 - math.hypot(
                    (x - MAP_COLS * 0.73) / 24,
                    (y - MAP_ROWS * 0.72) / 17,
                ) * 0.13,
            )

            detail = layered_noise(x, y, SEED)

            elevation = (
                continent
                + (detail - 0.5) * 0.70
                + west_peninsula
                + southeast
            )

            ridge_distance = min(
                distance_to_segment(
                    x, y,
                    MAP_COLS * 0.29, MAP_ROWS * 0.69,
                    MAP_COLS * 0.68, MAP_ROWS * 0.22,
                ),
                distance_to_segment(
                    x, y,
                    MAP_COLS * 0.50, MAP_ROWS * 0.51,
                    MAP_COLS * 0.79, MAP_ROWS * 0.48,
                ),
            )

            ridge_strength = max(
                0.0,
                1.0 - ridge_distance / 7.0,
            )
            elevation += ridge_strength * 0.20

            moisture = layered_noise(
                x + 117,
                y + 83,
                SEED + 200,
            )

            elevation_row.append(elevation)
            moisture_row.append(moisture)

        elevations.append(elevation_row)
        moisture_values.append(moisture_row)

    world = []

    for y in range(MAP_ROWS):
        row = []

        for x in range(MAP_COLS):
            elevation = elevations[y][x]
            moisture = moisture_values[y][x]

            if elevation < 0.31:
                kind = "deep_water"
            elif elevation < 0.39:
                kind = "water"
            elif elevation < 0.425:
                kind = "coast"
            elif elevation > 0.81:
                kind = "snow"
            elif elevation > 0.72:
                kind = "mountain"
            elif elevation > 0.64:
                kind = "hills"
            elif moisture > 0.63 and elevation < 0.52:
                kind = "marsh"
            elif moisture > 0.58:
                kind = "deep_forest"
            elif moisture > 0.48:
                kind = "forest"
            else:
                kind = "plain"

            row.append(kind)

        world.append(row)

    original = [row[:] for row in world]

    for y in range(1, MAP_ROWS - 1):
        for x in range(1, MAP_COLS - 1):
            if original[y][x] not in {
                "plain",
                "forest",
                "deep_forest",
                "marsh",
            }:
                continue

            adjacent_to_water = any(
                original[ny][nx] in WATER_TYPES
                for ny in range(y - 1, y + 2)
                for nx in range(x - 1, x + 2)
                if (nx, ny) != (x, y)
            )

            if adjacent_to_water:
                world[y][x] = "coast"

    return world, elevations


def find_place(
    world,
    target_x,
    target_y,
    allowed,
    min_distance=0,
    taken=(),
):
    candidates = []

    for y in range(2, MAP_ROWS - 2):
        for x in range(2, MAP_COLS - 2):
            if world[y][x] not in allowed:
                continue

            if any(
                math.hypot(x - tx, y - ty) < min_distance
                for tx, ty in taken
            ):
                continue

            distance = math.hypot(
                x - target_x,
                y - target_y,
            )
            candidates.append((distance, x, y))

    if not candidates:
        return None

    _, x, y = min(candidates)
    return x, y


def make_river(
    world,
    elevations,
    start_x,
    start_y,
    river_tiles,
):
    x, y = start_x, start_y
    visited = set()

    for _ in range(75):
        if not (1 <= x < MAP_COLS - 1 and 1 <= y < MAP_ROWS - 1):
            break

        if world[y][x] in WATER_TYPES:
            break

        if (x, y) in visited:
            break

        visited.add((x, y))
        river_tiles.add((x, y))

        neighbors = [
            (x + dx, y + dy)
            for dx, dy in (
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
            )
        ]

        neighbors.sort(
            key=lambda point: (
                0
                if world[point[1]][point[0]] in WATER_TYPES
                else 1,
                elevations[point[1]][point[0]]
                + hash_noise(
                    point[0],
                    point[1],
                    SEED + 900,
                ) * 0.025,
            )
        )

        next_point = next(
            (
                point
                for point in neighbors
                if point not in visited
            ),
            None,
        )

        if next_point is None:
            break

        x, y = next_point


def make_road(world, start, end):
    """Строит маршрут между поселениями в обход воды."""

    costs = {
        "plain": 1.0,
        "coast": 1.2,
        "forest": 1.6,
        "deep_forest": 2.2,
        "hills": 2.2,
        "marsh": 3.6,
        "mountain": 8.0,
        "snow": 11.0,
        "city": 1.0,
        "village": 1.0,
    }

    # В куче храним оценку и фактическую стоимость пути.
    queue = [(0.0, 0.0, start)]
    previous = {}
    best_cost = {start: 0.0}

    while queue:
        _, current_cost, current = heapq.heappop(queue)

        if current_cost > best_cost.get(
            current,
            float("inf"),
        ):
            continue

        if current == end:
            break

        x, y = current

        for dx, dy in (
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ):
            nx = x + dx
            ny = y + dy

            if not (
                0 <= nx < MAP_COLS
                and 0 <= ny < MAP_ROWS
            ):
                continue

            kind = world[ny][nx]

            if kind in WATER_TYPES:
                continue

            neighbor = (nx, ny)
            candidate = current_cost + costs.get(
                kind,
                1000.0,
            )

            if candidate < best_cost.get(
                neighbor,
                float("inf"),
            ):
                best_cost[neighbor] = candidate
                previous[neighbor] = current

                heuristic = (
                    abs(end[0] - nx)
                    + abs(end[1] - ny)
                ) * 0.8

                heapq.heappush(
                    queue,
                    (
                        candidate + heuristic,
                        candidate,
                        neighbor,
                    ),
                )

    if end not in previous and start != end:
        return []

    result = [end]
    current = end

    while current != start:
        current = previous[current]
        result.append(current)

    result.reverse()
    return result


def create_game_world():
    world, elevations = make_world()

    settlements = {}
    used_positions = []

    city_plans = [
        ("Златоград", 29, 23),
        ("Тихая Гавань", 16, 17),
        ("Каменгард", 39, 13),
        ("Серебряный Брод", 46, 29),
        ("Южный Предел", 31, 35),
    ]

    for name, target_x, target_y in city_plans:
        position = find_place(
            world,
            target_x,
            target_y,
            {"plain", "forest", "coast", "hills"},
            min_distance=9,
            taken=used_positions,
        )

        if position is not None:
            settlements[position] = name
            used_positions.append(position)
            world[position[1]][position[0]] = "city"

    village_plans = [
        ("Лесной Дол", 23, 13),
        ("Старый Тракт", 19, 29),
        ("Вереск", 43, 22),
        ("Белый Камень", 35, 31),
    ]

    for name, target_x, target_y in village_plans:
        position = find_place(
            world,
            target_x,
            target_y,
            {"plain", "forest", "coast", "hills"},
            min_distance=5,
            taken=used_positions,
        )

        if position is not None:
            settlements[position] = name
            used_positions.append(position)
            world[position[1]][position[0]] = "village"

    river_tiles = set()

    for target_x, target_y in (
        (38, 12),
        (33, 19),
        (44, 20),
        (29, 28),
    ):
        source = find_place(
            world,
            target_x,
            target_y,
            MOUNTAIN_TYPES | {"hills"},
        )

        if source is not None:
            make_river(
                world,
                elevations,
                source[0],
                source[1],
                river_tiles,
            )

    road_tiles = set()

    cities = [
        position
        for position in settlements
        if world[position[1]][position[0]] == "city"
    ]

    if cities:
        connected = [cities[0]]
        remaining = cities[1:]

        while remaining:
            start, end = min(
                (
                    (connected_city, city)
                    for connected_city in connected
                    for city in remaining
                ),
                key=lambda pair: math.dist(
                    pair[0],
                    pair[1],
                ),
            )

            road_tiles.update(
                make_road(world, start, end)
            )
            connected.append(end)
            remaining.remove(end)

        for position in settlements:
            if position in cities:
                continue

            closest_city = min(
                cities,
                key=lambda city: math.dist(
                    position,
                    city,
                ),
            )

            road_tiles.update(
                make_road(
                    world,
                    position,
                    closest_city,
                )
            )

    spawn = next(
        (
            position
            for position, name in settlements.items()
            if name == "Южный Предел"
        ),
        None,
    )
    if spawn is None:
        raise RuntimeError(
            "Не удалось создать город «Южный Предел»"
        )

    player_x, player_y = spawn

    return (
        world,
        settlements,
        river_tiles,
        road_tiles,
        player_x,
        player_y,
    )