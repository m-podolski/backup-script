# Scarab Backup

This is a tool to copy backups easily from the command line. It is an attempt to take most of the pain and risk out of manual backups. It is intended for use with local drives in a desktop-setup. Its main purpose is to make it easy to select and transfer data by offering different options for usage. Those are:

1. argument-configured commands,
2. simple select-menus for most missing arguments and
3. a configuration file which can be set up with any arguments under different profiles

So running your backup becomes a easy as remembering the names of your own profiles. The configuration-file also enables selective backups from certain directories which transfer only the paths you configure but keep the original directory structure (useful e.g. for quickly backing up the configuration-files of your user-home or ignoring that giant folder with images on your desktop).

## Features

- Early path-validation
- Drive-listing and -selection
- Auto-detection of backup-folders
- Easily selectable name formats (with source, timestamps, user/host)
- Profile-based YAML-config-file with optional list of selected sub-directories per source-location

## Installation

### Dependencies

- Python >= 3.10

## Usage

```conf
scarab backup
  [--help]
  [create | update]
  [--source <path>]
  [--target <path> | --media]
  [--name]

scarab backup [--help] profile <profile_name>

scarab config [--help] [put] [--force]
```

### Top-Level-Commands

| Name | Description |
| - | - |
| backup | Create or update backups |
| config | Control scarabs configuration file |

### Backup-Commands

| Name | Description |
| - | - |
| create | Create a new backup |
| update | Update an existing backup |
| profile | Use a profile from your config-file |

#### Options

Note that you can start scarab without any arguments and will be prompted for input afterwards.

| Short | Long | Description |
| - | - | - |
| -h | --help | show help message and exit |
| -s \<path> | --source \<path> | The source-path |
| -t \<path> | --target \<path> | The target-path |
| -m | --media | Select your media-directory as target |
| -n 1..6 | --name 1..6 | The name-format for your backup (see below) |

#### Arguments

| Name | Description |
| - | - |
| path | Can be relative or absolute. Variables and tilde will be expanded |
| profile_name | The name specified in your configuration-file und the "profile" key |

### Config-Commands

| Name | Description |
| - | - |
| put | Create a new example-config-file at ~/.scarab.yml (This does not override an existing config by default) |

#### Options

| Short | Long | Description |
| - | - | - |
| -h | --help | show help message and exit |
| -f | --force | Override an existing file |

### General Usage

The **create** and **update** commands can be run without any options and input-prompts or select-menus will be presented for any missing arguments.

The **profile** command will create or update automatically based on the existance of a directory with the specified name at the target location (see "*Using the Configuration File*" below). If the profile is missing required fields scarab will simply exit.

### Backup Directory Detection

Scarab will in any case look for a directory matching `[Bb]ackup[s]*` at the target location and use the first match. When running with **update** subdirectories at the target-location will be presented as a select-list.

### Override-Protection

When running with **create** scarab will check, if a directory with the specified name already exists and ask you to change the name.

### Name Formats

```txt
1. <source-dir>
2. <source-dir>_<date>
3. <source-dir>_<date-time>
4. <user>@<host>_<source-dir>
5. <user>@<host>_<source-dir>_<date>
6. <user>@<host>_<source-dir>_<date-time>

date = YYYY-MM-DD
date-time = YYYY-MM-DD-HH-MM-SS
```

### Using the configuration file

#### Load Order

While the **put**-command only uses the last location you can also move the file to one of the others.

1. /etc/scarab/scarab.yml
2. ~/.config/scarab/scarab.yml
3. ~/.scarab/config/scarab.yml
4. ~/.scarab.yml

#### Options

```yaml
scarab:
  profiles:
  - profile: MyProfile               (*)
    source: /path/source             (*)
    target: /path/target             (*)
    name: 5                          (*)
    ignore_datetime: true or false   (default false)

  - profile: MyOtherProfile
    ...
```

By default Scarab will search for an existing directory with the selected (filled-in) name-format and create it if it does not find one. If it finds an exact match, it will be used for an update. When using one of the date/date-time-formats this will result in creating a new backup if the name does not exactly match (i.e. the current date/time are different). This behaviour can be changed by setting **ignore_datetime: true**

- Options marked with **(*)** are required and will throw an error if omitted.
- **Paths** will be expanded and resolved as with **create** or **update** but relative paths should of course not be used.
- **ignore_datetime** can be used to control the updating behaviour. If **true** scarab will pick the most recent directory that matches the selected name-format without the date/date-time-part. (i.e. when the new name is **source_2023-01-01** and ignore_datetime is true, **source_2022-02-02** will be **selected and renamed** but not **source_2022-02-01**)
