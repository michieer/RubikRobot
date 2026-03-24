import cv2
import time
cam = cv2.VideoCapture(1)
cv2.namedWindow("Preview", cv2.WINDOW_AUTOSIZE)
time.sleep(2)
ret, frame = cam.read()
cv2.imshow("Preview", frame)

cropped = frame[5:370, 160:540]
cv2.imshow("Preview", cropped)

from rubikscubetracker import RubiksImage, RubiksVideo
cube_size = 3
rimg = RubiksImage(0, "D", debug=False)
rimg.analyze_image(frame)


cam = int(sys.argv[1])
cv2.namedWindow("preview")
vc = cv2.VideoCapture(cam)

ret, frame = vc.read()
cropped = frame[5:370, 160:540]
cv2.imshow("Preview", cropped)

cv2.destroyWindow("preview")
vc.release()

