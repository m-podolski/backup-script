# Commit

- add error for backup-dir identical with source

## In Progress

- refactor to handle controller-logic outside of Location
  - handle None and empty string input before initializing locations
  - introduce special-case-path-object
  - narrow to source/target-types

## Backlog

- add available-space-check
  - print target-stats

- update README

- add copy-operation

- add option to target preconfigured profiles
  - add command for generating local config-file

- add tree-diff for incremental backup

- ? add rsync-operation
  - add archive-mode-config

- configure ci/cd

> 0.6.0
