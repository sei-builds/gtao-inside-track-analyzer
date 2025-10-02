# config.py
# ==============================================================================
# プログラム全体の設定ファイル
# ==============================================================================

# --- 基準解像度 ---
# この解像度を元に、すべての座標の相対的な割合を計算します
BASE_WIDTH = 2559
BASE_HEIGHT = 1439

# --- パス設定 ---
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
STATS_FILE = 'win_rate_stats.json'
RACE_HISTORY_FILE = 'race_history.jsonl' # シミュレーター用のレース履歴
UNRESOLVED_RACE_FILE = 'unresolved_race.json' # 解析途中レースの一時ファイル
IMAGE_TEMPLATES_DIR = 'templates'
HORSE_NAME_TEMPLATES_DIR = 'horse_name_templates'
WINNING_HORSE_TEMPLATES_DIR = 'winning_horse_templates'
LOG_DIR = 'logs'
RENAME_LOG_FILE = 'rename_log.txt'

# --- 画像認識設定 ---
HORSE_NAME_MATCH_THRESHOLD = 0.95
WINNING_HORSE_MATCH_THRESHOLD = 0.80

# --- OCR領域 (すべて割合で指定) ---
CHIP_COUNT_AREA_PRIMARY_RATIO = {'left': 2300 / BASE_WIDTH, 'top': 20 / BASE_HEIGHT, 'width': 250 / BASE_WIDTH, 'height': 70 / BASE_HEIGHT}
CHIP_COUNT_AREA_FALLBACK_RATIO = {'left': 2300 / BASE_WIDTH, 'top': 135 / BASE_HEIGHT, 'width': 250 / BASE_WIDTH, 'height': 70 / BASE_HEIGHT}

ODDS_AREAS_RATIOS = [
    {'left': 230 / BASE_WIDTH, 'top': 460 / BASE_HEIGHT, 'width': 200 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 620 / BASE_HEIGHT, 'width': 200 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 780 / BASE_HEIGHT, 'width': 200 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 940 / BASE_HEIGHT, 'width': 200 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 1100 / BASE_HEIGHT, 'width': 200 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 1260 / BASE_HEIGHT, 'width': 200 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
]

HORSE_NAME_AREAS_RATIOS = [
    {'left': 230 / BASE_WIDTH, 'top': 380 / BASE_HEIGHT, 'width': 485 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 542 / BASE_HEIGHT, 'width': 485 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 704 / BASE_HEIGHT, 'width': 485 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 866 / BASE_HEIGHT, 'width': 485 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 1028 / BASE_HEIGHT, 'width': 485 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
    {'left': 230 / BASE_WIDTH, 'top': 1190 / BASE_HEIGHT, 'width': 485 / BASE_WIDTH, 'height': 60 / BASE_HEIGHT},
]

# ひし形領域の座標 (これも相対化)
WINNING_HORSE_DIAMOND_POINTS_RATIO = [
    (1274 / BASE_WIDTH, 641 / BASE_HEIGHT), (1333 / BASE_WIDTH, 701 / BASE_HEIGHT),
    (1274 / BASE_WIDTH, 761 / BASE_HEIGHT), (1213 / BASE_WIDTH, 701 / BASE_HEIGHT)
]


# --- ベット戦略設定 ---
HORSE_SELECTION_WEIGHTS = {
    'WEIGHTS': {
        'HIGH_CONFIDENCE': {'A': 0.8,  'B': 0.2,  'THRESHOLD': 100},
        'MID_CONFIDENCE':  {'A': 0.65, 'B': 0.35, 'THRESHOLD': 20},
        'LOW_CONFIDENCE':  {'A': 0.5,  'B': 0.5},
    }
}

# --- レポート表示設定 ---
HORSE_NAME_DISPLAY_LIMIT = 10
ODDS_PATTERN_DISPLAY_LIMIT = 5
HORSE_ODDS_DISPLAY_LIMIT = 20