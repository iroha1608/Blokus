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
        corners = set()

        rows = len(board_matrix)
        cols = len(board_matrix[0])
        diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        orthogonals = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for r in range(rows):
            for c in range(cols):
                if board_matrix[r][c] == player_block:
                    for dr, dc in diagonals:
                        nr, nc = r + dr, c + dc

                        if 0 <= nr < rows and 0 <= nc < cols and board_matrix[nr][nc] not in ("o", "x"):
                            is_valid_corner = True
                            for or_r, or_c in orthogonals:
                                nnr, nnc = nr + or_r, nc + or_c
                                if (0 <= nnr < rows and 0 <= nnc < cols and board_matrix[nnr][nnc] == player_block):
                                    is_valid_corner = False
                                    break
                            if is_valid_corner:
                                corners.add((nr, nc))
        return len(corners)


    def rate_board(self, board_matrix: list[list[str]]) -> float:
        """
            盤面評価関数。
        """
        my_block = "o" if self._player_number == 1 else "x"
        ene_block = "x" if self._player_number == 1 else "o"

        # 陣地の広さ
        my_area = sum(row.count(my_block) for row in board_matrix)
        ene_area = sum(row.count(ene_block) for row in board_matrix)

        # 増やせる角の数
        my_corners = self._count_corners(board_matrix, my_block)
        ene_corners = self._count_corners(board_matrix, ene_block)

        # スコアの計算
        weight_area = 0.0
        weight_my_corners = 0.0
        weight_ene_corners = 0.0
        if self.turn < 5:
            weight_area = 1.0
            weight_my_corners = 2.5
            weight_ene_corners = 2.0
        elif self.turn < 12:
            weight_area = 1.0
            weight_my_corners = 2.0
            weight_ene_corners = 2.5
        else:
            weight_area = 2.5
            weight_my_corners = 1.0
            weight_ene_corners = 2.0

        my_score = (my_area * weight_area) + (my_corners * weight_my_corners)
        ene_score = (ene_area * weight_area) + (ene_corners * weight_ene_corners)

        # for row in board_matrix:
            # for cell in row:
                # if cell == my_block:
                    # my_score += 1
                # elif cell == ene_block:
                    # ene_score += 1

        return my_score - ene_score

    def iterative_ab(
        self,
        board_matrix: list[list[str]], depth: int,
        alpha: float, beta: float, is_maximizing: bool,
        current_player, my_hands, ene_hands,
        p1_turn: int, p2_turn: int
    ):
        """n手先の盤面のスコアを計算して返す"""

        if depth == 0:
            return self.rate_board(board_matrix)

        # 現在のプレイヤー目線の持ちブロック、ターン数の取得
        current_hands = (
            my_hands
            if current_player == self.player_number
            else ene_hands
        )
        current_turn = p1_turn if current_player == 1 else p2_turn

        # 次に打つプレイヤー、ブロック、ターン数で有効手の取得
        ok_cases, tmp = get_ok_cases(
            board_matrix, current_player, current_turn, current_hands
        )

        if not ok_cases:
            return self.rate_board(board_matrix)

        # それぞれが今何ターン目か動的に設定
        next_player = 2 if current_player == 1 else 1
        next_p1_turn = p1_turn + 1 if current_player == 1 else p1_turn
        next_p2_turn = p2_turn + 1 if current_player == 2 else p2_turn

        # 上位10盤面に絞る
        search_width = 3
        scored_moves = []
        for move_string, move_data in zip(ok_cases, tmp):
            nb = apply_move(board_matrix, move_data, current_player)
            score = self.rate_board(nb)
            scored_moves.append((score, move_string, move_data))

        scored_moves.sort(key=lambda x: x[0], reverse=is_maximizing)
        ok_cases = [x[1] for x in scored_moves[:search_width]]
        tmp = [x[2] for x in scored_moves[:search_width]]

        if is_maximizing:
            max_rate = -math.inf

            for move_string, move_data in zip(ok_cases, tmp):
                new_board = apply_move(board_matrix, move_data, current_player)
                new_my_hands = [h for h in my_hands if h != move_string[0]]

                rate_score = self.iterative_ab(
                    board_matrix=new_board,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_maximizing=False,
                    current_player=next_player,
                    my_hands=new_my_hands,
                    ene_hands=ene_hands,
                    p1_turn=next_p1_turn,
                    p2_turn=next_p2_turn
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

                rate_score = self.iterative_ab(
                    board_matrix=new_board,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    is_maximizing=True,
                    current_player=next_player,
                    my_hands=my_hands,
                    ene_hands=new_ene_hands,
                    p1_turn=next_p1_turn,
                    p2_turn=next_p2_turn
                )

                min_rate = min(min_rate, rate_score)
                beta = min(beta, rate_score)

                # αカット
                if beta <= alpha:
                    break

            return min_rate

    def get_best_hand(
        self, board_matrix: list[list[str]], ok_cases: list[str], tmp: list
    ) -> str:
        """
            各手のn手先のスコアを調べ、最善手の文字列を返す。
        """
        if self.turn == 0:
            if self.player_number == 1:
                return 'R355'
            elif self.player_number == 2:
                return 'R399'

        depth = 3

        alpha = -math.inf
        beta = math.inf

        best_hand = ok_cases[0]
        max_rate = -math.inf

        # それぞれが今何ターン目か動的に設定
        next_player = 2 if self.player_number == 1 else 1
        p1_turn = self.turn if self.player_number == 1 else self.turn + 1
        p2_turn = self.turn if self.player_number == 2 else self.turn
        next_p1_turn = p1_turn + 1 if self.player_number == 1 else p1_turn
        next_p2_turn = p2_turn + 1 if self.player_number == 2 else p2_turn

        # 上位10盤面に絞る
        search_width = 5
        scored_moves = []
        for move_string, move_data in zip(ok_cases, tmp):
            nb = apply_move(board_matrix, move_data, self.player_number)
            score = self.rate_board(nb)
            scored_moves.append((score, move_string, move_data))

        scored_moves.sort(key=lambda x: x[0], reverse=True)
        ok_cases = [x[1] for x in scored_moves[:search_width]]
        tmp = [x[2] for x in scored_moves[:search_width]]

        for move_string, move_data in zip(ok_cases, tmp):
            new_board = apply_move(board_matrix, move_data, self.player_number)
            new_my_hands = [h for h in self.my_hands if h != move_string[0]]

            # 2手目以降をα-β探索+反復深化で評価
            rate_score = self.iterative_ab(
                board_matrix=new_board,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                is_maximizing=False,
                current_player=next_player,
                my_hands=new_my_hands,
                ene_hands=self.ene_hands,
                p1_turn=next_p1_turn,
                p2_turn=next_p2_turn
            )

            # スコアの更新
            if rate_score > max_rate:
                max_rate = rate_score
                best_hand = move_string

            alpha = max(alpha, rate_score)

        return best_hand
