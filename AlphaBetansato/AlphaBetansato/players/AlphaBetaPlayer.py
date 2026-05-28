import math

from AlphaBetansato.players.BasePlayer import BasePlayer
from AlphaBetansato.game_logic.BlockRules import apply_move
from AlphaBetansato.game_logic.util import get_ok_cases


class AlphaBetaPlayer(BasePlayer):
    """
    α-β探索+再帰で反復深化
    高いスコアの盤面以外切り落としていく
    get_best_hand->反復深化関数->評価関数
    """
    def _count_corners(
        self, board_matrix: list[list[int]], player_block: str
    ) -> int:
        """増やせる角の数を返す関数"""
        corner = set()

        rows = len(board_matrix)
        cols = len(board_matrix[0])
        diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        orthgonals = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for r in range(rows):
            for c in range(cols):
                if board_matrix[r][c] == player_block:
                    for dr, dc in diagonals:
                        nr, nc = r + dr, c + dc

                        if 0 <= nr < rows and 0 <= nc < cols and board_matrix[nr][nc]:
                            is*valid_corner = True
                            for or_r, or_c in orthogonals:
                                nnr, nnc = or_r, nc + or_c
                                if (0 <= nnr < rows and 0 <= nnc < cols and board_matrix[nnr][nnc] == player_block):
                                    is_valid_corner = False
                                    break
                            if is_valid_corner:
                                corners.add((nr, nc))
        return len(corners)


    def rate_board(self, board_matrix: list[list[str]]) -> float:
        """
            盤面評価関数。
            とりあえずマス目の数を数える。
        """
        my_block = "o" if self._player_number == 1 else "x"
        ene_block = "x" if self._player_number == 1 else "o"

        # 陣地の広さ
        weight_area = 1.0
        my_area = sum(row.count(my_block) for row in board_matrix)
        ene_area = sum(row.count(ene_block) for row in board_matrix)

        # 増やせる角の数
        weight_corner = 2.0
        my_corners = self._count_corners(board_matrix, my_block)
        ene_corners = self._count_corners(board_matrix, ene_block)

        # スコアの計算
        my_score = (my_area * weight_area) + (my_corners * weight_corners)
        ene_score = (ene_area * weight_area) + (ene_corners * weight_corners)

        # for row in board_matrix:
            # for cell in row:
                # if cell == my_block:
                    # my_score += 1
                # elif cell == ene_block:
                    # ene_score += 1

        return my_score - ene_score

    def iterative_ab(
            self, board_matrix, depth: int, alpha: float, beta: float,
        is_maximizing: bool, current_player, my_hands, ene_hands, turn: int
    ):
        """n手先の盤面のスコアを計算して返す"""

        if depth == 0:
            return self.rate_board(board_matrix)

        current_hands = (
            my_hands
            if current_player == self.player_number
            else ene_hands
        )
        ok_cases, tmp = get_ok_cases(
            board_matrix, current_player, turn, current_hands
        )

        if not ok_cases:
            return self.rate_board(board_matrix)

        if is_maximizing:
            max_rate = -math.inf

            for move_string, move_data in zip(ok_cases, tmp):
                new_board = apply_move(board_matrix, move_data, current_player)
                new_my_hands = [h for h in my_hands if h != move_string[0]]

                ene_player = 2 if current_player == 1 else 1

                rate_score = self.iterative_ab(
                    board_matrix=new_board,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_maximizing=False,
                    current_player=ene_player,
                    my_hands=new_my_hands,
                    ene_hands=ene_hands,
                    turn=turn + 1
                )

                max_rate = max(max_rate, rate_score)
                alpha = max(alpha, rate_score)

                # βカット
                if beta <= alpha:
                    break

            return max_rate
        else:
            min_rate = math.inf

            for move_string, move_data in zip(ok_cases, tmp):
                new_board = apply_move(board_matrix, move_data, current_player)
                new_ene_hands = [h for h in ene_hands if h != move_string[0]]

                ene_player = 2 if current_player == 1 else 1

                rate_score = self.iterative_ab(
                    board_matrix=new_board,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_maximizing=True,
                    current_player=ene_player,
                    my_hands=my_hands,
                    ene_hands=new_ene_hands,
                    turn=turn + 1
                )

                min_rate = min(min_rate, rate_score)
                beta = min(beta, rate_score)

                # αカット
                if beta <= alpha:
                    break

            return min_rate

    def get_best_hand(
        self, board_matrix: list[list[str]],
        ok_cases: list[str], tmp: list
    ) -> str:
        """
            各手のn手先のスコアを調べ、最善手の文字列を返す。
        """
        depth = 1

        alpha = -math.inf
        beta = math.inf

        best_hand = ok_cases[0]
        max_rate = -math.inf

        for move_string, move_data in zip(ok_cases, tmp):
            new_board = apply_move(board_matrix, move_data, self.player_number)
            new_my_hands = [h for h in self.my_hands if h != move_string[0]]

            ene_player = 2 if self.player_number == 1 else 1

            # 2手目以降をα-β探索+反復深化で評価
            rate_score = self.iterative_ab(
                board_matrix=new_board,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                is_maximizing=False,
                current_player=ene_player,
                my_hands=new_my_hands,
                ene_hands=self.ene_hands,
                turn=self.turn + 1
            )

            # スコアの更新
            if rate_score > max_rate:
                max_rate = rate_score
                best_hand = move_string

            alpha = max(alpha, rate_score)

        return best_hand
