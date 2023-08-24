# Commit

- refactor to use distinct location-types

## In Progress

- add destination-path (arg and selection)
  - get /media/USER when --media is set (ignore --dest)
  - generalize to also target arbitrary os locations
  - print destination contents
  - add rescan-option
  - add backup-folder-detection

## Backlog

- add mode-selection (or raise ex)

- add destination-name-selection
  - handle destination already exists when in create-mode

- add copy-operation

- add available-space-check
  - print destination-stats

- add option to target preconfigured profiles
  - add command for generating local config-file

- add tree-diff for incremental backup

- ? add rsync-operation
  - add archive-mode-selection

- configure ci and publish

> 0.6.0
