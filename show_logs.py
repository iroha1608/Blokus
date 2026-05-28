#!/usr/bin/env python3
"""
Blokus Duo 対戦ログ集計スクリプト

使い方:
  # ① ログが log/ フォルダにある（一番よく使う）
  python3 show_logs_v2_easy.py AI名1_AI名2

  # ② 出力するファイル名を自分で決めたい場合
  python3 show_logs_v2_easy.py AI名1_AI名2 ログフォルダのパス 出力ファイル名

例:
  python3 show_logs.py ss_tarou_1_ss_tarou_2
  python3 show_logs.py ss_tarou_1_ss_tarou_2 log/ result.md
"""

import json
import os
import sys

# ボードのサイズ（14×14）
BOARD_SIZE = 14

# 行・列のID（1〜9 はそのまま、10以降はA〜E）
ROW_IDS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E']

# 各ピースの形（1=ブロックあり、0=なし）
PIECE_SHAPES = {
    'A': [[1]],
    'B': [[1], [1]],
    'C': [[1], [1], [1]],
    'D': [[1, 0], [1, 1]],
    'E': [[1], [1], [1], [1]],
    'F': [[0, 1], [0, 1], [1, 1]],
    'G': [[1, 0], [1, 1], [1, 0]],
    'H': [[1, 1], [1, 1]],
    'I': [[1, 1, 0], [0, 1, 1]],
    'J': [[1], [1], [1], [1], [1]],
    'K': [[0, 1], [0, 1], [0, 1], [1, 1]],
    'L': [[0, 1], [0, 1], [1, 1], [1, 0]],
    'M': [[0, 1], [1, 1], [1, 1]],
    'N': [[1, 1], [0, 1], [1, 1]],
    'O': [[1, 0], [1, 1], [1, 0], [1, 0]],
    'P': [[0, 1, 0], [0, 1, 0], [1, 1, 1]],
    'Q': [[1, 0, 0], [1, 0, 0], [1, 1, 1]],
    'R': [[1, 1, 0], [0, 1, 1], [0, 0, 1]],
    'S': [[1, 0, 0], [1, 1, 1], [0, 0, 1]],
    'T': [[1, 0, 0], [1, 1, 1], [0, 1, 0]],
    'U': [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
}


# ピースを反時計回りに90度回転させる
def rotate_ccw(shape):
    h = len(shape)
    w = len(shape[0])
    result = [[shape[i][w - 1 - j] for i in range(h)] for j in range(w)]
    return result


# ピースを左右反転させる
def flip_lr(shape):
    return [row[::-1] for row in shape]


# rotation_flip の値に応じてピースを変換する
# ビット1-2: 回転回数, ビット0: 反転するかどうか
def apply_transform(shape, rotation_flip):
    rot_count = (rotation_flip & 0x06) >> 1
    is_flipped = (rotation_flip & 0x01) == 1
    result = [row[:] for row in shape]
    for _ in range((4 - rot_count) % 4):
        result = rotate_ccw(result)
    if is_flipped:
        result = flip_lr(result)
    return result


# moves のリストから最終的な盤面を作る（0=空, 1=P1, 2=P2）
def make_board(moves):
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    for move in moves:
        # パスの手は盤面に影響しない
        if move.get('action') == 'pass':
            continue
        piece = move.get('piece')
        if not piece or piece not in PIECE_SHAPES:
            continue
        player = 1 if move['player'] == 'P1' else 2
        rv = move.get('rotation_flip', 0)
        try:
            col = ROW_IDS.index(move['pos'][0])
            row = ROW_IDS.index(move['pos'][1])
        except (ValueError, IndexError, KeyError):
            continue
        shape = apply_transform(PIECE_SHAPES[piece], rv)
        for ri, srow in enumerate(shape):
            for ci, val in enumerate(srow):
                if val == 1:
                    r, c = row + ri, col + ci
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                        board[r][c] = player
    return board


# 盤面を文字で表示する（o=P1, x=P2, .=空）
def board_to_text(board):
    header = '   ' + ' '.join(ROW_IDS)
    rows = [header]
    for i, row in enumerate(board):
        cells = ' '.join(['o' if c == 1 else 'x' if c == 2 else '.' for c in row])
        rows.append(f'{ROW_IDS[i]}  {cells}')
    return '\n'.join(rows)


# ログフォルダから name1 と name2 の対戦ログを探す
def find_games(log_dir, name1, name2):
    if not os.path.isdir(log_dir):
        return []
    games = []
    for fname in sorted(os.listdir(log_dir)):
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(log_dir, fname)
        try:
            with open(fpath, encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        players = data.get('players', [])
        if len(players) < 2:
            continue
        p1 = players[0]['name'].lower()
        p2 = players[1]['name'].lower()
        n1, n2 = name1.lower(), name2.lower()
        # どちらの順番でもマッチするか確認する
        if (n1 in p1 and n2 in p2) or (n1 in p2 and n2 in p1):
            games.append((fname, data))
    return games


# 「name1_name2」を「_」で分割する位置をすべて試して、
# 一番多くのログが見つかった組み合わせを返す
def find_best_split(matchup, log_dir):
    parts = matchup.split('_')
    best = (parts[0], '_'.join(parts[1:]), [])
    for i in range(1, len(parts)):
        n1 = '_'.join(parts[:i])
        n2 = '_'.join(parts[i:])
        games = find_games(log_dir, n1, n2)
        if len(games) > len(best[2]):
            best = (n1, n2, games)
    return best


# Markdown ファイルを生成して保存する
def write_summary(name1, name2, games, output_path):
    lines = [f'# 対戦サマリー: {name1} vs {name2}', '', f'対象ログ数: {len(games)} 試合', '']

    if not games:
        lines.append('該当する対戦ログが見つかりませんでした。')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        return

    # 集計用の変数
    wins = {name1: 0, name2: 0, '引き分け': 0}
    total_score = {name1: 0, name2: 0}
    records = []

    for fname, data in games:
        players = data['players']
        end = data.get('end', {})
        moves = data.get('moves', [])
        p1_name = players[0]['name']
        p2_name = players[1]['name']
        score_p1 = end.get('score', {}).get('P1', 0)
        score_p2 = end.get('score', {}).get('P2', 0)
        winner_id = end.get('winner', '')
        reason = end.get('reason', '')

        # 勝者を名前に変換する
        if winner_id == 'draw':
            winner_label = '引き分け'
            wins['引き分け'] += 1
        elif winner_id == 'P1':
            winner_label = p1_name
            wins[name1 if name1.lower() in p1_name.lower() else name2] += 1
        else:
            winner_label = p2_name
            wins[name1 if name1.lower() in p2_name.lower() else name2] += 1

        # スコアを name1 基準で集計する
        if name1.lower() in p1_name.lower():
            total_score[name1] += score_p1
            total_score[name2] += score_p2
        else:
            total_score[name1] += score_p2
            total_score[name2] += score_p1

        place_count = sum(1 for m in moves if m.get('action') != 'pass')
        pass_count = len(moves) - place_count

        records.append({
            'fname': fname, 'p1_name': p1_name, 'p2_name': p2_name,
            'score_p1': score_p1, 'score_p2': score_p2,
            'winner': winner_label, 'reason': reason,
            'place_count': place_count, 'pass_count': pass_count,
            'board': board_to_text(make_board(moves)),
        })

    # 総合成績テーブル
    n = len(games)
    lines += ['## 総合成績', '', '| AI | 勝利数 | 勝率 | 合計スコア |', '|---|:---:|:---:|:---:|']
    for ai in [name1, name2]:
        rate = f'{wins[ai] / n * 100:.1f}%'
        lines.append(f'| {ai} | {wins[ai]} | {rate} | {total_score[ai]} |')
    lines += [f'| 引き分け | {wins["引き分け"]} | - | - |', '']

    # 試合一覧テーブル
    lines += ['## 試合一覧', '', '| # | ファイル | 先手(P1) | P1点 | 後手(P2) | P2点 | 勝者 | 終了理由 |', '|:---:|---|---|:---:|---|:---:|---|---|']
    for i, g in enumerate(records, 1):
        lines.append(f'| {i} | `{g["fname"]}` | {g["p1_name"]} | {g["score_p1"]} | {g["p2_name"]} | {g["score_p2"]} | {g["winner"]} | {g["reason"]} |')
    lines.append('')

    # 各試合の詳細（盤面付き）
    lines += ['## 各試合詳細', '']
    for i, g in enumerate(records, 1):
        lines += [
            f'### 試合 {i}  ―  {g["p1_name"]} vs {g["p2_name"]}',
            '',
            f'| | 先手 (P1) | 後手 (P2) |',
            f'|---|---|---|',
            f'| AI名 | {g["p1_name"]} | {g["p2_name"]} |',
            f'| 最終スコア | **{g["score_p1"]}点** | **{g["score_p2"]}点** |',
            '',
            f'- **勝者**: {g["winner"]}　／　**終了理由**: {g["reason"]}',
            f'- 配置手数: {g["place_count"]}手　パス: {g["pass_count"]}回',
            '',
            '**最終盤面**（`o`=P1, `x`=P2, `.`=空）',
            '',
            '```',
            g['board'],
            '```',
            '',
        ]

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'✅ サマリーを生成しました: {output_path}')


# メイン処理
def main():
    # コマンドライン引数を取得する
    if len(sys.argv) < 2:
        print('使い方: python3 show_logs_v2_easy.py AI名1_AI名2 [ログフォルダ] [出力ファイル名]')
        sys.exit(1)

    matchup = sys.argv[1]
    log_dir = sys.argv[2] if len(sys.argv) >= 3 else 'log'
    output_path = sys.argv[3] if len(sys.argv) >= 4 else f'{matchup}_summary.md'

    # AI名を自動で分割して対戦ログを探す
    name1, name2, games = find_best_split(matchup, log_dir)

    if games:
        print(f'🔍 {name1} vs {name2} の対戦を {len(games)} 試合発見')
    else:
        print(f'⚠️  {log_dir} に該当するログが見つかりませんでした。')

    write_summary(name1, name2, games, output_path)


if __name__ == '__main__':
    main()
