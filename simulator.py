# simulator.py
# ==============================================================================
# 保存されたレース履歴を元に、ベット戦略をシミュレーションする
# ==============================================================================

import json
from tqdm import tqdm
import utils
from config import *

def load_race_history():
    """レース履歴ファイルを読み込む"""
    if not os.path.exists(RACE_HISTORY_FILE):
        return []
    with open(RACE_HISTORY_FILE, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f]

def strategy_always_bet_on_favorite(race_data, stats_snapshot):
    """常に1番人気の馬にベットする戦略"""
    try:
        favorite_idx = race_data['ranks'].index(1)
        return favorite_idx + 1 # 馬番を返す (1-6)
    except ValueError:
        return None # 1番人気がいない場合はベットしない

def strategy_positive_ev(race_data, stats_snapshot):
    """期待値がプラスの馬の中で、最も期待値が高い馬にベットする戦略"""
    rank_apps, rank_wins, name_apps, name_wins, _ = stats_snapshot
    
    best_horse = {'ev': 0, 'b_num': None}

    for i in range(6):
        # 簡易的な勝率予測 (より高度な予測も可能)
        rank = race_data['ranks'][i]
        name = race_data['names'][i]
        
        rank_win_rate = rank_wins.get(rank, 0) / rank_apps.get(rank, 1)
        name_win_rate = name_wins.get(name, 0) / name_apps.get(name, 1)
        
        # ここでは単純に人気順の勝率を予測勝率とする (改善の余地あり)
        predicted_win_rate = rank_win_rate
        
        odds = race_data['odds'][i]
        if odds >= 999.0: continue
            
        expected_value = (predicted_win_rate * odds) - 1.0
        
        if expected_value > best_horse['ev']:
            best_horse['ev'] = expected_value
            best_horse['b_num'] = i + 1

    return best_horse['b_num']


def run_simulation(strategy_func, bet_amount=100):
    """指定された戦略でシミュレーションを実行する"""
    race_history = load_race_history()
    if not race_history:
        print("シミュレーション対象のレース履歴がありません。")
        return

    # 統計のスナップショットをレースごとに再現するための準備
    rank_apps, rank_wins = {i: 0 for i in range(1, 7)}, {i: 0 for i in range(1, 7)}
    name_apps, name_wins = {}, {}
    odds_patterns = {}
    
    total_bet = 0
    total_payout = 0
    wins = 0
    bets = 0

    print(f"シミュレーション開始: 戦略「{strategy_func.__name__}」 / 全{len(race_history)}レース")
    
    for race in tqdm(race_history):
        # レース前の統計スナップショットを作成
        stats_snapshot = (rank_apps.copy(), rank_wins.copy(), name_apps.copy(), name_wins.copy(), odds_patterns.copy())
        
        # 戦略に基づいてベットする馬を決定
        betted_horse = strategy_func(race, stats_snapshot)
        
        if betted_horse is not None:
            bets += 1
            total_bet += bet_amount
            if race['winner'] == betted_horse:
                wins += 1
                payout = bet_amount * race['odds'][betted_horse - 1]
                total_payout += payout

        # このレースの結果を統計に反映
        for i in range(6):
            if race['odds'][i] < 999.0:
                rank = race['ranks'][i]
                name = race['names'][i]
                rank_apps[rank] = rank_apps.get(rank, 0) + 1
                if name != "N/A":
                    name_apps[name] = name_apps.get(name, 0) + 1
        
        winner_idx = race['winner'] - 1
        rank_wins[race['ranks'][winner_idx]] = rank_wins.get(race['ranks'][winner_idx], 0) + 1
        if race['names'][winner_idx] != "N/A":
            name_wins[race['names'][winner_idx]] = name_wins.get(race['names'][winner_idx], 0) + 1

    # 結果表示
    profit = total_payout - total_bet
    roi = (profit / total_bet) * 100 if total_bet > 0 else 0
    win_rate = (wins / bets) * 100 if bets > 0 else 0
    
    print("\n--- シミュレーション結果 ---")
    print(f"  総ベットレース数: {bets} / {len(race_history)}")
    print(f"  勝敗: {wins}勝 / {bets}戦")
    print(f"  勝率: {win_rate:.2f}%")
    print(f"  総ベット額: {total_bet:,.0f}")
    print(f"  総払戻額: {total_payout:,.0f}")
    print(f"  純収支: {profit:,.0f}")
    print(f"  ROI (投資収益率): {roi:.2f}%")
    print("--------------------------")