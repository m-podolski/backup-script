import datetime
import os
import shutil
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Optional, Sequence

parser = ArgumentParser()
parser.add_argument(
    "--target", help="set the target root directory. (Will be deleted if it already exists!) "
)
args: Namespace = parser.parse_args()

env_home: Optional[str] = os.environ.get("HOME")
source_root: Path
if env_home is None:
    raise Exception("Could not get your user-home")
else:
    source_root: Path = Path(env_home)

target_root: Path
if args.target:
    target_root = Path(args.target)
else:
    date: str = datetime.datetime.today().strftime("%Y-%m-%d")  # pyright: ignore
    target_root = Path(f"/media/malte/VIRUS/Backup/{source_root.name}_{date}")

sources: Sequence[str] = (
    ".angular-config.json",
    ".bash_completion",
    ".bash_history",
    ".bash_logout",
    ".bashrc",
    ".config/autokey/data/Keys",
    ".config/Code/User/keybindings.json",
    ".config/Code/User/settings.json",
    ".config/Code/User/snippets",
    ".config/gh",
    ".config/JetBrains",
    ".config/pgadmin",
    ".git-template",
    ".gitconfig",
    ".gitstatus/gitstatus.prompt.zsh",
    ".kde",
    ".local/share/color-schemes",
    ".mongodb/mongosh/mongosh_repl_history",
    ".oh-my-zsh/custom",
    ".profile",
    ".psql_history",
    ".rsync-filter",
    ".ssh",
    ".vscode/extensions/extensions.json",
    ".zlogin",
    ".zprofile",
    ".zshrc",
    ".zshrc.zni",
    "Desktop/Büro",
    "Desktop/Dev",
    "Desktop/Kunst",
    "Desktop/Medien",
    "Desktop/Musik",
    "Desktop/Wiki-Inhalt",
    "Downloads",
    "home.code-workspace",
)

if target_root.exists():
    shutil.rmtree(target_root)

os.mkdir(target_root)

for source in sources:
    source_relative_path: Path = Path(source)
    source_path: Path = Path(os.path.join(source_root, source))
    target_path: Path = target_root / source

    source_levels: tuple[str, ...] = source_relative_path.parts
    current_level: list[str] = []

    for i, level in enumerate(source_levels):
        current_level.append(level)
        target_level: Path = target_root / "/".join(current_level)

        target_level_exists: bool = target_level.exists()
        current_is_last_level: bool = (i + 1) == len(source_levels)
        source_path_is_file: bool = source_path.is_file()
        level_is_file: bool = current_is_last_level and source_path_is_file

        if not target_level_exists and not level_is_file:
            os.mkdir(target_level)

    if source_path.is_dir():
        shutil.copytree(source_path, target_path, dirs_exist_ok=True)
    else:
        shutil.copy(source_path, target_path)

    print(source)

print("Scarab has finished!")
