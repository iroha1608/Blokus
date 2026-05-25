from __future__ import annotations
import asyncio
import websockets
import time
import math
import random


BOARD_SIZE = 14
START_POS = {1: (4, 4), 2: (9, 9)}
SIDE_DIRS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAG_DIRS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
ALL_PIECE_NAMES = list('ABCDEFGHIJKLMNOPQRSTU')
MCTS_TIME_LIMIT = 13.0
MAX_MCTS_DEPTH = 2

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

PIECE_SIZES = {n: sum(sum(r) for r in s) for n, s in PIECE_SHAPES.items()}


def _rot90_ccw(shape):
    h = len(shape)
    w = len(shape[0])
    return [[shape[i][w - 1 - j] for i in range(h)] for j in range(w)]


def _fliplr(shape):
    return [row[::-1] for row in shape]


def _get_cells(shape):
    return [(r, c) for r, row in enumerate(shape) for c, v in enumerate(row) if v == 1]


def _apply_rotation(shape, rv):
    rot_count = (rv & 0x06) >> 1
    is_flipped = rv & 0x01 == 0x01
    m = [row[:] for row in shape]
    for _ in range((4 - rot_count) % 4):
        m = _rot90_ccw(m)
    if is_flipped:
        m = _fliplr(m)
    return m


def _precompute_orientations():
    result = {}
    for name, shape in PIECE_SHAPES.items():
        orients = []
        seen = set()
        for rv in range(8):
            m = _apply_rotation(shape, rv)
            key = tuple(tuple(row) for row in m)
            if key not in seen:
                seen.add(key)
                cells = _get_cells(m)
                cells_set = frozenset(cells)
                orients.append((rv, len(m), len(m[0]), cells, cells_set))
        result[name] = orients
    return result


ORIENTATIONS = _precompute_orientations()


def _parse_board(board_str):
    lines = board_str.strip().split('\n')
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    for i, line in enumerate(lines[1:]):
        for j, c in enumerate(line[1:]):
            if c == 'o':
                board[i][j] = 1
            elif c == 'x':
                board[i][j] = 2
    return board


def _copy_board(board):
    return [row[:] for row in board]


def _apply_move(board, player, piece_name, rot_val, col, row):
    new_board = _copy_board(board)
    shape = _apply_rotation(PIECE_SHAPES[piece_name], rot_val)
    for ri, srow in enumerate(shape):
        for ci, val in enumerate(srow):
            if val == 1:
                new_board[row + ri][col + ci] = player
    return new_board


def _count_cells(board, player):
    total = 0
    for row in board:
        for c in row:
            if c == player:
                total += 1
    return total


def _get_my_cells(board, player):
    cells = set()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == player:
                cells.add((r, c))
    return cells


def _get_corner_candidates(board, player):
    my_cells = _get_my_cells(board, player)
    if not my_cells:
        return set()
    sides = set()
    corners = set()
    for r, c in my_cells:
        for dr, dc in SIDE_DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                sides.add((nr, nc))
        for dr, dc in DIAG_DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                corners.add((nr, nc))
    return {(r, c) for r, c in corners - sides - my_cells if board[r][c] == 0}


def _get_legal_moves(board, player, available_pieces, is_first):
    if is_first:
        sr, sc = START_POS[player]
        seen = set()
        moves = []
        for pname in available_pieces:
            for rv, h, w, cells, _ in ORIENTATIONS[pname]:
                for cr, cc in cells:
                    pr = sr - cr
                    pc = sc - cc
                    if pr < 0 or pr + h > BOARD_SIZE or pc < 0 or pc + w > BOARD_SIZE:
                        continue
                    key = (pname, rv, pc, pr)
                    if key in seen:
                        continue
                    if any(board[pr + dr][pc + dc] != 0 for dr, dc in cells):
                        continue
                    seen.add(key)
                    moves.append(key)
        return moves

    cc_set = _get_corner_candidates(board, player)
    if not cc_set:
        return []

    my_cells = _get_my_cells(board, player)
    seen = set()
    moves = []

    for pname in available_pieces:
        for rv, h, w, cells, _ in ORIENTATIONS[pname]:
            tried = set()
            for cr, cc in cells:
                for ccr, ccc in cc_set:
                    pr = ccr - cr
                    pc = ccc - cc
                    if (pr, pc) in tried:
                        continue
                    tried.add((pr, pc))
                    if pr < 0 or pr + h > BOARD_SIZE or pc < 0 or pc + w > BOARD_SIZE:
                        continue
                    if any(board[pr + dr][pc + dc] != 0 for dr, dc in cells):
                        continue
                    has_side = False
                    for dr, dc in cells:
                        ar, ac = pr + dr, pc + dc
                        for sr, sc in SIDE_DIRS:
                            if (ar + sr, ac + sc) in my_cells:
                                has_side = True
                                break
                        if has_side:
                            break
                    if has_side:
                        continue
                    key = (pname, rv, pc, pr)
                    if key not in seen:
                        seen.add(key)
                        moves.append(key)
    return moves


