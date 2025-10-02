# utils.py
# ==============================================================================
# 共通して使用される関数群
# ==============================================================================

import json
import os
import math
import unicodedata
import logging
from config import *

def setup_logging():
    """ログ機能の初期設定を行う"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    log_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file_path = os.path.join(LOG_DIR, f'analysis_log_{log_timestamp}.log')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file_path, filemode='w', encoding='utf-8')

def load_stats():
    """統計ファイル(STATS_FILE)を読み込む"""
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # データの整形や後方互換性の処理
        rank_stats = data.get('rank_stats', {})
        rank_apps = {int(k): v for k, v in rank_stats.get('appearances', {}).items()}
        rank_wins = {int(k): v for k, v in rank_stats.get('wins', {}).items()}

        horse_name_stats = data.get('horse_name_stats', {})
        horse_name_apps = horse_name_stats.get('appearances', {})
        horse_name_wins = horse_name_stats.get('wins', {})
        
        odds_pattern_stats = data.get('odds_pattern_stats', {})
        
        return (rank_apps, rank_wins, horse_name_apps, horse_name_wins, odds_pattern_stats)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.warning(f"{STATS_FILE}が見つからないか不正な形式です。新しい統計情報を作成します。")
        # (人気順位1-6, 馬番1-6), 馬名, オッズパターン
        return ({i: 0 for i in range(1, 7)}, {i: 0 for i in range(1, 7)}, {}, {}, {})

def save_stats(stats_data):
    """統計ファイル(STATS_FILE)に保存する"""
    (rank_apps, rank_wins, horse_name_apps, horse_name_wins, odds_pattern_stats) = stats_data
    data = {
        'rank_stats': {'appearances': rank_apps, 'wins': rank_wins},
        'horse_name_stats': {'appearances': horse_name_apps, 'wins': horse_name_wins},
        'odds_pattern_stats': odds_pattern_stats,
    }
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"統計情報を {STATS_FILE} に保存しました。")
    except Exception as e:
        logging.error(f"統計情報の保存に失敗しました: {e}")
        print(f"[エラー] 統計情報の保存に失敗しました: {e}")


def wilson_score_lower_bound(wins, appearances, confidence=0.95):
    """勝率のウィルソン信頼区間の下限を計算する"""
    if appearances == 0:
        return 0
    z = 1.96  # 信頼度95%
    p_hat = wins / appearances
    numerator = p_hat + z**2 / (2 * appearances) - z * math.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * appearances)) / appearances)
    denominator = 1 + z**2 / appearances
    return numerator / denominator

# --- 表示用ヘルパー関数 ---
def get_visual_width(s):
    """文字列の視覚的な幅を計算する（半角1, 全角2）"""
    width = 0
    for char in s:
        if unicodedata.east_asian_width(char) in 'FWA':
            width += 2
        else:
            width += 1
    return width

def pad_string(s, width, align='<'):
    """全角文字を考慮して文字列をパディングし、固定幅の文字列を返す"""
    padding_len = width - get_visual_width(s)
    if padding_len < 0:
        # 文字が幅を超える場合は、切り詰めるなどの処理も可能
        return s
    if align == '>':
        return ' ' * padding_len + s
    return s + ' ' * padding_len