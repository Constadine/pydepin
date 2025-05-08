# core_lsp.py
#!/usr/bin/env python3
import os
import ast
import networkx as nx
import jedi
from jedi import settings
settings.fast_parser = False
from concurrent.futures import ThreadPoolExecutor, as_completed

from .core import find_py_files, get_statuses

def build_graph(root: str, include_ignored: bool = False) -> nx.DiGraph:
    """
    Build a directed graph of Python-file dependencies using an LSP-style resolver (via Jedi).
    Parses import statements with ast, then asks Jedi to resolve each import to the actual file.
    """
    # Map relative → absolute paths
    file_map = {rel: os.path.join(root, rel) for rel in find_py_files(root, include_ignored)}
    G = nx.DiGraph()
    G.add_nodes_from(file_map.keys())

    # Create a Jedi project rooted at `root`
    project = jedi.Project(path=root)
        
    def _process(src_rel: str, abs_path: str):
        edges = []
        try:
            code = open(abs_path, 'r', encoding='utf-8', errors='ignore').read()
            tree = ast.parse(code, abs_path)
            script = jedi.Script(code, path=abs_path, project=project)
        except Exception:
            return edges

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    line = node.lineno
                    col0 = node.col_offset
                    line_text = code.splitlines()[line - 1]
                    col = line_text.find(alias.name, col0)
                    if col < 0:
                        col = col0

                    try:
                        defs = script.goto(line=line, column=col)
                    except Exception:
                        continue

                    for d in defs:
                        mp = d.module_path
                        if not mp:
                            continue
                        # Convert to str before checking path relationships
                        mp = str(mp)
                        if not mp.startswith(root):
                            continue
                        rel = os.path.relpath(mp, root)
                        if rel in file_map:
                            edges.append((src_rel, rel))
        return edges


    # Parallel processing of files
    with ThreadPoolExecutor(max_workers=1) as executor:
        futures = {
            executor.submit(_process, rel, abs_path): rel
            for rel, abs_path in file_map.items()
        }
        for future in as_completed(futures):
            for src, tgt in future.result():
                G.add_edge(src, tgt)

    return G
