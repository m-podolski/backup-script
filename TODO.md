# Commit

- refactor to use ScarabRecords
  - check name-formats

## In Progress

- refactor command-initialization
  - put newest-matching onto target
  - remove location-init from argument-init
  - improve argument-init interface(s)
  - rename interactions to init
  - refactor OutputMode.AUTO into separate function
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
