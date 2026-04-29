import json
import cv2
import os
import threading
import tkinter as tk
import analyzeCube.twophase.solver as tp
from pathlib import Path
from PIL import Image, ImageTk
from moveCube.moves import photo
from analyzeCube.cubeTracker import extract_colors_from_image
from analyzeCube.colorresolver.solver import resolve_colors
#from analyzeCube.solverSim import *
from analyzeCube.solver import *
from moveCube.handles import *

# -----------------------
# SETTINGS (edit here)
# -----------------------
MAIN_W, MAIN_H = 800, 650

PREVIEW_W, PREVIEW_H = 220, 160      # size of webcam preview
THUMBNAIL_SIZE = 70                  # face photo thumbnails in the net view
MARGIN = 10                          # distance from top/right edges

# Probe camera indices 0..MAX_INDEX-1
MAX_INDEX = 4                        # increase if you have many virtual cams

# Prefer DirectShow on Windows (often avoids black frames) [2](https://centricnetherlandsiit.sharepoint.com/sites/Wiki-Exports/Shared%20Documents/Wiki-PSS-InformationFlows-2025-03-27-22-37/s4igov-07---29043-Key2BM-GBA-V-Win-service-support-Unicode-format-60721028.aspx.pdf?web=1)
BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

# Update interval for GUI refresh
UPDATE_MS = 15

# Probe settings
PROBE_READS = 3                      # read a few frames (some cams return 1st frame black)
BLACK_MEAN_THRESHOLD = 1.0           # below this = treat as "black frame"
# -----------------------

tmp_dir = Path('tmp')

