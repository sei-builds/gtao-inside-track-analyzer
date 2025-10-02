# GTAO Inside Track Analyzer

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GTAオンラインのインサイドトラックを、データ分析とシミュレーションで攻略するためのツールキット。**

---

## 概要

このプロジェクトは、GTAオンラインのコンテンツ「インサイドトラック」におけるレース結果をデータとして収集・分析し、統計に基づいたベット戦略を研究・シミュレーションするためのツール群です。

**⚠️ 注意：このツールはゲームプレイを自動化するBOTではありません。**
ゲーム画面への自動入力やリアルタイムでの監視機能は一切含んでおらず、Rockstar Gamesの利用規約に抵触する行為を目的としたものではありません。あくまでユーザーが手動で取得したスクリーンショットを元に、オフラインで分析を行うためのものです。

## 主な機能

* **📊 データ収集 (`collector.py`)**
    * レースのベット画面や結果画面のスクリーンショットから、OCRと画像認識技術を用いてオッズ、馬名、勝ち馬などの情報を正確に抽出します。

* **📈 データ分析 (`analyzer.py`)**
    * 収集したデータに基づき、人気順位別勝率や馬名別勝率などの詳細な統計レポートを生成します。

* **🤖 戦略シミュレーション (`simulator.py`)**
    * 蓄積した過去の全レースデータに対し、「常に1番人気に賭ける」などのユーザー定義のベット戦略を適用した場合の収支やROI（投資収益率）を高速にバックテストします。

## 導入方法

### 1. 前提条件
* [Python 3.9](https://www.python.org/downloads/) 以降
* [Tesseract-OCR](https://github.com/tesseract-ocr/tessdoc) がインストールされ、PATHが通っていること。
    * インストール時に "Add Tesseract to system PATH" にチェックを入れてください。
    * Windows以外の場合は、`config.py`内の`TESSERACT_PATH`を適宜設定してください。

### 2. リポジトリのクローン
```bash
git clone [https://github.com/YOUR_USERNAME/gtao-inside-track-analyzer.git](https://github.com/YOUR_USERNAME/gtao-inside-track-analyzer.git)
cd gtao-inside-track-analyzer
```

### 3. 必要なライブラリのインストール
```bash
pip install -r requirements.txt
```
※ `requirements.txt` がない場合は、以下のコマンドでインストールしてください。
```bash
pip install opencv-python pytesseract numpy tqdm
```

### 4. テンプレート画像の準備
* `horse_name_templates/` フォルダに、馬名のテンプレート画像（例: `Hen House.png`）を配置してください。
* `winning_horse_templates/` フォルダに、勝ち馬番号（ひし形の中の数字）のテンプレート画像（例: `1_template_01.png`）を配置してください。

## 使用方法

すべてのコマンドは `main.py` を通じて実行します。

### ステップ1: レース前データの収集
ゲーム内でベット画面のスクリーンショット (`pre-race.png` など) を撮影し、以下のコマンドを実行します。
```bash
python main.py collect --pre pre-race.png
```

### ステップ2: レース後データの収集と統計の更新
レース終了後、結果画面のスクリーンショット (`post-race.png` など) を撮影します。仮にあなたが**3番**の馬に賭けていた場合、以下のコマンドを実行します。
```bash
python main.py collect --post post-race.png --bet 3
```
これにより、レース結果が `race_history.jsonl` と `win_rate_stats.json` に記録・更新されます。

### ステップ3: 分析レポートの表示
蓄積したデータの統計レポートを見るには、以下のコマンドを実行します。
```bash
python main.py analyze
```
特定のレポートのみ表示することも可能です。
```bash
python main.py analyze --report horse
```

### ステップ4: 戦略のシミュレーション
「期待値がプラスの馬に賭ける」戦略のパフォーマンスを検証するには、以下のコマンドを実行します。
```bash
python main.py simulate --strategy positive_ev
```

## 免責事項
本ツールの使用はすべて自己責任で行ってください。本ツールの使用によって生じたいかなる損害についても、作成者は一切の責任を負いません。

## ライセンス
このプロジェクトは [MIT License](LICENSE) のもとで公開されています。