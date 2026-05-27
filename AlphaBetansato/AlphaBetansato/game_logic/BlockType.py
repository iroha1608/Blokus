from enum import Enum
from typing import Any
import numpy as np


class BlockType(Enum):
    """
        ブロックの形状を定義するクラス。
        game/blocks_duo/BlockType.pyと同等。
        自分の手で角を増やす、相手の手で角を減らすため
        cornerの数メモ。
    """
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

    @property
    def block_map(self) -> np.ndarray[Any, np.dtype[int]]:

        if self == BlockType.A:
            """
                type A:
                ■
                corner: 4
            """
            return np.array([[1]])

        elif self == BlockType.B:
            """
                type B:
                ■
                ■
                corner: 4
            """
            return np.array([[1], [1]])

        elif self == BlockType.C:
            """
                type C:
                ■
                ■
                ■
                corner: 4
            """

            return np.array([[1], [1], [1]])

        elif self == BlockType.D:
            """
                type D:
                ■
                ■ ■
                corner: 5
            """
            return np.array([[1, 0], [1, 1]])

        elif self == BlockType.E:
            """
                type E:
                ■
                ■
                ■
                ■
                corner: 4
            """
            return np.array([[1], [1], [1], [1]])

        elif self == BlockType.F:
            """
                type F:
                ■
                ■
                ■ ■
                corner: 5
            """
            return np.array([[0, 1], [0, 1], [1, 1]])

        elif self == BlockType.G:
            """
                type G:
                ■
                ■ ■
                ■
                corner: 6
            """
            return np.array([[1, 0], [1, 1], [1, 0]])

        elif self == BlockType.H:
            """
                type H:
                ■ ■
                ■ ■
                corner: 4
            """
            return np.array([[1, 1], [1, 1]])

        elif self == BlockType.I:
            """
                type I:
                ■ ■
                ■ ■
                corner: 6
            """
            return np.array([[1, 1, 0], [0, 1, 1]])

        elif self == BlockType.J:
            """
                type J:
                ■
                ■
                ■
                ■
                ■
                corner: 4
            """
            return np.array([[1], [1], [1], [1], [1]])

        elif self == BlockType.K:
            """
                type K:
                   ■
                   ■
                   ■
                ■ ■
                corner: 5
            """
            return np.array([[0, 1], [0, 1], [0, 1], [1, 1]])

        elif self == BlockType.L:
            """
                type L:
                   ■
                   ■
                ■ ■
                ■
                corner: 6
            """
            return np.array([[0, 1], [0, 1], [1, 1], [1, 0]])

        elif self == BlockType.M:
            """
                type M:
                   ■
                ■ ■
                ■ ■
                corner: 5
            """
            return np.array([[0, 1], [1, 1], [1, 1]])

        elif self == BlockType.N:
            """
                type N:
                ■ ■
                ■
                ■ ■
                corner: 5
            """
            return np.array([[1, 1], [0, 1], [1, 1]])

        elif self == BlockType.O:
            """
                type O:
                ■
                ■ ■
                ■
                ■
                corner: 6
            """
            return np.array([[1, 0], [1, 1], [1, 0], [1, 0]])

        elif self == BlockType.P:
            """
                type P:
                ■
                ■
                ■ ■ ■
                corner: 6
            """
            return np.array([[0, 1, 0], [0, 1, 0], [1, 1, 1]])

        elif self == BlockType.Q:
            """
                type Q:
                ■
                ■
                ■ ■ ■
                corner: 5
            """
            return np.array([[1, 0, 0], [1, 0, 0], [1, 1, 1]])

        elif self == BlockType.R:
            """
                type R:
                ■ ■
                   ■ ■
                      ■
                corner: 7
            """
            return np.array([[1, 1, 0], [0, 1, 1], [0, 0, 1]])

        elif self == BlockType.S:
            """
                type S:
                ■
                ■ ■ ■
                      ■
                corner: 6
            """
            return np.array([[1, 0, 0], [1, 1, 1], [0, 0, 1]])

        elif self == BlockType.T:
            """
                type T:
                ■
                ■ ■ ■
                   ■
                corner: 7
            """
            return np.array([[1, 0, 0], [1, 1, 1], [0, 1, 0]])

        elif self == BlockType.U:
            """
                type U:
                   ■
                ■ ■ ■
                   ■
                corner: 8
            """
            return np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])

        elif self == BlockType.X:
            """
                type X:パスをする時用
            """
            return np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

        else:
            raise NotImplementedError
