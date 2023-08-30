# Changelog


## 0.5.0 (2022-11-19)

### Added

- flag for disabling backup-folder detection

## 0.4.0 (2022-10-29)

### Changed

- made free drive space check optional

### Fixed

- rename target only when rsync exited successfully
- enable rsync-options to be split
- prevent renaming when directory name stays the same
- disk space statistics are not hidden by clearing the screen anymore

## 0.3.2 (2022-10-19)

### Added

- optional "tree"-support
- backup-folder-detection at target
- accurate timestamps which are set at the very end

### Fixed

- path construction issues and cleaned up code with ShellCheck
- fixed some style issues according to the google-shell-styleguide

## 0.3.1

### Fixed

- with shellcheck

## 0.3.0

### Added

- backup folder auto-detection

## 0.2.0

### Added

- optional tree support

### Fixed

- script params

## 0.1.0

First functional version
