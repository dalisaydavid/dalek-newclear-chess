from math import atan2
from board import Board
import operator
import datetime
from copy import deepcopy

# All generated moves in generate_all_moves() function.
moves = {
    'b': [[[] for _ in range(9)] for _ in range(64)],
    'r': [[[] for _ in range(9)] for _ in range(64)],
    'n': [[[] for _ in range(9)] for _ in range(64)],
    'p': [[[] for _ in range(9)] for _ in range(64)],
    'P': [[[] for _ in range(9)] for _ in range(64)],
    'k': [[[] for _ in range(9)] for _ in range(64)],
    'K': [[[] for _ in range(9)] for _ in range(64)]
}

# All pieces and their initial legal move logic.
pieces = {
    'b': lambda x_move, y_move: abs(x_move) == abs(y_move),
    'r': lambda x_move, y_move: abs(x_move) == 0 or abs(y_move) == 0,
    'n': lambda x_move, y_move: (abs(x_move) + abs(y_move) == 3 and abs(x_move) > 0 and abs(y_move) > 0),
    'p': lambda x_move, y_move: (x_move == -1 and abs(y_move) <= 1),
    'P': lambda x_move, y_move: (x_move == 1 and abs(y_move) <= 1),
    'k': lambda x_move, y_move: (x_move == -1 and abs(y_move) <= 1),
    'K': lambda x_move, y_move: (x_move == 1 and abs(y_move) <= 1)
}

# Determinates whether or not certain pieces can explode themselves.
explosions = {
    'b': True,
    'r': True,
    'n': True,
    'p': True,
    'k': False
}

# All directions that pieces can move.
# @TODO: Redo the order of these directions. Because right now, South is commented as North for All Pieces*.
directions = [
    atan2(0,1),     # All Pieces* North
    atan2(1,1),     # All Pieces* NorthEast
    atan2(1,0),     # All Pieces* East
    atan2(1,-1),    # All Pieces* SouthEast
    atan2(0,-1),    # All Pieces* South
    atan2(-1,-1),   # All Pieces* SouthWest
    atan2(-1,0),    # All Pieces* West
    atan2(-1,1),    # All Pieces* NorthWest
    atan2(1,2),     # Knight NorthEast Vertical
    atan2(2,1),     # Knight NorthEast Horizontal
    atan2(2,-1),    # Knight SouthEast Horizontal
    atan2(1,-2),    # Knight SouthEast Vertical
    atan2(-1,-2),   # Knight SouthWest Vertical
    atan2(-2,-1),   # Knight SouthWest Horizontal
    atan2(-2,1),    # Knight NorthWest Horizontal
    atan2(-1,2),    # Knight NorthWest Vertical
]

# Material scores for the evaluation function.
# This determines the weight for each peice.
material = {
    'p': 100,
    'n': 300,
    'b': 300,
    'r': 500,
    'k': 20000
}

# Piece square table scores for the evaluation function.
# This determines the score of a piece at in a certain location.
piece_square_tables = {
    'p':
        [
            [  0,  0,   0,  0,   0,  0,  0], 
            [  0,  0,   0,  0,   0,  0,  0], 
            [  0,  0,   0,  0,   0,  0,  0], 
            [-10,  0, -10,  0, -10,  0,-10], 
            [  5, 10,  20, 20,  20, 20,  5], 
            [ 10, 20,  20, 20,  20, 20, 10], 
            [  0,  0,   0,  0,   0,  0,  0], 
            [  0,  0,   0,  0,   0,  0,  0], 
            [  0,  0,   0,  0,   0,  0,  0], 
        ],
    'n':
        [
            [-50, -40, -30, -30, -30, -40, -50],
            [-40, -20,   0,   0,   0, -20, -40],
            [-30,  10,  10,  15,  10,  10, -30],
            [-30,  10,  40,  40,  40,  10, -30],
            [-30,  10,  40,  40,  40,  10, -30],
            [-30,  10,  40,  40,  40,  10, -30],
            [-30,  10,  10,  10,  10,  10, -30],
            [-40, -20,   0,   0,   0, -20, -40], 
            [-50, -40, -30, -30, -30, -40, -50], 
        ],
    'b':
        [
            [-20, -10, -10, -10, -10, -10, -20],
            [-10,   0,   0,   0,   0,   0, -10],
            [-10,   0,  10,  20,  10,   0, -10],
            [-10,  10,  10,  20,  10,  10, -10],
            [-10,  10,  20,  20,  20,  10, -10],
            [-10,   0,  20,  20,  20,   0, -10],
            [-10,  20,  20,  20,  20,  20, -10],
            [-10,  10,   0,   0,   0,  10, -10],
            [-20, -10, -10, -10, -10, -10, -20],
        ],
    'r':
        [
            [ 0,  0,  0,  0,  0,  0,  0],
            [-5,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0, -5],
            [-5, 10, 10, 10, 10, 10, -5],
            [ 5, 20, 20, 20, 20, 20,  5],
            [ 0,  0,  0,  0,  0,  0,  0],
        ],
    'k':
        [
            [20, 30, 10, 0, 10, 30, 20],
            [20, 20, 0, 0, 0, 20, 20],
            [-5, -15, -15, -20, -15, -15, -5],
            [-10, -20, -20, -30, -20, -20, -10],
            [-20, -30, -30, -40, -30, -30, -20],
            [-30, -40, -40, -50, -40, -40, -0],
            [-30, -40, -40, -50, -40, -40, -0],
            [-30, -40, -40, -50, -40, -40, -0],
            [-30, -40, -40, -50, -40, -40, -0]
        ]
}