def _evaluate(board, my_player, my_pieces, opp_pieces):
    opp_player = 3 - my_player
    my_score = _count_cells(board, my_player)
    opp_score = _count_cells(board, opp_player)
    my_cc = len(_get_corner_candidates(board, my_player))
    opp_cc = len(_get_corner_candidates(board, opp_player))
    score = (my_score - opp_score) + 0.3 * (my_cc - opp_cc)
    return 1.0 / (1.0 + math.exp(-score / 8.0))


class _MCTSNode:
    __slots__ = ['board', 'my_player', 'my_pieces', 'opp_pieces',
                 'is_my_turn', 'is_first_me', 'is_first_opp',
                 'parent', 'move', 'children', 'untried_moves',
                 'wins', 'visits', 'depth']

    def __init__(self, board, my_player, my_pieces, opp_pieces,
                 is_my_turn, is_first_me, is_first_opp,
                 parent=None, move=None, depth=0):
        self.board = board
        self.my_player = my_player
        self.my_pieces = my_pieces
        self.opp_pieces = opp_pieces
        self.is_my_turn = is_my_turn
        self.is_first_me = is_first_me
        self.is_first_opp = is_first_opp
        self.parent = parent
        self.move = move
        self.children = []
        self.untried_moves = None
        self.wins = 0.0
        self.visits = 0
        self.depth = depth

    def _init_moves(self):
        if self.untried_moves is not None:
            return
        if self.depth >= MAX_MCTS_DEPTH:
            self.untried_moves = []
            return
        if self.is_my_turn:
            moves = _get_legal_moves(self.board, self.my_player, self.my_pieces, self.is_first_me)
        else:
            opp = 3 - self.my_player
            moves = _get_legal_moves(self.board, opp, self.opp_pieces, self.is_first_opp)
        random.shuffle(moves)
        self.untried_moves = moves

    def is_fully_expanded(self):
        self._init_moves()
        return len(self.untried_moves) == 0

    def expand(self):
        self._init_moves()
        move = self.untried_moves.pop()
        pname, rv, col, row = move
        if self.is_my_turn:
            new_board = _apply_move(self.board, self.my_player, pname, rv, col, row)
            new_my = [p for p in self.my_pieces if p != pname]
            child = _MCTSNode(
                new_board, self.my_player, new_my, self.opp_pieces,
                False, False, self.is_first_opp,
                self, move, self.depth + 1
            )
        else:
            opp = 3 - self.my_player
            new_board = _apply_move(self.board, opp, pname, rv, col, row)
            new_opp = [p for p in self.opp_pieces if p != pname]
            child = _MCTSNode(
                new_board, self.my_player, self.my_pieces, new_opp,
                True, self.is_first_me, False,
                self, move, self.depth + 1
            )
        self.children.append(child)
        return child

    def best_child(self, c=1.414):
        is_max = self.is_my_turn

        def ucb1(child):
            if child.visits == 0:
                return float('inf')
            exploit = child.wins / child.visits
            if not is_max:
                exploit = 1.0 - exploit
            explore = c * math.sqrt(math.log(self.visits) / child.visits)
            return exploit + explore

        return max(self.children, key=ucb1)

    def rollout(self):
        return _evaluate(self.board, self.my_player, self.my_pieces, self.opp_pieces)

    def backpropagate(self, value):
        self.visits += 1
        self.wins += value
        if self.parent:
            self.parent.backpropagate(value)


