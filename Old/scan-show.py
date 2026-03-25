import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import json
import time

from moveCube import home, mount, photo, resolve_colors
from rubikscubetracker import RubiksImage


# -----------------------
# SETTINGS
# -----------------------

MAIN_W, MAIN_H = 1200, 700
PREVIEW_W, PREVIEW_H = 280, 210
MARGIN = 15

PHOTO_DIR = "./tmp"

UPDATE_MS = 15
BLACK_MEAN_THRESHOLD = 1.0

os.makedirs(PHOTO_DIR, exist_ok=True)


class WebcamApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Rubiks Cube Solver")
        self.root.configure(bg="white")
        self._center(MAIN_W, MAIN_H)

        # -----------------------
        # PHOTO PREVIEW (top-left)
        # -----------------------

        self.photo_frame = tk.Frame(root, bg="white")
        self.photo_frame.place(x=MARGIN, y=MARGIN)

        self.photo_labels = {}

        self.positions = {
            "U": (0,1),
            "L": (1,0),
            "F": (1,1),
            "R": (1,2),
            "B": (1,3),
            "D": (2,1)
        }

        for face,(r,c) in self.positions.items():

            lbl = tk.Label(
                self.photo_frame,
                width=140,
                height=100,
                bg="#eeeeee",
                text=face,
                bd=1,
                relief="solid"
            )

            lbl.grid(row=r,column=c,padx=4,pady=4)

            self.photo_labels[face] = lbl

        # -----------------------
        # COLOR PREVIEW
        # -----------------------

        self.color_frame = tk.Frame(root, bg="white")
        self.color_frame.place(x=MARGIN, y=320)

        self.color_tiles = {}

        for face,(r,c) in self.positions.items():

            face_frame = tk.Frame(self.color_frame, bg="black", bd=1)
            face_frame.grid(row=r,column=c,padx=6,pady=6)

            tiles = []

            for y in range(3):
                row_tiles = []

                for x in range(3):

                    tile = tk.Label(
                        face_frame,
                        width=3,
                        height=1,
                        bg="#cccccc",
                        bd=1,
                        relief="solid"
                    )

                    tile.grid(row=y,column=x,padx=1,pady=1)

                    row_tiles.append(tile)

                tiles.append(row_tiles)

            self.color_tiles[face] = tiles

        # -----------------------
        # Webcam overlay
        # -----------------------

        self.overlay = tk.Frame(root, bg="white")
        self.overlay.place(relx=1.0, x=-MARGIN, y=MARGIN, anchor="ne")

        self.preview = tk.Label(self.overlay, bg="white", bd=1, relief="solid")
        self.preview.pack()

        # Mount button
        self.mnt_btn = tk.Button(
            self.overlay,
            text="Mount",
            command=self.mnt_cube,
            font=("Segoe UI",10,"bold"),
            bg="#4CAF50",
            fg="white"
        )

        # Parc button
        self.parc_btn = tk.Button(
            self.overlay,
            text="Parc",
            command=self.parc_robot,
            font=("Segoe UI",10,"bold"),
            bg="#4CAF50",
            fg="white"
        )

        # Scan button
        self.scan_btn = tk.Button(
            self.overlay,
            text="Scan",
            command=self.scan_cube,
            font=("Segoe UI",10,"bold"),
            bg="#4CAF50",
            fg="white"
        )

        # Home button
        self.home_btn = tk.Button(
            self.overlay,
            text="Home",
            command=self.home_robot,
            font=("Segoe UI",10,"bold"),
            bg="#4CAF50",
            fg="white"
        )

        self.mnt_btn.pack(pady=10)
        self.parc_btn.pack(pady=10)
        self.scan_btn.pack(pady=10)
        self.home_btn.pack(pady=10)

        self.status = tk.Label(
            self.overlay,
            text="",
            bg="white",
            fg="black"
        )

        self.status.pack()

        # -----------------------
        # Camera
        # -----------------------

        self.cap = cv2.VideoCapture(0)

        self.after_id = None
        self.imgtk_ref = None

        self.schedule_next()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # -----------------------

    def _center(self, w, h):

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        x = (sw-w)//2
        y = (sh-h)//2

        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # -----------------------

    def schedule_next(self):

        self.update_frame()
        self.after_id = self.root.after(UPDATE_MS, self.schedule_next)

    # -----------------------

    def update_frame(self):

        ok, frame = self.cap.read()

        if not ok:
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame,(PREVIEW_W,PREVIEW_H))

        imgtk = ImageTk.PhotoImage(Image.fromarray(frame))

        self.imgtk_ref = imgtk
        self.preview.config(image=imgtk)

    # -----------------------
    # LOAD PHOTO INTO GUI
    # -----------------------

    def show_photo(self, face, frame):

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame,(140,100))

        imgtk = ImageTk.PhotoImage(Image.fromarray(frame))

        lbl = self.photo_labels[face]
        lbl.config(image=imgtk,text="")
        lbl.image = imgtk

    # -----------------------
    # COLOR DISPLAY
    # -----------------------

    def update_face_colors(self, face, colors):

        tiles = self.color_tiles[face]

        i = 0

        for y in range(3):
            for x in range(3):

                r,g,b = colors[i]

                hex_color = f"#{r:02x}{g:02x}{b:02x}"

                tiles[y][x].config(bg=hex_color)

                i += 1

    # -----------------------
    # SCAN PROCESS
    # -----------------------

    def scan_cube(self):

        self.status.config(text="Scanning cube...")

        cube_size = 3
        sides = ["F","R","B","L","U","D"]

        results = []

        for side_index,side_name in enumerate(sides):

            self.status.config(text=f"Scanning {side_name}")
            self.root.update()

            photo(side_name)

            time.sleep(2)

            ret, frame = self.cap.read()

            if not ret:
                print("camera read failed")
                return

            cropped = frame[5:370,160:540]

            filename = f"{PHOTO_DIR}/rubiks-{side_name}.png"

            cv2.imwrite(filename,cropped)

            self.show_photo(side_name,cropped)

            rimg = RubiksImage(side_index,side_name,debug=False)

            rimg.analyze_file(filename,cube_size)

            results.append(rimg.data)

        # reorder like your script

        data_dict = {}
        data_dict.update(results[4])
        data_dict.update(results[3])
        data_dict.update(results[0])
        data_dict.update(results[1])
        data_dict.update(results[2])
        data_dict.update(results[5])

        data = {}

        i = 1

        for val in data_dict.values():
            data[i] = val
            i += 1

        jsonColors = json.dumps(data, sort_keys=True)

        colors = resolve_colors(jsonColors)

        # save json

        with open(f"{PHOTO_DIR}/colors.json","w") as f:
            json.dump(data,f)

        # update GUI colors

        idx = 1

        for face in ["U","L","F","R","B","D"]:

            cols = []

            for _ in range(9):

                c = data[idx]

                cols.append((c["r"],c["g"],c["b"]))

                idx += 1

            self.update_face_colors(face,cols)

        self.status.config(text="Scan complete")

        print(colors)

    # -----------------------

    def mnt_cube(self):
        self

    def parc_robot(self):
        self

    def home_robot(self):
        self

    # -----------------------

    def on_close(self):

        if self.after_id:
            self.root.after_cancel(self.after_id)

        if self.cap:
            self.cap.release()

        self.root.destroy()


# -----------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = WebcamApp(root)

    root.mainloop()