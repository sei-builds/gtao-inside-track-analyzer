# analyzer.py
# ==============================================================================
# 蓄積されたレースデータを分析し、レポートを表示する
# ==============================================================================

import utils
from config import *

def display_rank_stats(rank_apps, rank_wins):
    """人気順位別の勝率を表示する"""
    print("\n--- 人気順位別 勝率 ---")
    for rank in range(1, 7):
        appearances = rank_apps.get(rank, 0)
        wins = rank_wins.get(rank, 0)
        win_rate = (wins / appearances) * 100 if appearances > 0 else 0
        print(f"  {rank}番人気: {wins:>4}勝 / {appearances:>5}戦   ({win_rate:5.1f}%)")
    print("------------------------")

def display_horse_name_stats(name_apps, name_wins):
    """馬名別の勝率を上位から表示する"""
    print(f"\n--- 馬名別 勝率 (勝率上位{HORSE_NAME_DISPLAY_LIMIT}件) ---")
    if not name_apps:
        print("  - データがありません。")
        return

    valid_apps = {k: v for k, v in name_apps.items() if k != "N/A" and v > 0}
    sorted_names = sorted(
        valid_apps.items(),
        key=lambda item: (
            name_wins.get(item[0], 0) / item[1],
            item[1]
        ),
        reverse=True
    )
    
    header = f"  {utils.pad_string('馬名', 20)} | 勝率     | 成績"
    print(header)
    print("  " + "-" * (utils.get_visual_width(header) - 2))
    
    for i, (name, num_apps) in enumerate(sorted_names):
        if i >= HORSE_NAME_DISPLAY_LIMIT:
            break
        num_wins = name_wins.get(name, 0)
        win_rate = (num_wins / num_apps) * 100
        record_str = f"({num_wins}勝/{num_apps}戦)"
        print(f"  {utils.pad_string(name, 20)} | {win_rate:6.2f}% | {utils.pad_string(record_str, 12)}")
    print("-----------------------------------")


def show_report(report_type='all'):
    """指定されたタイプのレポートを表示する"""
    stats = utils.load_stats()
    if not stats[0]: # rank_appsが空ならデータなし
        print("統計データがまだありません。")
        return
        
    rank_apps, rank_wins, name_apps, name_wins, _ = stats

    print("="*40)
    print(" レースデータ分析レポート")
    print("="*40)

    if report_type in ['all', 'rank']:
        display_rank_stats(rank_apps, rank_wins)
    
    if report_type in ['all', 'horse']:
        display_horse_name_stats(name_apps, name_wins)
        
    print("\nレポート生成完了。")