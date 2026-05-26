from enum import Enum
from typing import Any
import numpy as np

# ピースの形状を定義するクラス ==========================done
class BlockType(Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = 'G'
    H = 'H'
    I = 'I'
    J = 'J'
    K = 'K'
    L = 'L'
    M = 'M'
    N = 'N'
    O = 'O'
    P = 'P'
    Q = 'Q'
    R = 'R'
    S = 'S'
    T = 'T'
    U = 'U'
    X = 'X'

    # size情報を取得できるようにプロパティを追加
    @property
    def size(self):
        if self == BlockType.A:
            return 1
        elif self == BlockType.B:
            return 2
        elif self in (BlockType.C, BlockType.D):
            return 3
        elif self in (BlockType.E, BlockType.F, BlockType.G, BlockType.H, BlockType.I):
            return 4
        elif self == BlockType.X:
            return 0
        else:
            return 5

    @property
    def block_map(self) -> np.ndarray[Any, np.dtype[int]]:
        if self == BlockType.A:
            '''
            type A:
            ■
            corner:4
            '''
            return np.array([[1]])
        elif self == BlockType.B:
            '''
            type B:
            ■
            ■
            corner: 4
            '''
            return np.array([[1], [1]])
        elif self == BlockType.C:
            '''
            type C:
            ■
            ■
            ■
            corner: 4
            '''
            return np.array([[1], [1], [1]])
        elif self == BlockType.D:
            '''
            type D:
            ■
            ■ ■
            corner: 5
            '''
            return np.array([[1, 0], [1, 1]])
        elif self == BlockType.E:
            '''
            type E:
            ■
            ■
            ■
            ■
            corner: 4
            '''
            return np.array([[1], [1], [1], [1]])
        elif self == BlockType.F:
            '''
            type F:
              ■
              ■
            ■ ■
            corner: 5
            '''
            return np.array([[0, 1], [0, 1], [1, 1]])
        elif self == BlockType.G:
            '''
            type G:
            ■
            ■ ■
            ■
            corner: 6
            '''
            return np.array([[1, 0], [1, 1], [1, 0]])
        elif self == BlockType.H:
            '''
            type H:
            ■ ■
            ■ ■
            corner: 4
            '''
            return np.array([[1, 1], [1, 1]])
        elif self == BlockType.I:
            '''
            type I:
            ■ ■
              ■ ■
            corner: 6
            '''
            return np.array([[1, 1, 0], [0, 1, 1]])
        elif self == BlockType.J:
            '''
            type J:
            ■
            ■
            ■
            ■
            ■
            corner: 4
            '''
            return np.array([[1], [1], [1], [1], [1]])
        elif self == BlockType.K:
            '''
            type K:
              ■
              ■
              ■
            ■ ■
            corner: 5
            '''
            return np.array([[0, 1], [0, 1], [0, 1], [1, 1]])
        elif self == BlockType.L:
            '''
            type L:
              ■
              ■
            ■ ■
            ■
            corner: 6
            '''
            return np.array([[0, 1], [0, 1], [1, 1], [1, 0]])
        elif self == BlockType.M:
            '''
            type M:
              ■
            ■ ■
            ■ ■
            corner: 5
            '''
            return np.array([[0, 1], [1, 1], [1, 1]])
        elif self == BlockType.N:
            '''
            type N:
            ■ ■
              ■
            ■ ■

            '''
            return np.array([[1, 1], [0, 1], [1, 1]])
        elif self == BlockType.O:
            '''
            type O:
            ■
            ■ ■
            ■
            ■
            corner: 6
            '''
            return np.array([[1, 0], [1, 1], [1, 0], [1, 0]])
        elif self == BlockType.P:
            '''
            type P:
              ■
              ■
            ■ ■ ■
            corner: 6
            '''
            return np.array([[0, 1, 0], [0, 1, 0], [1, 1, 1]])
        elif self == BlockType.Q:
            '''
            type Q:
            ■
            ■
            ■ ■ ■
            corner: 5
            '''
            return np.array([[1, 0, 0], [1, 0, 0], [1, 1, 1]])
        elif self == BlockType.R:
            '''
            type R:
            ■ ■
              ■ ■
                ■
            corner: 7
            '''
            return np.array([[1, 1, 0], [0, 1, 1], [0, 0, 1]])
        elif self == BlockType.S:
            '''
            type S:
            ■
            ■ ■ ■
                ■
            corner: 6
            '''
            return np.array([[1, 0, 0], [1, 1, 1], [0, 0, 1]])
        elif self == BlockType.T:
            '''
            type T:
            ■
            ■ ■ ■
              ■
            corner: 7
            '''
            return np.array([[1, 0, 0], [1, 1, 1], [0, 1, 0]])
        elif self == BlockType.U:
            '''
            type U:
              ■
            ■ ■ ■
              ■
            corner: 8
            '''
            return np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])
        elif self == BlockType.X:
            '''
            type X:パスをする時用



            '''
            return np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        else:
            raise NotImplementedError
