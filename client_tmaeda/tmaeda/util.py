from enum import Enum
from typing import Any
import numpy as np

# ピースの形状を定義するクラス gameディレクトリよりコピー==========================done
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

# ピース形状ごとのユニーク回転パターン配列表を定数化
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

def make_next_board_sets(action, board_sets):
    if action == "X000":
        return board_sets
    piece = action[0]
    rf = int(action[1])
    x = int(action[2], 16) - 1
    y = int(action[3], 16) - 1

    # actionから、実際に置かれるピースの座標集合を作る
    piece_cells = make_piece_cells(piece, rf, x, y)

    # ピースを置いた後の基本集合を作る
    next_my_cells = board_sets["my_cells"] | piece_cells
    next_empty_cells = board_sets["empty_cells"] - piece_cells
    next_ene_cells = board_sets["ene_cells"]
    # 自分と相手のNGセル、角セルの座標集合を作成
    next_my_ng_cells = make_ng_cells(next_my_cells, next_empty_cells)
    next_ene_ng_cells = make_ng_cells(next_ene_cells, next_empty_cells)
    next_my_corner_cells = make_corner_cells(next_my_cells, next_empty_cells, next_my_ng_cells)
    next_ene_corner_cells = make_corner_cells(next_ene_cells, next_empty_cells, next_ene_ng_cells)

    return {
        "my_cells": next_my_cells,
        "ene_cells": next_ene_cells,
        "empty_cells": next_empty_cells,
        "my_ng_cells": next_my_ng_cells,
        "ene_ng_cells": next_ene_ng_cells,
        "my_corner_cells": next_my_corner_cells,
        "ene_corner_cells": next_ene_corner_cells,
    }

