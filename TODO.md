# Commit

- improve records

- update README for auto-command

## In Progress

- refactor interactions-uses in auto() into separate functions
  - rename interactions to init
  - rename controller->s
  - catch EOFError form inputs
  - ? change typevar

## Backlog

- add copy-operation
  - add basic backup-strategy
  - add logging
  - add display of data transferred (with path.lstat().st_size)
  - add source-tree-generation for selective backup
  - add incremental backup-strategy

- configure ci/cd and publish
  - installation docs
    - cronjob-doc

> 0.6.0
