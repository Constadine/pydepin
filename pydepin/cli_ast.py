# pydepin/cli_ast.py
#!/usr/bin/env python3
import os
import difflib
import typer
from typing import List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core import build_graph, get_statuses

app = typer.Typer(help="AST-based (lightweight) file‐dependency inspector")
console = Console()

@app.command("pydepin")
def main(
    project_root: str = typer.Argument(..., help="Path to the project root."),
    start_files: List[str] = typer.Argument(..., help="One or more Python files (relative to root)."),
    downstream: bool = typer.Option(False, "--downstream", "-d", help="Show only descendants."),
    upstream:   bool = typer.Option(False, "--upstream",   "-u", help="Show only ancestors."),
    show_ignored:     bool = typer.Option(False, "--show-ignored",     help="Include ignored boilerplate."),
    only_highlighted: bool = typer.Option(False, "--only-highlighted", "-o", help="Hide ⚪ files."),
):
    """
    AST-only version (fast to install, minimal deps).
    """
    if not downstream and not upstream:
        downstream = upstream = True

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True, console=console) as progress:
        t1 = progress.add_task("Building graph…", total=None)
        G = build_graph(project_root, include_ignored=show_ignored)
        progress.update(t1, completed=True)

        t2 = progress.add_task("Analyzing…", total=None)
        normalized = [os.path.relpath(s, project_root) if os.path.isabs(s) else s
                      for s in start_files]

        missing = [s for s in normalized if s not in G]
        if missing:
            progress.update(t2, completed=True)
            for bad in missing:
                sugg = difflib.get_close_matches(bad, G.nodes(), n=3, cutoff=0.6)
                if sugg:
                    console.print(f"❌ File not found: [red]{bad}[/]. Did you mean {sugg}?")
                else:
                    console.print(f"❌ File not found: [red]{bad}[/]")
            raise typer.Exit(code=1)

        statuses = get_statuses(G, normalized, downstream=downstream, upstream=upstream)
        progress.update(t2, completed=True)

    for node, status in sorted(statuses.items()):
        if only_highlighted and status not in ("selected", "descendant", "ancestor"):
            continue
        if status == "selected":
            console.print(f"[blue]🔵 {node}[/]")
        elif status == "descendant":
            console.print(f"[green]🟢 {node}[/]")
        elif status == "ancestor":
            console.print(f"[bright_green]🟢 {node}[/]")
        elif status == "ignored":
            console.print(f"[grey]⚫ {node}[/]")
        else:
            console.print(f"[grey]⚪ {node}[/]")
