import random
import numpy as np

from .util import BlockType

# ===============================================
# FIXME: 人力でベストらしい選択をしているだけ
def nearest_piece(ok_cases, player_number, turn) -> str:
    if turn == 0 and player_number == 1:
        node = 'R455'
    elif turn == 0 and player_number == 2:
        node = 'R488'
    else:
        return ok_cases

    if node in ok_cases:
        return [node]
    else:
        return ok_cases


# NOTE: 相手の置ける場所を潰す
def jamming_piece(board_matrix, ok_cases, player_number) -> str:
    # step1 : 相手の置ける場所をマトリックスに表示する -> get_next_gridの応用
    def is_valid_position(matrix, r, c, block, rows, cols):
        if r < 0 or rows <= r:
            return True
        if c < 0 or cols <= c:
            return True
        if matrix[r][c] != block:
            return True
        return False

    def check_upper_right(matrix, r, c, block, rows, cols):
        return (
            is_valid_position(matrix, r - 1, c, block, rows, cols)
            and is_valid_position(matrix, r, c + 1, block, rows, cols)
            and is_valid_position(matrix, r - 1, c + 2, block, rows, cols)
            and is_valid_position(matrix, r - 2, c + 1, block, rows, cols)
            and is_valid_position(matrix, r - 1, c + 1, block, rows, cols)
        )

    def check_lower_right(matrix, r, c, block, rows, cols):
        return (
            is_valid_position(matrix, r + 1, c, block, rows, cols)
            and is_valid_position(matrix, r, c + 1, block, rows, cols)
            and is_valid_position(matrix, r + 1, c + 2, block, rows, cols)
            and is_valid_position(matrix, r + 2, c + 1, block, rows, cols)
            and is_valid_position(matrix, r + 1, c + 1, block, rows, cols)
        )

    def check_lower_left(matrix, r, c, block, rows, cols):
        return (
            is_valid_position(matrix, r + 1, c, block, rows, cols)
            and is_valid_position(matrix, r, c - 1, block, rows, cols)
            and is_valid_position(matrix, r + 1, c - 2, block, rows, cols)
            and is_valid_position(matrix, r + 2, c - 1, block, rows, cols)
            and is_valid_position(matrix, r + 1, c - 1, block, rows, cols)
        )

    def check_upper_left(matrix, r, c, block, rows, cols):
        return (
            is_valid_position(matrix, r - 1, c, block, rows, cols)
            and is_valid_position(matrix, r, c - 1, block, rows, cols)
            and is_valid_position(matrix, r - 1, c - 2, block, rows, cols)
            and is_valid_position(matrix, r - 2, c - 1, block, rows, cols)
            and is_valid_position(matrix, r - 1, c - 1, block, rows, cols)
        )

    def get_opp_positions(board_matrix, player_number):
        if player_number == 1:
            block = 'x'
        else:
            block = 'o'

        p = 'z'
        rows = len(board_matrix)
        cols = len(board_matrix[0])

        # 新しい行列を作成
        new_matrix = [row[:] for row in board_matrix]

        # ブロックの位置を記録するリスト
        block_positions = []

        # ブロックの位置を探して記録
        for r in range(rows):
            for c in range(cols):
                if board_matrix[r][c] == block:
                    block_positions.append((r, c))

        # 'block' の位置を基に対角線上の位置を 'p' に置き換え
        for r, c in block_positions:
            # 右上の座標 (r-1, c+1)
            if r > 0 and c < cols - 1 and check_upper_right(board_matrix, r, c, block, rows, cols):
                new_matrix[r - 1][c + 1] = p

            # 右下の座標 (r+1, c+1)
            if r < rows - 1 and c < cols - 1 and check_lower_right(board_matrix, r, c, block, rows, cols):
                new_matrix[r + 1][c + 1] = p

            # 左下の座標 (r+1, c-1)
            if r < rows - 1 and c > 0 and check_lower_left(board_matrix, r, c, block, rows, cols):
                new_matrix[r + 1][c - 1] = p

            # 左上の座標 (r-1, c-1)
            if r > 0 and c > 0 and check_upper_left(board_matrix, r, c, block, rows, cols):
                new_matrix[r - 1][c - 1] = p

        return new_matrix

    # step2 : ベターな置き方のリストを（それぞれ比較しながら）作る
    def better_jammers(opponent_start_positions, ok_cases):
        # a : 置き方一つが何個の置ける場所と重なっているかカウントする
        # NOTE: 辞書型で{case: z_count}を持つことにする
        better_cases_w_count = {}

        for cs in ok_cases:
            # NOTE: pieceを正しい向きで取得する
            piece = str(cs[0])
            rf = int(cs[1])

            if cs[2] in ['A', 'B', 'C', 'D', 'E']:
                j = ord(cs[2]) - 55 - 1
            else:
                j = int(cs[2]) - 1

            if cs[3] in ['A', 'B', 'C', 'D', 'E']:
                i = ord(cs[3]) - 55 - 1
            else:
                i = int(cs[3]) - 1

            piece_map_origin = BlockType(piece)
            piece_map = piece_map_origin.block_map

            if rf == 0 or rf == 1:
                pass
            elif rf == 2 or rf == 3:
                piece_map = np.rot90(piece_map, 3).copy()
            elif rf == 4 or rf == 5:
                piece_map = np.rot90(piece_map, 2).copy()
            elif rf == 6 or rf == 7:
                piece_map = np.rot90(piece_map, 1).copy()

            if rf % 2 == 1:
                piece_map = np.fliplr(piece_map)

            z_count = 0
            for p in range(piece_map.shape[0]):
                for q in range(piece_map.shape[1]):
                    if piece_map[p][q] == 1:
                        if opponent_start_positions[i + p][j + q] == 'z':
                            z_count += 1

            better_cases_w_count[cs] = z_count

        max_value = max(better_cases_w_count.values())

        # 最大値を持つキーのリストを作成する
        return [k for k, v in better_cases_w_count.items() if v == max_value]

    opponent_start_positions = get_opp_positions(board_matrix, player_number)

    better_cases = better_jammers(opponent_start_positions, ok_cases)
    return better_cases


