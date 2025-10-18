import cv2
import numpy as np  # Import numpy for mask combination
from PIL import Image
from util import get_limits

# Define the colors and their BGR values
colors_to_track = {
    'green': [0, 255, 0],  # BGR format
    'red': [0, 0, 255]  # BGR format
}

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video stream (Index 0). Try a different camera index (1, 2, etc.).")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: Failed to receive frame from stream. Exiting.")
        break

    hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Loop through each color to perform detection
    for color_name, bgr_color in colors_to_track.items():

        # Get the list of limits (1 for green, 2 for red wrap-around)
        limits_list = get_limits(color=bgr_color)

        # Initialize an empty mask for the current color
        final_mask = None

        # Iterate through all limit ranges provided by get_limits
        for lowerLimit, upperLimit in limits_list:

            # Create a mask for the current range
            mask_segment = cv2.inRange(hsvImage, lowerLimit, upperLimit)

            # Combine masks: OR operation for segments of the same color
            if final_mask is None:
                final_mask = mask_segment
            else:
                final_mask = cv2.bitwise_or(final_mask, mask_segment)

        # Now, final_mask contains the complete masked image for the current color

        # Use PIL to get the bounding box from the combined mask
        # Note: You need to pass the NumPy array (final_mask) to Image.fromarray
        mask_ = Image.fromarray(final_mask)
        bbox = mask_.getbbox()

        # If a bounding box is found, draw it
        if bbox is not None:
            x1, y1, x2, y2 = bbox

            # Draw the rectangle using the BGR color defined
            frame = cv2.rectangle(frame, (x1, y1), (x2, y2), bgr_color, 5)

            # Optional: Add text label
            cv2.putText(frame, color_name.upper(), (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, bgr_color, 2)

    # Display the final frame with all bounding boxes
    cv2.imshow('Color Tracker', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()