import random

from AlphaBetansato.players.BasePlayer import BasePlayer


class RandomPlayer(BasePlayer):
    def get_best_hand(
        self, board_matrix: list[list[int]],
        ok_cases: list[str], tmp: list
    ) -> str:
        # seed wo settei sitai toki you
        # random.seed(1)
        best_hand: str = random.choice(ok_cases)
        return best_hand
