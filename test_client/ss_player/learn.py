"""
対戦ログから評価関数の重みを学習し weights.json に保存する。

使い方:
  python learn.py [ログディレクトリ]
  デフォルトは ../../game/log/
"""
from __future__ import annotations
import json
import os
import sys
import math
import random

BOARD_SIZE = 14
START_POS = {1: (4, 4), 2: (9, 9)}
SIDE_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAG_DIRS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
ROW_IDS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E']

PIECE_SHAPES = {
    'A': [[1]], 'B': [[1],[1]], 'C': [[1],[1],[1]],
    'D': [[1,0],[1,1]], 'E': [[1],[1],[1],[1]],
    'F': [[0,1],[0,1],[1,1]], 'G': [[1,0],[1,1],[1,0]],
    'H': [[1,1],[1,1]], 'I': [[1,1,0],[0,1,1]],
    'J': [[1],[1],[1],[1],[1]], 'K': [[0,1],[0,1],[0,1],[1,1]],
    'L': [[0,1],[0,1],[1,1],[1,0]], 'M': [[0,1],[1,1],[1,1]],
    'N': [[1,1],[0,1],[1,1]], 'O': [[1,0],[1,1],[1,0],[1,0]],
    'P': [[0,1,0],[0,1,0],[1,1,1]], 'Q': [[1,0,0],[1,0,0],[1,1,1]],
    'R': [[1,1,0],[0,1,1],[0,0,1]], 'S': [[1,0,0],[1,1,1],[0,0,1]],
    'T': [[1,0,0],[1,1,1],[0,1,0]], 'U': [[0,1,0],[1,1,1],[0,1,0]],
}
PIECE_SIZES = {n: sum(sum(r) for r in s) for n, s in PIECE_SHAPES.items()}


def _rot90_ccw(shape):
    h, w = len(shape), len(shape[0])
    return [[shape[i][w-1-j] for i in range(h)] for j in range(w)]


def _fliplr(shape):
    return [row[::-1] for row in shape]


def _apply_rotation(shape, rv):
    rot_count = (rv & 0x06) >> 1
    is_flipped = rv & 0x01 == 0x01
    m = [row[:] for row in shape]
    for _ in range((4 - rot_count) % 4):
        m = _rot90_ccw(m)
    if is_flipped:
        m = _fliplr(m)
    return m


def _apply_move(board, player, piece, rv, col, row):
    b = [r[:] for r in board]
    shape = _apply_rotation(PIECE_SHAPES[piece], rv)
    for ri, srow in enumerate(shape):
        for ci, val in enumerate(srow):
            if val == 1:
                b[row + ri][col + ci] = player
    return b


def _count(board, player):
    return sum(c == player for row in board for c in row)


def _corner_candidates(board, player):
    my = {(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE)
          if board[r][c] == player}
    if not my:
        return set()
    sides = set()
    corners = set()
    for r, c in my:
        for dr, dc in SIDE_DIRS:
            nr, nc = r+dr, c+dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                sides.add((nr, nc))
        for dr, dc in DIAG_DIRS:
            nr, nc = r+dr, c+dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                corners.add((nr, nc))
    return {(r,c) for r,c in corners - sides - my if board[r][c] == 0}


def extract_features(board, my_player, my_pieces, opp_pieces):
    opp = 3 - my_player
    my_score = _count(board, my_player)
    opp_score = _count(board, opp)
    my_cc = len(_corner_candidates(board, my_player))
    opp_cc = len(_corner_candidates(board, opp))
    my_rem = sum(PIECE_SIZES[p] for p in my_pieces)
    opp_rem = sum(PIECE_SIZES[p] for p in opp_pieces)
    center_my = sum(1 for r in range(3,11) for c in range(3,11)
                    if board[r][c] == my_player)
    center_opp = sum(1 for r in range(3,11) for c in range(3,11)
                     if board[r][c] == opp)
    return [
        my_score - opp_score,
        my_cc - opp_cc,
        opp_rem - my_rem,
        center_my - center_opp,
    ]


