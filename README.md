# Scarab Backup

This is a simple BASH utility script to copy files from your machine to an external drive. It uses **rsync** for the copy operation and common GNU Coreutils. It is intended for personal use with local drives in a desktop-setup and does not use rsync's networking-capabilities. Its main purpose is to add some CLI-UX to the tools involved by presenting a thought-through flow with menus and results displayed.

The features that it adds are the following:

- Path validation
- Drive listing and selection
- Precise check for available space
- Easily selectable name formats (custom/system names/ISO-stamps)

## Usage

Put anywhere and run `scarab-backup/scarab.sh`:

```
./scarab.sh [-c | -u] <source-path>
```
-c will create a new backup
-u will update an existing backup

### Update Mode
The target path must point to an existing directory. Otherwise Scarab cannot calculate the available space correctly and you might encounter an error while copying!
