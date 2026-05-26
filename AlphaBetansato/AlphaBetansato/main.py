import sys
import asyncio

from AlphaBetansato.players.PlayerClient import PlayerClient
from AlphaBetansato.players.base_player import BasePlayer
# from AlphaBetansato.players.alpha_beta_players import AlphaBetaPlayer
from AlphaBetansato.players.random_player import RandomPlayer


ERROR = "[\33[31mERROR\33[0m]:"


def main():
    try:
        server_url = sys.argv[1]
        loop = asyncio.new_event_loop()
        print(f'client start : {server_url}')
    except (IndexError, UnboundLocalError) as e:
        print(f"{ERROR} {e}" , file=sys.stderr)
        sys.exit(1)

    asyncio.set_event_loop(loop)

    # Player erabu
    player: BasePlayer = RandomPlayer.create(server_url, loop)
    # player: BasePlayer = AlphaBetaPlayer.create(server_url, loop)
    client = loop.run_until_complete(player)

    try:
        loop.run_until_complete(client.play())

    except KeyboardInterrupt:
        print(
            f"{ERROR} Ctrl + C was entered."
            "The process will be terminated", file=sys.stderr
        )
        loop.run_until_complete(client.close())
        loop.close()
        sys.exit(1)

    except SystemExit:
        print(f"{ERROR} System Exit.", file=sys.stderr)
        loop.run_until_complete(client.close())
        loop.close()
        sys.exit(1)


if __name__ == '__main__':
    main()

