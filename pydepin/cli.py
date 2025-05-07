import click
from rich.console import Console
from .core import build_graph, get_statuses

console = Console()

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("project_root", type=click.Path(exists=True))
@click.argument("start_files", nargs=-1, required=True)
@click.option("-r", "--reverse", is_flag=True,
              help="Show which files import the selected ones")
@click.option("--show-ignored", is_flag=True,
              help="Include irrelevant files (tests, setup.py, __init__.py, etc.)")
def main(project_root, start_files, reverse, show_ignored):
    """
    Highlight file dependencies in a project.

    PROJECT_ROOT  Path to the project root.
    START_FILES   One or more Python files (relative to root).
    """
    # Build the import graph, optionally including ignored files
    G = build_graph(project_root, include_ignored=show_ignored)

    # Map each file to its status: 'selected', 'related', 'ignored', or 'unrelated'
    statuses = get_statuses(G, start_files, reverse=reverse)

    # Print with color-coded markers
    for node, status in sorted(statuses.items()):
        if status == "selected":
            console.print(f"[blue]🔵 {node}[/]")
        elif status == "related":
            console.print(f"[green]🟢 {node}[/]")
        elif status == "ignored":
            console.print(f"[grey]⚫ {node}[/]")
        else:
            console.print(f"[grey]⚪ {node}[/]")

if __name__ == "__main__":
    main()