# This table remembers board states and their evaluations.
# This table prevents re-evaluating board states.
transposition_table = {}

# This killer moves table remembers the two last moves that produce 
# alpha-beta cutoffs at each depth..
killer_moves = {
    # depth:
        # [hashed_move_key1...hashed_move_keyn]
}

# Position mapping when giving to enemy bot. 
inverted_position_mapping = {
    'a1': 'g9',
    'a2': 'g8',
    'a3': 'g7',
    'a4': 'g6',
    'a5': 'g5',
    'a6': 'g4',
    'a7': 'g3',
    'a8': 'g2',
    'a9': 'g1',
    'b1': 'f9',
    'b2': 'f8',
    'b3': 'f7',
    'b4': 'f6',
    'b5': 'f5',
    'b6': 'f4',
    'b7': 'f3',
    'b8': 'f2',
    'b9': 'f1',
    'c1': 'e9',
    'c2': 'e8',
    'c3': 'e7',
    'c4': 'e6',
    'c5': 'e5',
    'c6': 'e4',
    'c7': 'e3',
    'c8': 'e2',
    'c9': 'e1',
    'd1': 'd9',
    'd2': 'd8',
    'd3': 'd7',
    'd4': 'd6',
    'd5': 'd5',
    'd6': 'd4',
    'd7': 'd3',
    'd8': 'd2',
    'd9': 'd1',
    'e1': 'c9',
    'e2': 'c8',
    'e3': 'c7',
    'e4': 'c6',
    'e5': 'c5',
    'e6': 'c4',
    'e7': 'c3',
    'e8': 'c2',
    'e9': 'c1',
    'f1': 'b9',
    'f2': 'b8',
    'f3': 'b7',
    'f4': 'b6',
    'f5': 'b5',
    'f6': 'b4',
    'f7': 'b3',
    'f8': 'b2',
    'f9': 'b1',
    'g1': 'a9',
    'g2': 'a8',
    'g3': 'a7',
    'g4': 'a6',
    'g5': 'a5',
    'g6': 'a4',
    'g7': 'a3',
    'g8': 'a2',
    'g9': 'a1'
}

# Gets a nifty string hash key to remember moves quicker.
def get_move_hash(piece, move_from, move_to):
    return "{piece}{move_from}{move_to}".format(
        piece=piece,
        move_from=str(move_from[0])+str(move_from[1]),
        move_to=str(move_to[0])+str(move_to[1])
    )

# Does the inverse of get_move_hash function.
def unhash_move(move_hash):
    return (move_hash[0], (int(move_hash[1]),int(move_hash[2])), (int(move_hash[3]),int(move_hash[4])))

# Times a function. Used as decorator.
def time_function(f):
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        result = f(*args, **kwargs)
        end = datetime.datetime.now()
        seconds = (end-start).seconds
        if seconds > 0:
            print("{0} function took {1} seconds to finish.".format(f, (end-start).seconds))
        return result
    return wrapper

