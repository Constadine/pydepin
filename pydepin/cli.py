import click
from rich.console import Console
from .core import build_graph, highlight

console = Console()

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("project_root", type=click.Path(exists=True))
@click.argument("start_files", nargs=-1, required=True)
@click.option("-r", "--reverse", is_flag=True,
              help="Show which files import the selected ones")
def main(project_root, start_files, reverse):
    """
    Highlight file dependencies in a project.

    PROJECT_ROOT  Path to the project root.
    START_FILES   One or more Python files (relative to root).
    """
    G = build_graph(project_root)
    # run highlight logic (return dict mapping node→status)
    statuses = highlight(G, project_root, start_files, reverse=reverse)
    # print with colors
    for node, status in sorted(statuses.items()):
        if status == "selected":
            console.print(f"[blue]🔵 {node}[/]")
        elif status == "related":
            console.print(f"[green]🟢 {node}[/]")
        else:
            console.print(f"[grey]⚪ {node}[/]")

