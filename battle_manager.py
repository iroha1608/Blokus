import os
import shutil
import subprocess
import sys

# ================= ユーザー設定エリア =================
# プレイヤー名は `pip install` で登録された console_scripts 名を指定する
#   - mcts_sec_client            -> "ss_mcts"
#   - enemy_player/blokus_solver -> "sticky"
AI_1_NAME = "ss_mcts"
AI_2_NAME = "sticky"
TOTAL_MATCHES = 10  # 対戦回数 (1〜49, start_blocksduo の制約)
MODE = ""           # "view" を指定すると viewer 連携。通常は ""。
# =====================================================


def main():
    # AI コマンドが PATH 上にあるか事前に確認
    for name in (AI_1_NAME, AI_2_NAME, "start_blocksduo"):
        if shutil.which(name) is None:
            print(f"[!] '{name}' コマンドが見つかりません。venv を有効化して以下を実行してください:")
            print("    pip install ./game ./mcts_sec_client ./enemy_player/blokus_solver/client")
            sys.exit(1)

    os.makedirs("logs", exist_ok=True)
    os.makedirs("log", exist_ok=True)

    log_filename = f"{AI_1_NAME}_{AI_2_NAME}_{TOTAL_MATCHES}.log"
    log_filepath = os.path.join("logs", log_filename)

    cmd = ["start_blocksduo", AI_1_NAME, AI_2_NAME, str(TOTAL_MATCHES)]
    if MODE:
        cmd.append(MODE)

    print(f"[+] {AI_1_NAME} VS {AI_2_NAME} を {TOTAL_MATCHES} 回対戦させます...")
    print(f"    コマンド: {' '.join(cmd)}")

    with open(log_filepath, "w", encoding="utf-8") as log_file:
        log_file.write(f"=== {AI_1_NAME} vs {AI_2_NAME} : {TOTAL_MATCHES} matches ===\n\n")
        log_file.flush()
        # start_blocksduo は内部で複数試合を回し、各試合の JSON ログを `log/` に出力する。
        # ポート 8088 を共有しているため並列実行はできない (順次実行)。
        result = subprocess.run(cmd, stdout=log_file, stderr=subprocess.STDOUT, text=True)

    if result.returncode == 0:
        print(f"[+] 全試合終了。標準出力ログ: {log_filepath}")
        print(f"    JSON 形式の各試合ログ: log/ 以下を確認してください。")
        print(f"    集計コマンド例: python3 show_logs.py {AI_1_NAME}_{AI_2_NAME}")
    else:
        print(f"[!] start_blocksduo が異常終了しました (returncode={result.returncode})。")
        print(f"    詳細は {log_filepath} を参照してください。")
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
