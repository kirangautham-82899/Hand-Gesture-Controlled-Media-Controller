import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self, maxHands=1, detectionCon=0.7, trackCon=0.5, modelComplexity=0):
        self.maxHands = maxHands
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            max_num_hands=maxHands,
            model_complexity=modelComplexity,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon,
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None
        self._shape = (0, 0)

    def findHands(self, img, draw=True):
        if img is None:
            self.results = None
            return img

        self._shape = img.shape[:2]
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB.flags.writeable = False
        self.results = self.hands.process(imgRGB)
        imgRGB.flags.writeable = True

        if draw and self.results and self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img=None, handNo=0):
        lmList = []
        if not self.results or not self.results.multi_hand_landmarks:
            return lmList

        if handNo >= len(self.results.multi_hand_landmarks):
            return lmList

        if img is not None:
            h, w = img.shape[:2]
        else:
            h, w = self._shape

        myHand = self.results.multi_hand_landmarks[handNo]
        for idx, lm in enumerate(myHand.landmark):
            cx = int(lm.x * w)
            cy = int(lm.y * h)
            lmList.append((idx, cx, cy))

        return lmList