# ========================================================


# 受信した盤面からインデックスを削除し、2次元配列に変換する ==================done
def make_matrix(board):
    # １行ごとの文字列の配列に変換
    lines = board.splitlines()
    # 1行目は列番号なので除外する
    board_lines = lines[1:]
    # 空のリスト
    board_matrix = []
    for line in board_lines:
        # 各行の先頭1文字は行番号なので除外する
        cells = line[1:]
        # 文字列を1文字ずつのリストに変換する
        row = list(cells)
        # matrixに１行（リスト）を追加
        board_matrix.append(row)
    return board_matrix
# ===============================================

# 2次元配列の盤面を集合(SET)に変換する tmaeda試作 ==================done
def build_board_sets(board_matrix, player_number):
    # 自分と相手の記号を定義
    if player_number == 1:
        my_mark = 'o'
        ene_mark = 'x'
    else:
        my_mark = 'x'
        ene_mark = 'o'
    # 空の集合を準備
    my_cells = set()
    ene_cells = set()
    empty_cells = set()
    # 文字種ごとに集合に追加
    BOARD_SIZE = 14
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            cell = board_matrix[y][x]

            if cell == my_mark:
                my_cells.add((x, y))
            elif cell == ene_mark:
                ene_cells.add((x, y))
            elif cell == '.':
                empty_cells.add((x, y))
    # 自分と相手のNGセル、角セルの座標集合を作成
    my_ng_cells = make_ng_cells(my_cells, empty_cells)
    ene_ng_cells = make_ng_cells(ene_cells, empty_cells)
    my_corner_cells = make_corner_cells(my_cells, empty_cells, my_ng_cells)
    ene_corner_cells = make_corner_cells(ene_cells, empty_cells, ene_ng_cells)
    # 各種の座標集合をdict形式でまとめて返す
    return {
        "my_cells": my_cells,
        "ene_cells": ene_cells,
        "empty_cells": empty_cells,
        "my_ng_cells": my_ng_cells,
        "ene_ng_cells": ene_ng_cells,
        "my_corner_cells": my_corner_cells,
        "ene_corner_cells": ene_corner_cells,
    }

# board内チェック補助関数 tmaeda試作 ==================
def is_inside(x, y):
    return 0 <= x < 14 and 0 <= y < 14

# NGセル（辺隣接）集合作成補助関数 tmaeda試作 ==================
def make_ng_cells(cells, empty_cells):
    ng_cells = set()
    directions = [
        (0, -1),  # 上
        (1, 0),   # 右
        (0, 1),   # 下
        (-1, 0),  # 左
    ]
    for x, y in cells:
        for dx, dy in directions:
            nx = x + dx
            ny = y + dy
            # boardの内部にある and 空セル
            if is_inside(nx, ny) and (nx, ny) in empty_cells:
                ng_cells.add((nx, ny))
    return ng_cells

