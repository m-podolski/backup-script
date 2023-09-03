import shutil
from pathlib import Path

root: Path = Path("/home/malte/dev/test")
if root.exists():
    shutil.rmtree(root)
root.mkdir()

# target inside source + create

source_path: Path = Path("/home/malte/dev/test/source")
source_path.mkdir()
target_path: Path = Path("/home/malte/dev/test/source/target")
target_path.mkdir()
other1_path: Path = Path("/home/malte/dev/test/source/other1")
other1_path.mkdir()
backup_path: Path = Path("/home/malte/dev/test/source/target/backup")
backup_path.mkdir()
other2_path: Path = Path("/home/malte/dev/test/source/target/other2")
other2_path.mkdir()

# shutil.copytree(source_path, backup_path, dirs_exist_ok=True)  # -> RecursionError
# shutil.copytree(
#     source_path, backup_path, ignore=shutil.ignore_patterns("backup")
# )  # -> FileExistsError
shutil.copytree(
    source_path,
    backup_path,
    ignore=shutil.ignore_patterns("backup"),
    dirs_exist_ok=True,
)

# source inside target + update

# source_path: Path = Path("/home/malte/dev/test/target/backup/source")
# target_path: Path = Path("/home/malte/dev/test/target")

# backup_path: Path = target_path / "backup"

# shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
