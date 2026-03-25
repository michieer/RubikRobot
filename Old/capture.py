#!/usr/bin/env python3

import cv2
import sys

cam = int(sys.argv[1])
cv2.namedWindow("preview")
vc = cv2.VideoCapture(cam)

while True:
    ret, frame = vc.read()
    cv2.imshow("preview", frame)
    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break

cv2.destroyWindow("preview")
vc.release()
