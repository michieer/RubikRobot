import cv2
import time
import json
from moveCube.moves import photo
from analyzeCube.cubeTracker import extract_colors_from_image
from analyzeCube.colorresolver.solver import resolve_colors
from moveCube.logger import *
from PIL import Image, ImageTk

THUMBNAIL_SIZE = 70                  # face photo thumbnails in the net view
CAPTURE_FLUSH_READS = 5              # frames to discard before capture (flush stale buffer)

def update_thumbnail(image_path:str, side:str):
    im = Image.open(image_path).resize((THUMBNAIL_SIZE, THUMBNAIL_SIZE), resample=resample)
    top_images[side] = ImageTk.PhotoImage(im)

def get_photos(self, folder: str, action: str):
    match action:
        case "take_photos":
            log("Taking pictures.")
            
            # Reuse the already-open preview camera (self.cap)
            if self.cap is None or not self.cap.isOpened():
                log("Camera is not available")
                self.root.after(0, self._resume_preview)
                return

            # warm up camera auto-exposure/white balance before first useful frame
            for _ in range(6):
                self.cap.read()
                time.sleep(0.1)

            # Resume preview so user can see robot movements
            self._resume_preview_async()

            # capture cube faces in scanning order
            for side_name in ("F", "R", "B", "L", "U", "D", "finish"):
                if side_name != "finish":
                    croppedfile = folder / f"rubiks-{side_name}.png"

                    photo(side_name)
                    time.sleep(2)

                    # Pause preview to get exclusive camera access for capture
                    self._pause_preview_sync()

                    # Flush stale buffered frames so we capture a fresh image
                    for _ in range(CAPTURE_FLUSH_READS):
                        self.cap.read()

                    ret, frame = self.cap.read()
                    if not ret or frame is None or frame.size == 0:
                        log(f"Camera read failed for {side_name}")
                        self.root.after(0, self._resume_preview)
                        return

                    cropped = frame[10:390, 140:520]
                    cv2.imwrite(str(croppedfile), cropped)

                    self.root.after(0, self._update_face_thumbnail, side_name, croppedfile)

                    log(f"Captured {side_name}")

                    # Resume preview after capture
                    self._resume_preview_async()
                else:
                    photo(side_name)
                    break

        case "read_photos":
            log("Loading pictures from files.")

            # load the six faces from captured photos
            for side_name in ("U", "L", "F", "R", "B", "D"):
                croppedfile = folder / f"rubiks-{side_name}.png"
                if not croppedfile.exists():
                    log("Missing image {croppedfile}")
                    return

                self.root.after(0, lambda s=side_name, p=str(croppedfile): self._update_face_thumbnail(s, p))
                log(f"Loaded {side_name}")

def analyze_photos(self, folder: str):
    log("Analyzing pictures.")

    list_colors = []
    # load the six faces from captured photos
    for side_name in ("U", "L", "F", "R", "B", "D"):
        if side_name != "finish":
            image_path = folder / f"rubiks-{side_name}.png"
            if not image_path.exists():
                log("Missing image {image_path}")
                return

            colors = extract_colors_from_image(str(image_path))
            list_colors.append(colors)

    log("Pictures analyzed.")
    data = {}
    square_index = 1
    for face in list_colors:
        for rgb in face:
            data[square_index] = rgb
            square_index += 1

    json_str = json.dumps(data, sort_keys=True)

    return json_str
