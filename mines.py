#!/usr/bin/env python3

import doctest

def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION
def new_game_2d(nrows, ncolumns, mines):
    """
    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    dimensions = (nrows, ncolumns)
    mines_nd = [(mine[0], mine[1]) for mine in mines]
    return new_game_nd(dimensions, mines_nd)


def check_game_state(game):
    """
     Evaluate the current state of the Minesweeper game based on the board's condition

    Parameters:
        game (dict): A dictionary representing the game state, including the dimensions
        of the board, the board itself, the visibility status of each square,
        and the current game state ('victory',
        'defeat', or 'ongoing').

    Returns:
        None: The function modifies the 'state' field in the game dictionary
        to reflect the current state ('victory', 'defeat', or 'ongoing').

    """
    return check_game_state_nd(game)


def dig_2d(game, row, col):
    """
    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    coordinates = (row, col)
    return dig_nd(game, coordinates)


def render_2d_locations(game, all_visible=False):
    """
    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    render_nd_output = render_nd(game, all_visible)

    def recursive_convert_to_2d(nd_output):
        if isinstance(nd_output[0], str):
            return nd_output
        return [recursive_convert_to_2d(sublist) for sublist in nd_output]

    return recursive_convert_to_2d(render_nd_output)


def render_2d_board(game, all_visible=False):
    """
    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    render_2d_output = render_2d_locations(game, all_visible)

    def recursive_convert_to_string(output):
        if isinstance(output[0], str):
            return "".join(output)
        return "\n".join([recursive_convert_to_string(sublist) for sublist in output])

    return recursive_convert_to_string(render_2d_output)


# N-D IMPLEMENTATION

# helper functions


def generate_nd_board(dim, val):
    if len(dim) == 1:
        return [val] * dim[0]
    else:
        return [generate_nd_board(dim[1:], val) for _ in range(dim[0])]


def get_value(nd_array, coordinates):
    value = nd_array
    for coord in coordinates:
        value = value[coord]  # sets value to a smaller and smaller list
    return value


def set_value(nd_array, coordinates, value):
    target = nd_array
    for coord in coordinates[:-1]:  # all except last value of coordinates
        target = target[coord]
    target[coordinates[-1]] = value  # last value of coordinates


# iterative version
def check_game_state_nd(game):
    dimensions = game["dimensions"]
    num_dimensions = len(dimensions)
    board = game["board"]
    visible = game["visible"]

    num_unrevealed_squares = 0
    num_revealed_safe_squares = 0
    num_safe_squares = 0

    def increment_indices(indices):
        for i in range(num_dimensions - 1, -1, -1):
            indices[i] += 1
            if indices[i] < dimensions[i]:
                return True  # dimension index is still within bounds, move to next coordinates
            indices[
                i
            ] = 0  # dimension index is out of bounds, reset it & increment the next dimension
        return False  # iterated through the entire board already

    indices = [0] * num_dimensions

    while True:
        coords = tuple(indices)
        value = get_value(board, coords)
        is_visible = get_value(visible, coords)

        if is_visible and value == ".":
            game["state"] = "defeat"
            return
        elif not is_visible:
            num_unrevealed_squares += 1

        if value != ".":
            num_safe_squares += 1
            if is_visible:
                num_revealed_safe_squares += 1

        if not increment_indices(indices):
            break  # iterated through the entire board already

    game["state"] = (
        "victory"
        if num_unrevealed_squares == 0 or num_safe_squares == num_revealed_safe_squares
        else "ongoing"
    )


def get_neighbors(game, coordinates):
    dimensions = game["dimensions"]
    num_dimensions = len(dimensions)
    neighbors = []

    # generate neighbors
    def recursive_neighbors(coords, depth):
        if depth == num_dimensions:
            if coords != coordinates:  # Exclude the original coordinates
                neighbors.append(coords)
            return
        for delta in [-1, 0, 1]:
            new_coord = coords[depth] + delta
            if 0 <= new_coord < dimensions[depth]:
                recursive_neighbors(
                    coords[:depth] + (new_coord,) + coords[depth + 1 :], depth + 1
                )

    recursive_neighbors(coordinates, 0)
    return neighbors


def get_all_coordinates(game):
    dimensions = game["dimensions"]
    num_dimensions = len(dimensions)
    coordinates = []

    # generate coordinates
    def recursive_coordinates(coords, depth):
        if depth == num_dimensions:
            coordinates.append(coords)
            return
        for i in range(dimensions[depth]):
            recursive_coordinates(
                coords[:depth] + (i,) + coords[depth + 1 :], depth + 1
            )

    recursive_coordinates((), 0)
    return coordinates


def new_game_nd(dimensions, mines):
    """
    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    # Generate N-dimensional board filled with zeros

    new_board = generate_nd_board(dimensions, 0)
    visible = generate_nd_board(dimensions, False)

    # set the mine locations on the board
    for mine in mines:
        set_value(new_board, mine, ".")

    # mine counts for each location on the board
    all_coords = get_all_coordinates(
        {"dimensions": dimensions}
    )  # Get all coordinates in the board
    for coords in all_coords:
        if get_value(new_board, coords) != ".":  # Skip mine locations
            neighbors = get_neighbors(
                {"dimensions": dimensions}, coords
            )  # neighboring coordinates
            mine_count = sum(
                get_value(new_board, neighbor) == "." for neighbor in neighbors
            )  # count neighboring mines
            set_value(new_board, coords, mine_count)  # Update board with mine count

    return {
        "dimensions": dimensions,
        "board": new_board,
        "visible": visible,
        "state": "ongoing",
    }


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    if game["state"] != "ongoing":
        return 0  # Return 0 if game state is not ongoing

    board = game["board"]
    visible = game["visible"]
    check_game_state_nd(game)

    initial_value = get_value(board, coordinates)
    if initial_value == ".":
        set_value(visible, coordinates, True)
        game["state"] = "defeat"
        return 1

    if get_value(visible, coordinates):
        return 0

    set_value(visible, coordinates, True)  # Set the cell as visible
    revealed = 1  # The initial square is revealed

    def recursive_dig(coords):
        current_revealed = 0
        value = get_value(board, coords)
        if get_value(visible, coords) or value == ".":
            return 0  # Return if square is already visible or is a mine

        # Reveal the current square
        set_value(visible, coords, True)
        current_revealed += 1

        # Recursively dig neighbors if current square value is 0
        if value == 0:
            for neighbor in get_neighbors(game, coords):
                current_revealed += recursive_dig(neighbor)

        return current_revealed

    # If the value at the initial coordinates is 0, start recursive digging for its neighbors
    if initial_value == 0:
        for neighbor in get_neighbors(game, coordinates):
            revealed += recursive_dig(neighbor)

    check_game_state_nd(game)

    return revealed


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """

    def recursive_render(board, visible, coords=()):
        # Base case: if all dimensions are specified, return value at coords
        if len(coords) == len(game["dimensions"]):
            value = get_value(board, coords)
            is_visible = get_value(visible, coords)
            if all_visible or is_visible:
                if value == 0:
                    return " "
                elif value == ".":
                    return "."
                else:
                    return str(value)
            else:
                return "_"
        # Recursive case: build list by traversing the next dimension
        else:
            return [
                recursive_render(board, visible, coords + (i,))
                for i in range(game["dimensions"][len(coords)])
            ]

    # Start recursive rendering at top level
    return recursive_render(game["board"], game["visible"])


if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
