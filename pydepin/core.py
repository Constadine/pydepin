# core.py
#!/usr/bin/env python3
import os
import ast
import re
import fnmatch
import networkx as nx
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor, as_completed

# Patterns for files to ignore by default
IRRELEVANT_PATTERNS = [
    '__init__.py',
    'test_*.py', '*_test.py',
    'setup.py', 'conftest.py',
    'manage.py', 'wsgi.py', 'asgi.py'
]
# compile into a single regex
_IGNORE_RE = re.compile("|".join(fnmatch.translate(p) for p in IRRELEVANT_PATTERNS))


def find_py_files(root, include_ignored=False):
    """
    Yield all Python files under `root` as paths relative to `root`.
    Skips irrelevant files unless include_ignored=True.
    """
    ignore_dirs = {'.venv', 'venv', 'env', '__pycache__', '.git'}
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for fn in files:
            if not fn.endswith('.py'):
                continue
            if not include_ignored and _IGNORE_RE.match(fn):
                continue
            yield os.path.relpath(os.path.join(dirpath, fn), root)


@lru_cache(maxsize=None)
def parse_imports(path):
    """
    Parse a Python file and return a set of dotted module names it imports.
    Errors in reading/encoding are ignored.
    """
    imports = set()
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        tree = ast.parse(content, path)
    except Exception:
        return imports

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
    This version parses files in parallel.
    """
    file_map = {rel: os.path.join(root, rel)
                for rel in find_py_files(root, include_ignored)}
    G = nx.DiGraph()
    G.add_nodes_from(file_map.keys())

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(parse_imports, path): rel
                   for rel, path in file_map.items()}
        for future in as_completed(futures):
            src_rel = futures[future]
            imports = future.result()
            for mod in imports:
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
      'selected', 'descendant', 'ancestor', 'ignored', 'unrelated'.
    downstream includes descendants, upstream includes ancestors.
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
        elif _IGNORE_RE.match(os.path.basename(node)):
            statuses[node] = 'ignored'
        else:
            statuses[node] = 'unrelated'
    return statuses