# 発揮点（角隣接）集合作成補助関数 tmaeda試作 ==================
def make_corner_cells(cells, empty_cells, ng_cells):
    corner_cells = set()
    directions = [
        (-1, -1),  # 左上
        (1, -1),   # 右上
        (-1, 1),   # 左下
        (1, 1),    # 右下
    ]
    for x, y in cells:
        for dx, dy in directions:
            nx = x + dx
            ny = y + dy
            # boardの内部にある and 空セル and NGセルではない
            if is_inside(nx, ny) and (nx, ny) in empty_cells and (nx, ny) not in ng_cells:
                corner_cells.add((nx, ny))
    return corner_cells

# 合法手判定補助関数 tmaeda試作 ==================
def is_legal(piece_cells, board_sets, turn, start_point):
    empty_cells = board_sets["empty_cells"]
    my_ng_cells = board_sets["my_ng_cells"]
    my_corner_cells = board_sets["my_corner_cells"]

    # ピースすべてが空きマスに含まれていない場合は不適
    if not piece_cells <= empty_cells:
        return False
    # ピースが一部でもNGマスに含まれている場合は不適
    if len(piece_cells & my_ng_cells) > 0:
        return False
    # 出発点を含んでいるか（初手と２手目以降で条件分岐）
    if turn == 0:
        return start_point in piece_cells
    if len(piece_cells & my_corner_cells) == 0:
        return False

    return True

# ピース配列を回転・反転した形に変換する関数(gameから流用) ==================
def make_piece_map(piece, rf):
    # gameにあったピース形状クラスを流用
    block_type = BlockType(piece)
    # ピースのクラスから形状配列を取得
    temp_map = block_type.block_map
    # rf は 0〜7
    # 0,1: 回転0回
    # 2,3: 回転1回
    # 4,5: 回転2回
    # 6,7: 回転3回
    rotation_count = rf // 2
    # rfが奇数なら反転あり
    reversed_flag = rf % 2 == 1
    # np.rot90 は反時計回りのため、時計回り rotation_count 回に合わせる
    for _ in range((4 - rotation_count) % 4):
        temp_map = np.rot90(temp_map)

    if reversed_flag:
        temp_map = np.fliplr(temp_map)

    return temp_map

# ピースID、回転反転番号、左上座標から、実際に置かれる座標集合を作る補助関数
def make_piece_cells(piece, rf, origin_x, origin_y):
    piece_cells = set()
    # ピース配列を回転・反転
    piece_map = make_piece_map(piece, rf)
    # 回転したピース配列を順番に見て、セルがあったら座標集合に追加
    for y in range(piece_map.shape[0]):
        for x in range(piece_map.shape[1]):
            if piece_map[y][x] == 1:
                piece_cells.add((origin_x + x, origin_y + y))

    return piece_cells

# ピースID、回転反転番号、左上座標から、アクション文字列を作成
def make_action_string(piece, rf, x, y):
    return piece + str(rf) + format(x + 1, "X") + format(y + 1, "X")

# ピースID毎に、重複形状にならない回転・反転パターンを作成
def get_unique_rfs(piece):
    unique_rfs = []
    seen_maps = set()

    for rf in range(8):
        piece_map = make_piece_map(piece, rf)
        map_key = tuple(tuple(row) for row in piece_map.tolist())

        if map_key not in seen_maps:
            seen_maps.add(map_key)
            unique_rfs.append(rf)

    return unique_rfs

UNIQUE_RFS = {
    piece: get_unique_rfs(piece)
    for piece in "ABCDEFGHIJKLMNOPQRSTU"
}

# すべての合法手のアクションIDをリスト化
def get_ok_cases_by_sets(board_sets, my_hands, player_number, turn):
    ok_cases = []
    tmp = []

    if player_number == 1:
        start_point = (4, 4)
    else:
        start_point = (9, 9)

    # 持ってるピースをすべて試す
    for piece in my_hands:
        if piece == "X":
            continue
        # ユニークな回転・反転をすべて試す
        for rf in UNIQUE_RFS[piece]:
            # すべての座標に試す
            for y in range(14):
                for x in range(14):
                    # ピースを座標集合に変換
                    piece_cells = make_piece_cells(piece, rf, x, y)

                    if is_legal(piece_cells, board_sets, turn, start_point):
                        # アクション文字列を作成し格納
                        action = make_action_string(piece, rf, x, y)
                        ok_cases.append(action)

    return ok_cases, tmp


