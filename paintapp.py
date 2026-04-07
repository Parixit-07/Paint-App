import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import Image, ImageDraw, ImageTk
import random


class PaintApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Paint App")
        self.CANVAS_W = 980
        self.CANVAS_H = 620
        self.root.geometry("1200x760")
        self.root.minsize(1000, 700)

        # colors
        self.pen_color = "black"
        self.fill_color = "red"

        self.pen_size = 3
        self.brush_size = 16
        self.eraser_size = 20
        self.spray_size = 20
        self.spray_density = 50
        self.tool = "pen"
        self.shape_options = ["Line", "Rectangle", "Circle", "Triangle", "Diamond"]
        self.selected_shape = tk.StringVar(value=self.shape_options[0])

        self.active_button = None

        self.start_x = 0
        self.start_y = 0
        self.prev_x = 0
        self.prev_y = 0

        self.preview = None

        # undo / redo stacks
        self.undo_stack = []
        self.redo_stack = []
        self.current_action = []

        # ── Parallel PIL image (same size as canvas) ──────────────────────────
        # Every stroke / shape / fill is mirrored here so flood-fill works
        # without Ghostscript.
        self.pil_image = Image.new("RGB", (self.CANVAS_W, self.CANVAS_H), "white")
        self.pil_draw  = ImageDraw.Draw(self.pil_image)

        # ===== UI =====

        self.root.configure(bg="#f0f2f5")
        main_frame = tk.Frame(root, bg="#f0f2f5")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header Section
        header = tk.Frame(main_frame, bg="#f0f2f5")
        header.pack(fill="x", pady=(0, 12))
        tk.Label(header, text="🎨 Paint Application", bg="#f0f2f5", fg="#1c1e21",
                 font=("Segoe UI", 20, "bold")).pack(side="left")
        tk.Label(header, text="Draw using pen, brush, spray, shapes, fill, undo/redo and save.",
                 bg="#f0f2f5", fg="#65676b", font=("Segoe UI", 10)).pack(side="left", padx=16, pady=6)

        workspace = tk.Frame(main_frame, bg="#f0f2f5")
        workspace.pack(fill="both", expand=True)

        # Left Sidebar
        controls_frame = tk.Frame(workspace, bg="#ffffff", bd=2, relief=tk.GROOVE)
        controls_frame.pack(side="left", fill="y", padx=(0, 12), pady=0)
        controls_frame.pack_propagate(False)
        controls_frame.configure(width=340, height=650)

        # Make sidebar scrollable
        controls_canvas = tk.Canvas(controls_frame, bg="#ffffff", highlightthickness=0, height=650)
        controls_scrollbar = tk.Scrollbar(
            controls_frame,
            orient="vertical",
            command=controls_canvas.yview,
            bg="#ffffff",
            troughcolor="#ffffff",
            activebackground="#d9dde3",
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            width=12,
        )
        controls_canvas.configure(yscrollcommand=controls_scrollbar.set)
        controls_inner = tk.Frame(controls_canvas, bg="#ffffff")
        controls_canvas.create_window((0, 0), window=controls_inner, anchor="nw")
        def _configure_controls_canvas(event):
            controls_canvas.configure(scrollregion=(0, 0, controls_inner.winfo_reqwidth(), controls_inner.winfo_reqheight()))
        controls_inner.bind("<Configure>", _configure_controls_canvas)
        controls_canvas.pack(side="left", fill="both", expand=True)
        controls_scrollbar.pack(side="right", fill="y")

        def _on_controls_scrollbar_enter(event):
            controls_scrollbar.config(bg="#e4e6ea")
        def _on_controls_scrollbar_leave(event):
            controls_scrollbar.config(bg="#ffffff")

        controls_scrollbar.bind("<Enter>", _on_controls_scrollbar_enter)
        controls_scrollbar.bind("<Leave>", _on_controls_scrollbar_leave)

        self.controls_canvas = controls_canvas
        self.controls_scrollbar = controls_scrollbar
        self.controls_inner = controls_inner
        self.root.bind_all("<MouseWheel>", self._on_controls_mousewheel)
        self.root.bind_all("<Button-4>", lambda e: self.controls_canvas.yview_scroll(-1, "units"))
        self.root.bind_all("<Button-5>", lambda e: self.controls_canvas.yview_scroll(1, "units"))
        self.root.bind_all("<Control-z>", lambda e: self.undo())
        self.root.bind_all("<Control-Z>", lambda e: self.undo())
        self.root.bind_all("<Control-y>", lambda e: self.redo())
        self.root.bind_all("<Control-Y>", lambda e: self.redo())

        canvas_frame = tk.Frame(workspace, bg="#f0f2f5")
        canvas_frame.pack(side="left", fill="both", expand=True)

        self.button_style = {"padx": 14, "pady": 10, "bd": 0, "relief": tk.FLAT,
                             "bg": "#f0f2f5", "activebackground": "#e4e6ea",
                             "fg": "#1c1e21", "activeforeground": "#1c1e21", "cursor": "hand2",
                             "font": ("Segoe UI", 10, "bold")}

        self.selected_button_style = {"padx": 14, "pady": 10, "bd": 0, "relief": tk.FLAT,
                                      "bg": "#1877f2", "fg": "#ffffff", "activebackground": "#166fe5",
                                      "activeforeground": "#ffffff", "cursor": "hand2",
                                      "font": ("Segoe UI", 10, "bold")}

        # Drawing Tools Section
        drawing_frame = tk.LabelFrame(controls_inner, text="Drawing Tools", bg="#ffffff", fg="#1c1e21", labelanchor="n",
                                      bd=1, relief=tk.SOLID, padx=14, pady=14)
        drawing_frame.pack(fill="x", padx=14, pady=10)
        self.pen_btn = tk.Button(drawing_frame, text="✏️ Pen", command=self.use_pen, **self.button_style)
        self.pen_btn.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        self.brush_btn = tk.Button(drawing_frame, text="🖌️ Brush", command=self.use_brush, **self.button_style)
        self.brush_btn.grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        self.spray_btn = tk.Button(drawing_frame, text="💨 Spray", command=self.use_spray, **self.button_style)
        self.spray_btn.grid(row=1, column=0, sticky="ew", padx=6, pady=6)
        self.eraser_btn = tk.Button(drawing_frame, text="🧽 Eraser", command=self.use_eraser, **self.button_style)
        self.eraser_btn.grid(row=1, column=1, sticky="ew", padx=6, pady=6)
        self.shape_btn = tk.Button(drawing_frame, text="🔷 Shape", command=self.use_shape, **self.button_style)
        self.shape_btn.grid(row=2, column=0, sticky="ew", padx=6, pady=6)
        tk.Button(drawing_frame, text="🎨 Color", command=self.choose_pen_color, **self.button_style).grid(row=2, column=1, sticky="ew", padx=6, pady=6)
        self.pen_color_preview = tk.Label(drawing_frame, width=6, height=1, bg=self.pen_color, relief=tk.RAISED, bd=1)
        self.pen_color_preview.grid(row=3, column=0, columnspan=2, pady=(12, 0))
        drawing_frame.columnconfigure(0, weight=1)
        drawing_frame.columnconfigure(1, weight=1)

        # Fill Tool Section
        fill_frame = tk.LabelFrame(controls_inner, text="Fill Tool", bg="#ffffff", fg="#1c1e21", labelanchor="n",
                                   bd=1, relief=tk.SOLID, padx=14, pady=14)
        fill_frame.pack(fill="x", padx=14, pady=10)
        tk.Button(fill_frame, text="🪣 Fill", command=self.use_fill, **self.button_style).grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        tk.Button(fill_frame, text="🎨 Color", command=self.choose_fill_color, **self.button_style).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        self.fill_color_preview = tk.Label(fill_frame, width=6, height=1, bg=self.fill_color, relief=tk.RAISED, bd=1)
        self.fill_color_preview.grid(row=1, column=0, columnspan=2, pady=(12, 0))
        fill_frame.columnconfigure(0, weight=1)
        fill_frame.columnconfigure(1, weight=1)

        # Shapes Section
        shape_frame = tk.LabelFrame(controls_inner, text="Shapes", bg="#ffffff", fg="#1c1e21", labelanchor="n",
                                    bd=1, relief=tk.SOLID, padx=14, pady=14)
        shape_frame.pack(fill="x", padx=14, pady=10)
        tk.Label(shape_frame, text="Select shape", bg="#ffffff", fg="#1c1e21",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        self.shape_menu = tk.OptionMenu(shape_frame, self.selected_shape, *self.shape_options)
        self.shape_menu.config(bg="#f0f2f5", fg="#1c1e21", activebackground="#e4e6ea",
                               font=("Segoe UI", 10), bd=1, relief=tk.RAISED, highlightthickness=0)
        self.shape_menu.pack(fill="x", padx=6, pady=(0, 12))
        # Color Palette Section
        palette_frame = tk.LabelFrame(controls_inner, text="Color Palette", bg="#ffffff", fg="#1c1e21", labelanchor="n",
                                      bd=1, relief=tk.SOLID, padx=14, pady=14)
        palette_frame.pack(fill="x", padx=14, pady=10)
        colors = ["#000000", "#ffffff", "#ff0000", "#0000ff", "#00ff00", "#ffff00", "#ff8000", "#8000ff", "#ff00ff", "#800000", "#808080",
                  "#00ffff", "#ff0080", "#80ff00", "#0080ff", "#800080", "#808000", "#c0c0c0"]
        for i, color in enumerate(colors):
            btn = tk.Button(palette_frame, bg=color, width=4, height=1, bd=1, relief=tk.RAISED, cursor="hand2",
                            command=lambda c=color: self.set_pen_color(c))
            btn.grid(row=i//6, column=i%6, padx=3, pady=3)
        tk.Button(palette_frame, text="🎨 Custom", command=self.choose_pen_color, **self.button_style).grid(row=3, column=0, columnspan=6, sticky="ew", pady=(12, 0))

        # Actions Section
        other_frame = tk.LabelFrame(controls_inner, text="Actions", bg="#ffffff", fg="#1c1e21", labelanchor="n",
                                    bd=1, relief=tk.SOLID, padx=14, pady=14)
        other_frame.pack(fill="x", padx=14, pady=10)
        tk.Button(other_frame, text="↶ Undo",  command=self.undo, **self.button_style).grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        tk.Button(other_frame, text="↷ Redo",  command=self.redo, **self.button_style).grid(row=0, column=1, sticky="ew", padx=6, pady=6)
        tk.Button(other_frame, text="🗑️ Clear", command=self.clear, **self.button_style).grid(row=1, column=0, sticky="ew", padx=6, pady=6)
        tk.Button(other_frame, text="💾 Save",  command=self.save, **self.button_style).grid(row=1, column=1, sticky="ew", padx=6, pady=6)
        other_frame.columnconfigure(0, weight=1)
        other_frame.columnconfigure(1, weight=1)

        # Size Controls Section
        size_frame = tk.LabelFrame(controls_inner, text="Size Controls", bg="#ffffff", fg="#1c1e21", labelanchor="n",
                                   bd=1, relief=tk.SOLID, padx=14, pady=14)
        size_frame.pack(fill="x", padx=14, pady=10)

        tk.Label(size_frame, text="Pen Size", bg="#ffffff", fg="#1c1e21",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        self.pen_slider = tk.Scale(size_frame, from_=1, to=20, orient="horizontal",
                                   command=self.change_pen_size, bg="#ffffff", bd=1, highlightthickness=0, fg="#1c1e21", troughcolor="#e4e6ea", showvalue=1,
                                   font=("Segoe UI", 9))
        self.pen_slider.set(self.pen_size)
        self.pen_slider.pack(fill="x", padx=6)

        tk.Label(size_frame, text="Brush Size", bg="#ffffff", fg="#1c1e21",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 8))
        self.brush_slider = tk.Scale(size_frame, from_=8, to=40, orient="horizontal",
                                     command=self.change_brush_size, bg="#ffffff", bd=1, highlightthickness=0, fg="#1c1e21", troughcolor="#e4e6ea", showvalue=1,
                                     font=("Segoe UI", 9))
        self.brush_slider.set(self.brush_size)
        self.brush_slider.pack(fill="x", padx=6)

        tk.Label(size_frame, text="Eraser Size", bg="#ffffff", fg="#1c1e21",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 8))
        self.eraser_slider = tk.Scale(size_frame, from_=5, to=40, orient="horizontal",
                                      command=self.change_eraser_size, bg="#ffffff", bd=1, highlightthickness=0, fg="#1c1e21", troughcolor="#e4e6ea", showvalue=1,
                                      font=("Segoe UI", 9))
        self.eraser_slider.set(self.eraser_size)
        self.eraser_slider.pack(fill="x", padx=6)

        tk.Label(size_frame, text="Spray Size", bg="#ffffff", fg="#1c1e21",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 8))
        self.spray_size_slider = tk.Scale(size_frame, from_=5, to=50, orient="horizontal",
                                          command=self.change_spray_size, bg="#ffffff", bd=1, highlightthickness=0, fg="#1c1e21", troughcolor="#e4e6ea", showvalue=1,
                                          font=("Segoe UI", 9))
        self.spray_size_slider.set(self.spray_size)
        self.spray_size_slider.pack(fill="x", padx=6)

        tk.Label(size_frame, text="Spray Density", bg="#ffffff", fg="#1c1e21",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(12, 8))
        self.spray_density_slider = tk.Scale(size_frame, from_=10, to=100, orient="horizontal",
                                             command=self.change_spray_density, bg="#ffffff", bd=1, highlightthickness=0, fg="#1c1e21", troughcolor="#e4e6ea", showvalue=1,
                                             font=("Segoe UI", 9))
        self.spray_density_slider.set(self.spray_density)
        self.spray_density_slider.pack(fill="x", padx=6)

        # Canvas Area
        canvas_border = tk.Frame(canvas_frame, bg="#e4e6ea", bd=3, relief=tk.RIDGE, padx=12, pady=12)
        canvas_border.pack(fill="both", expand=True, padx=14, pady=10)
        self.canvas = tk.Canvas(canvas_border, bg="white", width=self.CANVAS_W, height=self.CANVAS_H,
                                highlightthickness=0, bd=0, relief=tk.FLAT, cursor="crosshair")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.handle_canvas_resize)

        self.status = tk.Label(canvas_frame, text="Tool: Pen | Color: black | Size: 3", bg="#f0f2f5", fg="#1c1e21",
                               anchor="w", font=("Segoe UI", 10), bd=2, relief=tk.GROOVE)
        self.status.pack(side="bottom", fill="x", padx=14, pady=(0, 10))

        copyright_label = tk.Label(canvas_frame, text="© Made by Parixit, Megh, Vivek", bg="#f0f2f5", fg="#65676b",
                                   anchor="e", font=("Segoe UI", 8))
        copyright_label.pack(side="bottom", fill="x", padx=14, pady=(0, 4))

        self.canvas.bind("<Button-1>",       self.start_draw)
        self.canvas.bind("<B1-Motion>",      self.draw)
        self.canvas.bind("<ButtonRelease-1>",self.stop_draw)

        # Initialize active tool
        self.set_active_tool(self.pen_btn)

        # Force update scroll region after UI is built
        self.root.after(100, lambda: _configure_controls_canvas(None))

    # ───────────────────────────── tool selection ──────────────────────────────

    def use_pen(self):
        self.set_active_tool(self.pen_btn)
        self.tool = "pen"
        self.canvas.config(cursor="crosshair")
        self.update_status()

    def use_eraser(self):
        self.set_active_tool(self.eraser_btn)
        self.tool = "eraser"
        self.canvas.config(cursor="dotbox")
        self.update_status()

    def use_fill(self):
        self.tool = "fill"
        self.canvas.config(cursor="spraycan")
        self.update_status()

    def use_line(self):
        self.tool = "line"
        self.canvas.config(cursor="crosshair")
        self.update_status()

    def use_rect(self):
        self.tool = "rect"
        self.canvas.config(cursor="crosshair")
        self.update_status()

    def use_circle(self):
        self.tool = "circle"
        self.canvas.config(cursor="crosshair")
        self.update_status()

    def use_brush(self):
        self.set_active_tool(self.brush_btn)
        self.tool = "brush"
        self.canvas.config(cursor="pencil")
        self.update_status()

    def use_spray(self):
        self.set_active_tool(self.spray_btn)
        self.tool = "spray"
        self.canvas.config(cursor="spraycan")
        self.update_status()

    def use_shape(self):
        self.set_active_tool(self.shape_btn)
        self.tool = "shape"
        self.canvas.config(cursor="crosshair")
        self.update_status()

    def set_active_tool(self, button):
        if self.active_button:
            self.active_button.config(**self.button_style)
        self.active_button = button
        button.config(**self.selected_button_style)

    def update_status(self):
        tool_name = self.tool.capitalize()
        if self.tool in ("pen", "brush", "spray", "eraser"):
            size = getattr(self, f"{self.tool}_size")
            self.status.config(text=f"Tool: {tool_name} | Color: {self.pen_color} | Size: {size}")
        else:
            self.status.config(text=f"Tool: {tool_name}")

    def _on_controls_mousewheel(self, event):
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget is None:
            return
        
        # Check if widget is part of the controls panel by walking up the hierarchy
        current = widget
        while current:
            if current == self.controls_inner or current == self.controls_canvas or current == self.controls_scrollbar:
                self.controls_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                break
            try:
                current = current.master
            except:
                break

    # ───────────────────────── color helpers ───────────────────────────────────

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _tk_color_to_rgb(self, color):
        """Works for named colors ('black') and hex ('#ff0000')."""
        r, g, b = self.root.winfo_rgb(color)
        return (r >> 8, g >> 8, b >> 8)

    # ─────────────────── PIL mirror helpers ────────────────────────────────────

    def _pil_line(self, x0, y0, x1, y1, color, width):
        rgb = self._tk_color_to_rgb(color)
        self.pil_draw.line([(x0, y0), (x1, y1)], fill=rgb, width=width)

    def _pil_rectangle(self, x0, y0, x1, y1, color, width):
        rgb = self._tk_color_to_rgb(color)
        self.pil_draw.rectangle([(x0, y0), (x1, y1)], outline=rgb, width=width)

    def _pil_polygon(self, points, color, width):
        rgb = self._tk_color_to_rgb(color)
        self.pil_draw.line(points + [points[0]], fill=rgb, width=width)

    def _pil_ellipse(self, x0, y0, x1, y1, color, width, fill=False):
        rgb = self._tk_color_to_rgb(color)
        if fill or width == 0:
            self.pil_draw.ellipse([(x0, y0), (x1, y1)], outline=rgb, fill=rgb)
        else:
            self.pil_draw.ellipse([(x0, y0), (x1, y1)], outline=rgb, width=width)

    # ──────────────────────── undo / redo helpers ──────────────────────────────

    def _item_descriptor(self, item_id):
        """Snapshot a canvas item so it can be recreated later."""
        item_type = self.canvas.type(item_id)
        coords    = self.canvas.coords(item_id)
        config    = {}
        keys = {
            "line":      ("fill", "width", "smooth", "capstyle", "dash"),
            "rectangle": ("outline", "fill", "width", "dash"),
            "oval":      ("outline", "fill", "width", "dash"),
        }.get(item_type, ())
        for k in keys:
            try:
                config[k] = self.canvas.itemcget(item_id, k)
            except tk.TclError:
                pass
        return {"type": item_type, "coords": coords, "config": config}

    def _recreate_item(self, descriptor):
        """Re-draw a canvas item from its snapshot. Returns new item id."""
        t      = descriptor["type"]
        coords = descriptor["coords"]
        cfg    = {k: v for k, v in descriptor["config"].items() if v != ""}
        if t == "line":
            return self.canvas.create_line(*coords, **cfg)
        elif t == "rectangle":
            return self.canvas.create_rectangle(*coords, **cfg)
        elif t == "oval":
            return self.canvas.create_oval(*coords, **cfg)
        return None

    # ──────────────────────────── flood fill ───────────────────────────────────

    def _flood_fill(self, x, y):
        """
        Flood-fill directly on the parallel PIL image (no Ghostscript needed),
        then refresh the canvas from that image.
        Saves before/after snapshots for undo/redo.
        """
        pre_img = self.pil_image.copy()

        fill_rgb = self._tk_color_to_rgb(self.fill_color)
        ImageDraw.floodfill(self.pil_image, (x, y), fill_rgb, thresh=30)
        # Redraw so ImageDraw stays in sync
        self.pil_draw = ImageDraw.Draw(self.pil_image)

        post_img = self.pil_image.copy()

        self._render_pil_to_canvas()

        action = [("image_fill", pre_img, post_img)]
        self.undo_stack.append(action)
        self.redo_stack.clear()

    def _render_pil_to_canvas(self):
        """Blit the PIL image onto the tkinter canvas."""
        self.canvas.delete("all")
        photo = ImageTk.PhotoImage(self.pil_image)
        self._photo_ref = photo          # prevent GC
        self.canvas.create_image(0, 0, anchor="nw", image=photo)

    def _resize_pil_image(self, width, height):
        if width <= self.CANVAS_W and height <= self.CANVAS_H:
            return
        new_image = Image.new("RGB", (width, height), "white")
        new_image.paste(self.pil_image, (0, 0))
        self.pil_image = new_image
        self.pil_draw = ImageDraw.Draw(self.pil_image)
        self.CANVAS_W = width
        self.CANVAS_H = height

    def handle_canvas_resize(self, event):
        self._resize_pil_image(event.width, event.height)

    # ──────────────────────────── drawing ──────────────────────────────────────

    def start_draw(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.current_action = []

        if self.tool == "fill":
            self._flood_fill(event.x, event.y)
            return

        self.prev_x = event.x
        self.prev_y = event.y

    def draw(self, event):

        if self.tool in ("pen", "eraser", "brush"):
            color = "white" if self.tool == "eraser" else self.pen_color
            width = self.eraser_size if self.tool == "eraser" else self.brush_size if self.tool == "brush" else self.pen_size

            # Make brush different: no smooth, butt capstyle for brush
            if self.tool == "brush":
                smooth = False
                capstyle = tk.BUTT
            else:
                smooth = True
                capstyle = tk.ROUND

            line = self.canvas.create_line(
                self.prev_x, self.prev_y,
                event.x,    event.y,
                fill=color, width=width,
                smooth=smooth, capstyle=capstyle
            )
            self._pil_line(self.prev_x, self.prev_y,
                           event.x,    event.y,
                           color, width)

            self.current_action.append(
                ("create", self._item_descriptor(line), line)
            )
            self.prev_x = event.x
            self.prev_y = event.y

        elif self.tool == "spray":
            for _ in range(self.spray_density):
                x = event.x + random.randint(-self.spray_size, self.spray_size)
                y = event.y + random.randint(-self.spray_size, self.spray_size)
                if 0 <= x < self.CANVAS_W and 0 <= y < self.CANVAS_H:
                    dot = self.canvas.create_oval(x-1, y-1, x+1, y+1, fill=self.pen_color, outline="")
                    self._pil_ellipse(x-1, y-1, x+1, y+1, self.pen_color, 0, fill=True)
                    self.current_action.append(("create", self._item_descriptor(dot), dot))

        else:
            if self.preview:
                self.canvas.delete(self.preview)

            shape = self.selected_shape.get().lower() if self.tool == "shape" else self.tool
            if shape == "line":
                self.preview = self.canvas.create_line(
                    self.start_x, self.start_y, event.x, event.y,
                    dash=(3, 2), fill=self.pen_color)
            elif shape in ("rectangle", "rect"):
                self.preview = self.canvas.create_rectangle(
                    self.start_x, self.start_y, event.x, event.y,
                    dash=(3, 2), outline=self.pen_color)
            elif shape == "circle":
                self.preview = self.canvas.create_oval(
                    self.start_x, self.start_y, event.x, event.y,
                    dash=(3, 2), outline=self.pen_color)
            elif shape == "triangle":
                x0, y0 = self.start_x, self.start_y
                x1, y1 = event.x, event.y
                points = [( (x0 + x1) / 2, y0 ), (x0, y1), (x1, y1)]
                self.preview = self.canvas.create_polygon(
                    *sum(points, ()), dash=(3, 2), outline=self.pen_color,
                    fill="", smooth=False)
            elif shape == "diamond":
                x0, y0 = self.start_x, self.start_y
                x1, y1 = event.x, event.y
                points = [((x0 + x1) / 2, y0), (x1, (y0 + y1) / 2),
                          ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2)]
                self.preview = self.canvas.create_polygon(
                    *sum(points, ()), dash=(3, 2), outline=self.pen_color,
                    fill="", smooth=False)

    def stop_draw(self, event):

        if self.preview:
            self.canvas.delete(self.preview)
            self.preview = None

        obj = None

        shape = self.selected_shape.get().lower() if self.tool == "shape" else self.tool

        if shape == "line":
            size = self.brush_size if self.tool == "brush" else self.pen_size
            obj = self.canvas.create_line(
                self.start_x, self.start_y, event.x, event.y,
                fill=self.pen_color, width=size)
            self._pil_line(self.start_x, self.start_y,
                           event.x,     event.y,
                           self.pen_color, size)

        elif shape in ("rectangle", "rect"):
            obj = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline=self.pen_color, width=self.pen_size)
            self._pil_rectangle(self.start_x, self.start_y,
                                 event.x,     event.y,
                                 self.pen_color, self.pen_size)

        elif shape == "circle":
            obj = self.canvas.create_oval(
                self.start_x, self.start_y, event.x, event.y,
                outline=self.pen_color, width=self.pen_size)
            self._pil_ellipse(self.start_x, self.start_y,
                              event.x,     event.y,
                              self.pen_color, self.pen_size)

        elif shape == "triangle":
            x0, y0 = self.start_x, self.start_y
            x1, y1 = event.x, event.y
            points = [( (x0 + x1) / 2, y0 ), (x0, y1), (x1, y1)]
            obj = self.canvas.create_polygon(
                *sum(points, ()), outline=self.pen_color, fill="",
                width=self.pen_size)
            self._pil_polygon(points, self.pen_color, self.pen_size)

        elif shape == "diamond":
            x0, y0 = self.start_x, self.start_y
            x1, y1 = event.x, event.y
            points = [((x0 + x1) / 2, y0), (x1, (y0 + y1) / 2),
                      ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2)]
            obj = self.canvas.create_polygon(
                *sum(points, ()), outline=self.pen_color, fill="",
                width=self.pen_size)
            self._pil_polygon(points, self.pen_color, self.pen_size)

        if obj is not None:
            self.current_action.append(
                ("create", self._item_descriptor(obj), obj)
            )

        if self.current_action:
            self.undo_stack.append(self.current_action)
            self.redo_stack.clear()

        self.current_action = []

    # ──────────────────────────── undo ─────────────────────────────────────────

    def undo(self):
        if not self.undo_stack:
            return

        action    = self.undo_stack.pop()
        redo_action = []

        for step in action:

            if step[0] == "create":
                _, descriptor, item_id = step
                self.canvas.delete(item_id)
                redo_action.append(("redo_create", descriptor))

            elif step[0] == "image_fill":
                _, pre_img, post_img = step
                self.pil_image = pre_img.copy()
                self.pil_draw  = ImageDraw.Draw(self.pil_image)
                self._render_pil_to_canvas()
                redo_action.append(("redo_image_fill", pre_img, post_img))

        self.redo_stack.append(redo_action)

    # ──────────────────────────── redo ─────────────────────────────────────────

    def redo(self):
        if not self.redo_stack:
            return

        action      = self.redo_stack.pop()
        undo_action = []

        for step in action:

            if step[0] == "redo_create":
                _, descriptor = step
                new_id = self._recreate_item(descriptor)
                if new_id is not None:
                    undo_action.append(("create", descriptor, new_id))

            elif step[0] == "redo_image_fill":
                _, pre_img, post_img = step
                self.pil_image = post_img.copy()
                self.pil_draw  = ImageDraw.Draw(self.pil_image)
                self._render_pil_to_canvas()
                undo_action.append(("image_fill", pre_img, post_img))

        self.undo_stack.append(undo_action)

    # ──────────────────────────── other ────────────────────────────────────────

    def set_pen_color(self, color):
        self.pen_color = color
        self.pen_color_preview.config(bg=color)
        self.update_status()

    def choose_pen_color(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.pen_color = c
            self.pen_color_preview.config(bg=c)
            self.update_status()

    def choose_fill_color(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.fill_color = c
            self.fill_color_preview.config(bg=c)

    def change_pen_size(self, val):
        self.pen_size = int(val)
        self.update_status()

    def change_brush_size(self, val):
        self.brush_size = int(val)
        self.update_status()

    def change_eraser_size(self, val):
        self.eraser_size = int(val)
        self.update_status()

    def change_spray_size(self, val):
        self.spray_size = int(val)
        self.update_status()

    def change_spray_density(self, val):
        self.spray_density = int(val)
        self.update_status()

    def clear(self):
        self.canvas.delete("all")
        self.pil_image = Image.new("RGB", (self.CANVAS_W, self.CANVAS_H), "white")
        self.pil_draw  = ImageDraw.Draw(self.pil_image)
        self.undo_stack.clear()
        self.redo_stack.clear()

    def save(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png"),
                       ("JPEG image", "*.jpg"),
                       ("All files", "*.*")]
        )
        if file:
            self.pil_image.save(file)
            print("Saved to", file)


# ── run ────────────────────────────────────────────────────────────────────────
root = tk.Tk()
PaintApp(root)
root.mainloop()
