# Commit

## In Progress

- refactor to use service class

## Backlog

- add destination-path (arg and selection)
  - get /media/USER when --media is set (ignore --dest)
  - print destination contents
  - add rescan-option
  - add backup-folder-detection

- add mode-selection (or raise ex)

- add destination-name-selection
  - handle destination already exists when in create-mode

- add copy-operation

- add available-space-check
  - print destination-stats

- add rsync-operation
  - add archive-mode-selection

- add option to target preconfigured profiles
  - add command for generating local config-file
  - generalize to also target arbitrary os locations

- ? replace jinja-templates with custom colored output

> 0.6.0
