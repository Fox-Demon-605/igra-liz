import random
import tkinter as tk

from .config import (
    CELL_SIZE,
    COLORS,
    MAP_COLS,
    MAP_ROWS,
    MOUNTAIN_TYPES,
    SEED,
    TERRAIN,
    WATER_TYPES,
)


class MapRenderer:
    def __init__(
        self,
        canvas,
        world,
        settlements,
        river_tiles,
        road_tiles,
    ):
        self.canvas = canvas
        self.world = world
        self.settlements = settlements
        self.river_tiles = river_tiles
        self.road_tiles = road_tiles

    def draw_tree(self, cx, cy, color, size=12):
        self.canvas.create_polygon(
            cx,
            cy - size,
            cx - size * 0.65,
            cy + size * 0.35,
            cx + size * 0.65,
            cy + size * 0.35,
            fill=color,
            outline="",
        )

        self.canvas.create_line(
            cx,
            cy + size * 0.2,
            cx,
            cy + size * 0.7,
            fill="#273B33",
            width=2,
        )

    def draw_tile(self, x, y):
        kind = self.world[y][x]
        tile = TERRAIN[kind]

        left = x * CELL_SIZE
        top = y * CELL_SIZE
        center_x = left + CELL_SIZE / 2
        center_y = top + CELL_SIZE / 2

        randomizer = random.Random(
            (
                x * 928371
                + y * 689287
                + SEED
            ) & 0xFFFFFFFF
        )

        self.canvas.create_rectangle(
            left,
            top,
            left + CELL_SIZE,
            top + CELL_SIZE,
            fill=tile["base"],
            outline="#25313A",
            width=1,
        )

        if kind in WATER_TYPES:
            for _ in range(2):
                wave_x = left + randomizer.randint(7, 32)
                wave_y = top + randomizer.randint(11, 35)

                self.canvas.create_arc(
                    wave_x,
                    wave_y,
                    wave_x + 13,
                    wave_y + 6,
                    start=190,
                    extent=150,
                    style=tk.ARC,
                    outline=tile["detail"],
                    width=2,
                )

        elif kind == "coast":
            for _ in range(4):
                dot_x = left + randomizer.randint(6, 42)
                dot_y = top + randomizer.randint(6, 42)

                self.canvas.create_oval(
                    dot_x,
                    dot_y,
                    dot_x + 2,
                    dot_y + 2,
                    fill=tile["detail"],
                    outline="",
                )

        elif kind in {"plain", "hills"}:
            for _ in range(3):
                grass_x = left + randomizer.randint(7, 40)
                grass_y = top + randomizer.randint(9, 39)

                self.canvas.create_line(
                    grass_x - 2,
                    grass_y + 3,
                    grass_x,
                    grass_y - 2,
                    grass_x + 2,
                    grass_y + 3,
                    smooth=True,
                    fill=tile["detail"],
                    width=1,
                )

            if kind == "hills":
                self.canvas.create_arc(
                    left + 7,
                    top + 16,
                    left + 39,
                    top + 42,
                    start=25,
                    extent=135,
                    style=tk.ARC,
                    outline=tile["detail"],
                    width=3,
                )

        elif kind in {"forest", "deep_forest"}:
            for offset_x, offset_y, size in (
                (-10, 3, 9),
                (8, -7, 12),
                (12, 12, 8),
            ):
                self.draw_tree(
                    center_x + offset_x,
                    center_y + offset_y,
                    tile["detail"],
                    size,
                )

        elif kind in MOUNTAIN_TYPES:
            self.canvas.create_polygon(
                left + 5,
                top + 40,
                left + 25,
                top + 8,
                left + 44,
                top + 40,
                fill=tile["detail"],
                outline="#48545B",
                width=1,
            )

            self.canvas.create_polygon(
                left + 19,
                top + 18,
                left + 25,
                top + 8,
                left + 31,
                top + 19,
                left + 25,
                top + 16,
                fill=(
                    "#F0F0E5"
                    if kind == "snow"
                    else "#D7D2C5"
                ),
                outline="",
            )

        elif kind == "marsh":
            for offset_x, offset_y in (
                (-10, -4),
                (9, 9),
            ):
                self.canvas.create_arc(
                    center_x + offset_x - 7,
                    center_y + offset_y - 2,
                    center_x + offset_x + 7,
                    center_y + offset_y + 7,
                    start=190,
                    extent=145,
                    style=tk.ARC,
                    outline=tile["detail"],
                    width=2,
                )

    def draw_roads(self):
        for x, y in self.road_tiles:
            if self.world[y][x] in WATER_TYPES:
                continue

            cx = x * CELL_SIZE + CELL_SIZE / 2
            cy = y * CELL_SIZE + CELL_SIZE / 2

            for dx, dy in ((1, 0), (0, 1)):
                if (x + dx, y + dy) not in self.road_tiles:
                    continue

                other_x = (
                    (x + dx) * CELL_SIZE
                    + CELL_SIZE / 2
                )
                other_y = (
                    (y + dy) * CELL_SIZE
                    + CELL_SIZE / 2
                )

                self.canvas.create_line(
                    cx,
                    cy,
                    other_x,
                    other_y,
                    fill="#3A2D24",
                    width=6,
                )

                self.canvas.create_line(
                    cx,
                    cy,
                    other_x,
                    other_y,
                    fill="#D9B77D",
                    width=3,
                )

    def draw_rivers(self):
        for x, y in self.river_tiles:
            if self.world[y][x] in WATER_TYPES:
                continue

            cx = x * CELL_SIZE + CELL_SIZE / 2
            cy = y * CELL_SIZE + CELL_SIZE / 2

            neighbors = [
                (x + dx, y + dy)
                for dx, dy in (
                    (1, 0),
                    (-1, 0),
                    (0, 1),
                    (0, -1),
                )
                if (x + dx, y + dy) in self.river_tiles
                or (
                    0 <= x + dx < MAP_COLS
                    and 0 <= y + dy < MAP_ROWS
                    and self.world[y + dy][x + dx]
                    in WATER_TYPES
                )
            ]

            if not neighbors:
                self.canvas.create_oval(
                    cx - 4,
                    cy - 4,
                    cx + 4,
                    cy + 4,
                    fill="#70B8D5",
                    outline="",
                )

            for nx, ny in neighbors:
                other_x = (
                    nx * CELL_SIZE
                    + CELL_SIZE / 2
                )
                other_y = (
                    ny * CELL_SIZE
                    + CELL_SIZE / 2
                )

                self.canvas.create_line(
                    cx,
                    cy,
                    other_x,
                    other_y,
                    fill="#173F59",
                    width=9,
                )

                self.canvas.create_line(
                    cx,
                    cy,
                    other_x,
                    other_y,
                    fill="#6CB2D0",
                    width=5,
                )

    def draw_settlements(self, player_x, player_y):
        for (x, y), name in self.settlements.items():
            cx = x * CELL_SIZE + CELL_SIZE / 2
            cy = y * CELL_SIZE + CELL_SIZE / 2

            is_city = self.world[y][x] == "city"

            self.canvas.create_oval(
                cx - 17,
                cy - 17,
                cx + 17,
                cy + 17,
                fill="#26303B",
                outline=COLORS["gold"],
                width=2 if is_city else 1,
            )

            self.canvas.create_text(
                cx,
                cy - 1,
                text="◆" if is_city else "◇",
                font=(
                    "Arial",
                    21 if is_city else 17,
                    "bold",
                ),
                fill=COLORS["gold"],
            )

            if (
                abs(player_x - x) <= 5
                and abs(player_y - y) <= 4
            ):
                self.canvas.create_text(
                    cx,
                    cy - 28,
                    text=name,
                    font=("Arial", 9, "bold"),
                    fill="#FFF2D5",
                )

    def draw_player(self, player_x, player_y):
        cx = player_x * CELL_SIZE + CELL_SIZE / 2
        cy = player_y * CELL_SIZE + CELL_SIZE / 2

        self.canvas.create_oval(
            cx - 20,
            cy - 20,
            cx + 20,
            cy + 20,
            outline=COLORS["gold"],
            width=3,
        )

        self.canvas.create_oval(
            cx - 9,
            cy - 9,
            cx + 9,
            cy + 9,
            fill=COLORS["player"],
            outline="#3E2B20",
            width=2,
        )

    def draw_map(self, player_x, player_y):
        self.canvas.delete("all")

        for y in range(MAP_ROWS):
            for x in range(MAP_COLS):
                self.draw_tile(x, y)

        self.draw_roads()
        self.draw_rivers()
        self.draw_settlements(player_x, player_y)
        self.draw_player(player_x, player_y)