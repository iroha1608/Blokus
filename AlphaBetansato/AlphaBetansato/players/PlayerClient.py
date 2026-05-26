from __future__ import annotations
import asyncio
import websockets

from AlphaBetansato.game_logic.util import make_matrix, get_ok_cases
from AlphaBetansato.players.strategies import dicide_hand

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
        # 現在の盤面を配列へ変換
        next_grid = make_matrix(board)

        # 打てる手の取得
        ok_cases, tmp = get_ok_cases(
            next_grid=next_grid,
            player_number=self.player_number,
            turn=self.turn,
            my_hands=self.my_hands,
        )
        # 置ける手がなければパス
        if len(ok_cases) == 0:
            self.turn += 1
            return 'X000'

        # 継承クラスのロジックで最適解取得
        best_action = self.best_hand(next_grid, ok, case, tmp)
        # 選択したピースを削除
        if best_action != 'X000':
            self.my_hands.remove(bast_action[0])

        self.turn += 1
        return this_turn_hand


    # staticmethod -> classmethod
    @classmethod
    async def create(
        url: str, loop: asyncio.AbstractEventLoop
    ) -> PlayerClient:
        socket = await websockets.connect(url)
        print('PlayerClient: connected')
        player_number = await socket.recv()
        print(f'player_number: {player_number}')
        return PlayerClient(int(player_number), socket, loop)
