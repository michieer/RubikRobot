import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk


class WebcamApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Webcam Viewer (Auto-detect 0..8)")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # ---- UI ----
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="Available cameras:").pack(side=tk.LEFT)

        self.radios_frame = ttk.Frame(top)
        self.radios_frame.pack(side=tk.LEFT, padx=(8, 12))

        self.refresh_btn = ttk.Button(top, text="Refresh", command=self.refresh_cameras)
        self.refresh_btn.pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Starting…")
        ttk.Label(self, textvariable=self.status_var, padding=(10, 0)).pack(anchor="w")

        self.video_label = ttk.Label(self)
        self.video_label.pack(side=tk.TOP, padx=10, pady=10)

        # ---- State ----
        self.cap = None
        self.running = True
        self.after_id = None

        self.available_ids = []
        self.radio_buttons = []
        self.selected_cam = tk.IntVar(value=-1)

        # Show GUI first, then scan/open (prevents "no window" feeling)
        self.after(0, self.refresh_cameras)
        self.after(0, self.update_frame)

    # ---------- Camera detection ----------
    def detect_cameras(self, max_id=8):
        """
        Return a list of camera indices that:
        - open successfully
        - and return at least one frame
        """
        found = []
        for cam_id in range(max_id + 1):
            cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)  # Windows DirectShow
            if not cap.isOpened():
                cap.release()
                continue

            # Try to read a few frames (some devices need warm-up)
            ok = False
            for _ in range(5):
                ret, _frame = cap.read()
                if ret:
                    ok = True
                    break

            cap.release()
            if ok:
                found.append(cam_id)

        return found

    def rebuild_radiobuttons(self):
        # Clear old radio buttons
        for rb in self.radio_buttons:
            rb.destroy()
        self.radio_buttons.clear()

        if not self.available_ids:
            ttk.Label(self.radios_frame, text="(none)").pack(side=tk.LEFT)
            self.radio_buttons.append(self.radios_frame.winfo_children()[-1])
            self.selected_cam.set(-1)
            return

        # Build new radio buttons
        for cam_id in self.available_ids:
            rb = ttk.Radiobutton(
                self.radios_frame,
                text=str(cam_id),
                value=cam_id,
                variable=self.selected_cam,
                command=self.on_camera_selected
            )
            rb.pack(side=tk.LEFT, padx=2)
            self.radio_buttons.append(rb)

    def refresh_cameras(self):
        self.status_var.set("Scanning cameras 0..8…")
        self.update_idletasks()

        # Detect
        self.available_ids = self.detect_cameras(max_id=8)

        # Rebuild UI
        # First remove any placeholder labels left in radios_frame
        for child in self.radios_frame.winfo_children():
            child.destroy()
        self.radio_buttons.clear()

        self.rebuild_radiobuttons()

        if not self.available_ids:
            self.status_var.set("No cameras detected (0..8). Check permissions / camera in use.")
            self.close_camera()
            return

        # Pick current selection if still valid; otherwise pick first available
        current = self.selected_cam.get()
        if current not in self.available_ids:
            self.selected_cam.set(self.available_ids[0])

        self.status_var.set(f"Detected cameras: {self.available_ids}. Opening {self.selected_cam.get()}…")
        self.open_camera(self.selected_cam.get())

    # ---------- Camera open/switch ----------
    def open_camera(self, cam_id: int):
        # release previous
        self.close_camera()

        cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap.release()
            self.status_var.set(f"Failed to open camera {cam_id}")
            messagebox.showerror("Camera Error", f"Could not open camera ID {cam_id}.")
            return

        self.cap = cap
        self.status_var.set(f"Showing camera {cam_id}")

    def on_camera_selected(self):
        cam_id = self.selected_cam.get()
        self.status_var.set(f"Switching to camera {cam_id}…")
        # schedule to keep UI responsive
        self.after(0, lambda: self.open_camera(cam_id))

    def close_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    # ---------- Frame loop ----------
    def update_frame(self):
        if not self.running:
            return

        if self.cap is not None:
            ok, frame = self.cap.read()
            if ok:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(img)
                self.video_label.configure(image=imgtk)
                self.video_label.image = imgtk  # keep reference
            else:
                self.status_var.set("Frame read failed (camera disconnected or busy?)")

        # 15ms ~ high FPS; use 33ms for ~30fps lower CPU
        self.after_id = self.after(15, self.update_frame)

    # ---------- Shutdown ----------
    def on_close(self):
        self.running = False
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.close_camera()
        self.destroy()


if __name__ == "__main__":
    app = WebcamApp()
    app.mainloop()