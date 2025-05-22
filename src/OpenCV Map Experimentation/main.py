import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(2)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

_wName = "OpenCV BotCam Spy"

def getColor(h, s, v):
    colorName = "none"
    if v < 50:
        colorName = "Black"
    elif s < 40 and v > 50 and v < 200:
        colorName = "Grey"
    elif s < 40 and v >= 200:
        colorName = "White"
    else:
        if (h <= 10) or (h >= 170):
            colorName = "Red"
        elif 11 <= h <= 25:
            colorName = "Orange"
        elif 26 <= h <= 34:
            colorName = "Yellow"  # optional if you want yellow too
        elif 35 <= h <= 85:
            colorName = "Green"
        elif 86 <= h <= 125:
            colorName = "Blue"
        elif 126 <= h <= 169:
            colorName = "Magenta"
        else:
            colorName = "Unknown"

    return colorName

mposx, mposy = 0, 0
def mouse_callback(event, x, y, flags, param):
    global mposx, mposy
    if event == cv2.EVENT_MOUSEMOVE:
        mposx, mposy = x, y

cv2.namedWindow(_wName)
cv2.setMouseCallback(_wName, mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # HSV thresholds
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 100, 100])
    upper_red2 = np.array([179, 255, 255])
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])

    # Masks
    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    green_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Find contours for red
    contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_red:
        area = cv2.contourArea(cnt)
        if area > 500:  # Minimum cluster size
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Red", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Find contours for green
    contours_green, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_green:
        area = cv2.contourArea(cnt)
        if area > 500:  # Minimum cluster size
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Green", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Display color at mouse pixel
    if mposx < 640-1 and mposx > 0 and mposy < 480-1 and mposy > 0:
        #h, s, v = hsv[mposx, mposy]
        cv2.rectangle(frame, (mposx - 5, mposy - 5), (mposx + 5, mposy + 5), (255, 255, 255), 2)
        cv2.rectangle(frame, (mposx - 3, mposy - 3), (mposx + 3, mposy + 3), (0, 0, 0), 2)

    cv2.imshow(_wName, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()