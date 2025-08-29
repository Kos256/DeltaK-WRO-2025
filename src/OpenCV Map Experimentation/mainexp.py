import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(2)  # Replace 2 with 0 on Raspberry Pi
width, height = 640, 480
cap.set(3, width)
cap.set(4, height)

_wName = "OpenCV BotCam Spy"

def clamp(v, minv, maxv):
    return max(minv, min(v, maxv))

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
            colorName = "Yellow"
        elif 35 <= h <= 85:
            colorName = "Green"
        elif 86 <= h <= 125:
            colorName = "Blue"
        elif 126 <= h <= 169:
            colorName = "Magenta"
        else:
            colorName = "Unknown"
    return colorName.lower()

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

    centroidData = []

    # Red contours
    contours_red, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_red:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cx, cy = x + w // 2, y + h // 2

            roi = hsv[y:y+h, x:x+w]
            avg_h = int(np.mean(roi[:, :, 0]))
            avg_s = int(np.mean(roi[:, :, 1]))
            avg_v = int(np.mean(roi[:, :, 2]))
            color_name = getColor(avg_h, avg_s, avg_v)

            centroidData.append((cx, cy, w, h, color_name))
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, "Red", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Green contours
    contours_green, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_green:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cx, cy = x + w // 2, y + h // 2

            roi = hsv[y:y+h, x:x+w]
            avg_h = int(np.mean(roi[:, :, 0]))
            avg_s = int(np.mean(roi[:, :, 1]))
            avg_v = int(np.mean(roi[:, :, 2]))
            color_name = getColor(avg_h, avg_s, avg_v)

            centroidData.append((cx, cy, w, h, color_name))
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "Green", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Draw centeroid annotations
    for cx, cy, w, h, color_name in centroidData:
        color = (0, 255, 255)
        if cx < width / 3: color = (255, 255, 0)
        if cx > width / 3 * 2: color = (255, 255, 0)
        cv2.circle(frame, (cx, cy), 10, color, -1)
        cv2.line(frame, (cx - 25, cy), (cx + 25, cy), color, 2)
        cv2.line(frame, (cx, cy - 25), (cx, cy + 25), color, 2)
        #cv2.putText(frame, f"{color_name.capitalize()} ({cx}, {cy})", (cx + 10, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Draw vertical guide lines
    cv2.line(frame, (round(width / 3), 0), (round(width / 3), height), (255, 255, 255), 2)
    cv2.line(frame, (round(width / 3 * 2), 0), (round(width / 3 * 2), height), (255, 255, 255), 2)





    # Display color at mouse pixel
    mposx = clamp(mposx, 0, width - 1)
    mposy = clamp(mposy, 0, height - 1)
    h, s, v = hsv[mposy, mposx]
    cv2.putText(frame, f"({mposx}, {mposy}) is {getColor(h, s, v)}", (mposx, mposy - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.rectangle(frame, (mposx - 5, mposy - 5), (mposx + 5, mposy + 5), (255, 255, 255), 2)
    cv2.rectangle(frame, (mposx - 3, mposy - 3), (mposx + 3, mposy + 3), (0, 0, 0), 2)

    # Optional: print to console
    # print("Boxes:", centroidData)

    cv2.imshow(_wName, frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
