# Generic Outline & Mindmap Visualizer

**Goal**: A *generic* tool to visualize document/presentation structure as a collapsible outline & mindmap.

- Input: **PDF**, **DOCX**, **PPTX**
- Output: **Interactive mindmap (HTML)**, **JSON**, **Markdown**, **OPML**
- Controls: **Max depth** slider, **Collapse single-child chains** toggle

## Why generic?
- Works with arbitrary RFQs, specs, contracts, slide decks, reports
- Language-aware heuristics for English/Japanese headings
- Robust PDF support: tries `pypdf` first, falls back to `PyPDF2`

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

> No system Graphviz required (uses PyVis). Suitable for Streamlit Cloud.
