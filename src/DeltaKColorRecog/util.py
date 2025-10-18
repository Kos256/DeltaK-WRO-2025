import numpy as np
import cv2


def get_limits(color):
    """
    Takes a BGR color tuple and returns a list of lower and upper HSV limits
    for color segmentation, correctly handling the hue wrap-around for red.
    Returns: A list of (lowerLimit, upperLimit) tuples.
    """
    # Create a 1x1 BGR NumPy array
    c = np.uint8([[color]])

    # Convert BGR to HSV
    hsvC = cv2.cvtColor(c, cv2.COLOR_BGR2HSV)

    # Extract the HUE value (0-179 in OpenCV)
    hue = hsvC[0][0][0]

    # Range width for the hue band (e.g., +/- 10)
    range_width = 10

    # Base Saturation (S) and Value (V) bounds
    # S and V are often set to a higher minimum (e.g., 100) to filter out gray/white/black.
    lower_s_v = 100
    upper_s_v = 255

    # List to hold the limit tuples (only one for most colors, two for wrap-around red)
    limits_list = []

    # 1. Calculate the standard lower and upper hue bounds
    lower_hue = hue - range_width
    upper_hue = hue + range_width

    # 2. Check for wrap-around (Red Hue)
    if lower_hue < 0:
        # If the lower bound is negative (e.g., -10), it means the color wraps around 0.
        # We need two ranges: [0, upper_hue] and [180 + lower_hue, 179]

        # Range 1 (High side)
        limits_list.append((
            np.array([180 + lower_hue, lower_s_v, lower_s_v], dtype=np.uint8),
            np.array([179, upper_s_v, upper_s_v], dtype=np.uint8)
        ))
        # Range 2 (Low side)
        limits_list.append((
            np.array([0, lower_s_v, lower_s_v], dtype=np.uint8),
            np.array([upper_hue, upper_s_v, upper_s_v], dtype=np.uint8)
        ))

    elif upper_hue > 179:
        # If the upper bound is over 179 (e.g., 185), this is the other red wrap case.
        # We need two ranges: [lower_hue, 179] and [0, upper_hue - 180]

        # Range 1 (High side)
        limits_list.append((
            np.array([lower_hue, lower_s_v, lower_s_v], dtype=np.uint8),
            np.array([179, upper_s_v, upper_s_v], dtype=np.uint8)
        ))
        # Range 2 (Low side)
        limits_list.append((
            np.array([0, lower_s_v, lower_s_v], dtype=np.uint8),
            np.array([upper_hue - 180, upper_s_v, upper_s_v], dtype=np.uint8)
        ))

    else:
        # 3. Standard case (Green, Yellow, Blue, etc.)
        limits_list.append((
            np.array([lower_hue, lower_s_v, lower_s_v], dtype=np.uint8),
            np.array([upper_hue, upper_s_v, upper_s_v], dtype=np.uint8)
        ))

    return limits_list