import math

def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.hypot(x2 - x1, y2 - y1)

def is_pinch(lmList, threshold=40):
    if len(lmList) < 9:
        return False
    thumb_tip = lmList[4][1:]
    index_tip = lmList[8][1:]
    return distance(thumb_tip, index_tip) < threshold

def is_open_palm(lmList):
    if len(lmList) < 20:
        return False
    dist = distance(lmList[4][1:], lmList[20][1:])
    return dist > 180
