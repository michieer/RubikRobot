import cv2
import json
import threading
import tkinter as tk
import analyzeCube.twophase.solver as tp
import analyzeCube.twophase.performance as pf
from analyzeCube.cubeTracker import extract_colors_from_image
from analyzeCube.colorresolver.solver import resolve_colors
from analyzeCube.solver import *
from analyzeCube.photos import *
from moveCube.calibration import open_calibration_window
from moveCube.handles import *
from moveCube.logger import *
from pathlib import Path
from PIL import Image, ImageTk
from tkinter import ttk

# -----------------------
# SETTINGS (edit here)
# -----------------------
MAIN_W, MAIN_H = 800, 650

PREVIEW_W, PREVIEW_H = 220, 160      # size of webcam preview
THUMBNAIL_SIZE = 70                  # face photo thumbnails in the net view
MARGIN = 10                          # distance from top/right edges

# Probe camera indices 0..MAX_INDEX-1
MAX_INDEX = 4                        # increase if you have many virtual cams

# Prefer DirectShow on Windows (often avoids black frames)
BACKENDS = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

# Update interval for GUI refresh
UPDATE_MS = 15

# Probe settings
PROBE_READS = 3                      # read a few frames (some cams return 1st frame black)
BLACK_MEAN_THRESHOLD = 1.0           # below this = treat as "black frame"
# -----------------------

