import random

from .util import BlockType, make_next_board_sets, make_piece_cells

# ===============================================
# 初手は決め打ち
def nearest_piece(ok_cases, player_number, turn) -> str:
    if turn == 0 and player_number == 1:
        node = 'R355'
    elif turn == 0 and player_number == 2:
        node = 'R388'
    else:
        return ok_cases

    if node in ok_cases:
        return [node]
    else:
        return ok_cases

# 集合版：相手の発揮点を最も多く潰す手だけ残すフィルタ関数 ==================yet
def jamming_filter(actions, board_sets):
    best_score = None
    best_cases = []

    for action in actions:
        
        piece = action[0]
        rf = int(action[1])
        x = int(action[2], 16) - 1
        y = int(action[3], 16) - 1

        piece_cells = make_piece_cells(piece, rf, x, y)

        # 相手の角セルとピースのかぶり集合の数を数える
        score = len(piece_cells & board_sets["ene_corner_cells"])

        if (best_score is None) or (score > best_score):
            best_score = score
            best_cases = [action]
        elif score == best_score:
            best_cases.append(action)

    return best_cases

# 評価関数　ピースのsizeに対しスコアをつける ==================yet
def piece_size_score(piece):
    size = BlockType(piece).size
    if size == 5:
        return 16
    elif size == 4:
        return 10
    else:
        return size * 2

# 評価関数　自分角の数の増加数をスコアとする ==================yet
def my_corner_score(board_sets, next_board_sets):
    my_corner_gain = (
        len(next_board_sets["my_corner_cells"])
        - len(board_sets["my_corner_cells"])
    )
    return my_corner_gain 

# 評価関数　相手の角の数の減少数をスコアとする ==================yet
def ene_corner_score(board_sets, next_board_sets):
    ene_corner_reduce = (
        len(board_sets["ene_corner_cells"])
        - len(next_board_sets["ene_corner_cells"])
    )
    return ene_corner_reduce

# すべての手に対してスコアを付ける関数 ==================yet
def score_actions(actions, board_matrix, board_sets, player_number, turn):
    scored_actions = []

    for action in actions:
        score = 0
        piece = action[0]
        # 次の盤面を作成
        next_board_sets = make_next_board_sets(action, board_sets)

        # 評価関数を適用
        score += piece_size_score(piece) * 1
        score += my_corner_score(board_sets, next_board_sets) * 1
        score += ene_corner_score(board_sets, next_board_sets) * 5
        scored_actions.append((action, score))

    return scored_actions


# スコアが最大の手を選ぶ関数 ==================yet
def select_best_scored_actions(scored_actions):
    best_score = None
    best_actions = []

    for action, score in scored_actions:
        if (best_score is None) or (score > best_score):
            best_score = score
            best_actions = [action]
        elif score == best_score:
            best_actions.append(action)

    return best_actions

# 手を選ぶ関数 ==================yet
def decide_hand(board_matrix, ok_cases, tmp, player_number, turn, board_sets) -> str:

    # 初手は既存の決め打ち候補を優先
    candidate_cases = nearest_piece(ok_cases, player_number, turn)

    # 妨害フィルタ（ene_corner_scoreと役割被りどちらを生かすか？）
    #candidate_cases = jamming_filter(candidate_cases, board_sets)

    # 各手に点数を付ける
    scored_actions = score_actions(
        candidate_cases,
        board_matrix,
        board_sets,
        player_number,
        turn,
    )
    candidate_cases = select_best_scored_actions(scored_actions)

    # 残ったものからランダムチョイス
    return random.choice(candidate_cases)

