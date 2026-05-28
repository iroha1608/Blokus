"""196-bit Python int bitboard primitives for 14x14 Blokus Duo.

Bit layout: cell (y, x) -> bit position y*14 + x.
Python ints are arbitrary precision, so a full board fits in a single int.
"""

from __future__ import annotations

BOARD_W = 14
BOARD_H = 14
N_CELLS = BOARD_W * BOARD_H
BOARD_MASK = (1 << N_CELLS) - 1

# Column masks
def _col_mask(x: int) -> int:
    m = 0
    for y in range(BOARD_H):
        m |= 1 << (y * BOARD_W + x)
    return m


COL_MASK = [_col_mask(x) for x in range(BOARD_W)]
NOT_COL_W = BOARD_MASK & ~COL_MASK[0]  # cells whose x >= 1 (safe to shift west)
NOT_COL_E = BOARD_MASK & ~COL_MASK[BOARD_W - 1]  # cells whose x <= 12 (safe to shift east)


def cell_bit(y: int, x: int) -> int:
    return 1 << (y * BOARD_W + x)


def bit_yx(bit_index: int) -> tuple[int, int]:
    return divmod(bit_index, BOARD_W)


def shift_n(b: int) -> int:
    return b >> BOARD_W


def shift_s(b: int) -> int:
    return (b << BOARD_W) & BOARD_MASK


def shift_w(b: int) -> int:
    return (b & NOT_COL_W) >> 1


def shift_e(b: int) -> int:
    return (b & NOT_COL_E) << 1


def shift_nw(b: int) -> int:
    return shift_n(shift_w(b))


def shift_ne(b: int) -> int:
    return shift_n(shift_e(b))


def shift_sw(b: int) -> int:
    return shift_s(shift_w(b))


def shift_se(b: int) -> int:
    return shift_s(shift_e(b))


def ortho_neighbours(b: int) -> int:
    """Cells orthogonally adjacent to any set bit in b."""
    return shift_n(b) | shift_s(b) | shift_w(b) | shift_e(b)


def diag_neighbours(b: int) -> int:
    """Cells diagonally adjacent to any set bit in b."""
    return shift_nw(b) | shift_ne(b) | shift_sw(b) | shift_se(b)


def corner_attach_mask(own: int, occupied: int) -> int:
    """Empty cells diagonally adjacent to own AND not orthogonally adjacent to own."""
    empty = BOARD_MASK & ~occupied
    return empty & diag_neighbours(own) & ~ortho_neighbours(own)


def side_touch_mask(own: int) -> int:
    """Cells orthogonally adjacent to own (placing on these is illegal)."""
    return ortho_neighbours(own)


def popcount(b: int) -> int:
    # Python 3.10+ has int.bit_count(); fall back to bin() for portability.
    try:
        return b.bit_count()
    except AttributeError:  # pragma: no cover
        return bin(b).count('1')


def iter_bits(b: int):
    """Yield each set-bit index of b (from low to high)."""
    while b:
        lsb = b & -b
        yield lsb.bit_length() - 1
        b ^= lsb


def board_str(own: int, opp: int) -> str:
    """ASCII rendering for debugging."""
    rows = []
    for y in range(BOARD_H):
        row = []
        for x in range(BOARD_W):
            bit = 1 << (y * BOARD_W + x)
            if own & bit:
                row.append('o')
            elif opp & bit:
                row.append('x')
            else:
                row.append('.')
        rows.append(''.join(row))
    return '\n'.join(rows)
