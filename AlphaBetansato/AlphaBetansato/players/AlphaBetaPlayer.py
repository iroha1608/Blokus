import math

from AlphaBetansato.players.BasePlayer import BasePlayer


class AlphaBetaPlayer(BasePlayer)
    """
    α-β探索+再帰で反復深化
    高いスコアの盤面以外切り落としていく
    get_best_hand->反復深化関数->評価関数
    """

    def rate_board(self, board_matrix: list[list[int]]) -> int:
        """
        盤面評価関数。
        とりあえずマス目の数を数える。
        """
        my_block = "o" if self._player_number == 1 else "x"
        ene_block = "x" if self._player_number == 1 else "o"

        my_score = 0
        ene_score = 0

        for row in board_matrix:
            for cell in row:
                if cell == my_block:
                    my_score += 1
                elif cell == ene_block:
                    ene_score += 1

        return my_score - ene_score

    def iterative_ab(
        self, board_matrix, depth, alpha, beta,
        is_maximizing, current_pllayer, my_hands, ene_hands, turn
    ):
        if depth == 0:
            return self.rate_board(board_matrix), None
        current_hands = my_hands if current_player


    def get_best_hand(
        self, board_matrix: list[list[int]],
        ok_cases: list[str], tmp: list
    ) -> str:

        depth = 1

        alpha = -math.inf
        beta = math.inf

        return best_hand
