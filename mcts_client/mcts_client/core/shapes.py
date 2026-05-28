"""Precomputed piece variants and full placement database.

For each (piece, rotation, top_y, top_x) that fits on the 14x14 board,
the placement is stored as:
  - cells: tuple of (y, x) board coordinates
  - mask: bitboard with those cells set

All placements are also indexed by "anchor cell" so move generation can
iterate only the placements that touch a given corner-attach cell.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from .bitboard import BOARD_H, BOARD_W, cell_bit

PIECE_DEFS: Dict[str, List[List[int]]] = {
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

ALL_PIECES = list(PIECE_DEFS.keys())
PIECE_SIZE = {n: sum(sum(r) for r in m) for n, m in PIECE_DEFS.items()}
PIECE_INDEX = {n: i for i, n in enumerate(ALL_PIECES)}


def _rotation_to_shape(base: np.ndarray, rot_value: int) -> np.ndarray:
    rot_count = (rot_value & 0b110) >> 1
    is_reversed = (rot_value & 0b001) == 1
    out = base.copy()
    for _ in range((4 - rot_count) % 4):
        out = np.rot90(out)
    if is_reversed:
        out = np.fliplr(out)
    return out.astype(np.int8)


class Placement:
    """A concrete placement of one piece at one (rotation, top-left)."""

    __slots__ = ('name', 'rotation', 'top_y', 'top_x', 'cells', 'mask', 'size')

    def __init__(
        self,
        name: str,
        rotation: int,
        top_y: int,
        top_x: int,
        cells: Tuple[Tuple[int, int], ...],
        mask: int,
    ):
        self.name = name
        self.rotation = rotation
        self.top_y = top_y
        self.top_x = top_x
        self.cells = cells
        self.mask = mask
        self.size = len(cells)

    def __repr__(self) -> str:  # pragma: no cover
        return f'Placement({self.name}/{self.rotation} top=({self.top_y},{self.top_x}))'


def encode_action(p: Placement) -> str:
    to_s = '0123456789ABCDE'
    return f"{p.name}{p.rotation}{to_s[p.top_x + 1]}{to_s[p.top_y + 1]}"


# Build all placements.
# PLACEMENTS_BY_PIECE[name] -> list[Placement]
# PLACEMENTS_BY_ANCHOR[name][bit_index] -> list[Placement]
# PLACEMENTS_COVERING_CELL[bit_index] -> dict[name -> list[Placement]]
PLACEMENTS_BY_PIECE: Dict[str, List[Placement]] = {}
PLACEMENTS_BY_ANCHOR: Dict[str, Dict[int, List[Placement]]] = {}


def _build_placements() -> None:
    for name in ALL_PIECES:
        base = np.array(PIECE_DEFS[name], dtype=np.int8)
        all_placements: List[Placement] = []
        seen_keys: set = set()
        for rot_value in range(8):
            shape = _rotation_to_shape(base, rot_value)
            H, W = shape.shape
            # Cells inside this oriented shape (dy, dx within the bounding box)
            ys, xs = np.where(shape == 1)
            shape_cells = list(zip(ys.tolist(), xs.tolist()))
            # Deduplicate identical post-rotation shapes (e.g. symmetric pieces)
            shape_key = (H, W, frozenset(shape_cells))
            if shape_key in seen_keys:
                continue
            seen_keys.add(shape_key)
            for top_y in range(BOARD_H - H + 1):
                for top_x in range(BOARD_W - W + 1):
                    cells = tuple(
                        (top_y + dy, top_x + dx) for dy, dx in shape_cells
                    )
                    mask = 0
                    for y, x in cells:
                        mask |= cell_bit(y, x)
                    all_placements.append(
                        Placement(name, rot_value, top_y, top_x, cells, mask)
                    )
        PLACEMENTS_BY_PIECE[name] = all_placements

        anchor_map: Dict[int, List[Placement]] = {}
        for p in all_placements:
            for y, x in p.cells:
                bit_index = y * BOARD_W + x
                anchor_map.setdefault(bit_index, []).append(p)
        PLACEMENTS_BY_ANCHOR[name] = anchor_map


_build_placements()


# Convenience: total number of placements per piece (sanity check)
def placement_counts() -> Dict[str, int]:  # pragma: no cover
    return {n: len(v) for n, v in PLACEMENTS_BY_PIECE.items()}


# First-move targets (0-indexed)
FIRST_TARGET = {1: (4, 4), 2: (9, 9)}
FIRST_TARGET_BIT = {p: cell_bit(*FIRST_TARGET[p]) for p in (1, 2)}
