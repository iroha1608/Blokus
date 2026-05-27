from __future__ import annotations
import asyncio
import websockets
import random

from AlphaBetansato.game_logic.util import make_matrix, get_ok_cases


class BasePlayer():
    def __init__(
        self,
        player_number: int,
        socket: websockets.WebSocketClientProtocol,
        loop: asyncio.AbstractEventLoop
    ) -> None:
        # loop
        self._loop = loop
        # 出入り口
        # ここから入力し、ここに出力するイメージ。
        # 使い方の詳細はもともとのプログラム参照。もしくはドキュメント。
        self._socket = socket

        # 先行=1, 後攻=2
        self._player_number = player_number
        # 自分の手番数
        self.turn = 0
        # 自分の残りピース
        self.my_hands: list[str] = [chr(ord("A") + i) for i in range(21)]
        # 相手の残りピース。現時点では未使用
        self.ene_hands: list[str] = [chr(ord("A") + i) for i in range(21)]

    @property
    def player_number(self) -> int:
        return self._player_number

    async def close(self):
        await self._socket.close()

    async def play(self):
        """
            mainで実行される。
            socketから盤面を受け取り、手を返す。
        """
        while True:
            board = await self._socket.recv()
            action = self.create_action(board)
            await self._socket.send(action)
            if action == 'X000':
                raise SystemExit

    def create_action(self, board: list[str]) -> str:
        """
            Args:
                board: socketから送られてくる
        """
        # 現在の盤面を二次元配列へ変換
        next_grid = make_matrix(board)

        # 打てる手の取得
        # list[str], list[list[Any]]
        ok_cases, tmp = get_ok_cases(
            next_grid=next_grid,
            player_number=self.player_number,
            turn=self.turn,
            my_hands=self.my_hands,
        )
        # 打てる手がなければパス
        if len(ok_cases) == 0:
            self.turn += 1
            return 'X000'

        # 継承クラスのロジックで最適解取得
        best_hand: str = self.get_best_hand(next_grid, ok_cases, tmp)
        # 選択したピースを削除(1moji me)
        if best_hand != 'X000':
            self.my_hands.remove(best_hand[0])

        self.turn += 1
        return best_hand

    def get_best_hand(
        self, board_matrix: list[list[str]],
        ok_case: list[str], tmp: list
    ) -> str:
        pass

    # staticmethod -> classmethod, hukusuu tukuru node
    @classmethod
    async def create(
        cls, url: str, loop: asyncio.AbstractEventLoop
    ) -> BasePlayer:
        """インスタンス作成時に一度のみ使用。"""
        socket = await websockets.connect(url)
        print(f'{cls.__name__}Player: connected')
        player_number = await socket.recv()
        print(f'player_number: {player_number}')
        return cls(int(player_number), socket, loop)
