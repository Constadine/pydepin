# pydepin

`pydepin` is a CLI tool that highlights file-dependency reachability in Python projects. It helps you identify which files are connected, which are obsolete, and how code flows through large codebases. Useful for refactoring or understanding legacy code.

---

## Installation

`pydepin` can be installed and managed with several tools. Choose your preferred approach:

### Option 1: Install via uv (recommended)

[`uv`](https://docs.astral.sh/uv/) is an all-in-one, ultra-fast Python package and project manager. It replaces pip, pipx, poetry, virtualenv, and more, with 10–100× faster installs and a unified lockfile.

1. **Install uv** (macOS/Linux):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   On Windows, follow the [Windows installer instructions](https://docs.astral.sh/uv/installation#windows).

2. **Install pydepin**:

   ```bash
   uv tool install git+https://github.com/Constadine/pydepin.git
   ```

The `uv tool install` command sets up `pydepin` in an isolated environment, similar to pipx but powered by uv’s global cache and workspace support.

### Option 2: Install via pipx

If you prefer the traditional pipx approach:

```bash
pipx install git+https://github.com/Constadine/pydepin.git
```

### Option 3: Run locally (dev mode)

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

## Optional: Enable LSP-powered analysis

`pydepin` offers a **heavier but more accurate** mode using static analysis via [Jedi](https://github.com/davidhalter/jedi), a Python language server backend. This mode resolves actual definitions and module paths more reliably than AST-based heuristics—useful for large or dynamic codebases.

### Install with LSP support

#### Via uv:

```bash
uv tool install 'git+https://github.com/Constadine/pydepin.git#egg=pydepin[lsp]'
```

#### Via pipx:

```bash
pipx install 'git+https://github.com/Constadine/pydepin.git#egg=pydepin[lsp]'
```

#### Local dev (virtualenv):

```bash
pip install -e .[lsp]
```

---

## CLI Usage

### Basic (lightweight) mode

```bash
pydepin ./myproject main.py
```

Uses only AST parsing for fast, dependency-light analysis.

### LSP (Jedi-enhanced) mode

```bash
pydepin-lsp ./myproject main.py
```

Uses Jedi to resolve actual module paths and dependencies. Slower but more precise.

#### Common flags

* `--downstream` / `-d`: show only files reachable *from* the starts.
* `--upstream`   / `-u`: show only files that reach *into* the starts.
* `--only-highlighted` / `-o`: hide unrelated files.
* `--show-ignored`: include boilerplate/ignored files in the graph.

---

## Updating & Uninstalling

* **Update**:

  * With uv: `uv tool update pydepin`
  * With pipx: `pipx reinstall pydepin`
  * In dev: re-run `pip install -e .`

* **Uninstall**:

  * With uv: `uv tool uninstall pydepin`
  * With pipx: `pipx uninstall pydepin`

---

## License

MIT © Konstantinos Papagiannopoulos

