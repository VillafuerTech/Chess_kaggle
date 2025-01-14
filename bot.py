import random
import math
import time

from Chessnut import Game

################################################################################
#                         PIECE-SQUARE TABLES & VALUES                         #
################################################################################

PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5,  5,  5, -5, -5,  0,  0,  0,
     2,  2,  2,  2,  2,  2, -2, -2,
     1,  1,  1,  2,  2,  1,  1,  1,
     1,  1,  2,  3,  3,  2,  1,  1,
     2,  2,  2,  4,  4,  2,  2,  2,
     5,  5,  5,  6,  6,  5,  5,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
   -5, -4, -2, -2, -2, -2, -4, -5,
   -4,  0,  0,  0,  0,  0,  0, -4,
   -2,  0,  1,  2,  2,  1,  0, -2,
   -2,  0,  2,  3,  3,  2,  0, -2,
   -2,  0,  2,  3,  3,  2,  0, -2,
   -2,  0,  1,  2,  2,  1,  0, -2,
   -4,  0,  0,  0,  0,  0,  0, -4,
   -5, -4, -2, -2, -2, -2, -4, -5
]

BISHOP_TABLE = [
   -2, -1, -1, -1, -1, -1, -1, -2,
   -1,  1,  0,  0,  0,  0,  1, -1,
   -1,  2,  2,  2,  2,  2,  2, -1,
   -1,  2,  3,  2,  2,  3,  2, -1,
   -1,  2,  3,  2,  2,  3,  2, -1,
   -1,  2,  2,  2,  2,  2,  2, -1,
   -1,  1,  0,  0,  0,  0,  1, -1,
   -2, -1, -1, -1, -1, -1, -1, -2
]

ROOK_TABLE = [
    0,  0,  1,  2,  2,  1,  0,  0,
    0,  0,  1,  2,  2,  1,  0,  0,
    0,  0,  1,  2,  2,  1,  0,  0,
    0,  0,  1,  2,  2,  1,  0,  0,
    0,  0,  1,  2,  2,  1,  0,  0,
    0,  0,  1,  2,  2,  1,  0,  0,
    0,  0,  1,  2,  2,  1,  0,  0,
    0,  0,  1,  2,  2,  1,  0,  0
]

QUEEN_TABLE = [
   -2, -1, -1,  0,  0, -1, -1, -2,
   -1,  0,  1,  1,  1,  1,  0, -1,
   -1,  0,  1,  1,  1,  1,  0, -1,
    0,  0,  1,  1,  1,  1,  0,  0,
    0,  0,  1,  1,  1,  1,  0,  0,
   -1,  0,  1,  1,  1,  1,  0, -1,
   -1,  0,  1,  1,  1,  1,  0, -1,
   -2, -1, -1,  0,  0, -1, -1, -2
]

KING_TABLE = [
   -3, -4, -4, -5, -5, -4, -4, -3,
   -3, -4, -4, -5, -5, -4, -4, -3,
   -3, -4, -4, -5, -5, -4, -4, -3,
   -3, -4, -4, -5, -5, -4, -4, -3,
   -2, -3, -3, -4, -4, -3, -3, -2,
   -1, -2, -2, -2, -2, -2, -2, -1,
    2,  2,  0,  0,  0,  0,  2,  2,
    2,  3,  1,  0,  0,  1,  3,  2
]

PIECE_VALUES = {
    'P': 100,   # Pawn
    'N': 320,   # Knight
    'B': 330,   # Bishop
    'R': 500,   # Rook
    'Q': 900,   # Queen
    'K': 20000  # King
}

################################################################################
#                      TRANSPOSITION TABLE (STORED BY FEN)                     #
################################################################################

TRANSPOSITION_TABLE = {}
MAX_TT_SIZE = 20000

################################################################################
#                               FEN PARSING                                    #
################################################################################

def parse_fen(fen):
    """
    Parse a FEN string into:
      - board_list of length 64 (index 0=a8, 63=h1)
      - side_to_move: 'w'/'b'
      - castling, en_passant, halfmove, fullmove
    """
    parts = fen.split()
    ranks = parts[0].split('/')
    side_to_move = parts[1]
    castling = parts[2] if len(parts) > 2 else ''
    en_passant = parts[3] if len(parts) > 3 else ''
    halfmove = parts[4] if len(parts) > 4 else '0'
    fullmove = parts[5] if len(parts) > 5 else '1'

    board_list = []
    for rank in ranks:
        expanded = []
        for ch in rank:
            if ch.isdigit():
                expanded.extend([' '] * int(ch))
            else:
                expanded.append(ch)
        board_list.extend(expanded)

    return board_list, side_to_move, castling, en_passant, halfmove, fullmove

