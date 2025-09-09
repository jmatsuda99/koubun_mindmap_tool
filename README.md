# 構文木の見える化ツール（PDF/DOCX/PPTX）

文書（PDF/DOCX）とプレゼン（PPTX）から見出し・スライド構造を抽出し、
**マインドマップ風**（Graphviz）と**インタラクティブネットワーク**（PyVis）で可視化します。
スライダーで**階層の深さ**を調整できます。

## 特徴
- PDF：しおり（アウトライン）があれば優先、なければヘッダ風テキストをヒューリスティクス抽出
- DOCX：見出しスタイル（Heading 1/見出し1 等）＋番号付き見出しをヒューリスティクス
- PPTX：スライドタイトルと箇条書きを階層化
- 出力：PNG（Graphviz）/ HTML（PyVis）/ JSON

## 使い方（ローカル）
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 設計メモ
- `utils/parser.py`：ファイル種別ごとのアウトライン抽出、`flatten_to_depth()`で階層トリミング
- `utils/visual.py`：Graphviz/pyvis へのレンダリング
- 将来的には DB 保存や全文検索の追加、章/節単位のフィルタ、検索ハイライト等を想定
