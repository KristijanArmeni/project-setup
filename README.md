# project-setup

Scaffold a new Python project with `uv`, `prek`, and a data science stack.

## Usage

```bash
uvx --from git+https://github.com/KristijanArmeni/project-setup project-setup my-project
```

This will:

1. Initialize a new uv project
2. Copy pre-commit hooks (prek), `.gitignore`, `.python-version`, and `ruff.toml`
3. Create standard directories: `scripts/`, `data/`, `out/`, `tmp/`, `notebooks/`, `doc/`, `tests/`
4. Add default dependencies: `matplotlib`, `numpy`, `polars`, `dotenv`, `pytest`
5. Set author info from your git config
6. Install git hooks via `prek install`
