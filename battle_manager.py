import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

# ================= ユーザー設定エリア =================
AI_1_NAME = "my_player"     # 自分のAIのファイル名（拡張子なし）
AI_2_NAME = "enemy_player"  # 対戦相手のAIのファイル名（拡張子なし）
TOTAL_MATCHES = 10          # 対戦回数
# =====================================================

def run_single_match(match_number):
    """1回分の対戦を実行し、それぞれのログを出力"""
    
    # ログファイルの保存先を設定 (例: logs/my_player_enemy_player_1.log)
    log_filename = f"{AI_1_NAME}_{AI_2_NAME}_{match_number}.log"
    log_filepath = os.path.join("logs", log_filename)
    
    with open(log_filepath, "w", encoding="utf-8") as log_file:
        # with 自動で閉じる write utf-8 文字コード　as 変数名
        log_file.write(f"=== Match {match_number} Start ===\n\n")
        
        # 1. AI_1 (my_player) の実行
        log_file.write(f"[{AI_1_NAME} Output]\n")
        # python コマンドでAIのスクリプトを裏で実行
        result_1 = subprocess.run(["python", f"{AI_1_NAME}.py"], capture_output=True, text=True)
        log_file.write(result_1.stdout) # AIが画面に出力した内容をログに書き込む
        if result_1.stderr:
            log_file.write(f"Error: {result_1.stderr}")
            
        log_file.write("\n" + "-"*30 + "\n\n")
        
        # 2. AI_2 (enemy_player) の実行
        log_file.write(f"[{AI_2_NAME} Output]\n")
        result_2 = subprocess.run(["python", f"{AI_2_NAME}.py"], capture_output=True, text=True)
        log_file.write(result_2.stdout)
        if result_2.stderr:
            log_file.write(f"Error: {result_2.stderr}")

    print(f"[-] マッチ {match_number} の対戦完了。ログを出力しました: {log_filename}")

def main():
    # ログを保存するフォルダがなければ自動で作る
    if not os.path.exists("logs"):
        os.makedirs("logs")
        
    print(f"[+] {AI_1_NAME} VS {AI_2_NAME} の並列対戦（計 {TOTAL_MATCHES} 回）を開始します...")

    # ThreadPoolExecutor を使って並列（同時）処理
    with ThreadPoolExecutor() as executor:
        # 1回目から10回目までの対戦を同時に実行S
        executor.map(run_single_match, range(1, TOTAL_MATCHES + 1))

    print("[+] すべての対戦が終了しました。'logs' フォルダを確認してください。")

if __name__ == "__main__":
    main()