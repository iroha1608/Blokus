"""Policy-guided MCTS (UCT) with bitboard rollouts.

This is a from-scratch alternative to alpha-beta: instead of pruning a
search tree by depth+evaluation, we expand a tree node-by-node and use
short policy-driven rollouts to estimate value.
"""

from __future__ import annotations

import math
import random
import time
from typing import List, Optional, Tuple

from .core.bitboard import corner_attach_mask, popcount
from .core.eval import evaluate
from .core.moves import generate_first_moves, generate_moves
from .core.shapes import Placement


C_PUCT = 1.4
ROLLOUT_DEPTH = 12  # plies of light playout
TOP_K_EXPAND = 24  # cap candidate moves per node


class Node:
    __slots__ = (
        'own', 'opp', 'my_usable', 'opp_usable',
        'my_first', 'opp_first', 'my_turn',
        'parent', 'parent_move',
        'children', 'visits', 'value_sum', 'prior',
        'untried_moves',
    )

    def __init__(
        self,
        own: int,
        opp: int,
        my_usable: frozenset,
        opp_usable: frozenset,
        my_first: bool,
        opp_first: bool,
        my_turn: bool,
        parent: Optional['Node'] = None,
        parent_move: Optional[Placement] = None,
        prior: float = 1.0,
    ):
        self.own = own
        self.opp = opp
        self.my_usable = my_usable
        self.opp_usable = opp_usable
        self.my_first = my_first
        self.opp_first = opp_first
        self.my_turn = my_turn
        self.parent = parent
        self.parent_move = parent_move
        self.children: List[Node] = []
        self.visits = 0
        self.value_sum = 0.0
        self.prior = prior
        self.untried_moves: Optional[List[Placement]] = None

    def q(self) -> float:
        if self.visits == 0:
            return 0.0
        return self.value_sum / self.visits

    def u(self, parent_visits: int) -> float:
        return C_PUCT * self.prior * math.sqrt(parent_visits + 1) / (1 + self.visits)


def _policy_score(p: Placement, opp_corner: int) -> float:
    return p.size * 4.0 + popcount(p.mask & opp_corner) * 2.0


def _legal_moves(node: Node, me: int, opp_num: int) -> List[Placement]:
    is_first = node.my_first if node.my_turn else node.opp_first
    occupied = node.own | node.opp
    if node.my_turn:
        own_bb, usable = node.own, node.my_usable
        side = me
    else:
        own_bb, usable = node.opp, node.opp_usable
        side = opp_num
    if is_first:
        return generate_first_moves(side, usable)
    return generate_moves(own_bb, occupied, usable)


def _expand_untried(node: Node, me: int, opp_num: int) -> List[Placement]:
    moves = _legal_moves(node, me, opp_num)
    if not moves:
        return []
    occupied = node.own | node.opp
    opp_attach = corner_attach_mask(
        node.opp if node.my_turn else node.own, occupied
    )
    moves.sort(key=lambda m: -_policy_score(m, opp_attach))
    return moves[:TOP_K_EXPAND]


def _child_state(node: Node, mv: Placement) -> Node:
    if node.my_turn:
        new_own = node.own | mv.mask
        new_my_usable = node.my_usable - {mv.name}
        return Node(
            new_own, node.opp, new_my_usable, node.opp_usable,
            my_first=False, opp_first=node.opp_first,
            my_turn=False, parent=node, parent_move=mv,
        )
    new_opp = node.opp | mv.mask
    new_opp_usable = node.opp_usable - {mv.name}
    return Node(
        node.own, new_opp, node.my_usable, new_opp_usable,
        my_first=node.my_first, opp_first=False,
        my_turn=True, parent=node, parent_move=mv,
    )


def _select(node: Node) -> Node:
    while node.children and (
        node.untried_moves is not None and not node.untried_moves
    ):
        node = max(
            node.children,
            key=lambda c: c.q() * (1 if node.my_turn else -1) + c.u(node.visits),
        )
    return node


def _expand(node: Node, me: int, opp_num: int) -> Node:
    if node.untried_moves is None:
        node.untried_moves = _expand_untried(node, me, opp_num)
    if not node.untried_moves:
        return node
    mv = node.untried_moves.pop(0)
    child = _child_state(node, mv)
    occupied = node.own | node.opp
    opp_attach = corner_attach_mask(
        node.opp if node.my_turn else node.own, occupied
    )
    child.prior = max(_policy_score(mv, opp_attach), 1.0)
    node.children.append(child)
    return child


def _rollout(node: Node, me: int, opp_num: int) -> float:
    own = node.own
    opp = node.opp
    my_usable = set(node.my_usable)
    opp_usable = set(node.opp_usable)
    my_first = node.my_first
    opp_first = node.opp_first
    my_turn = node.my_turn

    for _ in range(ROLLOUT_DEPTH):
        if my_turn:
            own_bb, usable = own, my_usable
            side = me
            is_first = my_first
        else:
            own_bb, usable = opp, opp_usable
            side = opp_num
            is_first = opp_first
        occupied = own | opp
        if is_first:
            moves = generate_first_moves(side, usable)
        else:
            moves = generate_moves(own_bb, occupied, usable)
        if moves:
            opp_attach = corner_attach_mask(
                opp if my_turn else own, occupied
            )
            top = sorted(moves, key=lambda m: -_policy_score(m, opp_attach))[:4]
            mv = random.choice(top)
            if my_turn:
                own |= mv.mask
                my_usable.discard(mv.name)
                my_first = False
            else:
                opp |= mv.mask
                opp_usable.discard(mv.name)
                opp_first = False
        my_turn = not my_turn

    return evaluate(own, opp, frozenset(my_usable), frozenset(opp_usable))


def _backup(node: Node, value: float) -> None:
    n = node
    while n is not None:
        n.visits += 1
        n.value_sum += value
        n = n.parent


class Searcher:
    def __init__(
        self,
        me: int,
        opp: int,
        time_budget: float = 8.0,
        max_simulations: int = 20000,
    ):
        self.me = me
        self.opp = opp
        self.time_budget = time_budget
        self.max_simulations = max_simulations
        self.last_visits = 0

    def search(
        self,
        own: int,
        opp: int,
        my_usable: frozenset,
        opp_usable: frozenset,
        my_first: bool,
        opp_first: bool,
    ) -> Tuple[Optional[Placement], float]:
        root = Node(
            own, opp, my_usable, opp_usable,
            my_first=my_first, opp_first=opp_first,
            my_turn=True,
        )
        root.untried_moves = _expand_untried(root, self.me, self.opp)
        if not root.untried_moves:
            return None, 0.0
        start = time.monotonic()
        sims = 0
        while sims < self.max_simulations and time.monotonic() - start < self.time_budget * 0.9:
            leaf = _select(root)
            if leaf.untried_moves is None:
                leaf.untried_moves = _expand_untried(leaf, self.me, self.opp)
            if leaf.untried_moves:
                leaf = _expand(leaf, self.me, self.opp)
            value = _rollout(leaf, self.me, self.opp)
            _backup(leaf, value)
            sims += 1
        self.last_visits = sims
        if not root.children:
            return None, 0.0
        best = max(root.children, key=lambda c: c.visits)
        return best.parent_move, best.q()
