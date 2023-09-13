# Commit

- refactor newest-backup-matching onto target

## In Progress

- refactor command-initialization
  - remove location-init from argument-init
  - improve argument-init interface(s)

- refactor interactions-uses in auto() into separate functions
  - rename interactions to init
  - ? change typevar

## Backlog

- add copy-operation
  - add basic backup-strategy
  - add logging
  - add display of data transferred (with path.lstat().st_size)
  - add source-tree-generation for selective backup
  - add incremental backup-strategy

- cronjob-doc

- configure ci/cd and publish

> 0.6.0
