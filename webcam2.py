import tkinter as tk
import cv2
from PIL import Image, ImageTk

# -----------------------
# SETTINGS (edit here)
# -----------------------
MAIN_W, MAIN_H = 1200, 700

PREVIEW_W, PREVIEW_H = 280, 210      # size of webcam preview
MARGIN = 15                          # distance from top/right edges

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


class WebcamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rubiks Cube Solver")
        self.root.configure(bg="white")
        self._center(MAIN_W, MAIN_H)

        # Container pinned top-right (preview + radios)
        self.overlay = tk.Frame(root, bg="white")
        self.overlay.place(relx=1.0, x=-MARGIN, y=MARGIN, anchor="ne")

        # Preview
        self.preview = tk.Label(self.overlay, bg="white", bd=1, relief="solid")
        self.preview.pack()

        # Radio buttons below preview
        self.rb_frame = tk.Frame(self.overlay, bg="white")
        self.rb_frame.pack(fill="x", pady=(8, 0))

        self.title_lbl = tk.Label(
            self.rb_frame, text="Camera:", bg="white", fg="black",
            font=("Segoe UI", 10, "bold")
        )
        self.title_lbl.pack(anchor="w")

        # Status line
        self.status = tk.Label(
            self.overlay, text="", bg="white", fg="black",
            font=("Consolas", 9), justify="left"
        )
        self.status.pack(fill="x", pady=(6, 0))

        # Keep overlay pinned top-right on resize
        self.root.bind("<Configure>", lambda e: self.overlay.place(relx=1.0, x=-MARGIN, y=MARGIN, anchor="ne"))

        # Camera state
        self.cap = None
        self.backend_used = None
        self.after_id = None
        self.imgtk_ref = None

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


if __name__ == "__main__":
    root = tk.Tk()
    app = WebcamApp(root)
    root.mainloop()

