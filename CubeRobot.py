import cv2
import json
import threading
import time
import tkinter as tk
import analyzeCube.twophase.solver as tp
from analyzeCube.cubeTracker import extract_colors_from_image
from analyzeCube.colorresolver.solver import resolve_colors
from analyzeCube.solver import *
from moveCube.handles import *
from moveCube.moves import photo
from pathlib import Path
from PIL import Image, ImageTk

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
CAPTURE_FLUSH_READS = 5              # frames to discard before capture (flush stale buffer)
# -----------------------


class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rubiks Cube Solver")
        self.root.configure(bg="white")
        self._center(MAIN_W, MAIN_H)

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

        self.scan_button = tk.Button(**button_opts, text="Scan", command=self.run_scan)
        self.scan_button.pack(anchor="w", padx=(0, 8), pady=2)

        self.solve_button = tk.Button(**button_opts, text="Solve", command=SolveCube)
        self.solve_button.pack(anchor="w", padx=(0, 8), pady=2)

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
        self.imgtk_ref = None
        self._preview_stopped = threading.Event()

        # Discover available cameras and build radios
        self.available = self.find_available_cameras(MAX_INDEX)
        self.cam_index = tk.IntVar(value=self.available[0] if self.available else 0)

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

        # Clean close handling (prevents your after() error) [1](https://learn.microsoft.com/en-us/training/modules/configure-user-experience-settings/?WT.mc_id=api_CatalogApi&sso=viva-learning)
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
        self.imgtk_ref = None

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

        imgtk = ImageTk.PhotoImage(Image.fromarray(frame))
        self.imgtk_ref = imgtk  # keep reference!
        self.preview.config(image=imgtk)

    def on_close(self):
        # Cancel scheduled after job to avoid "invalid command name ... (after script)" [1](https://learn.microsoft.com/en-us/training/modules/configure-user-experience-settings/?WT.mc_id=api_CatalogApi&sso=viva-learning)
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

    def run_scan(self):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Scanning... this may take 10-20s while twophase tables load\n")

        # Pause the live preview so the scan thread can reuse self.cap
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        thread = threading.Thread(target=self.run_photo_thread)
        thread.daemon = True
        thread.start()

    def _resume_preview(self):
        """Resume the live camera preview after scanning."""
        if self.cap is not None and self.after_id is None:
            self.schedule_next()

    def _pause_preview_sync(self):
        """Call from background thread to pause preview and wait until stopped."""
        self._preview_stopped.clear()
        self.root.after(0, self._do_pause_preview)
        self._preview_stopped.wait(timeout=2.0)

    def _do_pause_preview(self):
        """Runs on main thread. Cancels the preview loop and signals the event."""
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self._preview_stopped.set()

    def _resume_preview_async(self):
        """Call from background thread to resume preview on main thread."""
        self.root.after(0, self._resume_preview)

    def run_photo_thread(self):
        tmp_dir = Path('tmp')
        tmp_dir.mkdir(parents=True, exist_ok=True)

        # Reuse the already-open preview camera (self.cap)
        if self.cap is None or not self.cap.isOpened():
            self.root.after(0, lambda: self.results_text.insert(tk.END, "Camera is not available\n"))
            self.root.after(0, self._resume_preview)
            return

        # warm up camera auto-exposure/white balance before first useful frame
        for _ in range(6):
            self.cap.read()
            time.sleep(0.1)

        # Resume preview so user can see robot movements
        self._resume_preview_async()

        # capture cube faces in scanning order
        for side_name in ("F", "R", "B", "L", "U", "D"):
            croppedfile = tmp_dir / f"rubiks-{side_name}.png"

            photo(side_name)
            time.sleep(2)

            # Pause preview to get exclusive camera access for capture
            self._pause_preview_sync()

            # Flush stale buffered frames so we capture a fresh image
            for _ in range(CAPTURE_FLUSH_READS):
                self.cap.read()

            ret, frame = self.cap.read()
            if not ret or frame is None or frame.size == 0:
                self.root.after(0, lambda: self.results_text.insert(tk.END, f"Camera read failed for {side_name}\n"))
                self.root.after(0, self._resume_preview)
                return

            cropped = frame[10:390, 140:520]
            cv2.imwrite(str(croppedfile), cropped)

            # Resume preview after capture
            self._resume_preview_async()

            self.root.after(0, lambda s=side_name, p=str(croppedfile): self._update_face_thumbnail(s, p))
            self.root.after(0, lambda s=side_name: self.status.config(text=f"Captured {s}"))

        # load the six faces from captured photos
        list_colors = []
        for side_name in ("U", "L", "F", "R", "B", "D", "finish"):
            if side_name != "finish":
                image_path = tmp_dir / f"rubiks-{side_name}.png"
                if not image_path.exists():
                    self.root.after(0, lambda: self.results_text.insert(tk.END, f"Missing image {image_path}\n"))
                    return

                colors = extract_colors_from_image(str(image_path))
                list_colors.append(colors)
            else:
                photo(side_name)
                break

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

            solution = (twoPhase.split(' '))[:-1]
            steps = len(solution)
    
            self.result_line.config(text=f"Kociemba: {kociemba_string} \nSolution: {twoPhase} \nMoves: {str(steps)}")
            self.results_text.delete('1.0', tk.END)
            self.results_text.insert(tk.END, "Scan complete.\n")

        def resume_after_ui():
            update_ui()
            self._resume_preview()

        self.root.after(0, resume_after_ui)


if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()
