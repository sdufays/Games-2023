direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    num_rows = len(level_description)
    num_cols = len(level_description[0])
    player_position = None
    targets = set()
    computers = set()
    walls = set()

    board = []
    for i, row in enumerate(level_description):
        new_row = []
        for j, cell in enumerate(row):
            new_cell = set(cell)
            new_row.append(new_cell)

            if "player" in new_cell:
                player_position = (i, j)
            if "target" in new_cell:
                targets.add((i, j))
            if "computer" in new_cell:
                computers.add((i, j))
            if "wall" in new_cell:
                walls.add((i, j))

        board.append(tuple(new_row))

    return {
        # "board": tuple(board),
        "walls": walls,
        "player_position": player_position,
        "targets": targets,
        "computers": computers,
        "board_columns": num_cols,
        "board_rows": num_rows,
    }


def victory_check(game):
    if not game["targets"] or not game["computers"]:
        return False

    return game["targets"].issubset(game["computers"])


def step_game(game, direction):
    player_position = game["player_position"]
    computers = set(game["computers"])
    targets = set(game["targets"])
    walls = set(game["walls"])

    delta = direction_vector[direction]
    new_position = (player_position[0] + delta[0], player_position[1] + delta[1])

    if new_position in walls:
        return game

    if new_position not in computers:  # if there is an open space for the player
        player_position = new_position
    else:  # if there is a computer in the new_position
        computer_new_position = (new_position[0] + delta[0], new_position[1] + delta[1])
        # if the computer's new position is in bounds /
        #  there is not a wall or computer in its new position
        if (
            computer_new_position not in walls
            and computer_new_position not in computers
        ):
            computers.remove(new_position)
            computers.add(computer_new_position)

            player_position = new_position
        else:
            return game

    return {
        "walls": walls,
        "player_position": player_position,
        "targets": targets,
        "computers": computers,
        "board_columns": game["board_columns"],
        "board_rows": game["board_rows"],
    }


def dump_game(game):
    num_cols = game["board_columns"]
    num_rows = game["board_rows"]

    computers = set(game["computers"])
    targets = set(game["targets"])
    walls = set(game["walls"])
    player = game["player_position"]

    items = [(computers, "computer"), (targets, "target"), (walls, "wall")]

    board = []

    # create empty board
    for _ in range(num_rows):
        row_list = []
        for _ in range(num_cols):
            col_list = []
            row_list.append(col_list)
        board.append(row_list)

    # start to populate the board
    board[player[0]][player[1]].append("player")
    for sets, name in items:
        for x_loc, y_loc in sets:
            board[x_loc][y_loc].append(name)

    return board


def solve_puzzle(game):
    if victory_check(game):
        return []

    queue = [(game, [])]
    visited = {(game["player_position"], frozenset(game["computers"]))}

    while queue:
        current_game, current_path = queue.pop(0)

        for move in ["up", "down", "left", "right"]:
            next_game = step_game(current_game, move)

            for x, y in next_game["computers"]:
                if not (x, y) in next_game["targets"]:
                    continue

            game_hash = (
                next_game["player_position"],
                frozenset(next_game["computers"]),
            )

            if game_hash not in visited:
                visited.add(game_hash)
                new_path = current_path + [move]

                if victory_check(next_game):
                    return new_path

                queue.append((next_game, new_path))

    return None


if __name__ == "__main__":
    pass
