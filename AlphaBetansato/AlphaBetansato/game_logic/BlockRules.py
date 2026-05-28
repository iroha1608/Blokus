"""
    Gameのルールを格納する予定。
    utilから移動予定
"""
def apply_move(
    board_matrix, move_data, player_number: int
) -> list[list[str]]:
    """
        指定された手を盤面に適用、
        既存盤面を壊さずに新しい二次元配列()で返す。
        Args:
            board_matrix: 現在の盤面を二次元配列にしたもの。
            move_data: tmpに入ってる情報の展開。
            player_number: 先行=1, 後攻=2
        Returns:
            new_board: 現在の盤面のコピー。
    """
    new_board = [row[:] for row in board_matrix]

    _, _, _, i, j, a, b, piece_map = move_data

    block = 'o' if player_number == 1  else block = 'x'

    for p in range(piece_map.shape[0]):
        for q in range(piece_map.shape[1]):
            if piece_map[p][q] == 1:
                new_board[i - a + p][j - b + q] = block
    return new_board
