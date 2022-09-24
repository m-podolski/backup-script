#! /bin/zsh

# 2022 by Malte Podolski
# malte.podolski AT web DOT de
# github.com/m-podolski/scarab-backup

clear
cat ./welcome-art.txt

sourcepath=$1

# Check if backup-directory has been set as an argument
#   If not, prompt to enter

if [ $# -gt 0 ]; then
  echo "arg given"
else
  echo "arg not given"
  # printf "Enter your source directory (absolute path): "
  # read sourcepath
  # sourcepath=$1
fi

# Check if source is a valid directory
#   If not, prompt to enter again

if [[ -d $sourcepath ]]; then
  echo "ok"
else
  echo "not ok"
  # printf "Enter your source directory (absolute path): "
  # read name
fi

# Get list of drives and print it
# Set drive selection
#   Check free space at target location
#     Print message and sizes of source and target
#     Else, ask if user wants to proceed or quit
#       If yes, go back to drive selection
#       Else exit
# Set backup-directory name format
#   ("<user>@<host>:<directory>")
#   ("<user>@<host>:<directory>_<iso-date>")
#   ("<user>@<host>:<directory>_<iso-date-time>")
#     Check if it already exists
#       If yes, print warning and ask if to proceed
#         If yes, overwrite
#         Else, remove current option from list and prompt to choose option again
# Start copying and show progress
printf "Scarab starts rolling...\n"
# Notify when finished and print copied size again
# Make executable by putting on path
