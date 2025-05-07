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

Then run with:

```bash
pydepin path/to/project entry.py
```

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

