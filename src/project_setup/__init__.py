import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

TEMPLATES = ["prek.toml", ".gitignore", ".python-version", "ruff.toml"]

DIRS = ["scripts", "data", "out", "tmp", "notebooks", "doc", "tests"]

DEPS = ["matplotlib", "numpy", "polars", "dotenv", "pytest"]


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
        subprocess.run(["uv", "init", "--package", name], check=True)
        return Path(name)
    else:
        subprocess.run(["uv", "init", "--package"], check=True)
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
    subprocess.run(
        ["uv", "add"] + DEPS,
        cwd=project_dir, check=True,
    )


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
    subprocess.run(["prek", "install"], cwd=project_dir, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a new Python project with uv, prek, and a data science stack."
    )
    parser.add_argument("name", nargs="?", default=None, help="Project name (defaults to current directory)")
    args = parser.parse_args()

    project_dir = init_project(args.name)
    copy_templates(project_dir)
    create_dirs(project_dir)
    add_deps(project_dir)
    set_author(project_dir)
    install_hooks(project_dir)

    print(f"\nProject '{project_dir.name}' scaffolded successfully.")