# # ===============================================

# # 反則でない手を全列挙する関数 ===============================
# # 長いので階層構造に注意して読んでください。
# def get_ok_cases(next_grid, player_number, turn, my_hands) -> tuple[list[str], list]:
#     # 置けるますに対して、置ける手を全列挙する。
#     # 反則でないもののみをlistにappendしていく。
#     # そのリストを返す。

#     # 反則判定の関数 ========================================
#     # 完全に反則でない手の場合のみ、Trueを返す関数
#     # もちろん、反則はFalseを返す。
#     def is_ok(next_grid, piece_map, i, j, a, b) -> bool:

#         # ===== ピースの重なり判定=========================
#         def is_dup(next_grid, piece_map, i, j, a, b) -> bool:
#             for p in range(piece_map.shape[0]):
#                 for q in range(piece_map.shape[1]):
#                     if piece_map[p][q] == 1:
#                         if (
#                             next_grid[i - a + p][j - b + q] == 'o'
#                             or next_grid[i - a + p][j - b + q] == 'x'
#                         ):
#                             return True
#             return False

#         # ===== ピースの盤面外判定 ========================
#         def is_out(next_grid, piece_map, i, j, a, b) -> bool:
#             for p in range(piece_map.shape[0]):
#                 for q in range(piece_map.shape[1]):
#                     if piece_map[p][q] == 1:
#                         if i - a + p < 0 or i - a + p > 13 or j - b + q < 0 or j - b + q > 13:
#                             return True
#             return False

#         # ===== ピースの隣接判定 ==========================yet
#         def is_neighbor(next_grid, piece_map, i, j, a, b) -> bool:
#             if player_number == 1:
#                 block = 'o'
#             else:
#                 block = 'x'

#             grid_size = len(next_grid)
#             for p in range(piece_map.shape[0]):
#                 for q in range(piece_map.shape[1]):
#                     if piece_map[p][q] == 1:
#                         r = i - a + p
#                         c = j - b + q

#                         # Skip if r or c is out of the grid bounds
#                         if r < 0 or r >= grid_size or c < 0 or c >= grid_size:
#                             continue

#                         # Check corners and edges separately
#                         if r == 0 and c == 0:
#                             if next_grid[r + 1][c] == block or next_grid[r][c + 1] == block:
#                                 return True
#                         elif r == 0 and c == grid_size - 1:
#                             if next_grid[r + 1][c] == block or next_grid[r][c - 1] == block:
#                                 return True
#                         elif r == grid_size - 1 and c == 0:
#                             if next_grid[r - 1][c] == block or next_grid[r][c + 1] == block:
#                                 return True
#                         elif r == grid_size - 1 and c == grid_size - 1:
#                             if next_grid[r - 1][c] == block or next_grid[r][c - 1] == block:
#                                 return True
#                         elif r == 0:
#                             if (
#                                 next_grid[r][c + 1] == block
#                                 or next_grid[r + 1][c] == block
#                                 or next_grid[r][c - 1] == block
#                             ):
#                                 return True
#                         elif r == grid_size - 1:
#                             if (
#                                 next_grid[r - 1][c] == block
#                                 or next_grid[r][c + 1] == block
#                                 or next_grid[r][c - 1] == block
#                             ):
#                                 return True
#                         elif c == 0:
#                             if (
#                                 next_grid[r - 1][c] == block
#                                 or next_grid[r][c + 1] == block
#                                 or next_grid[r + 1][c] == block
#                             ):
#                                 return True
#                         elif c == grid_size - 1:
#                             if (
#                                 next_grid[r - 1][c] == block
#                                 or next_grid[r + 1][c] == block
#                                 or next_grid[r][c - 1] == block
#                             ):
#                                 return True
#                         else:
#                             if (
#                                 next_grid[r - 1][c] == block
#                                 or next_grid[r][c + 1] == block
#                                 or next_grid[r + 1][c] == block
#                                 or next_grid[r][c - 1] == block
#                             ):
#                                 return True

