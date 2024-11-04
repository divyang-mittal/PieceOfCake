from shapely.ops import split
from shapely.geometry import Polygon, LineString
import numpy as np
import miniball


def sneak(start_pos, end_pos, cake_width, cake_len):
    """
    Given a start position & goal position, uses the 1-pixel shaving technique
    to create a list of necessary steps to get from the start to the goal without
    cutting across the cake.
    """
    nearest_x, x_dist = nearest_edge_x(start_pos, cake_width)
    nearest_y, y_dist = nearest_edge_y(start_pos, cake_len)

    end_x, end_x_dist = nearest_edge_x(end_pos, cake_width)
    end_y, end_y_dist = nearest_edge_y(end_pos, cake_len)

    moves = []

    # if we are on the top or bottom or the board and require more than 1 move
    if y_dist == 0 and (x_dist > 0.1 or nearest_x != end_x):
        bounce_y = bounce(nearest_y)
        moves.append([end_x, bounce_y])

        # if the end is not on the same line so we must ricochet off of corner
        if end_y_dist > 0 or nearest_y != end_y:
            bounce_x = bounce(end_x)
            moves.append([bounce_x, nearest_y])

            # if the end position is on the opposite side
            if end_y_dist == 0:
                bounce_y = bounce(end_y)
                moves.append([bounce_x, end_y])
                moves.append([end_x, bounce_y])

    # if we are on the left or right side of the board and require more than 1 move
    elif x_dist == 0 and (y_dist > 0.1 or nearest_y != end_y):
        bounce_x = bounce(nearest_x)
        moves.append([bounce_x, end_y])

        # if the end is not on the same line so we must ricochet off of corner
        if end_x_dist > 0 or nearest_x != end_x:
            bounce_y = bounce(end_y)
            moves.append([nearest_x, bounce_y])

            # if the end position is on the opposite side
            if end_x_dist == 0:
                bounce_x = bounce(end_x)
                moves.append([end_x, bounce_y])
                moves.append([bounce_x, end_y])

    moves.append(end_pos)
    return moves


def nearest_edge_x(pos, cake_width):
    """
    Returns the nearest X-edge and the distance to said edge
    X-edge is 0 if the position is closer to the left side, or cake_width
        if it is closer to the right side.
    """
    min_x = pos[0]
    x_edge = 0
    if cake_width - pos[0] < min_x:
        min_x = cake_width - pos[0]
        x_edge = cake_width
    return x_edge, min_x


def nearest_edge_y(pos, cake_len):
    """
    Returns the nearest Y-edge and the distance to said edge
    Y-edge is 0 if the position is closer to the top, or cake_len
        if it is closer to the bottom.
    """
    min_y = pos[1]
    y_edge = 0
    if cake_len - pos[1] < min_y:
        min_y = cake_len - pos[1]
        y_edge = cake_len
    return y_edge, min_y


def bounce(margin):
    """
    Returns a value 0.01 away from the provided margin
    """
    if margin == 0:
        return 0.01
    return round(margin - 0.01, 2)


def divide_polygon(polygon: Polygon, from_point, to_point):
    """
    Divide a convex polygon by a line segment into two polygons.

    Parameters:
    - polygon: A convex polygon (as a Shapely Polygon object)
    - line_points: A list containing two points that represent the line segment

    Returns:
    - Two polygons (as shapely Polygon objects) that result from dividing the original polygon
    """

    line = LineString([tuple(from_point), tuple(to_point)])
    # Create the convex polygon and the line segment using Shapely
    # polygon = Polygon(polygon_points)
    # line = LineString(line_points)

    # Check if the line intersects with the polygon
    if not line.intersects(polygon):
        return [polygon]
    # Split the polygon into two pieces
    result = split(polygon, line)

    # Convert the result into individual polygons

    polygons = []
    for i in range(len(result.geoms)):
        polygons.append(result.geoms[i])

    return polygons


def can_cake_fit_in_plate(cake_piece, radius=12.5):
    """
    Check if the cake can fit inside a plate of radius 12.5.

    Parameters:
    - cake_pieces: Cake pieces (as shapely Polygon object)
    - radius: The radius of the circle

    Returns:
    - True if the cake can fit inside the plate, False otherwise
    """
    # Step 1: Get the points on the cake piece and store as numpy array

    cake_points = np.array(list(zip(*cake_piece.exterior.coords.xy)), dtype=np.double)

    # Step 2: Find the minimum bounding circle of the cake piece
    res = miniball.miniball(cake_points)

    return res["radius"] <= radius