def algebraic_to_index(sq):
    """
    e.g. 'a8' -> 0, 'h8'->7, 'a1'->56, 'h1'->63
    """
    file = ord(sq[0]) - ord('a')  # 0..7
    rank = int(sq[1])            # 1..8
    row = 8 - rank               # 0..7 (top rank=0)
    return 8 * row + file

################################################################################
#                           EVALUATION UTILITIES                               #
################################################################################

def piece_square_value(piece, sq_index):
    """
    e.g. piece='P' or 'k'. sq_index in [0..63], 0=a8, 63=h1.
    """
    is_white = piece.isupper()
    base_val = PIECE_VALUES.get(piece.upper(), 0)

    # piece-square table
    if piece.upper() == 'P':
        bonus = PAWN_TABLE[sq_index]
    elif piece.upper() == 'N':
        bonus = KNIGHT_TABLE[sq_index]
    elif piece.upper() == 'B':
        bonus = BISHOP_TABLE[sq_index]
    elif piece.upper() == 'R':
        bonus = ROOK_TABLE[sq_index]
    elif piece.upper() == 'Q':
        bonus = QUEEN_TABLE[sq_index]
    elif piece.upper() == 'K':
        bonus = KING_TABLE[sq_index]
    else:
        bonus = 0

    if not is_white:
        base_val = -base_val
        bonus = -bonus
    return base_val + bonus

def evaluate_position(board_list):
    """
    Sum up piece-square values for the entire board_list.
    """
    score = 0
    for sq_idx, piece in enumerate(board_list):
        if piece != ' ':
            score += piece_square_value(piece, sq_idx)
    return score

def evaluate_board(game):
    """
    Parse FEN once, evaluate with evaluate_position.
    """
    fen = str(game)
    board_list, _, _, _, _, _ = parse_fen(fen)
    return evaluate_position(board_list)

################################################################################
#                           MOVE / CAPTURE ORDERING                            #
################################################################################

def mvv_lva_score(board_list, move):
    """
    'MVV-LVA' = Most Valuable Victim - Least Valuable Attacker
    We'll parse the from/to squares, see what's captured, what's the attacker.
    Higher = better (victim value - attacker value).
    """
    from_sq, to_sq = move[:2], move[2:4]
    from_idx = algebraic_to_index(from_sq)
    to_idx = algebraic_to_index(to_sq)

    attacker_piece = board_list[from_idx]
    victim_piece = board_list[to_idx]  # might be ' ' if not a capture

    if victim_piece == ' ':
        return 0  # no capture => no special priority

    victim_value = PIECE_VALUES.get(victim_piece.upper(), 0)
    attacker_value = PIECE_VALUES.get(attacker_piece.upper(), 0)
    return victim_value - attacker_value

def order_moves(game, moves, board_list):
    """
    Sort moves so that bigger captures come first (MVV-LVA).
    Non-captures get lower priority.
    """
    scored = []
    for m in moves:
        score = mvv_lva_score(board_list, m)
        scored.append((m, score))
    # sort descending by score
    scored.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in scored]

################################################################################
#                           QUIESCENCE SEARCH                                  #
################################################################################

def quiescence_search(game, alpha, beta, start_time, time_limit):
    """
    Quiescence search: only explore captures when 'depth=0' in alpha-beta.
    Avoids horizon effect by continuing capturing lines.
    """
    # Time cutoff
    if time.time() - start_time > time_limit:
        return evaluate_board(game)

    stand_pat = evaluate_board(game)
    if stand_pat >= beta:
        return beta
    if alpha < stand_pat:
        alpha = stand_pat

    # Generate all moves, but consider only capturing moves for further search
    moves = game.get_moves()
    if not moves:
        return stand_pat

    fen = str(game)
    board_list, _, _, _, _, _ = parse_fen(fen)

    # Only keep capturing moves
    capturing_moves = []
    for mv in moves:
        to_sq = mv[2:4]
        to_idx = algebraic_to_index(to_sq)
        if board_list[to_idx] != ' ':
            # It's a capture
            capturing_moves.append(mv)

    # If no captures => evaluate stand pat
    if not capturing_moves:
        return stand_pat

    # Order captures by MVV-LVA
    capturing_moves.sort(key=lambda m: mvv_lva_score(board_list, m), reverse=True)

    # Explore capturing lines
    for move in capturing_moves:
        g_next = Game(fen)  # clone
        try:
            g_next.apply_move(move)
        except:
            continue

        score = -quiescence_search(g_next, -beta, -alpha, start_time, time_limit)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha

