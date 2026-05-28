# Blokus Duo ラウンドロビン トーナメント結果 (run 3, 10秒/手)

## 1. 実行概要

- 参加 AI (4 つ)
  - `mcts_ai` (`mcts_client`)
  - `sticky` (`enemy_player/blokus_solver`)
  - `AlphaBetansato`
  - `tmaeda` (`client_tmaeda`)
- 方式: 総当たり 6 ペア × 各ペア 10 試合 × 4 ラウンド = 1 ペアあたり 40 ラウンド (合計 **240 ラウンド**)
- 1 手あたり制限時間: **10.0 秒** (ハッカソン規定)
- 実行スクリプト: `tournament_runner.py`
- 集計元: `log/*.json` (240 ファイル) + `show_logs.py` 出力 (各ペアの `*_summary.md`)

## 2. 総合ランキング

| 順位 | AI | 勝 | 負 | 引 | 試合数 | 勝率 | 合計スコア |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| 🥇 1 | **mcts_ai** | 103 | 15 | 2 | 120 | **85.8%** | 8303 |
| 🥈 2 | **tmaeda** | 60 | 56 | 4 | 120 | **50.0%** | 7247 |
| 🥉 3 | **sticky** | 43 | 73 | 4 | 120 | **35.8%** | 6806 |
| 4 | **AlphaBetansato** | 27 | 89 | 4 | 120 | **22.5%** | 6775 |

**結論: 一番強かったのは `mcts_ai` (mcts_client)。** 120 ラウンド中 103 勝 (85.8%) で他を大きく引き離した。tmaeda は 2 位だが mcts_ai 相手以外には総じて優勢。

## 3. 対戦表 (head-to-head)

セルは「行プレイヤーから見た 勝-負-引分 / 勝率」。

| | mcts_ai | sticky | AlphaBetansato | tmaeda |
|---|:---:|:---:|:---:|:---:|
| **mcts_ai** | — | 31-8-1 (77.5%) | 39-1-0 (97.5%) | 33-6-1 (82.5%) |
| **sticky** | 8-31-1 (20.0%) | — | 20-18-2 (50.0%) | 15-24-1 (37.5%) |
| **AlphaBetansato** | 1-39-0 (2.5%) | 18-20-2 (45.0%) | — | 8-30-2 (20.0%) |
| **tmaeda** | 6-33-1 (15.0%) | 24-15-1 (60.0%) | 30-8-2 (75.0%) | — |

### 観察ポイント

- `mcts_ai` は **全 3 相手に対し 77% 以上の勝率**。最も接戦だったのは `sticky` 戦 (77.5%) と `tmaeda` 戦 (82.5%)。
- `tmaeda` は **mcts_ai 以外には強い** (sticky に 60%, AlphaBetansato に 75%)。
- `sticky` vs `AlphaBetansato` は **20-18 引き分け 2 のほぼ五分**。3 位 4 位は僅差。
- `AlphaBetansato` は `mcts_ai` に対してほぼ完敗 (2.5%)、`tmaeda` 相手にも劣勢 (20%)。`sticky` 相手のみ拮抗。

## 4. ペア別集計

| ペア | ラウンド | 勝者 (勝) | 敗者 (勝) | 引分 | 勝者勝率 | 勝者スコア | 敗者スコア |
|---|:---:|---|---|:---:|:---:|:---:|:---:|
| mcts_ai vs sticky | 40 | mcts_ai (31) | sticky (8) | 1 | 77.5% | 2678 | 2075 |
| mcts_ai vs AlphaBetansato | 40 | mcts_ai (39) | AlphaBetansato (1) | 0 | 97.5% | 2855 | 2000 |
| mcts_ai vs tmaeda | 40 | mcts_ai (33) | tmaeda (6) | 1 | 82.5% | 2770 | 2311 |
| sticky vs AlphaBetansato | 40 | sticky (20) | AlphaBetansato (18) | 2 | 50.0% | 2481 | 2346 |
| sticky vs tmaeda | 40 | tmaeda (24) | sticky (15) | 1 | 60.0% | 2407 | 2250 |
| AlphaBetansato vs tmaeda | 40 | tmaeda (30) | AlphaBetansato (8) | 2 | 75.0% | 2529 | 2429 |

## 5. 試合終了理由の内訳

全 240 試合のうち通常終了 (`normal`) が **235 件 (97.9%)**、反則負け (`resign`) が **5 件 (2.1%)**。

| 終了理由 | 件数 | 割合 |
|---|:---:|:---:|
| `normal` (置けなくなって通常終了) | 235 | 97.9% |
| `resign` (反則負け) | 5 | 2.1% |

### ペア別の終了理由

| ペア | normal | resign |
|---|:---:|:---:|
| mcts_ai vs sticky | 40 | 0 |
| mcts_ai vs AlphaBetansato | 37 | 3 |
| mcts_ai vs tmaeda | 40 | 0 |
| sticky vs AlphaBetansato | 40 | 0 |
| sticky vs tmaeda | 40 | 0 |
| AlphaBetansato vs tmaeda | 38 | 2 |

反則負けはすべて `AlphaBetansato` が絡むペア。10秒制限でも稀に時間内に合法手を返せず反則になっている模様。

## 6. スコアと AI の総合プロファイル

| AI | 1 ラウンドあたりの平均スコア | 備考 |
|---|:---:|---|
| mcts_ai | 8303 / 120 ≈ **69.2** | 突出した勝率・スコア両方で 1 位。 |
| tmaeda | 7247 / 120 ≈ **60.4** | mcts_ai に次ぐスコア。中位以下相手には安定。 |
| sticky | 6806 / 120 ≈ **56.7** | スコアは中庸。AlphaBetansato 戦で僅差勝ち。 |
| AlphaBetansato | 6775 / 120 ≈ **56.5** | スコア生成は sticky と互角だが勝負弱い。 |

## 7. 最終結論

| ランク | AI | 強さの根拠 |
|:---:|---|---|
| 1 位 | **mcts_ai** | 全 3 相手に 77% 以上の勝率。総合勝率 85.8%、合計スコア 8303 ともに最高。 |
| 2 位 | tmaeda | mcts_ai 以外には強い (vs sticky 60%, vs AlphaBetansato 75%)。 |
| 3 位 | sticky | AlphaBetansato 相手に拮抗するが、mcts_ai / tmaeda には劣勢。 |
| 4 位 | AlphaBetansato | mcts_ai 戦でほぼ完敗。スコアは sticky と互角だが勝負弱い。 |

**4 AI の中で一番強いのは `mcts_ai` (mcts_client)。**

## 8. 添付: ペアごとの詳細サマリー

`show_logs.py` が生成した各ペアの詳細 (試合一覧・最終盤面付き):

- [mcts_ai vs sticky](mcts_ai_sticky_summary.md)
- [mcts_ai vs AlphaBetansato](mcts_ai_AlphaBetansato_summary.md)
- [mcts_ai vs tmaeda](mcts_ai_tmaeda_summary.md)
- [sticky vs AlphaBetansato](sticky_AlphaBetansato_summary.md)
- [sticky vs tmaeda](sticky_tmaeda_summary.md)
- [AlphaBetansato vs tmaeda](AlphaBetansato_tmaeda_summary.md)
