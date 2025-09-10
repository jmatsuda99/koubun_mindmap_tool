
# -*- coding: utf-8 -*-
import streamlit as st, os, json, io
from utils.parser import parse_any, flatten_to_depth, collapse_single_chains
from utils.visual import to_pyvis

st.set_page_config(page_title="Generic Outline Visualizer", layout="wide")
st.title("📑 Generic Outline & Mindmap Visualizer")
st.caption("PDF / DOCX / PPTX → Outline JSON → Interactive mindmap (PyVis)")

with st.sidebar:
    st.markdown("### Display Options")
    max_depth = st.slider("Max depth (0 = root only)", 0, 10, 4, 1)
    collapse = st.toggle("Collapse single-child chains", value=False)

uploaded = st.file_uploader("Upload files (PDF/DOCX/PPTX)", type=["pdf","docx","pptx"], accept_multiple_files=True)

tabs = st.tabs(["🕸 Interactive Mindmap", "🧾 Outline JSON", "⬇️ Export"])

if uploaded:
    out_dir = "outputs"
    os.makedirs(out_dir, exist_ok=True)
    for file in uploaded:
        st.divider()
        st.subheader(file.name)

        raw_bytes = file.read()
        fpath = os.path.join(out_dir, file.name)
        with open(fpath, "wb") as f:
            f.write(raw_bytes)

        # parse
        try:
            base_tree = parse_any(fpath)
        except Exception as e:
            st.error(f"Parse error: {e}")
            continue

        # trim and normalize
        tree = flatten_to_depth(base_tree, max_depth=max_depth)
        if collapse:
            tree = collapse_single_chains(tree)

        with tabs[0]:
            net = to_pyvis(tree, height="720px", width="100%")
            html_path = os.path.join(out_dir, f"{os.path.splitext(file.name)[0]}.html")
            net.show(html_path)
            st.components.v1.html(open(html_path, "r", encoding="utf-8").read(), height=740, scrolling=True)

        with tabs[1]:
            st.json(tree)
        with tabs[2]:
            # JSON
            json_bytes = json.dumps(tree, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button("Download JSON", data=json_bytes, file_name=f"{os.path.splitext(file.name)[0]}_outline.json", mime="application/json")
            # Markdown (indented list)
            def to_md(n, d=0):
                s = "  " * d + f"- {n.get('title','')}\n"
                for c in n.get("children", []):
                    s += to_md(c, d+1)
                return s
            md = to_md(tree)
            st.download_button("Download Markdown", data=md.encode("utf-8"), file_name=f"{os.path.splitext(file.name)[0]}_outline.md", mime="text/markdown")
            # OPML (for mindmap apps)
            def to_opml(n):
                attrs = f'text="{n.get("title","").replace("\"","&quot;")}"'
                if not n.get("children"):
                    return f"<outline {attrs} />"
                return "<outline {attrs}>".format(attrs=attrs) + "".join(to_opml(c) for c in n.get("children",[])) + "</outline>"
            opml = '<?xml version="1.0" encoding="UTF-8"?>\n<opml version="2.0"><head><title>Outline</title></head><body>' + to_opml(tree) + "</body></opml>"
            st.download_button("Download OPML", data=opml.encode("utf-8"), file_name=f"{os.path.splitext(file.name)[0]}_outline.opml", mime="text/xml")
else:
    st.info("Upload one or more files to visualize their outlines.")
