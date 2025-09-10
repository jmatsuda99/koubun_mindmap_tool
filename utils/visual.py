from typing import Dict, Any
from pyvis.network import Network
import uuid, json

def safe_set_options(net: Network, options_json: str):
    # Ensure JSON (PyVis parses JSON only)
    json.loads(options_json)
    net.set_options(options_json)

def to_pyvis(tree: Dict[str, Any], height="720px", width="100%"):
    net = Network(height=height, width=width, directed=True)
    def add(node, parent=None):
        nid = str(uuid.uuid4())[:8]
        net.add_node(nid, label=node.get("title",""), shape="box")
        if parent:
            net.add_edge(parent, nid)
        for ch in node.get("children", []):
            add(ch, nid)
    add(tree, None)
    safe_set_options(net, """{
  "physics": { "stabilization": true },
  "layout": { "improvedLayout": true }
}
""")
    return net
