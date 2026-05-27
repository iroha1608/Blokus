from __future__ import annotations
import asyncio
import websockets

from .util import make_matrix, build_board_sets, get_ok_cases_by_sets #, get_ok_cases
from .strategies import dicide_hand

class PlayerClient:
    def __init__(self, player_number: int, socket: websockets.WebSocketClientProtocol, loop: asyncio.AbstractEventLoop):
        self._loop = loop

        #ソケット(出入り口)
        #ここから入力し、ここに出力するイメージ。使い方の詳細はもともとのプログラム参照。もしくはドキュメント。
        self._socket = socket

        # 先行の場合は1, 後攻の場合は2 ??
        # 要確認。説明スライドではスライドではこう言ってただけ。
        self._player_number = player_number

        # 自分の手番数
        self.turn = 0

        # 自分の残りピース
        self.my_hands = [chr(ord("A") + i) for i in range(21)]

        # 相手の残りピース。現時点では未使用
        self.ene_hands = [chr(ord("A") + i) for i in range(21)]

    @property
    def player_number(self) -> int:
        return self._player_number

    async def close(self):
        await self._socket.close()

    async def play(self):
        while True:
            board = await self._socket.recv()
            action = self.create_action(board)
            await self._socket.send(action)
            if action == 'X000':
                raise SystemExit

    def create_action(self, board):
        # 盤面文字列を2次元配列へ変換
        next_grid = make_matrix(board)
        board_sets = build_board_sets(
            board_matrix=next_grid,
            player_number=self.player_number,
        )

        # 反則でない手を全列挙
        # ok_cases, tmp = get_ok_cases(
        #     next_grid=next_grid,
        #     player_number=self.player_number,
        #     turn=self.turn,
        #     my_hands=self.my_hands,
        # )
         # 反則でない手を全列挙
        ok_cases, tmp = get_ok_cases_by_sets(
            board_sets=board_sets,
            my_hands=self.my_hands,
            player_number=self.player_number,
            turn=self.turn,
        )

        # 置ける手がなければパス
        if len(ok_cases) == 0:
            self.turn += 1
            return 'X000'

        # ヒューリスティックで手を選択
        this_turn_hand = dicide_hand(
            board_matrix=next_grid,
            ok_cases=ok_cases,
            tmp=tmp,
            player_number=self.player_number,
            turn=self.turn,
            board_sets=board_sets,
        )

        # 選択したピースを手札から削除
        if this_turn_hand != 'X000':
            self.my_hands.remove(this_turn_hand[0])

        # 次の手番に備えて手番数を進める
        self.turn += 1

        return this_turn_hand


    @staticmethod
    async def create(url: str, loop: asyncio.AbstractEventLoop) -> PlayerClient:
        socket = await websockets.connect(url)
        print('PlayerClient: connected')
        player_number = await socket.recv()
        print(f'player_number: {player_number}')
        return PlayerClient(int(player_number), socket, loop)
