import glob
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= ユーザー設定エリア =================
# プレイヤー名は `pip install` で登録された console_scripts 名を指定する
#   - mcts_client                -> "mcts_ai"  (ユニークなパッケージ名で衝突回避)
#   - enemy_player/blokus_solver -> "sticky"
AI_1_NAME = "mcts_ai"
AI_2_NAME = "sticky"
TOTAL_MATCHES = 10   # 並列で走らせる試合数
NUM_ROUNDS = 4       # 1試合あたりのラウンド数 (GameMaster.switch_players() で先後を入れ替えながら回す)
MAX_PARALLEL = 5     # 同時実行数 (各ワーカが別ポートを掴むため衝突しない範囲で設定)
BASE_PORT = 9500     # ワーカ毎に BASE_PORT + match_number を割り当てる

# 各エンジンの 1 手あたり制限時間 (秒)。KOYON / BITFIST / MCTS / HYBRID / UNIFIED / AEGIS のクライアントが参照する。
TIME_BUDGET = "8.0"
# =====================================================


# サブプロセス内で WebsocketServer.PORT を上書きしてから start_blocksduo を起動する。
# こうすることでマッチ毎に別ポートを掴めるようになり、ThreadPoolExecutor で並列実行できる。
# urllib3 v2 の NotOpenSSLWarning (macOS の LibreSSL 由来) もここで抑止する。
_RUNNER_TEMPLATE = (
    "import sys, warnings; "
    "warnings.filterwarnings('ignore'); "
    "import blocks_duo.WebsocketServer as ws; "
    "ws.PORT = {port}; "
    "from blocks_duo.GameMaster import main; "
    "sys.argv = ['start_blocksduo', {ai1!r}, {ai2!r}, {rounds!r}]; "
    "main()"
)


def _make_env() -> dict:
    """各エンジンが参照する time budget を環境変数に詰める"""
    env = os.environ.copy()
    for eng in ("KOYON", "BITFIST", "MCTS", "HYBRID", "UNIFIED", "AEGIS"):
        env[f"{eng}_BUDGET"] = TIME_BUDGET
    return env


def run_single_match(match_number: int) -> tuple[int, int]:
    """1試合 (NUM_ROUNDS ラウンド) を別ポート・別作業ディレクトリで実行する"""
    port = BASE_PORT + match_number
    work_dir = os.path.abspath(os.path.join("tmp", "parallel", f"match_{match_number}"))
    os.makedirs(work_dir, exist_ok=True)

    log_filename = f"{AI_1_NAME}_{AI_2_NAME}_{match_number}.log"
    log_filepath = os.path.abspath(os.path.join("logs", log_filename))

    # GameMaster.switch_players() がラウンド毎に先後を入れ替えるので、
    # この並列版は外側で偶奇制御せず、毎試合 同じ引数順で起動する。
    runner_code = _RUNNER_TEMPLATE.format(
        port=port, ai1=AI_1_NAME, ai2=AI_2_NAME, rounds=str(NUM_ROUNDS),
    )

    with open(log_filepath, "w", encoding="utf-8") as log_file:
        log_file.write(
            f"=== Match {match_number} (port={port}, "
            f"rounds={NUM_ROUNDS}, budget={TIME_BUDGET}s) ===\n\n"
        )
        log_file.flush()
        result = subprocess.run(
            [sys.executable, "-c", runner_code],
            cwd=work_dir,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
            env=_make_env(),
        )

    # ワーカ毎の log/ 配下にある JSON ログを、トップレベルの log/ に集約する。
    top_log_dir = os.path.abspath("log")
    os.makedirs(top_log_dir, exist_ok=True)
    for src in glob.glob(os.path.join(work_dir, "log", "*.json")):
        base = os.path.basename(src)
        dst = os.path.join(top_log_dir, base)
        # 並列で実行するとタイムスタンプが衝突しうるので、衝突したらマッチ番号を付与
        if os.path.exists(dst):
            name, ext = os.path.splitext(base)
            dst = os.path.join(top_log_dir, f"{name}_m{match_number}{ext}")
        shutil.move(src, dst)

    # 収集後にワーカ用の作業ディレクトリを削除（空のフォルダだけ残るのを防ぐ）
    shutil.rmtree(work_dir, ignore_errors=True)

    return match_number, result.returncode


def main():
    for name in (AI_1_NAME, AI_2_NAME, "start_blocksduo"):
        if shutil.which(name) is None:
            print(f"[!] '{name}' コマンドが見つかりません。venv を有効化して以下を実行してください:")
            print("    pip install ./game ./mcts_client ./enemy_player/blokus_solver/client")
            sys.exit(1)

    os.makedirs("logs", exist_ok=True)
    os.makedirs("log", exist_ok=True)
    os.makedirs(os.path.join("tmp", "parallel"), exist_ok=True)

    total_rounds = TOTAL_MATCHES * NUM_ROUNDS
    print(
        f"[+] {AI_1_NAME} VS {AI_2_NAME} の並列対戦"
        f" (試合 {TOTAL_MATCHES} × {NUM_ROUNDS} ラウンド = 計 {total_rounds} ラウンド,"
        f" 同時 {MAX_PARALLEL}, budget={TIME_BUDGET}s)"
        f" を開始します..."
    )

    failures = []
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as executor:
        futures = {
            executor.submit(run_single_match, i): i
            for i in range(1, TOTAL_MATCHES + 1)
        }
        for fut in as_completed(futures):
            n, rc = fut.result()
            if rc == 0:
                print(f"[-] マッチ {n} 完了 (logs/{AI_1_NAME}_{AI_2_NAME}_{n}.log)")
            else:
                print(f"[!] マッチ {n} 異常終了 (rc={rc})")
                failures.append(n)

    if failures:
        print(f"[!] 失敗した試合: {failures}")
        sys.exit(1)

    # 空になった tmp/parallel/ も削除
    shutil.rmtree(os.path.join("tmp", "parallel"), ignore_errors=True)
    try:
        os.rmdir("tmp")  # 他に何も無ければ削除
    except OSError:
        pass

    print("[+] すべての対戦が終了しました。")
    print(f"    JSON 形式の各ラウンドログ: log/ 以下に集約済み ({total_rounds} 件想定)")
    print(f"    集計コマンド例: python3 show_logs.py {AI_1_NAME}_{AI_2_NAME}")


if __name__ == "__main__":
    main()
