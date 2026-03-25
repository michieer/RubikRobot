"""
Given the following .png files in /tmp/

For each png
- find all of the rubiks squares
- return a list of RGB values for each square (3x3 grid, top-left to bottom-right)
"""

import cv2
import numpy as np
import math


def pixel_distance(A, B):
    """
    Return the distance between two pixels
    """
    (col_A, row_A) = A
    (col_B, row_B) = B
    return math.sqrt(math.pow(col_B - col_A, 2) + math.pow(row_B - row_A, 2))


def get_angle(A, B, C):
    """
    Return the angle at C (in radians) for the triangle formed by A, B, C
    """
    (col_A, row_A) = A
    (col_B, row_B) = B
    (col_C, row_C) = C
    a = pixel_distance(C, B)
    b = pixel_distance(A, C)
    c = pixel_distance(A, B)

    try:
        cos_angle = (math.pow(a, 2) + math.pow(b, 2) - math.pow(c, 2)) / (2 * a * b)
    except ZeroDivisionError:
        raise

    # Handle invalid cos_angle
    if cos_angle > 1:
        cos_angle = 1
    elif cos_angle < -1:
        cos_angle = -1

    angle_ACB = math.acos(cos_angle)
    return angle_ACB


def sort_corners(corner1, corner2, corner3, corner4):
    """
    Sort the corners such that
    - A is top left
    - B is top right
    - C is bottom left
    - D is bottom right
    Return an (A, B, C, D) tuple
    """
    results = []
    corners = (corner1, corner2, corner3, corner4)

    min_x = None
    max_x = None
    min_y = None
    max_y = None

    for (x, y) in corners:
        if min_x is None or x < min_x:
            min_x = x
        if max_x is None or x > max_x:
            max_x = x
        if min_y is None or y < min_y:
            min_y = y
        if max_y is None or y > max_y:
            max_y = y

    # top left
    top_left = None
    top_left_distance = None
    for (x, y) in corners:
        distance = pixel_distance((min_x, min_y), (x, y))
        if top_left_distance is None or distance < top_left_distance:
            top_left = (x, y)
            top_left_distance = distance

    results.append(top_left)

    # top right
    top_right = None
    top_right_distance = None
    for (x, y) in corners:
        if (x, y) in results:
            continue
        distance = pixel_distance((max_x, min_y), (x, y))
        if top_right_distance is None or distance < top_right_distance:
            top_right = (x, y)
            top_right_distance = distance
    results.append(top_right)

    # bottom left
    bottom_left = None
    bottom_left_distance = None
    for (x, y) in corners:
        if (x, y) in results:
            continue
        distance = pixel_distance((min_x, max_y), (x, y))
        if bottom_left_distance is None or distance < bottom_left_distance:
            bottom_left = (x, y)
            bottom_left_distance = distance
    results.append(bottom_left)

    # bottom right
    bottom_right = None
    bottom_right_distance = None
    for (x, y) in corners:
        if (x, y) in results:
            continue
        distance = pixel_distance((max_x, max_y), (x, y))
        if bottom_right_distance is None or distance < bottom_right_distance:
            bottom_right = (x, y)
            bottom_right_distance = distance
    results.append(bottom_right)

    return results