tmp_dir = Path('tmp')
tmp_dir.mkdir(parents=True, exist_ok=True)

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

        form_frame = tk.Frame(self.left_frame, bg="white")
        form_frame.pack(fill="x", padx=10, pady=5)

        # Cube row
        tk.Label(form_frame, text="Cube:", bg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.cube_line = tk.Entry(form_frame, bg="white", font=("Segoe UI", 10, "bold"), relief="solid")
        self.cube_line.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Random cube row
        self.random_button = tk.Button(form_frame, text="Random Cube", command=self.run_get_cube_string)
        self.random_button.grid(row=1, column=0, sticky="w", padx=5, pady=5)

        self.newCube_line = tk.Entry(form_frame, bg="white", font=("Segoe UI", 10, "bold"), relief="solid")
        self.newCube_line.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Solution row
        tk.Label(form_frame, text="Solution:", bg="white").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.result_line = tk.Entry(form_frame,bg="white",font=("Segoe UI", 10, "bold"),relief="flat")
        self.result_line.insert(0, "Solution will appear here")
        self.result_line.config(state="readonly")
        self.result_line.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Make entry column stretch
        form_frame.columnconfigure(1, weight=1)        # Make the right column expand
        self.left_frame.columnconfigure(1, weight=1)

        # Frame specifically for text + scrollbar
        text_frame = tk.Frame(self.left_frame)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # Text widget
        self.results_text = tk.Text(
            text_frame,
            wrap="word",
            font=("Consolas", 10),
            bg="white",
            highlightthickness=0
        )
        self.results_text.pack(side="left", fill="both", expand=True)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(text_frame, command=self.results_text.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.results_text.config(yscrollcommand=self.scrollbar.set)

        init_logger(self.root, self.results_text)

        scrollbar = tk.Scrollbar(self.left_frame, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        log("Press 'Take Photo' to run cube detection and solve.\n")

        # Container on the right for camera and controls
        self.overlay = self.right_frame

        # Preview
        self.preview = tk.Label(self.overlay, bg="white", bd=1, relief="solid")
        self.preview.pack(padx=10, pady=10)

        # Radio buttons below preview
        self.rb_frame = tk.Frame(self.overlay, bg="white")
        self.rb_frame.pack(fill="x", pady=(8, 0))

        self.title_lbl = tk.Label(
            self.rb_frame, text="Camera:", bg="white", fg="black",
            font=("Segoe UI", 10, "bold")
        )
        self.title_lbl.pack(anchor="w")

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

        self.scan_button = tk.Button(**button_opts, text="Take Photos", command=self.run_take_photos)
        self.scan_button.pack(anchor="w", padx=(0, 8), pady=(20,2))

        self.scan_button = tk.Button(**button_opts, text="Read Photos", command=self.run_scan_photos)
        self.scan_button.pack(anchor="w", padx=(0, 8), pady=2)

        self.solve_button = tk.Button(**button_opts, text="Solve", command=self.run_solve)
        self.solve_button.pack(anchor="w", padx=(0, 8), pady=2)

        self.calibrate_button = tk.Button(**button_opts, text="Calibrate", command=lambda: open_calibration_window(self.root))
        self.calibrate_button.pack(anchor="w", padx=(0, 8), pady=(20,2))

        self.close_button = tk.Button(**button_opts, text="Close", command=self.root.quit)
        self.close_button.pack(anchor="w", padx=(0, 8), pady=(20,2))

        # Status line
        self.status = tk.Label(
            self.overlay, text="", bg="white", fg="black",
            font=("Consolas", 9), justify="left"
        )
        self.status.pack(fill="x", pady=(6, 0))

        # helper for live face updates during scan
        self.face_image_refs = {**self.face_image_refs}

        # Camera state
        self.cap = None
        self.backend_used = None
        self.after_id = None
        self._preview_stopped = threading.Event()

        # Discover available cameras and build radios
        self.available = self.find_available_cameras(MAX_INDEX)
        self.cam_index = tk.IntVar(value=max(self.available) if self.available else 0)

        if not self.available:
            self.status.config(
                text=f"No usable cameras found in indices 0..{MAX_INDEX-1}.\n"
                     f"Close Teams/Zoom/Browser camera use and try again.",
                fg="red"
            )
        else:
            self.build_radiobuttons(self.available)
            self.open_camera(self.cam_index.get())
            self.schedule_next()

        # Clean close handling (prevents your after() error)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, message):
        def append_text():
            self.results_text.insert("end", message + "\n")
            self.results_text.see("end")
        self.root.after(0, append_text)

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

    def try_open(self, index):
        for be in BACKENDS:
            c = cv2.VideoCapture(index, be)
            if c.isOpened():
                return c, be
            c.release()
        return None, None

    def is_usable_camera(self, index):
        cap, be = self.try_open(index)
        if cap is None:
            return False

        ok_frame = False
        try:
            # Read a few frames; first frame can be black on some setups
            for _ in range(PROBE_READS):
                ok, frame = cap.read()
                if ok and frame is not None and frame.size > 0 and frame.mean() >= BLACK_MEAN_THRESHOLD:
                    ok_frame = True
                    break
        finally:
            cap.release()

        return ok_frame

    def find_available_cameras(self, max_index):
        found = []
        for i in range(max_index):
            if self.is_usable_camera(i):
                found.append(i)
        return found

    def build_radiobuttons(self, indices):
        # Clear old radios
        for w in self.rb_frame.winfo_children():
            w.destroy()

        tk.Label(self.rb_frame, text="Camera:", bg="white", fg="black",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")

        for idx in indices:
            tk.Radiobutton(
                self.rb_frame,
                text=f"{idx}",
                value=idx,
                variable=self.cam_index,
                command=self.on_camera_change,
                bg="white",
                fg="black",
                activebackground="white",
                activeforeground="black",
                selectcolor="white",
                anchor="w"
            ).pack(side="left", padx=8)

    def open_camera(self, index):
        # Release existing camera
        if self.cap is not None:
            try:
                self.cap.release()
            except:
                pass
            self.cap = None

        cap, be = self.try_open(index)
        self.cap = cap
        self.backend_used = be

        if self.cap is None:
            self.status.config(text=f"Could not open camera {index}.", fg="red")

        # Clear image on switch
        self.preview.config(image="")

    def on_camera_change(self):
        self.open_camera(self.cam_index.get())

    def schedule_next(self):
        self.update_frame()
        self.after_id = self.root.after(UPDATE_MS, self.schedule_next)

    def update_frame(self):
        if self.cap is None:
            return

        ok, frame = self.cap.read()
        if not ok or frame is None or frame.size == 0:
            self.status.config(
                text=f"Read failed on camera {self.cam_index.get()} (backend={self.backend_used}).",
                fg="red"
            )
            return

        if frame.mean() < BLACK_MEAN_THRESHOLD:
            self.status.config(
                text=(f"Black frame from camera {self.cam_index.get()} (backend={self.backend_used}).\n"
                        f"Try another camera."),
                fg="red"
            )
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (PREVIEW_W, PREVIEW_H), interpolation=cv2.INTER_AREA)

        self.imgtk = ImageTk.PhotoImage(Image.fromarray(frame))
        self.preview.config(image=self.imgtk)

    def on_close(self):
        try:
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
                self.after_id = None
        except:
            pass

        try:
            if self.cap is not None:
                self.cap.release()
        finally:
            self.root.destroy()

    def run_take_photos(self):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Scanning cube...\n")
        
        # Pause the live preview so the scan thread can reuse self.cap
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        thread = threading.Thread(target=self.run_photo_thread, args=(tmp_dir, "take_photos"))
        thread.daemon = True
        thread.start()

    def run_scan_photos(self):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Scanning photos...\n")

        thread = threading.Thread(target=self.run_photo_thread, args=(tmp_dir, "read_photos"))
        thread.daemon = True
        thread.start()

    def run_get_cube_string(self):
        s=pf.getCubeString()
        self.newCube_line.delete(0, tk.END)
        self.newCube_line.insert(0, s)

    def run_solve(self):
        if self.newCube_line.get().strip() == "":
            twoPhase = tp.solve(self.Cube_line.get().strip(), 5, 5)
        else:
            twoPhase = tp.solveto(self.newCube_line.get().strip(), self.cube_line.get().strip(), 20, 0.1)
        
        self.solution = twoPhase
        solution = (twoPhase.split(' '))[:-1]
        steps = len(solution)

        self.result_line.config(state="normal")
        self.result_line.delete(0, tk.END)
        self.result_line.insert(0, f"{twoPhase} ({steps} steps)")
        self.result_line.config(state="readonly")

        if self.solution is None:
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, "No solution available. Please run Scan first to analyze the cube.\n")
            return

        thread = threading.Thread(target=SolveCube, args=(self, self.solution))
        thread.daemon = True
        thread.start()

    def _resume_preview(self):
        #Resume the live camera preview after scanning.
        if self.cap is not None and self.after_id is None:
            self.schedule_next()

    def _pause_preview_sync(self):
        #Call from background thread to pause preview and wait until stopped.
        self._preview_stopped.clear()
        self.root.after(0, self._do_pause_preview)
        self._preview_stopped.wait(timeout=2.0)

    def _do_pause_preview(self):
        #Runs on main thread. Cancels the preview loop and signals the event.
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self._preview_stopped.set()

    def _resume_preview_async(self):
        #Call from background thread to resume preview on main thread.
        self.root.after(0, self._resume_preview)

    def run_photo_thread(self, folder: str, action: str):
        get_photos(self, folder, action)

        json_str = analyze_photos(self, tmp_dir)
        resolved_json_str = resolve_colors(rgb=json_str, use_json=True)
        resolved_data = json.loads(resolved_json_str)

        self.kociemba_string = resolved_data['kociemba']

        def update_ui():
            # Render colorresolver cube output with exact sticker colors
            face_color_map = {}
            for side_name, side_value in resolved_data.get('sides', {}).items():
                if 'colorHTML' in side_value and 'colorName' in side_value:
                    c = side_value['colorHTML']
                    face_color_map[side_name] = f"#{int(c['red']):02x}{int(c['green']):02x}{int(c['blue']):02x}"

            # Layout from kociemba: URFDLB -> faces U, R, F, D, L, B
            kociemba = self.kociemba_string.strip()
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

            self.cube_line.insert(0, self.kociemba_string)
                        
            log("Scan complete.")

        def resume_after_ui():
            update_ui()
            self._resume_preview()

        self.root.after(0, resume_after_ui)


if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()