# NOTE: ピースの大きさを優先する
def big_piece(better_cases) -> str:
    better_cases_w_size = {}

    for cs in better_cases:
        # NOTE: pieceを正しい向きで取得する
        piece = str(cs[0])
        rf = int(cs[1])

        if cs[2] in ['A', 'B', 'C', 'D', 'E']:
            j = ord(cs[2]) - 55 - 1
        else:
            j = int(cs[2]) - 1

        if cs[3] in ['A', 'B', 'C', 'D', 'E']:
            i = ord(cs[3]) - 55 - 1
        else:
            i = int(cs[3]) - 1

        piece_map_origin = BlockType(piece)
        piece_map = piece_map_origin.block_map

        if rf == 0 or rf == 1:
            pass
        elif rf == 2 or rf == 3:
            piece_map = np.rot90(piece_map, 3).copy()
        elif rf == 4 or rf == 5:
            piece_map = np.rot90(piece_map, 2).copy()
        elif rf == 6 or rf == 7:
            piece_map = np.rot90(piece_map, 1).copy()

        if rf % 2 == 1:
            piece_map = np.fliplr(piece_map)

        size_count = 0
        for p in range(piece_map.shape[0]):
            for q in range(piece_map.shape[1]):
                if piece_map[p][q] == 1:
                    size_count += 1

        better_cases_w_size[cs] = size_count

    max_value = max(better_cases_w_size.values())

    # 最大値を持つキーのリストを作成する
    return [k for k, v in better_cases_w_size.items() if v == max_value]


# TODO: 次に置ける角の数を優先
def more_corner_piece(better_cases) -> str:
    selected_cases = [case for case in better_cases if 'U' in case]
    if len(selected_cases) > 0:
        return selected_cases

    selected_cases.extend([case for case in better_cases if 'T' in case or 'R' in case])
    if len(selected_cases) > 0:
        return selected_cases

    selected_cases.extend(
        [
            case
            for case in better_cases
            if 'S' in case
            or 'P' in case
            or 'O' in case
            or 'I' in case
            or 'L' in case
            or 'G' in case
        ]
    )
    if len(selected_cases) > 0:
        return selected_cases

    selected_cases.extend(
        [
            case
            for case in better_cases
            if 'Q' in case
            or 'N' in case
            or 'M' in case
            or 'K' in case
            or 'F' in case
            or 'D' in case
        ]
    )
    if len(selected_cases) > 0:
        return selected_cases

    return better_cases

# 一つの手に対しスコアをつける関数 ==================yet
def score_action(action, board_matrix, board_sets, player_number, turn):
    score = 0
    piece = action[0]
    score += piece_size_score(piece)
    return score

# ピースのsizeに対しスコアをつける関数 ==================yet
def piece_size_score(piece):
    size = BlockType(piece).size
    if size == 5:
        return 16
    elif size == 4:
        return 10
    else:
        return size * 2

# ヒューリスティックに良い手を選ぶ関数 ==================yet
def dicide_hand(board_matrix, ok_cases, tmp, player_number, turn, board_sets) -> str:
    better_cases_1 = []
    better_cases_2 = []
    better_cases_3 = []
    better_cases_4 = []

    better_cases_1 = nearest_piece(ok_cases, player_number, turn)
    better_cases_2 = jamming_piece(board_matrix, better_cases_1, player_number)
    better_cases_3 = big_piece(better_cases_2)
    better_cases_4 = more_corner_piece(better_cases_3)

    id = random.randrange(len(better_cases_4))
    return better_cases_4[id]