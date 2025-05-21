import cv2

# Open webcam
cap = cv2.VideoCapture(2)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Get frame dimensions and center coordinates
    height, width, _ = frame.shape
    cx, cy = width // 2, height // 2

    # Convert frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get HSV value at center pixel
    hsv_value = hsv_frame[cy, cx]
    h, s, v = hsv_value

    # Draw a circle at the center
    cv2.circle(frame, (cx, cy), 5, (0, 255, 255), 2)

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

    # First line (HSV)
    cv2.putText(frame, f"H: {h}  S: {s}  V: {v}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Second line (Color name)
    cv2.putText(frame, f"Color: {colorName}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Show the frame
    cv2.imshow("HSV Viewer", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()