# collector.py

import cv2
import numpy as np
import pytesseract
import json
import os
from datetime import datetime

from config import *
import utils

# Tesseractのパスを設定
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# --- グローバル変数 ---
winning_horse_templates = {}

# --- 画像処理・OCR関連関数 ---

def _calculate_coords(ratio_dict, width, height):
    """割合で定義された辞書から、実際のピクセル座標を計算する"""
    return {
        'left': int(ratio_dict['left'] * width),
        'top': int(ratio_dict['top'] * height),
        'width': int(ratio_dict['width'] * width),
        'height': int(ratio_dict['height'] * height)
    }

def _get_resized_template(template_img, scale_factor):
    """スケールファクターに基づいてテンプレート画像をリサイズするヘルパー関数"""
    if abs(scale_factor - 1.0) > 0.01:
        new_width = int(template_img.shape[1] * scale_factor)
        new_height = int(template_img.shape[0] * scale_factor)
        if new_width > 0 and new_height > 0:
            return cv2.resize(template_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return template_img

def get_odds_text(image_np, area):
    """指定領域からオッズ文字列をOCRで読み取る"""
    x, y, w, h = area['left'], area['top'], area['width'], area['height']
    cropped_image = image_np[y:y+h, x:x+w]
    
    gray_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    _, thresh_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    correction_map = {'S': '5', 'I': '1', 'O': '0', 'G': '6', 'B': '8'}
    config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789/EVENS'
    text = pytesseract.image_to_string(thresh_image, config=config, lang='eng').strip().upper()

    return "".join(correction_map.get(char, char) for char in text)

def parse_odds_to_float(odds_str):
    """OCRで読み取ったオッズ文字列を浮動小数点数に変換する"""
    try:
        if 'EVENS' in odds_str: return 2.0
        if '/' in odds_str:
            parts = odds_str.split('/')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() and int(parts[1]) == 1:
                calculated_odds = (int(parts[0]) / int(parts[1])) + 1.0
                return calculated_odds if 2.0 <= calculated_odds <= 31.0 else 999.0
    except (ValueError, IndexError, ZeroDivisionError):
        return 999.0
    return 999.0

def load_horse_name_templates():
    """馬名テンプレート画像を読み込む"""
    templates = {}
    if not os.path.exists(HORSE_NAME_TEMPLATES_DIR):
        os.makedirs(HORSE_NAME_TEMPLATES_DIR)
    for filename in os.listdir(HORSE_NAME_TEMPLATES_DIR):
        if filename.endswith(".png"):
            filepath = os.path.join(HORSE_NAME_TEMPLATES_DIR, filename)
            horse_name = os.path.splitext(filename)[0].split('_')[0]
            try:
                n = np.fromfile(filepath, np.uint8)
                template_img = cv2.imdecode(n, cv2.IMREAD_GRAYSCALE)
                if template_img is not None:
                    templates[filepath] = {'name': horse_name, 'image': template_img}
            except Exception as e:
                utils.logging.error(f"馬名テンプレートの読み込み失敗: {filepath} ({e})")
    return templates

def identify_horse_name_by_image(image_np, area, templates):
    """画像マッチングで馬名を特定する（動的リサイズ対応）"""
    current_width = image_np.shape[1]
    scale_factor = current_width / BASE_WIDTH

    x, y, w, h = area['left'], area['top'], area['width'], area['height']
    screenshot_roi = image_np[y:y+h, x:x+w]
    gray_screenshot = cv2.cvtColor(screenshot_roi, cv2.COLOR_BGR2GRAY)

    best_match = {'score': -1, 'name': 'N/A'}
    for _, template_data in templates.items():
        original_template = template_data['image']
        
        template_img = _get_resized_template(original_template, scale_factor)

        if template_img.shape[0] > gray_screenshot.shape[0] or template_img.shape[1] > gray_screenshot.shape[1]:
            continue
        res = cv2.matchTemplate(gray_screenshot, template_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(res)
        if max_val > best_match['score']:
            best_match = {'score': max_val, 'name': template_data['name']}
    
    return best_match['name'] if best_match['score'] >= HORSE_NAME_MATCH_THRESHOLD else "N/A"

def load_winning_horse_templates():
    """勝ち馬番号テンプレートを読み込む"""
    global winning_horse_templates
    if not os.path.exists(WINNING_HORSE_TEMPLATES_DIR):
        os.makedirs(WINNING_HORSE_TEMPLATES_DIR)
    templates = {i: [] for i in range(1, 7)}
    for filename in os.listdir(WINNING_HORSE_TEMPLATES_DIR):
        if filename.endswith(".png"):
            try:
                horse_num = int(filename.split('_')[0])
                filepath = os.path.join(WINNING_HORSE_TEMPLATES_DIR, filename)
                image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
                if image is not None:
                    templates[horse_num].append({'image': image, 'path': filepath})
            except (ValueError, IndexError):
                continue
    winning_horse_templates = templates

def get_winning_horse_number(image_np):
    """結果画面の画像から勝ち馬の番号を特定する（動的リサイズ対応）"""
    height, width, _ = image_np.shape
    
    scale_factor = width / BASE_WIDTH

    points_abs = np.array([(int(p[0] * width), int(p[1] * height)) for p in WINNING_HORSE_DIAMOND_POINTS_RATIO], np.int32)
    rect = cv2.boundingRect(points_abs)
    x, y, w, h = rect
    roi_bgr = image_np[y:y+h, x:x+w]

    points_relative = points_abs.copy()
    points_relative[:, 0] -= x
    points_relative[:, 1] -= y
    mask = np.zeros(roi_bgr.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [points_relative], (255))
    
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 60])
    black_mask = cv2.inRange(hsv, lower_black, upper_black)
    processed_img = cv2.bitwise_and(black_mask, black_mask, mask=mask)

    best_match = {'score': -1.0, 'number': None}
    for number, template_list in winning_horse_templates.items():
        for template_info in template_list:
            original_template = template_info['image']

            template_img = _get_resized_template(original_template, scale_factor)

            if template_img.shape[0] > processed_img.shape[0] or template_img.shape[1] > processed_img.shape[1]:
                continue
            res = cv2.matchTemplate(processed_img, template_img, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > best_match['score']:
                best_match = {'score': max_val, 'number': number}
    
    return best_match['number'] if best_match['score'] >= WINNING_HORSE_MATCH_THRESHOLD else None

def assign_ranks(odds_values):
    """オッズリストから人気順位を割り当てる"""
    indexed_odds = sorted(enumerate(odds_values), key=lambda x: x[1])
    ranks = [0] * len(odds_values)
    i = 0
    while i < len(indexed_odds):
        current_odds = indexed_odds[i][1]
        j = i
        while j < len(indexed_odds) and abs(indexed_odds[j][1] - current_odds) < 0.01:
            j += 1
        current_rank = i + 1
        for k in range(i, j):
            original_index = indexed_odds[k][0]
            ranks[original_index] = current_rank
        i = j
    return ranks

# --- メインロジック ---

def extract_pre_race_data(image_path):
    """レース前のスクリーンショットからオッズと馬名を抽出する"""
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"[エラー] 画像ファイルが読み込めません: {image_path}")
            return
        
        height, width, _ = image.shape
        print(f"画像を読み込みました: {width}x{height}")

        odds_areas = [_calculate_coords(r, width, height) for r in ODDS_AREAS_RATIOS]
        odds_values = [parse_odds_to_float(get_odds_text(image, area)) for area in odds_areas]
        
        horse_name_templates = load_horse_name_templates()
        name_areas = [_calculate_coords(r, width, height) for r in HORSE_NAME_AREAS_RATIOS]
        horse_names = [identify_horse_name_by_image(image, area, horse_name_templates) for area in name_areas]

        if any(o >= 999.0 for o in odds_values) or "N/A" in horse_names:
            print("[警告] データの一部が正しく読み取れませんでした。")
        
        ranks = assign_ranks(odds_values)
        
        race_data = {
            'timestamp': datetime.now().isoformat(),
            'resolution': f'{width}x{height}',
            'odds': odds_values,
            'names': horse_names,
            'ranks': ranks
        }
        
        with open(UNRESOLVED_RACE_FILE, 'w', encoding='utf-8') as f:
            json.dump(race_data, f, indent=4)
            
        print(f"レース前データを抽出し、'{UNRESOLVED_RACE_FILE}' に一時保存しました。")
        print("  - オッズ:", odds_values)
        print("  - 馬名:", horse_names)
        print("  - 人気:", ranks)

    except Exception as e:
        print(f"[エラー] レース前データの抽出中にエラーが発生しました: {e}")
        utils.logging.error(f"レース前データ抽出エラー: {e}")

