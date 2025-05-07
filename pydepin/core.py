#!/usr/bin/env python3
import os
import ast
import networkx as nx
import charset_normalizer as cn
import fnmatch

IRRELEVANT_PATTERNS = [
    '__init__.py',
    'test_*.py', '*_test.py',
    'setup.py', 'conftest.py',
    'manage.py', 'wsgi.py', 'asgi.py'
]


def find_py_files(root, include_ignored=False):
    """
    Yield all Python files under `root` as paths relative to `root`.
    Skips boilerplate/irrelevant files unless include_ignored=True.
    """
    ignore_dirs = {'.venv', 'venv', 'env', '__pycache__', '.git'}
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for fn in files:
            if not fn.endswith('.py'):
                continue
            if not include_ignored and fn in IRRELEVANT_PATTERNS:
                continue
            yield os.path.relpath(os.path.join(dirpath, fn), root)


def parse_imports(path):
    """
    Parse a Python file and return a set of dotted module names it imports.
    """
    imports = set()
    raw = open(path, 'rb').read()
    matches = cn.from_bytes(raw)
    try:
        encoding = matches.best().encoding
    except Exception:
        encoding = 'utf-8'
    content = raw.decode(encoding, errors='replace')
    tree = ast.parse(content, path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            for alias in node.names:
                full_mod = f"{base}.{alias.name}" if base else alias.name
                imports.add(full_mod)
    return imports


def build_graph(root, include_ignored=False):
    """
    Build a directed graph where nodes are Python files (relative paths)
    and edges A -> B denote A imports or depends on B.
    """
    file_map = {rel: os.path.join(root, rel) for rel in find_py_files(root, include_ignored)}
    G = nx.DiGraph()
    G.add_nodes_from(file_map.keys())

    for src_rel, src_abs in file_map.items():
        for mod in parse_imports(src_abs):
            full_path = mod.replace('.', os.sep) + '.py'
            parent = '.'.join(mod.split('.')[:-1])
            parent_path = parent.replace('.', os.sep) + '.py' if parent else None
            for candidate in (full_path, parent_path):
                if candidate in file_map:
                    G.add_edge(src_rel, candidate)
                    break
    return G


def get_statuses(G, roots, downstream=True, upstream=False):
    """
    Return a dict mapping node -> status:
      'selected'   (# roots),
      'descendant' (files your roots import),
      'ancestor'   (files that import your roots),
      'ignored'    (boilerplate like __init__.py),
      'unrelated'  (everything else).
    downstream=True includes descendants, upstream=True includes ancestors.
    """
    desc = set()
    anc = set()
    if downstream:
        for r in roots:
            desc |= nx.descendants(G, r)
    if upstream:
        for r in roots:
            anc |= nx.ancestors(G, r)

    statuses = {}
    for node in sorted(G.nodes()):
        if node in roots:
            statuses[node] = 'selected'
        elif node in desc:
            statuses[node] = 'descendant'
        elif node in anc:
            statuses[node] = 'ancestor'
        elif os.path.basename(node) in IRRELEVANT_PATTERNS:
            statuses[node] = 'ignored'
        else:
            statuses[node] = 'unrelated'
    return statuses