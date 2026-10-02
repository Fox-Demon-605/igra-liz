from collections import deque
import tkinter as tk

from .config import (
    CELL_SIZE,
    COLORS,
    MAP_COLS,
    MAP_ROWS,
    TERRAIN,
    VIEW_HEIGHT,
    VIEW_WIDTH,
    WATER_TYPES,
)
from .rendering import MapRenderer
from .world import create_game_world


def run():
    (
        world,
        settlements,
        river_tiles,
        road_tiles,
        player_x,
        player_y,
    ) = create_game_world()

    root = tk.Tk()
    root.title("Хроники пограничья — карта мира")
    root.configure(bg=COLORS["background"])
    root.geometry("1260x790")
    root.minsize(870, 560)

    header = tk.Frame(
        root,
        bg=COLORS["background"],
    )
    header.pack(
        fill=tk.X,
        padx=16,
        pady=(14, 10),
    )

    tk.Label(
        header,
        text="ХРОНИКИ ПОГРАНИЧЬЯ",
        bg=COLORS["background"],
        fg=COLORS["gold"],
        font=("Georgia", 21, "bold"),
    ).pack(anchor="w")

    tk.Label(
        header,
        text=(
            "ЛКМ — идти к клетке  •  "
            "ПКМ + движение — перемещать карту  •  "
            "Колёсико — масштаб"
        ),
        bg=COLORS["background"],
        fg=COLORS["muted"],
        font=("Arial", 10),
    ).pack(anchor="w", pady=(3, 0))

    main = tk.Frame(
        root,
        bg=COLORS["background"],
    )
    main.pack(
        fill=tk.BOTH,
        expand=True,
        padx=16,
        pady=(0, 16),
    )

    map_panel = tk.Frame(
        main,
        bg=COLORS["panel"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
    )
    map_panel.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True,
    )

    canvas = tk.Canvas(
        map_panel,
        width=VIEW_WIDTH,
        height=VIEW_HEIGHT,
        bg=COLORS["background"],
        highlightthickness=0,
        cursor="hand2",
    )

    vertical_scrollbar = tk.Scrollbar(
        map_panel,
        orient=tk.VERTICAL,
        command=canvas.yview,
    )
    horizontal_scrollbar = tk.Scrollbar(
        map_panel,
        orient=tk.HORIZONTAL,
        command=canvas.xview,
    )

    canvas.configure(
        xscrollcommand=horizontal_scrollbar.set,
        yscrollcommand=vertical_scrollbar.set,
        scrollregion=(
            0,
            0,
            MAP_COLS * CELL_SIZE,
            MAP_ROWS * CELL_SIZE,
        ),
    )

    map_panel.grid_rowconfigure(0, weight=1)
    map_panel.grid_columnconfigure(0, weight=1)

    canvas.grid(
        row=0,
        column=0,
        sticky="nsew",
    )
    vertical_scrollbar.grid(
        row=0,
        column=1,
        sticky="ns",
    )
    horizontal_scrollbar.grid(
        row=1,
        column=0,
        sticky="ew",
    )

    sidebar = tk.Frame(
        main,
        width=270,
        bg=COLORS["panel"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
    )
    sidebar.pack(
        side=tk.LEFT,
        fill=tk.Y,
        padx=(12, 0),
    )
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="АТЛАС МИРА",
        bg=COLORS["panel"],
        fg=COLORS["gold"],
        font=("Georgia", 15, "bold"),
    ).pack(
        anchor="w",
        padx=14,
        pady=(16, 5),
    )

    location_label = tk.Label(
        sidebar,
        text="",
        bg=COLORS["panel"],
        fg=COLORS["text"],
        font=("Arial", 11, "bold"),
        justify=tk.LEFT,
        wraplength=235,
    )
    location_label.pack(
        anchor="w",
        padx=14,
        pady=(4, 2),
    )

    coordinates_label = tk.Label(
        sidebar,
        text="",
        bg=COLORS["panel"],
        fg=COLORS["muted"],
        font=("Arial", 10),
    )
    coordinates_label.pack(
        anchor="w",
        padx=14,
        pady=(0, 14),
    )

    tk.Frame(
        sidebar,
        bg=COLORS["border"],
        height=1,
    ).pack(
        fill=tk.X,
        padx=14,
    )

    tk.Label(
        sidebar,
        text="УСЛОВНЫЕ ОБОЗНАЧЕНИЯ",
        bg=COLORS["panel"],
        fg=COLORS["gold"],
        font=("Arial", 10, "bold"),
    ).pack(
        anchor="w",
        padx=14,
        pady=(14, 7),
    )

    legend = [
        ("#255878", "≈  море"),
        ("#BCA877", "·  побережье"),
        ("#71845A", "·  равнина"),
        ("#345F4F", "♠  лес"),
        ("#777B7C", "▲  горы"),
        ("#8C665B", "◆  город"),
        ("#8F7959", "◇  деревня"),
    ]

    for color, label in legend:
        line = tk.Frame(
            sidebar,
            bg=COLORS["panel"],
        )
        line.pack(
            anchor="w",
            padx=14,
            pady=2,
        )

        tk.Label(
            line,
            text="  ",
            bg=color,
            width=2,
        ).pack(side=tk.LEFT)

        tk.Label(
            line,
            text=label,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Arial", 10),
        ).pack(
            side=tk.LEFT,
            padx=(9, 0),
        )

    tk.Frame(
        sidebar,
        bg=COLORS["border"],
        height=1,
    ).pack(
        fill=tk.X,
        padx=14,
        pady=(14, 0),
    )

    tk.Label(
        sidebar,
        text="ЖУРНАЛ ПУТЕШЕСТВИЯ",
        bg=COLORS["panel"],
        fg=COLORS["gold"],
        font=("Arial", 10, "bold"),
    ).pack(
        anchor="w",
        padx=14,
        pady=(14, 7),
    )

    log_text = tk.Text(
        sidebar,
        bg=COLORS["panel"],
        fg=COLORS["text"],
        font=("Arial", 10),
        wrap="word",
        relief="flat",
        state="disabled",
    )
    log_text.pack(
        fill=tk.BOTH,
        expand=True,
        padx=12,
        pady=(0, 12),
    )
    log_text.tag_configure(
        "entry",
        spacing3=10,
    )

    renderer = MapRenderer(
        canvas,
        world,
        settlements,
        river_tiles,
        road_tiles,
    )

    def add_log(message):
        log_text.configure(state="normal")
        log_text.insert(
            tk.END,
            f"• {message}\n",
            "entry",
        )
        log_text.configure(state="disabled")
        log_text.see(tk.END)

    def update_location():
        kind = world[player_y][player_x]
        position = (player_x, player_y)

        if position in settlements:
            text = (
                f"{settlements[position]} — "
                f"{TERRAIN[kind]['name']}"
            )
        else:
            text = TERRAIN[kind]["name"]

        if position in river_tiles:
            text += "\nРядом протекает река"

        location_label.configure(text=text)
        coordinates_label.configure(
            text=f"Координаты: {player_x}, {player_y}"
        )

        # Размер клетки, которым пользуются существующие методы отрисовки.
    # Масштабируем уже нарисованный Canvas, поэтому размеры мира
    # в координатах Canvas тоже меняются.
    zoom = 1.0
    zoom_min = 0.5
    zoom_max = 2.0
    zoom_step = 1.1

    movement_after_id = None
    movement_path = deque()
    movement_delay_ms = 110

    def update_scrollregion():
        canvas.configure(
            scrollregion=(
                0,
                0,
                MAP_COLS * CELL_SIZE * zoom,
                MAP_ROWS * CELL_SIZE * zoom,
            )
        )

    def center_on_player():
        root.update_idletasks()

        world_width = MAP_COLS * CELL_SIZE * zoom
        world_height = MAP_ROWS * CELL_SIZE * zoom
        player_center_x = (player_x + 0.5) * CELL_SIZE * zoom
        player_center_y = (player_y + 0.5) * CELL_SIZE * zoom

        if world_width > canvas.winfo_width():
            left = player_center_x - canvas.winfo_width() / 2
            canvas.xview_moveto(
                max(
                    0.0,
                    min(
                        1.0,
                        left / world_width,
                    ),
                )
            )
        else:
            canvas.xview_moveto(0)

        if world_height > canvas.winfo_height():
            top = player_center_y - canvas.winfo_height() / 2
            canvas.yview_moveto(
                max(
                    0.0,
                    min(
                        1.0,
                        top / world_height,
                    ),
                )
            )
        else:
            canvas.yview_moveto(0)

    def find_path(start, goal):
        """Ищет путь по соседним клеткам в обход моря."""
        queue = deque([start])
        previous = {start: None}

        while queue:
            x, y = queue.popleft()

            if (x, y) == goal:
                break

            for dx, dy in (
                (1, 0),
                (-1, 0),
                (0, 1),
                (0, -1),
            ):
                nx = x + dx
                ny = y + dy
                neighbor = (nx, ny)

                if not (
                    0 <= nx < MAP_COLS
                    and 0 <= ny < MAP_ROWS
                ):
                    continue
                if neighbor in previous:
                    continue
                if world[ny][nx] in WATER_TYPES:
                    continue

                previous[neighbor] = (x, y)
                queue.append(neighbor)

        if goal not in previous:
            return []

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = previous[current]

        path.reverse()
        return path

    def move_one_cell():
        nonlocal player_x, player_y, movement_after_id

        movement_after_id = None
        if not movement_path:
            return

        player_x, player_y = movement_path.popleft()

        # Не вызываем draw_map(): меняется только маркер.
        renderer.draw_player(player_x, player_y)
        update_location()

        position = (player_x, player_y)
        if position in settlements:
            add_log(f"Вы прибыли в {settlements[position]}.")

        if movement_path:
            movement_after_id = root.after(
                movement_delay_ms,
                move_one_cell,
            )
        else:
            kind = world[player_y][player_x]
            if position not in settlements:
                add_log(
                    f"Прибыли на клетку "
                    f"({player_x}, {player_y}): "
                    f"{TERRAIN[kind]['name'].lower()}."
                )

    def on_click(event):
        nonlocal movement_after_id, movement_path

        cell_size = CELL_SIZE * zoom
        x = int(canvas.canvasx(event.x) // cell_size)
        y = int(canvas.canvasy(event.y) // cell_size)

        if not (
            0 <= x < MAP_COLS
            and 0 <= y < MAP_ROWS
        ):
            return

        if world[y][x] in WATER_TYPES:
            add_log(
                "Здесь море. Пока без корабля не пройти."
            )
            return

        if (x, y) == (player_x, player_y):
            return

        path = find_path(
            (player_x, player_y),
            (x, y),
        )
        if not path:
            add_log("До этой клетки нет сухопутного пути.")
            return

        # Новый клик заменяет прежний маршрут.
        if movement_after_id is not None:
            root.after_cancel(movement_after_id)
            movement_after_id = None

        movement_path = deque(path)
        add_log(
            f"Отправляемся к клетке ({x}, {y}). "
            f"Шагов: {len(path)}."
        )
        move_one_cell()

    def zoom_at(event, direction):
        nonlocal zoom

        factor = (
            zoom_step
            if direction > 0
            else 1 / zoom_step
        )
        new_zoom = max(
            zoom_min,
            min(zoom_max, zoom * factor),
        )

        if abs(new_zoom - zoom) < 1e-9:
            return "break"

        # Сохраняем точку под указателем мыши на том же
        # месте экрана после изменения масштаба.
        old_x = canvas.canvasx(event.x)
        old_y = canvas.canvasy(event.y)
        actual_factor = new_zoom / zoom

        canvas.scale(
            "all",
            0,
            0,
            actual_factor,
            actual_factor,
        )
        zoom = new_zoom
        update_scrollregion()
        root.update_idletasks()

        new_x = old_x * actual_factor
        new_y = old_y * actual_factor

        world_width = MAP_COLS * CELL_SIZE * zoom
        world_height = MAP_ROWS * CELL_SIZE * zoom

        if world_width > canvas.winfo_width():
            desired_left = new_x - event.x
            canvas.xview_moveto(
                max(
                    0.0,
                    min(
                        1.0,
                        desired_left / world_width,
                    ),
                )
            )

        if world_height > canvas.winfo_height():
            desired_top = new_y - event.y
            canvas.yview_moveto(
                max(
                    0.0,
                    min(
                        1.0,
                        desired_top / world_height,
                    ),
                )
            )

        return "break"

    def on_mouse_wheel(event):
        if event.delta == 0:
            return "break"

        direction = 1 if event.delta > 0 else -1
        return zoom_at(event, direction)

    def on_linux_mouse_wheel(event):
        direction = 1 if event.num == 4 else -1
        return zoom_at(event, direction)

    def on_pan_start(event):
        canvas.configure(cursor="fleur")
        canvas.scan_mark(event.x, event.y)

    def on_pan_drag(event):
        canvas.scan_dragto(
            event.x,
            event.y,
            gain=1,
        )

    def on_pan_end(_event):
        canvas.configure(cursor="hand2")

    canvas.bind("<Button-1>", on_click)
    canvas.bind("<ButtonPress-3>", on_pan_start)
    canvas.bind("<B3-Motion>", on_pan_drag)
    canvas.bind("<ButtonRelease-3>", on_pan_end)
    canvas.bind("<MouseWheel>", on_mouse_wheel)
    canvas.bind("<Button-4>", on_linux_mouse_wheel)
    canvas.bind("<Button-5>", on_linux_mouse_wheel)

    renderer.draw_map(player_x, player_y)
    update_location()
    add_log(
        "Путешествие начинается в городе "
        "Южный Предел."
    )

    center_on_player()
    root.mainloop()