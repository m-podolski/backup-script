# Scarab Backup

This is a simple BASH utility script to copy files from your machine to an external drive. It is an attempt to take most of the pain and risk out of manual backups. It is intended for personal use with local drives in a desktop-setup. Its main purpose is to add some CLI-UX to the tools involved by presenting a nice flow with menus and results displayed.

## Additional Features

- Path validation
- Drive listing and selection
- Auto-detection of backup-folders
- Precise check for available space
- Easily selectable name formats (with source, timestamps, user/host)
- Preconfigured Rsync options
- Execution of a custom script before backing up

## Dependencies

- BASH
- GNU Coreutils
- [Rsync](https://rsync.samba.org/)
- [Tree (optional)](https://ubuntu.pkgs.org/22.04/ubuntu-universe-amd64/tree_2.0.2-1_amd64.deb.html)

## Usage

Put anywhere and run `scarab-backup/scarab.sh`:

```
./scarab.sh [-c | -u <source-path>] [-s]
```
- `-c` create a new backup
- `-u` update an existing backup
- `-s` check if there is enough available space for the backup

Note that `-c` and `-u` are only shortcuts. You can start the script without them and will be prompted for the options.

### Backup Directory Detection

Scarab will in any case look for a directory matching `[Bb]ackup[s]*` at the target drive and use the first match as destination. Otherwise you can enter your own. When updating subdirectories will be presented as a select-list.

### Backup Preparation

Before the actual backup process starts the script will look for a file at the source root called `.scarabprepare.sh` and execute it. This is a good way to avoid using links when you want to backup certain files from outside your source directory but not the entire other directories. Just add some copy-instructions and you're done.

### Excluding Files

`.rsync-filter-example` gives an example for backing up selected parts of your home-directory.
All archive options  support **rsync-filter-files** by looking for a file in every directory named `.rsync-filter`. This file is fed into rsync's `--filter` option ([see Docs](https://download.samba.org/pub/rsync/rsync.1#opt--filter)). You can check out the rules for the ignorefile [here](https://download.samba.org/pub/rsync/rsync.1#FILTER_RULES) and specific information on pattern matching [here](https://download.samba.org/pub/rsync/rsync.1#PATTERN_MATCHING_RULES).

**Note that the first matching rule will always take effect!** Besides the most important differences to the .gitignore-syntax are that rules for exclusions from transfer are prefixed with `- `(minus space) while inclusions are prefixed `+ `(plus space) and that rules to **include certain files from otherwise excluded locations** have to come **before** the respective exclude-rule.

#### Examples

- `- *.o` would exclude all filenames ending with .o
- `- /foo` would exclude a file (or directory) named foo in the transfer-root directory
- `- foo/` would exclude any directory named foo
- `- foo/*/bar` would exclude any file/dir named bar which is at two levels below a directory named foo (if foo is in the transfer)
- `- /foo/**/bar` would exclude any file/dir named bar that was two or more levels below a top-level directory named foo (note that /foo/bar is not excluded by this)
- `+ */` `+ *.c` `- *` would include all directories and .c source files but nothing else
- `+ foo/` `+ foo/bar.c` `- *` would include only the foo directory and foo/bar.c (the foo directory must be explicitly included or it would be excluded by the "- *")

### Archive Configurations

All options are configured with extensive logging and progress display.

- **Scarab Archive:** Non-existing files at the source will be deleted from an existing backup. Works recursively. Keeps symlinks, permissions, modification-times, access times, groups, owner, device properties and special files. Files can be excluded with `.rsync-filter`.
- **Scarab Archive with hardlinks:** Also keeps hardlinks. May be slower
- **Custom:** Enter any flags as a string which will be passed directly to the `rsync`-command.
- **(Dry Run) "Option"** All options can be started as a dry run with extensive logging.

All options delete files from the destination that are not present at the source as well as files which are excluded (if a `.rsync-filter` is used).

