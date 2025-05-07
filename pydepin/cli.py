# cli.py
#!/usr/bin/env python3
import os
import sys
import difflib

import click
from rich.console import Console

from .core import build_graph, get_statuses

console = Console()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("project_root", type=click.Path(exists=True))
@click.argument("start_files", nargs=-1, required=True)
@click.option("-d", "--downstream", is_flag=True,
              help="Show only files your selected files import (descendants).")
@click.option("-u", "--upstream", is_flag=True,
              help="Show only files that import your selected files (ancestors).")
@click.option("--show-ignored", is_flag=True,
              help="Include ignored files like __init__.py")
@click.option("-o", "--only-highlighted", is_flag=True,
              help="Only show selected (blue) and related files")
@click.version_option()  # Assumes __version__ in your package __init__.py
def main(project_root, start_files, downstream, upstream, show_ignored, only_highlighted):
    """
    Highlight file dependencies in a project.

    PROJECT_ROOT  Path to the project root.
    START_FILES   One or more Python files (relative to root).
    """
    # Mutually exclusive flags
    if downstream and upstream:
        raise click.UsageError("Cannot use both --downstream and --upstream together")

    # Default to united mode (both directions) if neither flag is provided
    if not downstream and not upstream:
        downstream = upstream = True

    # Build the graph
    G = build_graph(project_root, include_ignored=show_ignored)

    # Normalize and validate start files
    normalized = []
    for s in start_files:
        if os.path.isabs(s) and s.startswith(project_root):
            rel = os.path.relpath(s, project_root)
        else:
            rel = s
        normalized.append(rel)

    missing = [s for s in normalized if s not in G]
    if missing:
        for bad in missing:
            suggestions = difflib.get_close_matches(bad, G.nodes(), n=3, cutoff=0.6)
            if suggestions:
                console.print(
                    f"❌ File not found: [red]{bad}[/]. Did you mean: "
                    + ", ".join(f"[blue]{c}[/]" for c in suggestions)
                    + "?",
                    style="red"
                )
            else:
                console.print(f"❌ File not found: [red]{bad}[/]", style="red")
        sys.exit(1)

    # Compute statuses
    statuses = get_statuses(G, normalized,
                            downstream=downstream,
                            upstream=upstream)

    # Print results with different green shades
    for node, status in sorted(statuses.items()):
        if only_highlighted and status not in ("selected", "descendant", "ancestor"):
            continue

        if status == "selected":
            console.print(f"[blue]🔵 {node}[/]")
        elif status == "descendant":
            console.print(f"[green]🟢 {node}[/]")         # standard green
        elif status == "ancestor":
            console.print(f"[bright_green]🟢 {node}[/]")  # lighter green
        elif status == "ignored":
            console.print(f"[grey]⚫ {node}[/]")
        else:
            console.print(f"[grey]⚪ {node}[/]")


if __name__ == "__main__":
    main()
