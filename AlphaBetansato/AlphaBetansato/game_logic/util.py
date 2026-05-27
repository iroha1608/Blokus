"""
    make_matrix, get_ok_casesを提供。
"""
from enum import Enum
from typing import Any
import numpy as np

from AlphaBetansato.game_logic.BlockType import BlockType


def make_matrix(board) -> list[list[str]]:
    """
        もらった盤面を2次元配列に変換する。
    """
    l = 0
    new = ""
    for char in board:
        if char in ('.', 'o', 'x', '\n'):
            new += str(char)
    if new.startswith('\n'):
        new = new[1:]
    if new.endswith('\n'):
        new = new[:-1]
    board_list = new.split(sep='\n')
    board_matrix = [[char for char in string] for string in board_list]
    return board_matrix

def get_ok_cases(
    next_grid: list[list[str]],
    player_number: int,
    turn: int,
    my_hands: list[str]
) -> tuple[list[str], list]:
    """
        反則でない手を全列挙する関数。
        置けるマスに対し置ける手を全列挙し、
        反則でない手のみlistに追加、そのリストを返す。
        最初に盤面外判定 -> 他の場面でも安心して検証できる。
        is_corner() -> is_ok() -> get_ok_string()

        Args:
            next_grid:
            player_number:
            turn:
            my_hands:
        Returns:
            ok_cases list[str]: 合法手のリスト
            tmp list[list[Any]]: 判定結果の保存したリスト
    """
    # is_neighbor()とis_corner()で使用。最初にまとめて処理。
    if player_number == 1:
        block = 'o'
    else:
        block = 'x'

    def is_ok(next_grid, piece_map, i, j, a, b) -> bool:
        """
            反則判定関数。
            is_out(盤面外) -> is_dup(重なり) -> is_neighbor(辺の隣接)を判定。
            Returns:
                Bool: 合法手にTrue、反則はFalseを返す。
        """

        def is_out(next_grid, piece_map, i, j, a, b) -> bool:
            """
                ピースの盤面外判定関数。
                ピースは盤面外に置いてはいけない。
            """
            for p in range(piece_map.shape[0]):
                for q in range(piece_map.shape[1]):
                    if piece_map[p][q] == 1:
                        if i - a + p < 0 or i - a + p > 13 or j - b + q < 0 or j - b + q > 13:
                            return True
            return False

        def is_dup(next_grid, piece_map, i, j, a, b) -> bool:
            """
                ピースの重なり判定関数。
                自分/敵のピースでも重なってはいけない。
            """
            for p in range(piece_map.shape[0]):
                for q in range(piece_map.shape[1]):
                    if piece_map[p][q] == 1:
                        if (
                            next_grid[i - a + p][j - b + q] == 'o'
                            or next_grid[i - a + p][j - b + q] == 'x'
                        ):
                            return True
            return False

        def is_neighbor(next_grid, piece_map, i, j, a, b) -> bool:
            """
                ピースの隣接判定。
                既に置かれている自分のピースと辺で隣接してはいけない。
            """
            grid_size = len(next_grid)
            for p in range(piece_map.shape[0]):
                for q in range(piece_map.shape[1]):
                    if piece_map[p][q] == 1:
                        r = i - a + p
                        c = j - b + q

                        # Skip if r or c is out of the grid bounds
                        if r < 0 or r >= grid_size or c < 0 or c >= grid_size:
                            continue

                        # Check corners and edges separately
                        if r == 0 and c == 0:
                            if next_grid[r + 1][c] == block or next_grid[r][c + 1] == block:
                                return True
                        elif r == 0 and c == grid_size - 1:
                            if next_grid[r + 1][c] == block or next_grid[r][c - 1] == block:
                                return True
                        elif r == grid_size - 1 and c == 0:
                            if next_grid[r - 1][c] == block or next_grid[r][c + 1] == block:
                                return True
                        elif r == grid_size - 1 and c == grid_size - 1:
                            if next_grid[r - 1][c] == block or next_grid[r][c - 1] == block:
                                return True
                        elif r == 0:
                            if (
                                next_grid[r][c + 1] == block
                                or next_grid[r + 1][c] == block
                                or next_grid[r][c - 1] == block
                            ):
                                return True
                        elif r == grid_size - 1:
                            if (
                                next_grid[r - 1][c] == block
                                or next_grid[r][c + 1] == block
                                or next_grid[r][c - 1] == block
                            ):
                                return True
                        elif c == 0:
                            if (
                                next_grid[r - 1][c] == block
                                or next_grid[r][c + 1] == block
                                or next_grid[r + 1][c] == block
                            ):
                                return True
                        elif c == grid_size - 1:
                            if (
                                next_grid[r - 1][c] == block
                                or next_grid[r + 1][c] == block
                                or next_grid[r][c - 1] == block
                            ):
                                return True
                        else:
                            if (
                                next_grid[r - 1][c] == block
                                or next_grid[r][c + 1] == block
                                or next_grid[r + 1][c] == block
                                or next_grid[r][c - 1] == block
                            ):
                                return True

            return False

        # --------------- is_ok()のメインフロー ---------------
        if is_out(next_grid, piece_map, i, j, a, b):
            return False

        if is_dup(next_grid, piece_map, i, j, a, b):
            return False

        if is_neighbor(next_grid, piece_map, i, j, a, b):
            return False

        return True

    def get_ok_string(piece, rf, i, j, a, b) -> str:
        """
            情報から手の文字列を生成する関数
            i, j と報告すべき座標が異なるため計算し文字列に変換。
            piece: ピースのID
            rf: 回転、反転表参照
            j: 横座標
            i: 縦座標
        """
        J = j - b + 1
        I = i - a + 1

        if J >= 10:
            J = chr(ord('A') + J - 10)
        if I >= 10:
            I = chr(ord('A') + I - 10)

        return piece + str(rf) + str(J) + str(I)

    def is_corner(i, j) -> bool:
        """
            角判定
        """
        if i == 0 and j == 0:
            if next_grid[1][1] == block:
                return True
            return False

        if i == 0 and j == 13:
            if next_grid[1][12] == block:
                return True
            return False

        if i == 13 and j == 0:
            if next_grid[12][1] == block:
                return True
            return False

        if i == 13 and j == 13:
            if next_grid[12][12] == block:
                return True
            return False

        if i == 0:
            if next_grid[1][j - 1] == block or next_grid[1][j + 1] == block:
                return True
            return False

        if i == 13:
            if next_grid[12][j - 1] == block or next_grid[12][j + 1] == block:
                return True
            return False

        if j == 0:
            if next_grid[i - 1][1] == block or next_grid[i + 1][1] == block:
                return True
            return False

        if j == 13:
            if next_grid[i - 1][12] == block or next_grid[i + 1][12] == block:
                return True
            return False

        if (
            next_grid[i - 1][j - 1] == block
            or next_grid[i - 1][j + 1] == block
            or next_grid[i + 1][j - 1] == block
            or next_grid[i + 1][j + 1] == block
        ):
            return True

        return False
    # --------------- ここまで関数定義 ---------------

    # --------------- get_ok_cases()のメインフロー開始 ---------------
    ok_cases: list = []
    tmp: list = []

    for i in range(14):
        for j in range(14):
            cell = next_grid[i][j]

            # 一つずつマスを見ていく
            # もし置けるマスであれば、そのマスに対して全ての手を試す
            if (
                is_corner(i, j)
                or (player_number == 1 and turn == 0 and i == 4 and j == 4)
                or (player_number == 2 and turn == 0 and i == 9 and j == 9)
            ):
                for piece in my_hands:
                    for rf in range(8):  # rotate & flip
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

                        for a in range(piece_map.shape[0]):
                            for b in range(piece_map.shape[1]):
                                if piece_map[a][b] == 1:
                                    if is_ok(next_grid, piece_map, i, j, a, b):
                                        ok_string = get_ok_string(piece, rf, i, j, a, b)
                                        ok_cases.append(ok_string)
                                        tmp.append([ok_string, piece, rf, i, j, a, b, piece_map])

    return ok_cases, tmp
