"""Position evaluation function (shared across all paradigms)."""

from __future__ import annotations

from typing import Iterable

from .bitboard import (
    BOARD_MASK,
    corner_attach_mask,
    diag_neighbours,
    ortho_neighbours,
    popcount,
)
from .shapes import PIECE_SIZE


def remaining_value(usable: Iterable[str]) -> int:
    return sum(PIECE_SIZE[n] for n in usable)


def evaluate(
    own: int,
    opp: int,
    my_usable: frozenset,
    opp_usable: frozenset,
    *,
    w_score: float = 1.0,
    w_corner: float = 0.6,
    w_reach: float = 2.0,
    w_territory: float = 0.25,
) -> float:
    """Heuristic estimate of (my final score) - (opp final score).

    Components:
      score     : current squares-on-board difference (drives win)
      corner    : corner-attach count difference (mobility)
      reach     : asymmetric penalty for near-suffocation
      territory : Voronoi-style 2-step reach difference
      bonus     : +20/-20 if one side has emptied its tray
    """
    occupied = own | opp

    my_sq = popcount(own)
    opp_sq = popcount(opp)

    my_attach = corner_attach_mask(own, occupied)
    opp_attach = corner_attach_mask(opp, occupied)
    my_corner = popcount(my_attach)
    opp_corner = popcount(opp_attach)

    bonus = 0.0
    if not my_usable:
        bonus += 20.0
    if not opp_usable:
        bonus -= 20.0

    reach = 0.0
    if my_corner <= 2:
        reach -= (3 - my_corner) ** 2
    if opp_corner <= 2:
        reach += (3 - opp_corner) ** 2

    # Cheap Voronoi proxy: 2-step diagonal+orthogonal reach.
    # Counts cells we can plausibly extend into within ~2 moves.
    empty = BOARD_MASK & ~occupied
    my_reach = (diag_neighbours(my_attach) | ortho_neighbours(my_attach)) & empty
    opp_reach = (diag_neighbours(opp_attach) | ortho_neighbours(opp_attach)) & empty
    my_only = popcount(my_reach & ~opp_reach)
    opp_only = popcount(opp_reach & ~my_reach)
    territory = my_only - opp_only

    return (
        w_score * (my_sq - opp_sq)
        + w_corner * (my_corner - opp_corner)
        + w_reach * reach
        + w_territory * territory
        + bonus
    )
