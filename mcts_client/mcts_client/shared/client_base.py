"""Common WebSocket client base — parses board strings and tracks usable pieces.

Subclasses provide ``choose_action(own, occupied, my_usable, opp_usable, first_move)``
returning a :class:`Placement` or ``None`` for pass.
"""

from __future__ import annotations

import asyncio
import time
from typing import Optional, Set

import websockets

from ..core.bitboard import BOARD_H, BOARD_W, board_str, cell_bit, popcount
from ..core.shapes import (
    ALL_PIECES,
    PIECE_SIZE,
    PLACEMENTS_BY_PIECE,
    Placement,
    encode_action,
)


CHAR_TO_PLAYER = {'o': 1, 'x': 2}


def parse_board(text: str, me: int) -> tuple[int, int]:
    """Parse the server's print-string into (own_bb, opp_bb) bitboards."""
    own = 0
    opp = 0
    rows: list[str] = []
    for line in text.split('\n'):
        cells = [c for c in line if c in ('.', 'o', 'x')]
        if len(cells) == BOARD_W:
            rows.append(''.join(cells))
    if len(rows) != BOARD_H:
        raise ValueError(f'expected {BOARD_H} rows, got {len(rows)}')
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


class BaseClient:
    name: str = 'base'

    def __init__(self, player_number: int, socket, loop) -> None:
        self._loop = loop
        self._socket = socket
        self._player_number = player_number
        self._opp_number = 3 - player_number
        self._my_usable: Set[str] = set(ALL_PIECES)
        self._opp_usable: Set[str] = set(ALL_PIECES)
        self._turn_count = 0
        self._prev_own = 0
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

    # ------------------------------------------------------------------
    # opponent tracking
    # ------------------------------------------------------------------
    def _update_opp_usable(self, opp_bb: int) -> None:
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
        # Find a placement of any matching piece whose mask equals diff
        for name in candidates:
            for p in PLACEMENTS_BY_PIECE[name]:
                if p.mask == diff:
                    self._opp_usable.discard(name)
                    return
        self._opp_usable.discard(candidates[0])

    # ------------------------------------------------------------------
    # core decision
    # ------------------------------------------------------------------
    def _compute_action(self, board_text: str) -> str:
        try:
            own, opp = parse_board(board_text, self._player_number)
        except Exception as exc:  # pragma: no cover
            print(f'{self.name} parse error: {exc}', flush=True)
            return 'X000'
        self._update_opp_usable(opp)

        first_move = (self._turn_count == 0)
        start = time.monotonic()
        placement: Optional[Placement] = self.choose_action(
            own, opp, first_move,
        )
        elapsed = time.monotonic() - start

        if placement is None:
            print(
                f'{self.name} P{self._player_number} turn={self._turn_count} pass=X000 '
                f'elapsed={elapsed:.2f}s',
                flush=True,
            )
            self._prev_own = own
            self._prev_opp = opp
            self._turn_count += 1
            return 'X000'

        self._my_usable.discard(placement.name)
        action = encode_action(placement)
        new_own = own | placement.mask
        self._prev_own = new_own
        self._prev_opp = opp
        print(
            f'{self.name} P{self._player_number} turn={self._turn_count} action={action} '
            f'size={placement.size} elapsed={elapsed:.2f}s',
            flush=True,
        )
        self._turn_count += 1
        return action

    # ------------------------------------------------------------------
    # to be overridden
    # ------------------------------------------------------------------
    def choose_action(self, own: int, opp: int, first_move: bool) -> Optional[Placement]:
        raise NotImplementedError

    # ------------------------------------------------------------------
    # factory
    # ------------------------------------------------------------------
    @classmethod
    async def create(cls, url: str, loop: asyncio.AbstractEventLoop) -> 'BaseClient':
        socket = await websockets.connect(url)
        print(f'{cls.name} PlayerClient: connected', flush=True)
        player_number = await socket.recv()
        print(f'{cls.name} player_number: {player_number}', flush=True)
        return cls(int(player_number), socket, loop)
