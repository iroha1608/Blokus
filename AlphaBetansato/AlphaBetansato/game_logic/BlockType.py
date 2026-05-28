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
    def size(self):
        """ブロックの大きさを取得するプロパティ"""
        if self == BlockType.A:
            return 1
        elif self == BlockType.B:
            return 2
        elif self in (BlockType.C, BlockType.D):
            return 3
        elif self in (
            BlockType.E, BlockType.F, BlockType.G, BlockType.H, BlockType.I
        ):
            return 4
        elif self == BlockType.X:
            return 0
        else:
            return 5

    @property
    def corner(self):
        """ブロックの角の数を取得するプロパティ"""
        if self in (
            BlockType.A, BlockType.B, BlockType.C, BlockType.E,
            BlockType.H, BlockType.J
        ):
            return 4
        elif self in (
            BlockType.D, BlockType.F, BlockType.K, BlockType.M,
            BlockType.N, BlockType.Q
        ):
            return 5
        elif self in (
            BlockType.G, BlockType.I, BlockType.L, BlockType.O,
            BlockType.P, BlockType.S
        ):
            return 6
        elif self in (
            BlockType.R, BlockType.T
        ):
            return 7
        elif self == BlockType.X:
            return 0
        # U
        else:
            return 8

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
                ■  ■
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
                ■  ■
                corner: 5
            """
            return np.array([[0, 1], [0, 1], [0, 1], [1, 1]])

        elif self == BlockType.L:
            """
                type L:
                    ■
                    ■
                ■  ■
                ■
                corner: 6
            """
            return np.array([[0, 1], [0, 1], [1, 1], [1, 0]])

        elif self == BlockType.M:
            """
                type M:
                    ■
                ■  ■
                ■  ■
                corner: 5
            """
            return np.array([[0, 1], [1, 1], [1, 1]])

        elif self == BlockType.N:
            """
                type N:
                ■  ■
                ■
                ■  ■
                corner: 5
            """
            return np.array([[1, 1], [0, 1], [1, 1]])

        elif self == BlockType.O:
            """
                type O:
                ■
                ■  ■
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
                ■  ■  ■
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
                ■  ■
                    ■  ■
                        ■
                corner: 7
            """
            return np.array([[1, 1, 0], [0, 1, 1], [0, 0, 1]])

        elif self == BlockType.S:
            """
                type S:
                ■
                ■  ■  ■
                        ■
                corner: 6
            """
            return np.array([[1, 0, 0], [1, 1, 1], [0, 0, 1]])

        elif self == BlockType.T:
            """
                type T:
                ■
                ■  ■  ■
                    ■
                corner: 7
            """
            return np.array([[1, 0, 0], [1, 1, 1], [0, 1, 0]])

        elif self == BlockType.U:
            """
                type U:
                    ■
                ■  ■  ■
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