class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rubiks Cube Solver")
        self.root.configure(bg="white")
        self._center(MAIN_W, MAIN_H)
        
        # Solution state (set after a successful scan/analyze)
        self.solution = None
        
        # Main container: left for results, right for camera controls
        self.main_container = tk.Frame(root, bg="white")
        self.main_container.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_container, bg="white")
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.right_frame = tk.Frame(self.main_container, bg="white", width=340)
        self.right_frame.pack(side="right", fill="y")

        # Top: cube face image grid (net layout U / L F R B / D)
        self.cube_images_frame = tk.Frame(self.left_frame, bg="white")
        self.cube_images_frame.pack(anchor="n", pady=10)

        self.face_canvases = {}
        self.face_image_refs = {}

        net_positions = {
            "U": (0, 1),
            "L": (1, 0),
            "F": (1, 1),
            "R": (1, 2),
            "B": (1, 3),
            "D": (2, 1),
        }

        for side, (r, c) in net_positions.items():
            frame = tk.Frame(self.cube_images_frame, bg="white", bd=1, relief="solid")
            frame.grid(row=r, column=c, padx=1, pady=1)
            canvas = tk.Canvas(frame, width=THUMBNAIL_SIZE, height=THUMBNAIL_SIZE, bg="white", bd=0, highlightthickness=0)
            canvas.pack()
            self.face_canvases[side] = canvas

        # Add spacing cells so grid remains aligned
        for row in range(3):
            for col in range(4):
                if (row, col) not in net_positions.values():
                    spacer = tk.Label(self.cube_images_frame, text="", bg="white", width=2, height=2, bd=0)
                    spacer.grid(row=row, column=col, padx=1, pady=1)

        # Middle: colorresolver 3x3 color output grid (same net layout, matching image size)
        self.color_grid_frame = tk.Frame(self.left_frame, bg="white")
        self.color_grid_frame.pack(anchor="n", pady=5)

        self.color_face_canvases = {}
        for side, (r, c) in net_positions.items():
            frame = tk.Frame(self.color_grid_frame, bg="white", bd=1, relief="solid")
            frame.grid(row=r, column=c, padx=1, pady=1)
            canvas = tk.Canvas(frame, width=THUMBNAIL_SIZE, height=THUMBNAIL_SIZE, bg="white", bd=0, highlightthickness=0)
            canvas.pack()
            self.color_face_canvases[side] = canvas

        # Add spacing cells for the color grid too
        for row in range(3):
            for col in range(4):
                if (row, col) not in net_positions.values():
                    spacer = tk.Label(self.color_grid_frame, text="", bg="white", width=1, height=1, bd=0)
                    spacer.grid(row=row, column=col, padx=1, pady=1)

        # Bottom: Kociemba + solution lines (no HTML text window)
        self.result_line = tk.Label(self.left_frame, text="Kociemba + solution will appear here", bg="white", justify="left", anchor="w", font=("Segoe UI", 10, "bold"))
        self.result_line.pack(fill="x", padx=10, pady=(0, 5))

        self.results_text = tk.Text(self.left_frame, wrap="word", font=("Consolas", 10), bg="white")
        self.results_text.pack(fill="both", expand=True, padx=10, pady=(0,10))
        self.results_text.insert(tk.END, "Press 'Scan' to run cube detection and solve.\n")

        # Container on the right for camera and controls
        self.overlay = self.right_frame

        # Buttons below radio buttons
        self.button_frame = tk.Frame(self.overlay, bg="white")
        self.button_frame.pack(fill="x", pady=(8, 0))

        button_opts = dict(master=self.button_frame, width=12, height=1, padx=0, pady=0)

        self.home_button = tk.Button(**button_opts, text="Home", command=home)
        self.home_button.pack(anchor="w", padx=(0, 8), pady=2)

        self.park_button = tk.Button(**button_opts, text="Park", command=park)
        self.park_button.pack(anchor="w", padx=(0, 8), pady=2)

        self.mount_button = tk.Button(**button_opts, text="Mount", command=mount)
        self.mount_button.pack(anchor="w", padx=(0, 8), pady=2)

        self.scan_button = tk.Button(**button_opts, text="Scan", command=self.run_scan)
        self.scan_button.pack(anchor="w", padx=(0, 8), pady=2)

        self.solve_button = tk.Button(**button_opts, text="Solve", command=self.run_solve)
        self.solve_button.pack(anchor="w", padx=(0, 8), pady=2)

        # Status line
        self.status = tk.Label(
            self.overlay, text="", bg="white", fg="black",
            font=("Consolas", 9), justify="left"
        )
        self.status.pack(fill="x", pady=(6, 0))

        # helper for live face updates during scan
        self.face_image_refs = {**self.face_image_refs}

        # Clean close handling (prevents your after() error)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _center(self, w, h):
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        x, y = (sw - w) // 2, (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _update_face_thumbnail(self, side_name, image_path):
        try:
            resample_method = getattr(Image, 'Resampling', None)
            resample = Image.Resampling.LANCZOS if resample_method is not None else Image.LANCZOS
            thumbnail = Image.open(image_path).resize((THUMBNAIL_SIZE, THUMBNAIL_SIZE), resample=resample)
            photo = ImageTk.PhotoImage(thumbnail)
            canvas = self.face_canvases.get(side_name)
            if canvas is not None:
                canvas.delete("all")
                canvas.create_image(THUMBNAIL_SIZE // 2, THUMBNAIL_SIZE // 2, image=photo)
            self.face_image_refs[side_name] = photo
        except Exception as ex:
            self.root.after(0, lambda: self.results_text.insert(tk.END, f"Failed to show {side_name}: {ex}\n"))

    def on_close(self):
        self.root.destroy()

    def run_scan(self):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Scanning... this may take 10-20s while twophase tables load\n")

        thread = threading.Thread(target=self.run_scan_thread)
        thread.daemon = True
        thread.start()

    def run_solve(self):
        if self.solution is None:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "No solution available. Please run Scan first to analyze the cube.\n")
            return
        SolveCube(self.solution)

    def run_scan_thread(self):
        # load the six faces from captured photos
        list_colors = []
        for side_name in ("U", "L", "F", "R", "B", "D"):
            image_path = tmp_dir / f"rubiks-{side_name}.png"
            if not image_path.exists():
                self.root.after(0, lambda: self.results_text.insert(tk.END, f"Missing image {image_path}\n"))
                return

            self.root.after(0, lambda s=side_name, p=str(image_path): self._update_face_thumbnail(s, p))
            colors = extract_colors_from_image(str(image_path))
            list_colors.append(colors)

        data = {}
        square_index = 1
        for face in list_colors:
            for rgb in face:
                data[square_index] = rgb
                square_index += 1

        json_str = json.dumps(data, sort_keys=True)
        resolved_json_str = resolve_colors(rgb=json_str, use_json=True)
        resolved_data = json.loads(resolved_json_str)

        kociemba_string = resolved_data['kociemba']
        twoPhase = tp.solve(kociemba_string, 10, 2)

        # load and display image thumbnails
        top_images = {}
        for side in ("U", "L", "F", "R", "B", "D"):
            image_path = tmp_dir / f"rubiks-{side}.png"
            # Pillow 10+ uses Resampling enum; Image.ANTIALIAS is removed
            resample_method = getattr(Image, 'Resampling', None)
            if resample_method is not None:
                resample = Image.Resampling.LANCZOS
            else:
                resample = Image.LANCZOS

            im = Image.open(image_path).resize((THUMBNAIL_SIZE, THUMBNAIL_SIZE), resample=resample)
            top_images[side] = ImageTk.PhotoImage(im)

        def update_ui():
            for side, photo in top_images.items():
                canvas = self.face_canvases.get(side)
                if canvas is not None:
                    canvas.delete("all")
                    canvas.create_image(THUMBNAIL_SIZE // 2, THUMBNAIL_SIZE // 2, image=photo)
                    self.face_image_refs[side] = photo

            # Render colorresolver cube output with exact sticker colors
            face_color_map = {}
            for side_name, side_value in resolved_data.get('sides', {}).items():
                if 'colorHTML' in side_value and 'colorName' in side_value:
                    c = side_value['colorHTML']
                    face_color_map[side_name] = f"#{int(c['red']):02x}{int(c['green']):02x}{int(c['blue']):02x}"

                # Layout from kociemba: URFDLB -> faces U, R, F, D, L, B
            kociemba = kociemba_string.strip()
            face_order = ['U', 'R', 'F', 'D', 'L', 'B']
            face_squares = {}
            if len(kociemba) >= 54:
                for idx, side in enumerate(face_order):
                    start = idx * 9
                    face_squares[side] = list(kociemba[start:start + 9])

            # Use resolved sides for cell color; rendered on canvas to match thumbnail size
            cell_size = THUMBNAIL_SIZE / 3
            for face_name, canvas in self.color_face_canvases.items():
                canvas.delete("all")
                if face_name not in face_color_map or face_name not in face_squares:
                    # blank face if no data
                    canvas.create_rectangle(0, 0, THUMBNAIL_SIZE, THUMBNAIL_SIZE, fill="#eee", outline="#000")
                    continue

                for i, cube_face_letter in enumerate(face_squares[face_name]):
                    x = (i % 3) * cell_size
                    y = (i // 3) * cell_size
                    color = face_color_map.get(cube_face_letter, face_color_map.get(face_name, '#fff'))
                    canvas.create_rectangle(x, y, x + cell_size, y + cell_size, fill=color, outline="#000")

            self.solution = twoPhase
            solution = (twoPhase.split(' '))[:-1]
            steps = len(solution)
    
            self.result_line.config(text=f"Kociemba: {kociemba_string} \nSolution: {twoPhase} \nMoves: {str(steps)}")
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert(tk.END, "Scan complete.\n")

        self.root.after(0, update_ui)

if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()