################################################################################
#                         UTILITY: CLONING + HASHING                           #
################################################################################

def board_hash(game):
    """
    Use FEN as the position key.
    """
    return str(game)

def clone_game(original):
    """
    Clone via FEN.
    """
    return Game(str(original))

################################################################################
#                              ALPHA-BETA SEARCH                               #
################################################################################

def alpha_beta_search(game, depth, alpha, beta, maximizing, start_time, time_limit):
    """
    Alpha-beta with quiescence:
      - If depth=0 => go to quiescence_search
      - Otherwise => normal alpha-beta
    """
    # Time check
    if time.time() - start_time > time_limit:
        return evaluate_board(game), None

    # Moves
    moves = game.get_moves()
    if not moves:
        # No legal moves => terminal
        return evaluate_board(game), None

    # Depth cutoff => quiescence
    if depth == 0:
        val = quiescence_search(game, alpha, beta, start_time, time_limit)
        return val, None

    # Transposition Table check
    state_key = board_hash(game)
    if state_key in TRANSPOSITION_TABLE:
        (stored_depth, stored_alpha, stored_beta, stored_value, stored_move) = TRANSPOSITION_TABLE[state_key]
        if stored_depth >= depth and stored_alpha <= alpha and stored_beta >= beta:
            return stored_value, stored_move

    # Move ordering
    fen = str(game)
    board_list, _, _, _, _, _ = parse_fen(fen)
    moves_ordered = order_moves(game, moves, board_list)

    best_move = None
    if maximizing:
        value = -math.inf
        for move in moves_ordered:
            g_next = clone_game(game)
            try:
                g_next.apply_move(move)
            except:
                continue

            new_val, _ = alpha_beta_search(g_next, depth - 1, alpha, beta,
                                           False, start_time, time_limit)
            if new_val > value:
                value = new_val
                best_move = move

            alpha = max(alpha, value)
            if alpha >= beta:
                break
    else:
        value = math.inf
        for move in moves_ordered:
            g_next = clone_game(game)
            try:
                g_next.apply_move(move)
            except:
                continue

            new_val, _ = alpha_beta_search(g_next, depth - 1, alpha, beta,
                                           True, start_time, time_limit)
            if new_val < value:
                value = new_val
                best_move = move

            beta = min(beta, value)
            if beta <= alpha:
                break

    # Store in TT
    if len(TRANSPOSITION_TABLE) < MAX_TT_SIZE:
        TRANSPOSITION_TABLE[state_key] = (depth, alpha, beta, value, best_move)

    return value, best_move

################################################################################
#                           ITERATIVE DEEPENING                                #
################################################################################

def iterative_deepening(game, max_depth=1, time_limit=0.10):
    """
    Iteratively deepen from 1..max_depth or until time expires.
    """
    start_time = time.time()
    best_move = None
    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            break
        val, move = alpha_beta_search(game, depth, -math.inf, math.inf, True,
                                      start_time, time_limit)
        if move:
            best_move = move
        # If we're nearly out of time, break
        if time.time() - start_time > time_limit:
            break
    return best_move

################################################################################
#                          BOT + KAGGLE AGENT INTERFACE                        #
################################################################################

def advanced_chess_bot(obs, max_depth=1, move_time=0.10):
    """
    1) Build a Chessnut Game from obs.board (FEN).
    2) Iterative deepening with alpha-beta + quiescence.
    3) Return best move in UCI (e.g. 'e2e4'), or None if no moves.
    """
    game = Game(obs.board)
    moves = game.get_moves()
    if not moves:
        return None  # no moves => terminal

    best_move = iterative_deepening(game, max_depth, move_time)
    if not best_move:
        # fallback
        best_move = random.choice(moves)
    return best_move

def agent(obs, config):
    """
    Kaggle agent entry point.
    """
    return advanced_chess_bot(obs, max_depth=2, move_time=0.20)
