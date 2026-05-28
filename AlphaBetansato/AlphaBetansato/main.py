"""
    提供されたsocket, loopで通信とループ周りの処理。
    player.createで初期化
    -> play()でsocketから盤面を受け取る
        -> create_action()の実行
            -> make_matrix(), get_ok_cases()で有効手を取得
            -> メインロジックのget_best_hand()で選択
        -> socketに手を返す
    上記を勝敗がつくまでループ
"""
import sys
import asyncio

from AlphaBetansato.players.PlayerClient import PlayerClient
from AlphaBetansato.players.BasePlayer import BasePlayer
from AlphaBetansato.players.AlphaBetaPlayer import AlphaBetaPlayer
# from AlphaBetansato.players.RandomPlayer import RandomPlayer


ERROR = "[\33[31mERROR\33[0m]:"


def main():
    try:
        server_url = sys.argv[1]
        loop = asyncio.new_event_loop()
        print(f'Client start : {server_url}')
    except (IndexError, UnboundLocalError) as e:
        print(f"{ERROR} {e}" , file=sys.stderr)
        sys.exit(1)

    asyncio.set_event_loop(loop)

    # Playerをランダムとα-β探索から選ぶ。
    # player: BasePlayer = RandomPlayer.create(server_url, loop)
    player: BasePlayer = AlphaBetaPlayer.create(server_url, loop)

    client = loop.run_until_complete(player)

    try:
        # play: socketから盤面を受け取り、手を返す。そのループ処理。
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

