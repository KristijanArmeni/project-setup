import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATES = ["prek.toml", ".gitignore", ".python-version", "ruff.toml"]

DIRS = ["scripts", "data", "out", "tmp", "notebooks", "doc", "tests"]

DEPS = ["matplotlib", "numpy", "polars", "dotenv", "pytest"]


def _run(cmd: list[str], cwd: Path | None = None) -> None:
    cwd_str = f" (cwd: {cwd})" if cwd else ""
    print(f"  $ {' '.join(cmd)}{cwd_str}")
    subprocess.run(cmd, cwd=cwd, check=True)


def get_git_config(key: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "config", f"user.{key}"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def init_project(name: str | None) -> Path:
    if name:
        _run(["uv", "init", "--package", name])
        return Path(name)
    else:
        _run(["uv", "init", "--package"])
        return Path.cwd()


def copy_templates(project_dir: Path) -> None:
    template_dir = Path(__file__).parent / "templates"
    for template in TEMPLATES:
        src = template_dir / template
        dst = project_dir / template
        shutil.copy2(src, dst)


def create_dirs(project_dir: Path) -> None:
    for d in DIRS:
        (project_dir / d).mkdir(exist_ok=True)


def add_deps(project_dir: Path) -> None:
    _run(["uv", "add"] + DEPS, cwd=project_dir)


def set_author(project_dir: Path) -> None:
    pyproject = project_dir / "pyproject.toml"
    text = pyproject.read_text()

    author_name = get_git_config("name")
    author_email = get_git_config("email")

    if not (author_name or author_email):
        return

    parts = []
    if author_name:
        parts.append(f'name = "{author_name}"')
    if author_email:
        parts.append(f'email = "{author_email}"')
    authors_block = f'authors = [\n    {{ {", ".join(parts)} }}\n]\n'

    import re
    if re.search(r'authors\s*=', text):
        text = re.sub(r'authors\s*=\s*\[.*?\]', authors_block.rstrip('\n'), text, flags=re.DOTALL)
    else:
        text = re.sub(r'(readme = ".*?"\n)', r'\1' + authors_block, text)

    pyproject.write_text(text)


def install_hooks(project_dir: Path) -> None:
    _run(["prek", "install"], cwd=project_dir)


def _build_preview(args: argparse.Namespace) -> list[tuple[str, list[str]]]:
    project_name = args.name
    actions: list[tuple[str, list[str]]] = []

    init_cmd = ["uv", "init", "--package"]
    if project_name:
        init_cmd.append(project_name)
    actions.append(("Init project", [f"$ {' '.join(init_cmd)}"]))

    actions.append(("Copy templates", [f"  - {t}" for t in TEMPLATES]))

    actions.append(("Create directories", [f"  - {d}" for d in DIRS]))

    deps_cmd = ["uv", "add"] + DEPS
    actions.append(("Add dependencies", [f"$ {' '.join(deps_cmd)}"]))

    author_name = get_git_config("name")
    author_email = get_git_config("email")
    if author_name or author_email:
        parts = []
        if author_name:
            parts.append(f'name = "{author_name}"')
        if author_email:
            parts.append(f'email = "{author_email}"')
        actions.append(("Set author (modify pyproject.toml)", [f"  - authors = [{{ {', '.join(parts)} }}]"]))

    prek_cmd = ["prek", "install"]
    actions.append(("Install hooks", [f"$ {' '.join(prek_cmd)}"]))

    return actions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a new Python project with uv, prek, and a data science stack."
    )
    parser.add_argument("name", nargs="?", default=None, help="Project name (defaults to current directory)")
    args = parser.parse_args()

    actions = _build_preview(args)

    print("The following actions will be performed:")
    print()
    for desc, items in actions:
        print(f"  {desc}:")
        for item in items:
            print(f"    {item}")
    print()

    confirm = input("Proceed? (y/n): ")
    if confirm.lower() != "y":
        print("Aborted.")
        sys.exit(0)

    project_dir = init_project(args.name)
    copy_templates(project_dir)
    create_dirs(project_dir)
    add_deps(project_dir)
    set_author(project_dir)
    install_hooks(project_dir)

    print(f"\nProject '{project_dir.name}' scaffolded successfully.")