def process_post_race_data(image_path, betted_horse_number):
    """レース後のスクリーンショットを解析し、統計を更新する"""
    if not os.path.exists(UNRESOLVED_RACE_FILE):
        print(f"[エラー] 解析途中の一時ファイル '{UNRESOLVED_RACE_FILE}' が見つかりません。")
        print("先にレース前のスクリーンショットを解析してください。")
        return

    try:
        with open(UNRESOLVED_RACE_FILE, 'r', encoding='utf-8') as f:
            pre_race_data = json.load(f)

        image = cv2.imread(image_path)
        if image is None:
            print(f"[エラー] 画像ファイルが読み込めません: {image_path}")
            return
        
        load_winning_horse_templates()
        winning_horse_num = get_winning_horse_number(image)
        
        if winning_horse_num is None:
            print("[エラー] 勝ち馬の番号を特定できませんでした。テンプレート画像を確認してください。")
            return
            
        print(f"勝ち馬を「{winning_horse_num}番」と認識しました。")
        
        stats = utils.load_stats()
        rank_apps, rank_wins, name_apps, name_wins, odds_patterns = stats

        odds = pre_race_data['odds']
        ranks = pre_race_data['ranks']
        names = pre_race_data['names']
        
        for i in range(6):
            if odds[i] < 999.0:
                rank_apps[ranks[i]] = rank_apps.get(ranks[i], 0) + 1
                if names[i] != "N/A":
                    name_apps[names[i]] = name_apps.get(names[i], 0) + 1

        winner_idx = winning_horse_num - 1
        rank_wins[ranks[winner_idx]] = rank_wins.get(ranks[winner_idx], 0) + 1
        if names[winner_idx] != "N/A":
            name_wins[names[winner_idx]] = name_wins.get(names[winner_idx], 0) + 1
            
        utils.save_stats((rank_apps, rank_wins, name_apps, name_wins, odds_patterns))
        
        is_win = (winning_horse_num == betted_horse_number)
        history_entry = {
            **pre_race_data,
            'winner': winning_horse_num,
            'betted_on': betted_horse_number,
            'is_win': is_win
        }
        with open(RACE_HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(history_entry) + '\n')
            
        print("統計データとレース履歴を更新しました。")
        os.remove(UNRESOLVED_RACE_FILE)
        print(f"一時ファイル '{UNRESOLVED_RACE_FILE}' を削除しました。")

    except Exception as e:
        print(f"[エラー] レース後データの処理中にエラーが発生しました: {e}")
        utils.logging.error(f"レース後データ処理エラー: {e}")