"""Deterministic Graphify map. Run with the isolated graphifyy==0.9.92 Python runtime."""
from pathlib import Path
import json
import hashlib
from importlib.metadata import version
from graphify.extract import extract
from graphify.build import build_from_json
from graphify.export import to_json, to_html

root = Path(__file__).resolve().parents[1]
paths = sorted(p for directory in ["src", "scripts", "tests"] for p in (root / directory).rglob("*") if p.suffix in {".ts", ".tsx", ".mjs", ".py"})
cache = root / "graphify-out"
cache.mkdir(exist_ok=True)
raw = extract(paths, cache_root=cache, root=root, parallel=False)
graph = build_from_json(raw, directed=True, root=root, dedup=False)
output = root / "docs/codebase-map.json"
to_json(graph, {}, str(output), force=True)
to_html(graph, {}, str(root / "docs/codebase-map.html"))
(root / "docs/codebase-map-inputs.json").write_text(json.dumps({
    "graphifyy": version("graphifyy"), "method": "local deterministic AST extraction; no agents, providers, semantic extraction or watchers",
    "files": {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    "nodes": graph.number_of_nodes(), "edges": graph.number_of_edges(),
    "limits": "Static extracted relationships are not complete runtime/dependency proof; review aliases, dynamic imports, React event wiring and JSON/media boundaries manually.",
}, indent=2) + "\n")
print(f"Mapped {len(paths)} files: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges.")
