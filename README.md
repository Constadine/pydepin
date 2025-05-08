# pydepin

`pydepin` is a CLI tool that highlights file-dependency reachability in Python projects. It helps you identify which files are connected, which are obsolete, and how code flows through large codebases. Useful for refactoring or understanding legacy code.

---

## Installation

### Option 1: Install via pipx (recommended)

Make sure you have [pipx](https://pypa.github.io/pipx/) installed:

```bash
# On Ubuntu/Debian:
sudo apt install pipx
pipx ensurepath

# On macOS (with Homebrew):
brew install pipx
pipx ensurepath
```

Then install `pydepin` globally:

```bash
pipx install git+https://github.com/Constadine/pydepin.git
```

This makes the `pydepin` command available globally, without modifying your system Python.

---

### Option 2: Run locally (dev mode)

Clone the repo and install into a virtual environment:

```bash
git clone https://github.com/Constadine/pydepin.git
cd pydepin
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```
## Optional: Enable LSP-powered analysis

`pydepin` offers a **heavier but more accurate** mode using static analysis via [Jedi](https://github.com/davidhalter/jedi), a Python language server backend.

This mode leverages Jedi's ability to resolve actual definitions and module paths more reliably than AST-based heuristics. It's useful when your project structure or dynamic imports make `pydepin`'s basic analysis insufficient.

### Install with LSP support

#### Option A: via pipx (recommended)

```bash
pipx install 'git+https://github.com/Constadine/pydepin.git#egg=pydepin[lsp]'
```
#### Option B: in a local dev environment
```bash
git clone https://github.com/Constadine/pydepin.git
cd pydepin
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[lsp]
```
## CLI usage
### Basic (lightweight) mode
```bash
pydepin ./myproject main.py
```
Uses only AST parsing for fast, dependency-light analysis.

### LSP (Jedi-enhanced) mode
```bash
pydepin-lsp ./myproject main.py
```

Uses Jedi to resolve actual module paths and dependencies. Slower but more precise. Ideal for large, complex, or unfamiliar codebases.

---

## Update the app

To update after making changes:

```bash
pipx reinstall pydepin
```

To uninstall:

```bash
pipx uninstall pydepin
```