def _mcts_search(board, my_player, my_pieces, opp_pieces,
                 is_first_me, is_first_opp, time_limit=MCTS_TIME_LIMIT):
    root = _MCTSNode(board, my_player, my_pieces, opp_pieces,
                     True, is_first_me, is_first_opp)
    root._init_moves()

    if not root.untried_moves:
        return None
    if len(root.untried_moves) == 1:
        return root.untried_moves[0]

    start = time.time()
    iterations = 0

    while time.time() - start < time_limit:
        node = root

        while node.is_fully_expanded() and node.children:
            node = node.best_child()

        if not node.is_fully_expanded():
            node = node.expand()

        value = node.rollout()
        node.backpropagate(value)
        iterations += 1

    elapsed = time.time() - start
    print(f'MCTS: {iterations} iterations, {elapsed:.2f}s')

    if not root.children:
        return root.untried_moves[0] if root.untried_moves else None

    best = max(root.children, key=lambda c: c.visits)
    print(f'Best: {best.move}, visits={best.visits}, '
          f'wr={best.wins / best.visits:.3f}')
    return best.move


class PlayerClient:
    def __init__(self, player_number: int,
                 socket: websockets.WebSocketClientProtocol,
                 loop: asyncio.AbstractEventLoop):
        self._loop = loop
        self._socket = socket
        self._player_number = player_number
        self._my_pieces = list(ALL_PIECE_NAMES)
        self._opp_pieces = list(ALL_PIECE_NAMES)
        self._prev_board = None

    @property
    def player_number(self) -> int:
        return self._player_number

    async def close(self):
        await self._socket.close()

    async def play(self):
        while True:
            board_str = await self._socket.recv()
            action = self.create_action(board_str)
            await self._socket.send(action)
            if action == 'X000':
                raise SystemExit

    def create_action(self, board_str):
        board = _parse_board(board_str)

        if self._prev_board is not None:
            self._track_opponent(board)
        else:
            self._init_opponent(board)

        is_first_me = _count_cells(board, self._player_number) == 0
        opp = 3 - self._player_number
        is_first_opp = _count_cells(board, opp) == 0

        move = _mcts_search(
            board, self._player_number,
            self._my_pieces, self._opp_pieces,
            is_first_me, is_first_opp
        )

        if move is None:
            self._prev_board = _copy_board(board)
            return 'X000'

        pname, rv, col, row = move
        self._my_pieces.remove(pname)
        self._prev_board = _apply_move(
            board, self._player_number, pname, rv, col, row
        )

        x_hex = format(col + 1, 'X')
        y_hex = format(row + 1, 'X')
        return f'{pname}{rv}{x_hex}{y_hex}'

    def _init_opponent(self, board):
        opp = 3 - self._player_number
        opp_cells = [(r, c) for r in range(BOARD_SIZE)
                     for c in range(BOARD_SIZE) if board[r][c] == opp]
        if opp_cells:
            self._detect_and_remove_opp(opp_cells)

    def _track_opponent(self, board):
        opp = 3 - self._player_number
        new_cells = [(r, c) for r in range(BOARD_SIZE)
                     for c in range(BOARD_SIZE)
                     if board[r][c] == opp and self._prev_board[r][c] != opp]
        if new_cells:
            self._detect_and_remove_opp(new_cells)

    def _detect_and_remove_opp(self, cells):
        min_r = min(r for r, _ in cells)
        min_c = min(c for _, c in cells)
        normalized = frozenset((r - min_r, c - min_c) for r, c in cells)
        for pname in self._opp_pieces:
            for _, _, _, _, cells_set in ORIENTATIONS[pname]:
                if cells_set == normalized:
                    self._opp_pieces.remove(pname)
                    return

    @staticmethod
    async def create(url: str,
                     loop: asyncio.AbstractEventLoop) -> PlayerClient:
        socket = await websockets.connect(url)
        print('PlayerClient: connected')
        player_number = await socket.recv()
        print(f'player_number: {player_number}')
        return PlayerClient(int(player_number), socket, loop)
