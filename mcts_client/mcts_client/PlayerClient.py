"""mcts_ai client — Policy-guided MCTS (UCT) on bitboards."""

from __future__ import annotations

import os
from typing import Optional

from .core.shapes import Placement
from .shared.client_base import BaseClient
from .search import Searcher

TURN_TIME_BUDGET = float(os.environ.get('MCTS_BUDGET', '8.0'))


class PlayerClient(BaseClient):
    name = 'mcts_ai'

    def choose_action(self, own: int, opp: int, first_move: bool) -> Optional[Placement]:
        opp_first = (opp == 0)
        searcher = Searcher(
            me=self._player_number,
            opp=self._opp_number,
            time_budget=TURN_TIME_BUDGET,
        )
        move, value = searcher.search(
            own,
            opp,
            frozenset(self._my_usable),
            frozenset(self._opp_usable),
            my_first=first_move,
            opp_first=opp_first,
        )
        return move
