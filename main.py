# main.py
# ==============================================================================
# メイン実行ファイル (コマンドラインインターフェース)
# ==============================================================================

import argparse
import collector
import analyzer
import simulator

def main():
    parser = argparse.ArgumentParser(
        description="GTAオンライン インサイドトラック レースアナライザー＆戦略シミュレーター",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', required=True, help='実行するコマンド')

    # --- データ収集コマンド ---
    parser_collect = subparsers.add_parser('collect', help='スクリーンショットからレースデータを収集する')
    parser_collect.add_argument('--pre', type=str, metavar='IMAGE_PATH', help='レース前のベット画面のスクリーンショット画像パス')
    parser_collect.add_argument('--post', type=str, metavar='IMAGE_PATH', help='レース後の結果画面のスクリーンショット画像パス')
    parser_collect.add_argument('--bet', type=int, metavar='N', help='(結果画面と同時に指定) ベットした馬の番号 (1-6)')

    # --- データ分析コマンド ---
    parser_analyze = subparsers.add_parser('analyze', help='収集したデータを分析しレポートを表示する')
    parser_analyze.add_argument('--report', type=str, default='all', choices=['all', 'rank', 'horse'], help='表示するレポートの種類')

    # --- シミュレーションコマンド ---
    parser_simulate = subparsers.add_parser('simulate', help='ベット戦略のシミュレーションを実行する')
    parser_simulate.add_argument('--strategy', type=str, default='favorite', choices=['favorite', 'positive_ev'], help='使用する戦略')

    args = parser.parse_args()

    if args.command == 'collect':
        if args.pre:
            collector.extract_pre_race_data(args.pre)
        elif args.post:
            if args.bet is None:
                parser.error("--post には --bet (ベットした馬番号) の指定が必須です。")
            collector.process_post_race_data(args.post, args.bet)
        else:
            print("[エラー] --pre または --post のいずれかを指定してください。")

    elif args.command == 'analyze':
        analyzer.show_report(args.report)

    elif args.command == 'simulate':
        if args.strategy == 'favorite':
            strategy_func = simulator.strategy_always_bet_on_favorite
        elif args.strategy == 'positive_ev':
            strategy_func = simulator.strategy_positive_ev
        else:
            print(f"[エラー] 不明な戦略です: {args.strategy}")
            return
        simulator.run_simulation(strategy_func)

if __name__ == '__main__':
    main()