
# -*- coding: utf-8 -*-
from typing import Dict, Any
from graphviz import Digraph
from pyvis.network import Network
import uuid

def to_graphviz(tree: Dict[str, Any], title="Document Tree"):
    dot = Digraph(comment=title, format="png")
    dot.attr('node', shape='box', style='rounded,filled', color='lightblue2', fontname="Noto Sans CJK JP")
    def add(node, parent_id=None):
        nid = str(uuid.uuid4())[:8]
        label = node.get("title", "")
        dot.node(nid, label)
        if parent_id:
            dot.edge(parent_id, nid)
        for ch in node.get("children", []):
            add(ch, nid)
    add(tree, None)
    return dot

def to_pyvis(tree: Dict[str, Any], height="700px", width="100%"):
    net = Network(height=height, width=width, directed=True)
    def add(node, parent_id=None):
        nid = str(uuid.uuid4())[:8]
        net.add_node(nid, label=node.get("title", ""), shape="box")
        if parent_id:
            net.add_edge(parent_id, nid)
        for ch in node.get("children", []):
            add(ch, nid)
    add(tree, None)
    return net
