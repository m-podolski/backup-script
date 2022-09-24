# Scarab Backup

This is a simple BASH/ZSH utility script to copy files from your machine to an external drive. It uses **rsync** for the copy operation, so check if you have that installed. It is intended for personal use with local drives in a desktop-setup and does not use rsync's networking-capabilities.

The features that it adds are the following:

- source path validation
- drive listing and selection
- check for available space
- easily settable name format (plain, with date or with date and time)
- check for already existing folders/overwriting

## Usage

Put anywhere and run `scarab-backup/main.sh`