#             return False

#         # 以下、この関数のフロー
#         # 最初に盤面外判定をしておかないと、他の場面で安心して検証ができない。
#         # next_grid をインデックスアウトしないようにするために。
#         if is_out(next_grid, piece_map, i, j, a, b):
#             return False

#         if is_dup(next_grid, piece_map, i, j, a, b):
#             # 敵のピースでも自分のピースでも、重なってはいけないことに注意
#             return False

#         if is_neighbor(next_grid, piece_map, i, j, a, b):
#             # すでに置かれている「自分の」ピースと辺で隣接してしまう場合
#             return False

#         return True

#     # 情報から、手の文字列を生成する関数 =======================yet
#     # i, j と、本当に報告すべき座標は異なる。計算が必要。
#     def get_ok_string(piece, rf, i, j, a, b) -> str:
#         I = i - a + 1
#         J = j - b + 1

#         if I >= 10:
#             I = chr(ord('A') + I - 10)
#         if J >= 10:
#             J = chr(ord('A') + J - 10)

#         return piece + str(rf) + str(J) + str(I)

#     def is_corner(i, j) -> bool:
#         if player_number == 1:
#             block = 'o'
#         else:
#             block = 'x'

#         if i == 0 and j == 0:
#             if next_grid[1][1] == block:
#                 return True
#             return False

#         if i == 0 and j == 13:
#             if next_grid[1][12] == block:
#                 return True
#             return False

#         if i == 13 and j == 0:
#             if next_grid[12][1] == block:
#                 return True
#             return False

#         if i == 13 and j == 13:
#             if next_grid[12][12] == block:
#                 return True
#             return False

#         if i == 0:
#             if next_grid[1][j - 1] == block or next_grid[1][j + 1] == block:
#                 return True
#             return False

#         if i == 13:
#             if next_grid[12][j - 1] == block or next_grid[12][j + 1] == block:
#                 return True
#             return False

#         if j == 0:
#             if next_grid[i - 1][1] == block or next_grid[i + 1][1] == block:
#                 return True
#             return False

#         if j == 13:
#             if next_grid[i - 1][12] == block or next_grid[i + 1][12] == block:
#                 return True
#             return False

#         if (
#             next_grid[i - 1][j - 1] == block
#             or next_grid[i - 1][j + 1] == block
#             or next_grid[i + 1][j - 1] == block
#             or next_grid[i + 1][j + 1] == block
#         ):
#             return True

#         return False

#     ok_cases = []
#     tmp = []

#     for i in range(14):
#         for j in range(14):
#             cell = next_grid[i][j]

#             # 一つずつマスを見ていく
#             # もし置けるマスであれば、そのマスに対して全ての手を試す
#             if (
#                 is_corner(i, j)
#                 or (player_number == 1 and turn == 0 and i == 4 and j == 4)
#                 or (player_number == 2 and turn == 0 and i == 9 and j == 9)
#             ):
#                 for piece in my_hands:
#                     for rf in range(8):  # rotate & flip
#                         piece_map_origin = BlockType(piece)
#                         piece_map = piece_map_origin.block_map

#                         if rf == 0 or rf == 1:
#                             pass
#                         elif rf == 2 or rf == 3:
#                             piece_map = np.rot90(piece_map, 3).copy()
#                         elif rf == 4 or rf == 5:
#                             piece_map = np.rot90(piece_map, 2).copy()
#                         elif rf == 6 or rf == 7:
#                             piece_map = np.rot90(piece_map, 1).copy()

#                         if rf % 2 == 1:
#                             piece_map = np.fliplr(piece_map)

#                         for a in range(piece_map.shape[0]):
#                             for b in range(piece_map.shape[1]):
#                                 if piece_map[a][b] == 1:
#                                     if is_ok(next_grid, piece_map, i, j, a, b):
#                                         ok_string = get_ok_string(piece, rf, i, j, a, b)
#                                         ok_cases.append(ok_string)
#                                         tmp.append([ok_string, piece, rf, i, j, a, b, piece_map])

#     return ok_cases, tmp
