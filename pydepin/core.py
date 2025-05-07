#!/usr/bin/env python3
import os
import ast
import networkx as nx
import argparse
import sys

def find_py_files(root):
    """
    Yield all Python files under `root` as paths relative to `root`.
    """
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.endswith('.py'):
                yield os.path.relpath(os.path.join(dirpath, fn), root)


def parse_imports(path):
    """
    Parse a Python file and return a set of dotted module names it imports.

    - `import foo.bar`       → yields "foo.bar"
    - `from foo import bar`  → yields "foo.bar"
    - `from foo.bar import baz` → yields "foo.bar.baz"
    """
    imports = set()
    with open(path, 'r', encoding='utf8') as f:
        tree = ast.parse(f.read(), path)

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


def build_graph(root):
    """
    Build a directed graph where nodes are Python files (relative paths)
    and edges A → B denote that file A imports or depends on file B.
    """
    file_map = {rel: os.path.join(root, rel) for rel in find_py_files(root)}
    G = nx.DiGraph()
    G.add_nodes_from(file_map.keys())

    for src_rel, src_abs in file_map.items():
        for mod in parse_imports(src_abs):
            full_path = mod.replace('.', os.sep) + '.py'
            parent = '.'.join(mod.split('.')[:-1])
            parent_path = parent.replace('.', os.sep) + '.py' if parent else None

            for candidate in (full_path, parent_path):
                if candidate and candidate in file_map:
                    G.add_edge(src_rel, candidate)
                    break
    return G


def highlight(G, root, starts, reverse=False):
    """
    Highlight files reachable from (or reaching) any of the `starts` files.

    - Normal mode: green (🟢) = downstream imports, blue (🔵) = selected,
      grey (⚪) = unrelated.
    - Reverse mode (-r): green (🟢) = upstream importers (files that use the selected),
      blue (🔵) = selected, grey (⚪) = unrelated.
    """
    G = build_graph(root)
    missing = [s for s in starts if s not in G]
    if missing:
        print("❌ These files weren’t found in the graph:")
        for s in missing:
            print("   ", s)
        sys.exit(1)

    reach = set(starts)
    if reverse:
        for s in starts:
            reach |= nx.ancestors(G, s)
    else:
        for s in starts:
            reach |= nx.descendants(G, s)
    d = {}
    for node in sorted(G.nodes()):
        if node in starts:
            d[node] = 'selected'
        elif node in reach:
            d[node] = 'related'
        else:
            d[node] = 'unrelated'
        
    return d


def main():
    parser = argparse.ArgumentParser(
        description='Dep Inspector: highlight file dependencies in a project')
    parser.add_argument('project_root', help='Path to the project root')
    parser.add_argument('start_files', nargs='+', help='One or more files to inspect')
    parser.add_argument('-r', '--reverse', action='store_true',
                        help='Reverse mode: show which files import the selected ones')
    args = parser.parse_args()

    highlight(args.project_root, args.start_files, reverse=args.reverse)


if __name__ == '__main__':
    main()

