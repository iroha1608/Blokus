"""Legal move generation using bitboards + precomputed placement DB."""

from __future__ import annotations

from typing import Iterable, List

from .bitboard import corner_attach_mask, iter_bits, side_touch_mask
from .shapes import (
    FIRST_TARGET_BIT,
    PLACEMENTS_BY_ANCHOR,
    PLACEMENTS_BY_PIECE,
    Placement,
)


def generate_first_moves(player: int, usable: Iterable[str]) -> List[Placement]:
    """Legal opening moves — must cover the player's start cell."""
    target_bit = FIRST_TARGET_BIT[player]
    out: List[Placement] = []
    for name in usable:
        for p in PLACEMENTS_BY_PIECE[name]:
            if p.mask & target_bit:
                out.append(p)
    return out


def generate_moves(
    own: int,
    occupied: int,
    usable: Iterable[str],
) -> List[Placement]:
    """Legal subsequent placements for *own* given current occupancy."""
    corner = corner_attach_mask(own, occupied)
    if corner == 0:
        return []
    side = side_touch_mask(own)
    out: List[Placement] = []
    seen: set = set()
    for cell_bit_idx in iter_bits(corner):
        for name in usable:
            anchor_table = PLACEMENTS_BY_ANCHOR[name].get(cell_bit_idx)
            if not anchor_table:
                continue
            for p in anchor_table:
                key = (p.name, p.rotation, p.top_y, p.top_x)
                if key in seen:
                    continue
                mask = p.mask
                if mask & occupied:
                    continue
                if mask & side:
                    continue
                # corner_attach is already satisfied — we anchored on a corner cell.
                seen.add(key)
                out.append(p)
    return out
