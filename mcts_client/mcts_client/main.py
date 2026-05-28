import asyncio
import sys

from .PlayerClient import PlayerClient


def main() -> None:
    server_url = sys.argv[1]
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    print(f'mcts_ai client start : {server_url}', flush=True)
    client = loop.run_until_complete(PlayerClient.create(server_url, loop))
    try:
        loop.run_until_complete(client.play())
    except (KeyboardInterrupt, SystemExit):
        loop.run_until_complete(client.close())
        loop.close()


if __name__ == '__main__':
    main()
