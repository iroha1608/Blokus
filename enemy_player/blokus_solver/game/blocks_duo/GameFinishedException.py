from Blokus.enemy_player.blokus_solver.game.blocks_duo.FinishedReason import FinishedReason
from Blokus.enemy_player.blokus_solver.game.blocks_duo.Player import Player


class GameFinishedException(Exception):
    def __init__(self, winner: Player, reason: FinishedReason):
        super().__init__()
        self.winner = winner
        self.reason = reason
