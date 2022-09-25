#! /bin/bash

# 2022 by Malte Podolski
# malte.podolski AT web DOT de
# github.com/m-podolski/scarab-backup

# set -x

clear
cat ./welcome-art.txt

c_error="\e[0;91m\e[1mError: "
c_reset="\e[0m"

sourcepath=$1

# Check if backup-directory has been set as an argument
#   If not, prompt to enter
read_sourcepath() {
  read -p "Enter your source directory: " sourcepath
  sourcepath=${sourcepath/#\~/$HOME}
  validate_sourcepath
}

# Check if source is a valid directory
#   If not, prompt to enter again
validate_sourcepath() {
  if [ ! -d $sourcepath ]; then
    echo -e "${c_error}Your source path is not a valid directory!${c_reset}"
    read_sourcepath
  fi
}

if [ ! $# -gt 0 ]; then
  read_sourcepath
fi
validate_sourcepath

# Get list of drives and print it
# Set drive selection
#   Check if there is enough free space at target location
#     If yes,
#       print message and sizes of source and target
#       print top-level directory of selected drive
#     Else, ask if user wants to select another drive or quit
#       If yes, go back to drive selection
#       Else exit
# Set target at drive
#   Check if target is a valid directory
#     If not, prompt to enter again
# Set backup-directory name format
#   (same as source)
#   ("<user>@<host>:<directory>")
#   ("<user>@<host>:<directory>_<iso-date>")
#   ("<user>@<host>:<directory>_<iso-date-time>")
#     Check if it already exists
#       If yes, print warning and ask if to proceed
#         If yes, overwrite
#         Else, remove current option from list and prompt to choose option again
# Start copying and show progress
# printf "Scarab starts rolling...\n"
# Notify when finished and print copied size again
# Make executable by putting on path