# Generates all moves using directional rays.
@time_function
def generate_all_moves():
    """
    moves['q'][7][0] = [6, 5, 4, 3, 2, 1, 0]  # sorted by distance from idx = 7
    moves[<piece>][<starting index>][<direction>] = [list of moves]
    """

    #      - N R K R N -    0  through 6
    #      - - - B - - -    7  through 13
    #      - - - B - - -    14 through 20
    #      P - P - P - P    21 through 27
    #      - - - - - - -    28 through 34
    #      p - p - p - p    35 through 41
    #      - - - b - - -    42 through 48
    #      - - - b - - -    49 through 55
    #      - n r k r n -    56 through 62

    # Go through every piece.
    for piece_name, legal_move in pieces.items():
        # Go through every possible starting position on the board.
        for start_index in range(63):
            # Go through every possible ending position on the board.
            start_row = abs((7-(start_index+1))//7)
            start_col = start_index%7

            # Ensure we're looking at the closest positions first.
            for end_index in sorted(range(63), key=lambda sort_end_index: abs(sort_end_index - start_index)):
                end_row = abs((7-(end_index+1))//7)
                end_col = end_index%7

                x_move = end_row - start_row
                y_move = end_col - start_col

                # Handle explosions elsewhere...
                if start_index == end_index:
                    continue

                if legal_move(x_move, y_move):
                    direction = atan2(y_move, x_move)
                    # print("direction: {}".format(direction))
                    # raw_input()
                    if direction in directions:
                        # Get the index of the direction found in the list.
                        # And mod it by 9 (total number of distinct directions).
                        # Moding allows knight moves to be indexes between 0 and 9 as well.
                        direction_index = directions.index(direction) % 8
                            # print("start_index, end_index: {0}, {1}".format(start_index, end_index))
                            # print("start_row,start_col: {0},{1}".format(start_row,start_col))
                            # print("end_row,end_col: {0},{1}".format(end_row,end_col))
                            # print("x_move,y_move: {0},{1}".format(x_move,y_move))
                            # print("legal_move({0},{1}) = {2}".format(x_move,y_move,legal_move(x_move,y_move)))

                        moves[piece_name][start_index][direction_index].append(end_index)

# @param move: A2 or D2
# i.e. A is col 0, 2 is row 7.
@time_function
def convert_move_notation_to_board(move):
    # A == col 0
    # 2 == row 7
    x = 9-int(move[1])
    y = ord(move[0]) % 97
    return x,y

# @param move: (0,2) or (1,3)
# i.e. (0,7) = A2
@time_function
def convert_board_notation_to_move(move):
    x = str(9-move[0])
    y = chr(move[1]+97)
    return y+x

# Checks all the legal move things that aren't included in the pieces dictionary.
@time_function
def is_legal_move(piece, all_moves, start, end, indexed_board, board, humans_turn):
    # Check if the location the player is trying to move is empty...
    if piece == '-':
        return False

    # Check if the player is moving their own piece.
    if humans_turn:
        if piece.isupper():
            # print("Human can't move computer's pieces.")
            return False
    else: # its the computer's turn.
        if piece.islower():
            # print("Computer can't move human's pieces.")
            return False

    # Check if choosing to explode!
    if start[0] == end[0] and start[1] == end[1]:
        if not explosions[piece.lower()]:
            # print("{piece} can't explode.".format(piece=piece))
            return False
        else:
            return True

    # Check if the piece can move these amount of spaces.
    # print("start[0]: {0}, start[1]: {1}, end[0]: {2}, end[1]: {3}".format(start[0],start[1],end[0],end[1]))
    start_board_index = indexed_board[start[0]][start[1]]
    end_board_index = indexed_board[end[0]][end[1]]
    direction = atan2(end[1]-start[1], end[0]-start[0])
    if direction in directions:
        direction_index = directions.index(direction) % 8
    else:
        # print("{piece} doesn't know how to move in that direction.".format(piece=piece))
        return False
     
    ### DEBUGGING ###
    # print("all_moves[{piece}][{start_board_index}][{direction_index}]: {result}\n".format(
    #     piece=piece,
    #     start_board_index=start_board_index,
    #     direction_index=direction_index,
    #     result=all_moves[piece][start_board_index][direction_index]
    # ))
    
    move_piece = piece.lower() if piece not in ('P', 'K') else piece
    path = all_moves[move_piece][start_board_index][direction_index]
    if end_board_index not in path:
        # print("{piece} doesn't know how to move to ({end_x},{end_y}).".format(piece=piece, end_x=end[0], end_y=end[1]))
        return False

    # Check if the piece is trying to move backwards and is restricted to backwards captures!
    if piece.lower() in ['b','r','n']:
        if humans_turn:
            if end[0] > start[0]: # human is trying to move piece down, allowed if capture.
                if board[end[0]][end[1]].islower() or board[end[0]][end[1]] == '-':
                    return False
            # Check if the piece is trying to move sideways. It can only do so if its a capture!
            if piece.lower() == 'r':
                if end[0] == start[0] and end[1] != start[1]: # @TODO: Second condition is redundant methinks..
                    if board[end[0]][end[1]].islower() or board[end[0]][end[1]] == '-':
                        return False
        else:
            if end[0] < start[0]: # bot is trying to move piece up, allowed if capture.
                if board[end[0]][end[1]].isupper() or board[end[0]][end[1]] == '-':
                    return False

            if piece.lower() == 'r':
                if end[0] == start[0] and end[1] != start[1]: # @TODO: Second condition is redundant methinks..
                    if board[end[0]][end[1]].isupper() or board[end[0]][end[1]] == '-':
                        return False

        



    # Check for Pawn forward captures. If it's a diagonal movement, and there's no enemy piece, return False.
    if piece.lower() == 'p':
        if end[1] != start[1]: # is a diagonal movement.
            if board[end[0]][end[1]] == '-':
                return False
        else: # is a straight movement. Can't capture straight.
            if board[end[0]][end[1]] != '-':
                return False

    # Check if the piece's path is obstructed. 
    # We don't care about a knight's path, since they can jump over pieces.
    # This is sorted from the closest index to start_board_index to the furthest.
    if piece.lower() != "n":
        for p in range(path.index(end_board_index)):
            path_position_index = path[p]
            path_position_row = abs((7-(path_position_index+1))//7)
            path_position_col = path_position_index%7
            if board[path_position_row][path_position_col] != "-":
                # print("There's a piece obstructing that move.")
                return False

    # Check if the piece is trying to capture it's own piece.
    # We only care if it's a capture move.
    if board[end[0]][end[1]] != '-':
        if (piece.isupper() and board[end[0]][end[1]].isupper()) or (not piece.isupper() and not board[end[0]][end[1]].isupper()):
            # print("Can't capture your own piece.")
            return False

    return True

# Gets all the moves remaining on the board. This sucks, it's expensive.
@time_function
def get_all_remaining_moves(board, humans_turn, indexed_board, pieces_remaining):
    all_remaining_moves = [] # [(piece, (from_x,from_y),(to_x,to_y))]
    pieces_remaining_for_certain_player = filter(lambda p: p.islower() if humans_turn else p.isupper(), pieces_remaining)
    for piece in pieces_remaining_for_certain_player:
        # Go through each of the 63 moves for that piece. @TODO: Too much work. Fix this.
        for move_from_index in range(63):
            move_from_row = abs((7-(move_from_index+1))//7)
            move_from_col = move_from_index%7

            # If the piece isn't in the right position to make the move, skip this move index.
            if board[move_from_row][move_from_col] == "-" or board[move_from_row][move_from_col] != piece:
                continue

            # Add explosions to the moves!!!
            all_remaining_moves.append((piece, (move_from_row, move_from_col), (move_from_row, move_from_col)))

            move_piece = piece.lower() if piece not in ('P', 'K') else piece
            # Go through every direction, if there is at least 1 good direction, then you know there still might be a legal move.
            for direction in range(len(moves[move_piece][move_from_index])):
                for move_to_index in moves[move_piece][move_from_index][direction]:
                    move_to_row = abs((7-(move_to_index+1))//7)
                    move_to_col = move_to_index%7
                    if is_legal_move(piece, moves, (move_from_row,move_from_col), (move_to_row,move_to_col), indexed_board, board, humans_turn):
                        all_remaining_moves.append(
                            (piece, (move_from_row,move_from_col),(move_to_row,move_to_col))
                        )
    return all_remaining_moves

# Checks to see if the game is over.
# Returns tuple like (is_game_over, winner).
@time_function
def is_game_over(board, humans_turn, indexed_board, pieces_remaining):
    # Check to see if there's at least one king dead. 
    # If at least one king is dead, then the game's over.
    kings_alive = []
    for row in board:
        if 'k' in row:
            kings_alive.append('k')
        if 'K' in row:
            kings_alive.append('K')

        if len(kings_alive) >= 2:
            break

    # When explosion kills both kings,
    # the player committing the explosion loses.
    if not kings_alive:
        if humans_turn:
            return (True,'c') # Return 'c' if computer wins.
        else:
            return (True, 'h') # Return 'h' if human wins.
    elif len(kings_alive) == 1: # When one king is killed.
        if kings_alive[0].islower():
            return (True, 'h')
        else:
            return (True, 'c')

    # Check if there are still legal moves.
    # Only check pieces that are still on the board, but player that's making the move.
    pieces_remaining_for_certain_player = filter(lambda p: p.islower() if humans_turn else p.isupper(), pieces_remaining)
    for piece in pieces_remaining_for_certain_player:
        # Go through each of the 63 moves for that piece. @TODO: Too much work. Fix this.
        for move_from_index in range(63):
            move_from_row = abs((7-(move_from_index+1))//7)
            move_from_col = move_from_index%7

            # If the piece isn't in the right position to make the move, skip this move index.
            if board[move_from_row][move_from_col] == "-" or board[move_from_row][move_from_col] != piece:
                continue

            move_piece = piece.lower() if piece not in ('P', 'K') else piece
            # Go through every direction, if there is at least 1 good direction, then you know there's still a legal move.
            for direction in range(len(moves[move_piece][move_from_index])):
                for move_to_index in moves[move_piece][move_from_index][direction]:
                    move_to_row = abs((7-(move_to_index+1))//7)
                    move_to_col = move_to_index%7
                    if is_legal_move(piece, moves, (move_from_row,move_from_col), (move_to_row,move_to_col), indexed_board, board, humans_turn):
                        return (False, None)
    return (True, 'h' if humans_turn else 'c')

    # THIS WILL GO AWAY WHEN THE ABOVE PSUEDO CODE FOR LEGAL MOVES IS DONE!!!
    # return (False, None)

class TimesUpException(Exception):
    def __init__(self):
        print("TIMES UP.")

# @param time_elapsed: timedelta
def check_if_time_is_up(time_elapsed):
    if time_elapsed.seconds >= 5:
        raise TimesUpException()

# Start of minimax function.
@time_function
def minimax_start(board_object, max_depth, humans_turn):
    remaining_moves = get_all_remaining_moves(board_object.board, humans_turn, board_object.indexed_board, board_object.get_pieces_remaining().keys())
    
    # Used just in case best moves aren't found.
    last_move = None
    last_move_value = None

    best_move_value = -9999
    best_move = None

    time_elapsed = datetime.timedelta(0)
    # ITERATIVE DEEPENING || for current_depth in range(1, max_depth+1):
    for current_depth in range(2, max_depth+1):
        for piece, move_from, move_to in remaining_moves:
            try:
                check_if_time_is_up(time_elapsed)
            except TimesUpException:
                if best_move is None:
                    return (last_move, last_move_value)
                else:
                    return (best_move, best_move_value)

            start_timestamp = datetime.datetime.now()
            board_object.move(piece, move_from, move_to)
            move_value = minimax(board_object, 1, current_depth, not humans_turn, -10000, 10000, time_elapsed)
            board_object.retract_move()

            if move_value > best_move_value:
                best_move_value = move_value
                best_move = (piece, move_from, move_to)

            last_move_value = move_value
            last_move = (piece, move_from, move_to)

            time_elapsed += datetime.datetime.now()-start_timestamp
            print("minimax_start || current_depth: {current_depth}, max_depth: {max_depth}, time_elapsed: {time_elapsed}, {min_or_max}, {move_from}{move_to}, eval={eval}.".format(current_depth=current_depth, max_depth=max_depth, time_elapsed=time_elapsed, min_or_max="min" if humans_turn else "max", move_from=convert_board_notation_to_move(move_from), move_to=convert_board_notation_to_move(move_to), eval=move_value))

    return (best_move, best_move_value)

# THIS FUNCTION RETURNS HOW VALUABLE THIS BOARD STATE IS TO 
# THE CHESS BOT.
@time_function
def evaluate(board_object, humans_turn):
    # If board state is a game over... return eval!
    # game_over,winner = is_game_over(board_object.board, humans_turn, board_object.indexed_board, board_object.pieces_remaining)
    
    # if the game's over, the bot found a winning move on one side.
    # if game_over:
    #     if winner == 'c':
    #         return 9999
    #     else:
    #         return -9999

    evaluation = 0
    # Sum material.
    piece_material_scores = {
        'k': 0,
        'r': 0,
        'n': 0,
        'b': 0,
        'p': 0
    }

    items = board_object.get_pieces_remaining().items()
    for piece,location in items:
        if piece.isupper(): # it's the bot's piece, that's good!
            piece_material_scores[piece.lower()] += 1 # material[piece.lower()]
        else:
            piece_material_scores[piece.lower()] -= 1 # material[piece.lower()]

        # Piece Square Table evaluation scores.
        if piece.lower() in piece_square_tables.keys():
            if piece.isupper():
                evaluation += piece_square_tables[piece.lower()][location[0]][location[1]]
            else:
                evaluation -= [reverse_row for reverse_row in reversed(piece_square_tables[piece.lower()])][location[0]][location[1]]

    material_score = piece_material_scores['k']*material['k'] \
        + piece_material_scores['r']*material['r'] \
        + piece_material_scores['n']*material['n'] \
        + piece_material_scores['b']*material['b'] \
        + piece_material_scores['p']*material['p']

    evaluation += material_score

    #Give higher score when Rooks can go on open files. Open files = columns without any obstruction.
    # rook_directions = [0,4]
    # rook_open_file_score = 40
    # for piece,location in items:
    #     if piece.lower() != 'r':
    #         continue
    #     # moves[<piece>][<starting index>][<direction>] = [list of moves]
    #     rook_has_open_file = True
    #     for rook_direction in rook_directions:
    #         for move in moves['r'][board_object.indexed_board[location[0]][location[1]]][rook_direction]:
    #             move_row = abs((7-(move+1))//7)
    #             move_col = move%7

    #             if board_object.board[move_row][move_col] != '-':
    #                 rook_has_open_file = False
    #                 break
    #         if rook_has_open_file == False:
    #             break
        
    #     if rook_has_open_file:
    #         evaluation += rook_open_file_score

    return evaluation

# Orders all remaining moves in order to find alpha beta cutoffs easier.
# This uses the killer moves technique.
@time_function
def order_moves(board_object, humans_turn, remaining_moves, depth):
    move_evaluations = {}
    for move in remaining_moves:
        piece = move[0]
        move_from = move[1]
        move_to = move[2]    
        board_object.move(piece, move_from, move_to)
        move_evaluations[move] = evaluate(board_object, humans_turn)
        board_object.retract_move()
    move_evaluations_sorted = sorted(move_evaluations.items(), key=operator.itemgetter(1), reverse=True)

    # Put killer moves at the front!
    killer_moves_on_depth = killer_moves.get(depth)
    if killer_moves_on_depth:
        if len(killer_moves_on_depth) > 0:
            top_killer_moves = [unhash_move(killer_move) for killer_move in killer_moves[depth]]
            return top_killer_moves + [move[0] for move in move_evaluations_sorted if move not in top_killer_moves]

    return [move[0] for move in move_evaluations_sorted]

# Recursive minimax function.
def minimax(board_object, depth, max_depth, humans_turn, alpha, beta, time_elapsed):
    start_timestamp = datetime.datetime.now()

    # If board state has been seen before, return the evaluation.
    # @TODO: If the board state has been seen before but hasn't been evaluated, return the best move.
    previously_seen_state_info = transposition_table.get(board_object.get_state_hash())
    if previously_seen_state_info:
        seen_evaluation = previously_seen_state_info.get('evaluation')
        if seen_evaluation:
            return seen_evaluation

    if depth == max_depth:
        # evaluation = evaluate(board_object, humans_turn)
        evaluation = evaluate(board_object, humans_turn)
        transposition_table[deepcopy(board_object.get_state_hash())] = {'evaluation': evaluation}
        return evaluation

    remaining_moves = get_all_remaining_moves(board_object.board, humans_turn, board_object.indexed_board, board_object.get_pieces_remaining().keys())
    ordered_remaining_moves = order_moves(board_object, humans_turn, remaining_moves, depth)
    if not humans_turn:
        best_move_value = -9999
        for piece, move_from, move_to in ordered_remaining_moves:
            try:
                check_if_time_is_up(time_elapsed)
            except TimesUpException:
                return best_move_value

            exploded, captured = board_object.move(piece, move_from, move_to)
            minimax_best_move_value = minimax(
                board_object, 
                depth+1, 
                max_depth, 
                not humans_turn,
                alpha, 
                beta,
                time_elapsed + (datetime.datetime.now()-start_timestamp)
            )
            best_move_value = max(best_move_value, minimax_best_move_value)
            board_object.retract_move()
            alpha = max(alpha, best_move_value)

            move_hash = get_move_hash(piece,move_from,move_to)
            
            if depth not in killer_moves.keys() and depth > 1 and (exploded == False or captured == False):
                killer_moves[depth] = []

            if beta <= alpha: # If alpha-beta cutoff.
                if depth in killer_moves.keys():
                    if move_hash not in killer_moves.get(depth, []):
                        killer_moves[depth].insert(0, move_hash)

                        if len(killer_moves) > 2:
                            killer_moves[depth] = killer_moves[depth][:2]

                return best_move_value

        return best_move_value
    else:
        best_move_value = 9999
        for piece, move_from, move_to in ordered_remaining_moves:
            try:
                check_if_time_is_up(time_elapsed)
            except TimesUpException:
                return best_move_value
            exploded, captured = board_object.move(piece, move_from, move_to)
            minimax_best_move_value = minimax(
                board_object, 
                depth+1, 
                max_depth, 
                not humans_turn, 
                alpha, 
                beta,
                time_elapsed + (datetime.datetime.now()-start_timestamp)
            )
            best_move_value = min(best_move_value, minimax_best_move_value)
            board_object.retract_move()
            beta = min(beta, best_move_value)

            move_hash = get_move_hash(piece,move_from,move_to)
            
            if depth not in killer_moves.keys() and depth > 1 and (exploded == False or captured == False):
                killer_moves[depth] = []

            if beta <= alpha: # If alpha-beta cutoff.
                if depth in killer_moves.keys():
                    if move_hash not in killer_moves[depth]:
                        killer_moves[depth].insert(0, move_hash)

                        if len(killer_moves) > 2:
                            killer_moves[depth] = killer_moves[depth][:2]

                return best_move_value

        return best_move_value

# Main method. Script starts here.
if __name__ == '__main__':
    # Check if the human moves first.
    human_goes_first = None
    while human_goes_first not in ["y","n"]:
        human_goes_first = raw_input("Human goes first (Y/N)? ").lower()
    human_goes_first = True if human_goes_first == 'y' else False
    humans_turn = human_goes_first

    # Create the board object.
    board_object = Board(9,7)

    # Generate all moves and put those moves in the global moves dictionary variable.
    generate_all_moves()

    game_over = False
    winner = None

    # Game loop!
    while not game_over:
        board_object.display()

        if humans_turn:
            human_move_input = raw_input("Human's move i.e. A2D2: ").lower()
            human_move_start_pos = convert_move_notation_to_board(human_move_input[:2])
            human_move_end_pos = convert_move_notation_to_board(human_move_input[2:])
            piece = board_object.board[human_move_start_pos[0]][human_move_start_pos[1]]
            if not is_legal_move(piece, moves, human_move_start_pos, human_move_end_pos, board_object.indexed_board, board_object.board, humans_turn):
                print("Illegal move.")
                continue
            board_object.move(piece, human_move_start_pos, human_move_end_pos)
        else:
            print("Computer's move.")
            best_bot_move, best_move_value = minimax_start(board_object, 5000, humans_turn)
            from_position_converted, to_position_converted = convert_board_notation_to_move(best_bot_move[1]), convert_board_notation_to_move(best_bot_move[2])
            print("Bot moving: {piece}, {start}{end} ({start_inverted}{end_inverted})".format(piece=best_bot_move[0], start=from_position_converted, end=to_position_converted, start_inverted=inverted_position_mapping[from_position_converted], end_inverted=inverted_position_mapping[to_position_converted]))
            board_object.move(best_bot_move[0], best_bot_move[1], best_bot_move[2])

        game_over,winner = is_game_over(board_object.board, humans_turn, board_object.indexed_board, board_object.get_pieces_remaining().keys())
        humans_turn = not humans_turn
    board_object.display()
    print("Game Over.")
    print("Winner: {winner}".format(winner=winner))