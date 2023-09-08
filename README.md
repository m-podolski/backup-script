# Scarab Backup

This is a tool to copy backups easily from the command line. It is an attempt to take most of the pain and risk out of manual backups. It is intended for use with local drives in a desktop-setup. Its main purpose is to make it easy to select and transfer data by offering different options for usage. Those are (1) argument-configured commands, (2) simple select-menus for any arguments missing and (3) a configuration file which can be set up with any arguments under different profiles so running your backup becomes a easy as remembering the names of your own profiles. This also enables selective backups from certain directories which transfer only the paths you configure but keep the original directory structure (useful e.g. for quickly backing up the configuration-files of your user-home).

## Features

- Early path-validation
- Drive-listing and -selection
- Auto-detection of backup-folders
- Easily selectable name formats (with source, timestamps, user/host)
- Profile-based YAML-config-file with optional list of selected sub-directories per source-location

## Dependencies

- Python >= 3.10

## Installation

## Usage

```txt
scarab backup [--help] [--source <path>] [--target <path> | --media] [--create | --update]  [--name]
```

### Options

| Short | Long | Description |
| - | - | - |
| -h | --help | show help message and exit |
| -s SOURCE | --source SOURCE | The source-path |
| -t TARGET | --target TARGET | The target-path |
| -m | --media | Select your media-directory as target |
| -c | --create | Create a new backup |
| -u | --update | Update an existing backup |
| -n 1..6 | --name 1..6 | The name-format for your backup |

### Name Formats

```txt
1. <source-dir>
2. <source-dir>_<date>
3. <source-dir>_<date-time>
4. <user>@<host>_<source-dir>
5. <user>@<host>_<source-dir>_<date>
6. <user>@<host>_<source-dir>_<date-time>
```

Note that you can start the script without any arguments and will be prompted for input afterwards.

### Backup Directory Detection

Scarab will in any case look for a directory matching `[Bb]ackup[s]*` at the target location and use the first match. When updating subdirectories at the target-location will be presented as a select-list.

### Using the configuration file
