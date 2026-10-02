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
            "Исследуй материк  •  Клик — перемещение  •  "
            "Колёсико — прокрутка карты  •  "
            "Shift + колёсико — по горизонтали"
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

    def on_click(event):
        nonlocal player_x, player_y

        x = int(canvas.canvasx(event.x) // CELL_SIZE)
        y = int(canvas.canvasy(event.y) // CELL_SIZE)

        if not (0 <= x < MAP_COLS and 0 <= y < MAP_ROWS):
            return

        kind = world[y][x]

        if kind in WATER_TYPES:
            add_log(
                "Здесь море. Пока без корабля не пройти."
            )
            return

        if (x, y) == (player_x, player_y):
            return

        player_x = x
        player_y = y

        if (x, y) in settlements:
            add_log(
                f"Вы прибыли в {settlements[(x, y)]}."
            )
        else:
            add_log(
                f"Клетка ({x}, {y}): "
                f"{TERRAIN[kind]['name'].lower()}."
            )

        update_location()
        renderer.move_player(player_x, player_y)

    def on_mouse_wheel(event):
        if event.delta == 0:
            return "break"

        direction = -1 if event.delta > 0 else 1
        steps = max(1, abs(event.delta) // 120)

        if event.state & 0x0001:
            canvas.xview_scroll(
                direction * steps,
                "units",
            )
        else:
            canvas.yview_scroll(
                direction * steps,
                "units",
            )

        return "break"

    def on_linux_mouse_wheel(event):
        direction = -1 if event.num == 4 else 1

        if event.state & 0x0001:
            canvas.xview_scroll(
                direction,
                "units",
            )
        else:
            canvas.yview_scroll(
                direction,
                "units",
            )

        return "break"

    canvas.bind("<Button-1>", on_click)
    canvas.bind("<MouseWheel>", on_mouse_wheel)
    canvas.bind("<Button-4>", on_linux_mouse_wheel)
    canvas.bind("<Button-5>", on_linux_mouse_wheel)

    renderer.draw_map(player_x, player_y)
    update_location()
    add_log(
        "Путешествие начинается. "
        "Перед вами огромный материк."
    )

    root.update_idletasks()
    canvas.xview_moveto(0.28)
    canvas.yview_moveto(0.27)

    root.mainloop()