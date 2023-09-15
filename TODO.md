# Commit

- add separate class hierarchy for dataclass-scarab-records

## In Progress

- refactor interactions for use with auto
  - refactor interactions-uses in auto() into separate functions
  - ? change typevar

- catch EOFError from inputs

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
