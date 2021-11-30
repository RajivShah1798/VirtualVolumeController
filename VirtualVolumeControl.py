import cv2
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandGesture as hg
import math
import numpy as np
import pycaw
import time


###################################
wCam, hCam = 640, 480
###################################


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = hg.HandDetector(detectionConfidence=0.75)

# Setting up Volume Controls
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVolume = volRange[0]
maxVolume = volRange[1]

vol = 0
volBar = 400
volPer = 100
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        #print(lmList[4], lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 7, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 1)

        cx, cy = (x1+x2)//2, (y1+y2)//2
        cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)
        #print(length)
        # Hand Range: 30 : 190
        # Volume Range: -65 : 0

        vol = np.interp(length, [30, 200], [minVolume, maxVolume])
        volBar = np.interp(length, [30, 200], [400, 150])
        volPer = np.interp(length, [30, 200], [0, 100])
        volume.SetMasterVolumeLevel(vol, None)

        if length< 40:
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
    cv2.rectangle(img, [50, 150], [60, 400], (255, 0, 0), 1)
    cv2.rectangle(img, [50, int(volBar)], [60, 400], (255, 0, 0), cv2.FILLED)
    cv2.putText(img, str(int(volPer))+"%", (40, 450), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)

    fps, cTime, pTime = hg.get_frame_rate_info(pTime)
    cv2.putText(img, "Frame Rate: " + str(int(fps)), (10, 70), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
    cv2.imshow("Image", img)
    cv2.waitKey(1)