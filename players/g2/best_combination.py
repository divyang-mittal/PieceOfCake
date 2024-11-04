from typing import Callable
from shapely.geometry import Polygon
import constants
from players.g2.assigns import sorted_assign
from players.g2.helpers import sneak, divide_polygon, can_cake_fit_in_plate
import random


def get_cuts_spread(requests: list[float]) -> tuple[int, int]:
    count = len(requests)

    # the absolute maximum number of cuts required to match the number of requests
    # in practice, this should never be reached
    max_cuts = count - 1

    # an average cut will create 3 new slices
    # * Actually, its dependent on the number of existing cuts,
    # * the more existing cuts on the cake, the more slices will be created
    # * from the next cut
    min_cuts = count // 3

    # ensure max_cuts > min_cuts
    max_cuts = max(max_cuts, min_cuts + 1)

    return min_cuts, max_cuts


def find_best_cuts(
    requests: list[float], cuts: int, cake_len: float, cake_width: float
) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    # how many different points should be considered on each edge
    JUMPS = 6
    GAP = JUMPS - 1
    LEFT = [(0, round(cake_len * i / GAP, 2)) for i in range(JUMPS)]
    RIGHT = [(cake_width, round(cake_len * i / GAP, 2)) for i in range(JUMPS)]
    UP = [(round(cake_width * i / GAP, 2), 0) for i in range(JUMPS)]
    DOWN = [(round(cake_width * i / GAP, 2), cake_len) for i in range(JUMPS)]

    points = set(LEFT + RIGHT + UP + DOWN)

    selected: set[tuple[tuple[float, float], tuple[float, float]]] = set()

    while len(selected) < cuts:
        from_point = random.sample(list(points), 1)[0]

        if from_point in LEFT:
            to_point = random.sample(list(points.difference(LEFT)), 1)[0]
        elif from_point in RIGHT:
            to_point = random.sample(list(points.difference(RIGHT)), 1)[0]
        elif from_point in UP:
            to_point = random.sample(list(points.difference(UP)), 1)[0]
        else:
            to_point = random.sample(list(points.difference(DOWN)), 1)[0]

        if (from_point, to_point) not in selected or (
            to_point,
            from_point,
        ) not in selected:
            selected.add((from_point, to_point))

    return list(selected)


def __calculate_penalty(
    assign_func: Callable[[list[Polygon], list[float]], list[int]],
    requests: list[float],
    polygons: list[Polygon],
    tolerance=0,
) -> float:
    penalty = 0
    assignments: list[int] = assign_func(polygons, requests, tolerance)

    for request_index, assignment in enumerate(assignments):
        # check if the cake piece fit on a plate of diameter 25 and calculate penaly accordingly
        if assignment == -1 or (not can_cake_fit_in_plate(polygons[assignment])):
            penalty += 100
        else:
            penalty_percentage = (
                100
                * abs(polygons[assignment].area - requests[request_index])
                / requests[request_index]
            )
            if penalty_percentage > tolerance:
                penalty += penalty_percentage
    return penalty


def penalty(
    cuts: list[tuple[tuple[float, float], tuple[float, float]]],
    requests: list[float],
    cake_len,
    cake_width,
    # tolerance,
):
    polygons = [
        Polygon(
            [
                (0, 0),
                (0, cake_len),
                (cake_width, cake_len),
                (cake_width, 0),
            ]
        )
    ]

    for cut in cuts:
        from_point = cut[0]
        to_point = cut[1]
        new_polygons = []
        for polygon in polygons:
            new_polygons.extend(divide_polygon(polygon, from_point, to_point))

        polygons = new_polygons

    return __calculate_penalty(sorted_assign, requests, polygons)


def best_combo(
    requests: list[float], cake_len: float, cake_width: float
) -> list[tuple[tuple[float, float], tuple[float, float]]]:

    min_cuts, max_cuts = get_cuts_spread(requests)

    best_cuts = []
    min_penalty = curr_penalty = float("inf")
    for cuts in range(min_cuts, max_cuts + 1):
        cuts_contender = find_best_cuts(requests, cuts, cake_len, cake_width)

        if (
            not best_cuts
            or (curr_penalty := penalty(cuts_contender, requests, cake_len, cake_width))
            < min_penalty
        ):
            best_cuts = cuts_contender
            min_penalty = curr_penalty

    return best_cuts


def cuts_to_moves(
    cuts: list[tuple[tuple[float, float], tuple[float, float]]], cake_len, cake_width
) -> list[tuple[int, list]]:
    moves = []
    last_point = None
    for cut in cuts:
        from_point = list(cut[0])
        to_point = list(cut[1])
        if not moves:
            moves.append((constants.INIT, from_point))
        else:
            sneak_points = sneak(last_point, from_point, cake_width, cake_len)
            for point in sneak_points:
                # moves.append((constants.CUT, [last_point, point]))
                moves.append((constants.CUT, point))
                last_point = point

        # moves.append((constants.CUT, [from_point, to_point]))
        moves.append((constants.CUT, to_point))
        last_point = to_point

    # TODO: figure out assignment
    # moves.append(sorted_assign)

    return moves
