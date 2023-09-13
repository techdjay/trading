import cv2
import os
from datetime import datetime

def imgconcat(imgs,ip):
    t = []
    for k, v in imgs.items():
        if k == "isup":
            continue
        t.append(cv2.imread(v[1]))
    im_v = cv2.vconcat(t)
    cv2.imwrite(ip, im_v)