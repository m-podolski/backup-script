import datetime
import os
from pathlib import Path
import shutil
from typing import Optional, Sequence
from argparse import Namespace, ArgumentParser

parser = ArgumentParser()
parser.add_argument(
    "--dest", help="set the destination root directory. (Will be deleted if it already exists!) "
)
args: Namespace = parser.parse_args()

env_home: Optional[str] = os.environ.get("HOME")
source_root: Path
if env_home is None:
    raise Exception("Could not get your user-home")
else:
    source_root: Path = Path(env_home)

destination_root: Path
if args.dest:
    destination_root = Path(args.dest)
else:
    date: str = datetime.datetime.today().strftime("%Y-%m-%d")  # pyright: ignore
    destination_root = Path(f"/media/malte/VIRUS/Backup/{source_root.name}_{date}")

sources: Sequence[str] = (
    ".config/autokey/data/Keys",
    ".config/gh",
    ".config/JetBrains",
    ".config/pgadmin",
    ".config/Code/User/snippets",
    ".config/Code/User/keybindings.json",
    ".config/Code/User/settings.json",
    ".git-template",
    ".gitconfig",
    ".gitstatus/gitstatus.prompt.zsh",
    ".kde",
    ".local/share/color-schemes",
    ".mongodb/mongosh/mongosh_repl_history",
    ".oh-my-zsh/custom",
    ".ssh",
    ".vscode/extensions/extensions.json",
    "Desktop/Dev/Dev-Wiki",
    "Desktop/Wiki-Inhalt",
    "home.code-workspace",
    ".zshrc",
    ".zprofile",
    ".zlogin",
    ".bashrc",
    ".profile",
    ".bashrc",
    ".bash_completion",
    ".bash_history",
    ".bash_logout",
    ".psql_history",
    ".rsync-filter",
)

if destination_root.exists():
    shutil.rmtree(destination_root)

os.mkdir(destination_root)

for source in sources:
    source_relative_path: Path = Path(source)
    source_path: Path = Path(os.path.join(source_root, source))
    destination_path: Path = destination_root / source

    source_levels: tuple[str, ...] = source_relative_path.parts
    current_level: list[str] = []

    for i, level in enumerate(source_levels):
        current_level.append(level)
        destination_level: Path = destination_root / "/".join(current_level)

        dest_level_exists: bool = destination_level.exists()
        current_is_last_level: bool = (i + 1) == len(source_levels)
        source_path_is_file: bool = source_path.is_file()
        level_is_file: bool = current_is_last_level and source_path_is_file

        if not dest_level_exists and not level_is_file:
            os.mkdir(destination_level)

    if source_path.is_dir():
        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
    else:
        shutil.copy(source_path, destination_path)

    print(source)

print("Scarab has finished!")