def approx_is_square(approx, SIDE_VS_SIDE_THRESHOLD=0.60, ANGLE_THRESHOLD=20):
    """
    Rules
    - there must be four corners
    - all four lines must be roughly the same length
    - all four corners must be roughly 90 degrees
    """
    # There must be four corners
    if len(approx) != 4:
        return False

    # Find the four corners
    (A, B, C, D) = sort_corners(
        tuple(approx[0][0]),
        tuple(approx[1][0]),
        tuple(approx[2][0]),
        tuple(approx[3][0]),
    )

    # Find the lengths of all four sides
    AB = pixel_distance(A, B)
    AC = pixel_distance(A, C)
    DB = pixel_distance(D, B)
    DC = pixel_distance(D, C)
    distances = (AB, AC, DB, DC)
    max_distance = max(distances)
    cutoff = int(max_distance * SIDE_VS_SIDE_THRESHOLD)

    # If any side is much smaller than the longest side, return False
    for distance in distances:
        if distance < cutoff:
            return False

    # all four corners must be roughly 90 degrees
    min_angle = 90 - ANGLE_THRESHOLD
    max_angle = 90 + ANGLE_THRESHOLD

    # Angle at A
    angle_A = int(math.degrees(get_angle(C, B, A)))
    if angle_A < min_angle or angle_A > max_angle:
        return False

    # Angle at B
    angle_B = int(math.degrees(get_angle(A, D, B)))
    if angle_B < min_angle or angle_B > max_angle:
        return False

    # Angle at C
    angle_C = int(math.degrees(get_angle(A, D, C)))
    if angle_C < min_angle or angle_C > max_angle:
        return False

    # Angle at D
    angle_D = int(math.degrees(get_angle(C, B, D)))
    if angle_D < min_angle or angle_D > max_angle:
        return False

    return True


def square_width_height(approx):
    """
    Return the width and height of the square.
    """
    width = 0
    height = 0

    # Find the four corners
    (A, B, C, D) = sort_corners(
        tuple(approx[0][0]),
        tuple(approx[1][0]),
        tuple(approx[2][0]),
        tuple(approx[3][0]),
    )

    # Find the lengths of all four sides
    AB = pixel_distance(A, B)
    AC = pixel_distance(A, C)
    DB = pixel_distance(D, B)
    DC = pixel_distance(D, C)

    width = max(AB, DC)
    height = max(AC, DB)

    return (width, height)


def sort_by_row_col(contours, size=3):
    """
    Sort contours by row and column for a 3x3 grid
    """
    result = []

    for row_index in range(size):
        # Get contours in this row
        row_contours = []
        for con in contours:
            M = cv2.moments(con)
            if M["m00"]:
                cY = int(M["m01"] / M["m00"])
                row_contours.append((cY, con))

        # Sort by Y and take the top size contours
        row_contours.sort()
        top_row = row_contours[:size]

        # Now sort by X
        row_by_x = []
        for (cY, con) in top_row:
            M = cv2.moments(con)
            cX = int(M["m10"] / M["m00"])
            row_by_x.append((cX, con))

        row_by_x.sort()
        for (cX, con) in row_by_x:
            result.append(con)

        # Remove used contours
        for (_, con) in top_row:
            contours.remove(con)

    return result


def extract_colors_from_image(image_path):
    """
    Extract RGB colors from a 3x3 Rubik's cube face image.
    Returns a list of 9 RGB tuples, ordered top-left to bottom-right.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Remove noise
    nonoise = cv2.fastNlMeansDenoising(gray, 10, 15, 7, 21)

    # Canny edge detection
    canny = cv2.Canny(nonoise, 5, 10)

    # Dilate to thicken edges
    kernel = np.ones((4, 4), np.uint8)
    dilated = cv2.dilate(canny, kernel, iterations=4)

    # Find contours
    contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.1 * peri, True)
        area = cv2.contourArea(contour)

        if len(approx) == 4 and area > 30 and approx_is_square(approx):
            candidates.append(contour)

    if len(candidates) != 9:
        raise ValueError(f"Expected 9 squares, found {len(candidates)}")

    # Sort candidates into 3x3 grid
    sorted_contours = sort_by_row_col(candidates, 3)

    # Extract RGB values
    colors = []
    for contour in sorted_contours:
        mask = np.zeros(gray.shape, np.uint8)
        cv2.drawContours(mask, [contour], 0, 255, -1)
        (mean_blue, mean_green, mean_red, _) = cv2.mean(image, mask=mask)
        colors.append((int(mean_red), int(mean_green), int(mean_blue)))

    return colors
