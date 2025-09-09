
# -*- coding: utf-8 -*-
"""
Lightweight document outline parsers for PDF/DOCX/PPTX.
Returns a uniform tree structure:
{"title": "...", "children": [ ... ], "meta": {...}}
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import re

# PDF
from pypdf import PdfReader
# DOCX
from docx import Document
# PPTX
from pptx import Presentation

HEADING_PAT = re.compile(r"^(?:\d+(?:\.\d+)*[\)\.]\s*)|(?:第[一二三四五六七八九十]+章)|(?:[A-Z]\.)")

@dataclass
class Node:
    title: str
    level: int = 1
    children: List["Node"] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "level": self.level,
            "children": [c.to_dict() for c in self.children],
            "meta": self.meta,
        }

def _nest_by_levels(items: List[Tuple[int, str, Dict[str, Any]]], root_title="ROOT") -> Dict[str, Any]:
    root = Node(root_title, level=0)
    stack = [root]
    for lvl, title, meta in items:
        node = Node(title=title.strip(), level=lvl, meta=meta)
        # climb up
        while stack and lvl <= stack[-1].level:
            stack.pop()
        stack[-1].children.append(node)
        stack.append(node)
    return root.to_dict()

def parse_pdf(path: str) -> Dict[str, Any]:
    reader = PdfReader(path)
    items: List[Tuple[int, str, Dict[str, Any]]] = []
    # Try PDF outline (bookmarks)
    try:
        outlines = reader.outline
        def walk(out, level=1):
            for o in out:
                if isinstance(o, list):
                    walk(o, level+1)
                else:
                    title = str(getattr(o, "title", o))
                    items.append((level, title, {"type": "pdf_outline"}))
        if outlines:
            walk(outlines, 1)
    except Exception:
        pass
    # Fallback: infer from headings-like lines on first N pages
    if not items:
        for i, page in enumerate(reader.pages[:30]):
            text = page.extract_text() or ""
            for line in text.splitlines():
                line_s = line.strip()
                if not line_s:
                    continue
                # Heading heuristics
                if HEADING_PAT.search(line_s) or len(line_s) <= 30:
                    # rough level by count of dots like 1.2.3 -> 3; or bullets
                    m = re.match(r"^(\d+(?:\.\d+)+)", line_s)
                    if m:
                        level = m.group(1).count(".") + 1
                    elif re.match(r"^\d+[\.\)]", line_s):
                        level = 1
                    elif re.match(r"^[A-Z]\.", line_s):
                        level = 1
                    elif re.match(r"^第[一二三四五六七八九十]+章", line_s):
                        level = 1
                    else:
                        level = 2
                    items.append((level, line_s, {"type": "pdf_text", "page": i+1}))
    return _nest_by_levels(items or [(1, "Document", {})], root_title="PDF")

def parse_docx(path: str) -> Dict[str, Any]:
    doc = Document(path)
    items: List[Tuple[int, str, Dict[str, Any]]] = []
    for p in doc.paragraphs:
        style = getattr(p.style, "name", "")
        text = p.text.strip()
        if not text:
            continue
        lvl = None
        # Heading styles
        if style.startswith("Heading") or style.startswith("見出し"):
            m = re.search(r"(\d+)$", style)
            lvl = int(m.group(1)) if m else 1
        # Numbered headings heuristic
        if lvl is None:
            if HEADING_PAT.search(text):
                m = re.match(r"^(\d+(?:\.\d+)+)", text)
                if m:
                    lvl = m.group(1).count(".") + 1
                else:
                    lvl = 2
        if lvl is not None:
            items.append((lvl, text, {"type": "docx_heading", "style": style}))
    if not items:
        # fallback to first paragraphs
        for p in doc.paragraphs[:50]:
            t = p.text.strip()
            if t:
                items.append((1, t[:40], {"type": "docx_text"}))
    return _nest_by_levels(items or [(1, "Document", {})], root_title="DOCX")

def parse_pptx(path: str) -> Dict[str, Any]:
    prs = Presentation(path)
    items: List[Tuple[int, str, Dict[str, Any]]] = []
    for i, slide in enumerate(prs.slides, start=1):
        title = None
        for shape in slide.shapes:
            if hasattr(shape, "text_frame") and shape.text_frame:
                # assume the first text frame is title-ish
                txt = shape.text_frame.text.strip()
                if txt:
                    if title is None:
                        title = txt
                    else:
                        # add bullet lines as children level 2
                        for p in shape.text_frame.paragraphs:
                            t = "".join(run.text for run in p.runs).strip() or p.text.strip()
                            if t:
                                items.append((2, t, {"type": "pptx_bullet", "slide": i}))
        if title:
            items.append((1, f"Slide {i}: {title}", {"type": "pptx_title", "slide": i}))
        else:
            items.append((1, f"Slide {i}", {"type": "pptx_title", "slide": i}))
    return _nest_by_levels(items, root_title="PPTX")

def parse_any(path: str) -> Dict[str, Any]:
    low = path.lower()
    if low.endswith(".pdf"):
        return parse_pdf(path)
    if low.endswith(".docx"):
        return parse_docx(path)
    if low.endswith(".pptx"):
        return parse_pptx(path)
    raise ValueError("Unsupported file type")

def flatten_to_depth(tree: Dict[str, Any], max_depth: int) -> Dict[str, Any]:
    """Trim children beyond max_depth (root level=0)"""
    def rec(node: Dict[str, Any], depth: int) -> Dict[str, Any]:
        nd = {"title": node.get("title", ""), "level": node.get("level", depth), "meta": node.get("meta", {})}
        if depth >= max_depth:
            nd["children"] = []
        else:
            nd["children"] = [rec(c, depth+1) for c in node.get("children", [])]
        return nd
    return rec(tree, 0)
