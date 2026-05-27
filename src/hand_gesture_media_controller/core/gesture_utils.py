import math


def distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.hypot(x2 - x1, y2 - y1)


def finger_distance(lmList, finger_a=4, finger_b=8):
    if len(lmList) <= max(finger_a, finger_b):
        return float("inf")
    return distance(lmList[finger_a][1:], lmList[finger_b][1:])


def is_pinch(lmList, threshold=40):
    return finger_distance(lmList, 4, 8) < threshold


def is_open_palm(lmList):
    if len(lmList) < 21:
        return False

    index_up, middle_up, ring_up, pinky_up = extended_fingers(lmList)
    all_fingers_up = index_up and middle_up and ring_up and pinky_up
    if not all_fingers_up:
        return False

    scale = hand_scale(lmList)
    thumb_index = distance(lmList[4][1:], lmList[8][1:])
    thumb_pinky = distance(lmList[4][1:], lmList[20][1:])
    return thumb_index > scale * 0.33 and thumb_pinky > scale * 1.25


def hand_scale(lmList):
    if len(lmList) < 10:
        return 100.0
    # Stable palm measure for normalization.
    return max(distance(lmList[0][1:], lmList[9][1:]), 60.0)


def is_finger_extended(lmList, tip_idx, pip_idx, mcp_idx):
    if len(lmList) <= max(tip_idx, pip_idx, mcp_idx, 0):
        return False

    scale = hand_scale(lmList)
    margin = max(5.0, scale * 0.08)

    tip_y = lmList[tip_idx][2]
    pip_y = lmList[pip_idx][2]
    mcp_y = lmList[mcp_idx][2]

    vertical_ok = (tip_y < pip_y - margin * 0.35) and (pip_y < mcp_y - margin * 0.25)

    wrist = lmList[0][1:]
    tip_dist = distance(lmList[tip_idx][1:], wrist)
    pip_dist = distance(lmList[pip_idx][1:], wrist)
    radial_ok = tip_dist > pip_dist * 1.08

    return vertical_ok or radial_ok


def extended_fingers(lmList):
    """Return booleans for index/middle/ring/pinky finger extension."""
    if len(lmList) < 21:
        return (False, False, False, False)

    index_up = is_finger_extended(lmList, 8, 6, 5)
    middle_up = is_finger_extended(lmList, 12, 10, 9)
    ring_up = is_finger_extended(lmList, 16, 14, 13)
    pinky_up = is_finger_extended(lmList, 20, 18, 17)
    return (index_up, middle_up, ring_up, pinky_up)


def is_v_sign(lmList):
    if len(lmList) < 21:
        return False
    index_up, middle_up, ring_up, pinky_up = extended_fingers(lmList)
    if not (index_up and middle_up and not ring_up and not pinky_up):
        return False

    scale = hand_scale(lmList)
    finger_gap = distance(lmList[8][1:], lmList[12][1:])
    return finger_gap > scale * 0.2


def is_rock_sign(lmList):
    if len(lmList) < 21:
        return False
    index_up, middle_up, ring_up, pinky_up = extended_fingers(lmList)
    if not (index_up and not middle_up and not ring_up and pinky_up):
        return False

    scale = hand_scale(lmList)
    spread = distance(lmList[8][1:], lmList[20][1:])
    return spread > scale * 0.5


def is_fist(lmList):
    if len(lmList) < 21:
        return False
    index_up, middle_up, ring_up, pinky_up = extended_fingers(lmList)
    if index_up or middle_up or ring_up or pinky_up:
        return False

    scale = hand_scale(lmList)
    thumb_index = distance(lmList[4][1:], lmList[8][1:])
    return thumb_index < scale * 1.0
