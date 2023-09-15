# Commit

- refactor to use NameFormats instead of init.select_backup_name

## In Progress

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