def replay_game(game_data):
    """ゲームログをリプレイし、各ターン終了時の特徴量とMCTS視点のラベルを返す。"""
    players = game_data['players']
    moves = game_data['moves']
    end = game_data['end']

    mcts_id = None
    for p in players:
        if 'mcts' in p['name']:
            mcts_id = p['id']
    if mcts_id is None:
        return []

    mcts_player = 1 if mcts_id == 'P1' else 2
    mcts_won = (end['winner'] == mcts_id)
    label = 1.0 if mcts_won else 0.0

    if end['reason'] != 'normal':
        return []

    board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
    p1_pieces = list('ABCDEFGHIJKLMNOPQRSTU')
    p2_pieces = list('ABCDEFGHIJKLMNOPQRSTU')

    samples = []
    for move in moves:
        if 'action' in move and move['action'] == 'pass':
            continue
        pid = move['player']
        player_num = 1 if pid == 'P1' else 2
        piece = move['piece']
        rv = move['rotation_flip']
        col = ROW_IDS.index(move['pos'][0])
        row = ROW_IDS.index(move['pos'][1])

        board = _apply_move(board, player_num, piece, rv, col, row)
        if player_num == 1:
            p1_pieces.remove(piece)
        else:
            p2_pieces.remove(piece)

        my_p = p1_pieces if mcts_player == 1 else p2_pieces
        opp_p = p2_pieces if mcts_player == 1 else p1_pieces
        feats = extract_features(board, mcts_player, list(my_p), list(opp_p))
        samples.append((feats, label))

    return samples


def sigmoid(x):
    if x > 500:
        return 1.0
    if x < -500:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def predict(features, weights, temp):
    raw = sum(w * f for w, f in zip(weights, features))
    return sigmoid(raw / temp)


def loss_and_grad(samples, weights, temp, reg=0.01):
    total_loss = 0.0
    grad = [0.0] * len(weights)
    grad_temp = 0.0

    for feats, label in samples:
        p = predict(feats, weights, temp)
        p = max(1e-7, min(1 - 1e-7, p))
        total_loss += -(label * math.log(p) + (1 - label) * math.log(1 - p))
        err = p - label
        raw = sum(w * f for w, f in zip(weights, feats))
        for i in range(len(weights)):
            grad[i] += err * feats[i] / temp
        grad_temp += err * (-raw / (temp * temp))

    n = len(samples)
    total_loss /= n
    for i in range(len(weights)):
        total_loss += 0.5 * reg * weights[i] ** 2
        grad[i] = grad[i] / n + reg * weights[i]
    grad_temp /= n

    return total_loss, grad, grad_temp


def train(samples, lr=0.01, epochs=2000, reg=0.01):
    weights = [1.0, 0.3, 0.1, 0.2]
    temp = 8.0

    best_loss = float('inf')
    best_weights = weights[:]
    best_temp = temp

    for epoch in range(epochs):
        l, grad, grad_t = loss_and_grad(samples, weights, temp, reg)
        for i in range(len(weights)):
            weights[i] -= lr * grad[i]
        temp -= lr * grad_t
        temp = max(1.0, temp)

        if l < best_loss:
            best_loss = l
            best_weights = weights[:]
            best_temp = temp

        if epoch % 500 == 0:
            print(f'  epoch {epoch}: loss={l:.4f} w={[round(w,3) for w in weights]} temp={temp:.2f}')

    return best_weights, best_temp, best_loss


def main():
    log_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), '..', '..', 'game', 'log')
    log_dir = os.path.abspath(log_dir)

    print(f'Loading logs from: {log_dir}')
    all_samples = []
    game_count = 0

    for fname in sorted(os.listdir(log_dir)):
        if not fname.endswith('.json'):
            continue
        with open(os.path.join(log_dir, fname)) as f:
            data = json.load(f)
        samples = replay_game(data)
        if samples:
            all_samples.extend(samples)
            game_count += 1
            result = 'WIN' if samples[0][1] == 1.0 else 'LOSE'
            print(f'  {fname}: {len(samples)} states, MCTS {result}')

    print(f'\nTotal: {game_count} games, {len(all_samples)} training samples')

    if len(all_samples) < 5:
        print('Not enough data to train. Need at least 5 samples.')
        return

    print('\nTraining...')
    weights, temp, loss = train(all_samples)

    result = {
        'w_score': round(weights[0], 4),
        'w_corner': round(weights[1], 4),
        'w_remaining': round(weights[2], 4),
        'w_center': round(weights[3], 4),
        'sigmoid_temp': round(temp, 4),
    }

    out_path = os.path.join(os.path.dirname(__file__), 'weights.json')
    with open(out_path, 'w') as f:
        json.dump(result, f, indent=2)

    print(f'\nFinal loss: {loss:.4f}')
    print(f'Learned weights: {json.dumps(result, indent=2)}')
    print(f'Saved to: {out_path}')


if __name__ == '__main__':
    main()
