
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os, json, time
from utils.parser import parse_any, flatten_to_depth
from utils.visual import to_graphviz, to_pyvis

st.set_page_config(page_title="構文木の見える化ツール", layout="wide")
st.title("📑 構文木の見える化ツール（PDF/DOCX/PPTX）")

st.markdown("""
- 対象：**文書（PDF/DOCX）** / **プレゼン（PPTX）**
- 機能：**階層の深さをスライダーで調整**、**マインドマップ風/ネットワーク図**で可視化、**PNG/HTML出力**
""")

uploaded = st.file_uploader("ファイルをアップロード（複数可：PDF/DOCX/PPTX）", type=["pdf","docx","pptx"], accept_multiple_files=True)
max_depth = st.slider("表示する階層の深さ（0=ルートのみ）", min_value=0, max_value=8, value=4, step=1)

tab1, tab2, tab3 = st.tabs(["🧠 Mindmap (Graphviz)", "🕸 Network (PyVis)", "🧾 JSON"])

if uploaded:
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    for file in uploaded:
        with st.spinner(f"解析中：{file.name}"):
            path = os.path.join(out_dir, file.name)
            with open(path, "wb") as f:
                f.write(file.getbuffer())
            tree = parse_any(path)
            trimmed = flatten_to_depth(tree, max_depth=max_depth)

        with tab3:
            st.subheader(file.name)
            st.json(trimmed)

        with tab1:
            st.subheader(file.name)
            dot = to_graphviz(trimmed, title=file.name)
            png_path = os.path.join(out_dir, f"{file.name}.png")
            dot.render(png_path[:-4], format="png", cleanup=True)
            st.image(png_path, use_column_width=True)
            st.download_button("PNGをダウンロード", data=open(png_path, "rb").read(), file_name=os.path.basename(png_path), mime="image/png")

        with tab2:
            st.subheader(file.name)
            net = to_pyvis(trimmed, height="700px", width="100%")
            html_path = os.path.join(out_dir, f"{file.name}.html")
            net.show(html_path)
            st.components.v1.html(open(html_path, "r", encoding="utf-8").read(), height=720, scrolling=True)
            st.download_button("HTML（インタラクティブ）をダウンロード", data=open(html_path, "rb").read(), file_name=os.path.basename(html_path), mime="text/html")
else:
    st.info("上のエリアからファイルを選んでください。")
