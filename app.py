import streamlit as st, os, json
from utils.parser import parse_any, flatten_to_depth, collapse_single_chains
from utils.visual import to_pyvis

st.set_page_config(page_title="構文木の見える化ツール", layout="wide")
st.title("📑 構文木の見える化ツール（koubun_mindmap_tool_fix2）")

with st.sidebar:
    max_depth = st.slider("表示する階層の深さ（0=ルートのみ）", 0, 10, 4, 1)
    collapse = st.toggle("単一路線をまとめる", value=False)

uploaded = st.file_uploader("ファイルをアップロード（PDF/DOCX/PPTX）", type=["pdf","docx","pptx"], accept_multiple_files=True)
tabs = st.tabs(["🕸 Mindmap", "🧾 JSON", "⬇️ Export"])

if uploaded:
    out_dir = "outputs"; os.makedirs(out_dir, exist_ok=True)
    for file in uploaded:
        st.subheader(file.name)
        safe_name = os.path.basename(file.name)
        fpath = os.path.join(out_dir, safe_name)
        with open(fpath, "wb") as f: f.write(file.read())
        try:
            tree = parse_any(fpath)
        except Exception as e:
            st.exception(e); continue
        tree = flatten_to_depth(tree, max_depth=max_depth)
        if collapse: tree = collapse_single_chains(tree)

        net = to_pyvis(tree, height="720px", width="100%")
        html_path = os.path.join(out_dir, f"{os.path.splitext(safe_name)[0]}.html")
        net.write_html(html_path)  # **重要：show() を使わない**
        with open(html_path, "r", encoding="utf-8") as fp:
            st.components.v1.html(fp.read(), height=740, scrolling=True)

        tabs[1].json(tree)
        # export buttons
        json_bytes = json.dumps(tree, ensure_ascii=False, indent=2).encode("utf-8")
        tabs[2].download_button("Download JSON", data=json_bytes, file_name=f"{os.path.splitext(safe_name)[0]}_outline.json", mime="application/json")
        def to_md(n, d=0):
            s = "  " * d + f"- {n.get('title','')}
"
            for c in n.get("children", []): s += to_md(c, d+1)
            return s
        md = to_md(tree)
        tabs[2].download_button("Download Markdown", data=md.encode("utf-8"), file_name=f"{os.path.splitext(safe_name)[0]}_outline.md", mime="text/markdown")
        def to_opml(n):
            attrs = f'text="{n.get("title","").replace("\\"","&quot;")}"'
            if not n.get("children"): return f"<outline {attrs} />"
            return "<outline {attrs}>".format(attrs=attrs) + "".join(to_opml(c) for c in n.get("children",[])) + "</outline>"
        opml = '<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0"><head><title>Outline</title></head><body>' + to_opml(tree) + "</body></opml>"
        tabs[2].download_button("Download OPML", data=opml.encode("utf-8"), file_name=f"{os.path.splitext(safe_name)[0]}_outline.opml", mime="text/xml")
else:
    st.info("上のエリアからファイルを選んでください。")
