from __future__ import annotations
import asyncio
import os
import time
from typing import Optional, Set

import websockets

from .core.bitboard import BOARD_H, BOARD_W, cell_bit, popcount
from .core.shapes import (
    ALL_PIECES,
    PIECE_SIZE,
    PLACEMENTS_BY_PIECE,
    Placement,
    encode_action,
)
from .core.moves import generate_first_moves, generate_moves
from .mcts_search import Searcher

TURN_TIME_BUDGET = float(os.environ.get('MCTS_BUDGET', '8.0'))
CHAR_TO_PLAYER = {'o': 1, 'x': 2}


def _parse_board(text: str, me: int):
    own = 0
    opp = 0
    rows = []
    for line in text.split('\n'):
        cells = [c for c in line if c in ('.', 'o', 'x')]
        if len(cells) == BOARD_W:
            rows.append(''.join(cells))
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c == '.':
                continue
            bit = cell_bit(y, x)
            if CHAR_TO_PLAYER[c] == me:
                own |= bit
            else:
                opp |= bit
    return own, opp


class PlayerClient:
    def __init__(self, player_number: int,
                 socket: websockets.WebSocketClientProtocol,
                 loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._socket = socket
        self._player_number = player_number
        self._opp_number = 3 - player_number
        self._my_usable: Set[str] = set(ALL_PIECES)
        self._opp_usable: Set[str] = set(ALL_PIECES)
        self._turn_count = 0
        self._prev_opp = 0

    @property
    def player_number(self) -> int:
        return self._player_number

    async def close(self):
        await self._socket.close()

    async def play(self):
        while True:
            board_text = await self._socket.recv()
            action = self._compute_action(board_text)
            await self._socket.send(action)
            if action == 'X000':
                raise SystemExit

    def _update_opp_usable(self, opp_bb: int):
        diff = opp_bb & ~self._prev_opp
        n = popcount(diff)
        if n == 0:
            return
        candidates = [p for p in self._opp_usable if PIECE_SIZE[p] == n]
        if not candidates:
            return
        if len(candidates) == 1:
            self._opp_usable.discard(candidates[0])
            return
        for name in candidates:
            for p in PLACEMENTS_BY_PIECE[name]:
                if p.mask == diff:
                    self._opp_usable.discard(name)
                    return
        self._opp_usable.discard(candidates[0])

    def _compute_action(self, board_text: str) -> str:
        own, opp = _parse_board(board_text, self._player_number)
        self._update_opp_usable(opp)

        first_move = (self._turn_count == 0)
        opp_first = (opp == 0)

        searcher = Searcher(
            me=self._player_number,
            opp=self._opp_number,
            time_budget=TURN_TIME_BUDGET,
        )
        placement, value = searcher.search(
            own, opp,
            frozenset(self._my_usable),
            frozenset(self._opp_usable),
            my_first=first_move,
            opp_first=opp_first,
        )

        if placement is None:
            print(f'P{self._player_number} turn={self._turn_count} pass',
                  flush=True)
            self._prev_opp = opp
            self._turn_count += 1
            return 'X000'

        self._my_usable.discard(placement.name)
        action = encode_action(placement)
        self._prev_opp = opp
        print(f'P{self._player_number} turn={self._turn_count} action={action} '
              f'size={placement.size} visits={searcher.last_visits}',
              flush=True)
        self._turn_count += 1
        return action

    @staticmethod
    async def create(url: str,
                     loop: asyncio.AbstractEventLoop) -> PlayerClient:
        socket = await websockets.connect(url)
        print('PlayerClient: connected', flush=True)
        player_number = await socket.recv()
        print(f'player_number: {player_number}', flush=True)
        return PlayerClient(int(player_number), socket, loop)
