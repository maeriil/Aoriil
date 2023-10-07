def unpack_box(box: tuple) -> (list, list, list, list):
    """"""
    if box is None:
        raise ValueError("Did not provide a box to unpack")
    if len(box) != 4:
        raise ValueError("Inappropriate amount of values provided to box")

    (top_left, top_right, bottom_right, bottom_left) = box

    # each of them could be float64 format. We will round them to integer
    top_left = list(map(round, top_left))
    top_right = list(map(round, top_right))
    bottom_right = list(map(round, bottom_right))
    bottom_left = list(map(round, bottom_left))

    return top_left, top_right, bottom_right, bottom_left


def calculate_width(box: tuple) -> int:
    """"""
    (top_left, top_right, _, _) = unpack_box(box)

    return calculate_width(top_left, top_right)


def calculate_width(left_point: list, right_point: list) -> int:
    """"""
    return abs(left_point[0] - right_point[0])


def calculate_width(left_point_x: int, right_point_x: int) -> int:
    """"""
    return abs(left_point_x - right_point_x)


def calculate_height(box: tuple) -> int:
    """"""
    (top_left, _, _, bottom_left) = unpack_box(box)

    return calculate_height(top_left, bottom_left)


def calculate_height(left_point: list, right_point: list) -> int:
    """"""
    return abs(left_point[1] - right_point[1])


def calculate_height(left_point_y: int, right_point_y: int) -> int:
    """"""
    return abs(left_point_y - right_point_y)
