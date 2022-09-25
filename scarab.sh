#! /bin/bash

# 2022 by Malte Podolski
# malte.podolski AT web DOT de
# github.com/m-podolski/scarab-backup

clear
# cat ./welcome-art.txt

style_ok='\e[0;32m\e[1m'
style_warn='\e[0;33m\e[1mWarning: '
style_error='\e[0;91m\e[1mError: '
style_menu='\e[0;34m\e[1m'
style_heading='\e[1m'
style_reset='\e[0m'

select_mode() {
  clear
  PS3="$(echo -en ${style_reset})Select the backup-mode (number): "
  options=('Create new' 'Update existing')

  echo -en "${style_menu}"

  select answer in "${options[@]}"; do
    case $answer in
    ${options[0]})
      create_flag='true'
      break
      ;;
    ${options[1]})
      update_flag='true'
      break
      ;;
    esac
  done
}

read_sourcepath() {
  echo -en ${style_menu}
  read -p "${style_menu}Enter your source directory: ${style_reset}" sourcepath
  echo -en ${style_reset}
  sourcepath=${sourcepath/#\~/$HOME}
  validate_sourcepath
}

# Check if source is a valid directory
#   If not, prompt to enter again

validate_sourcepath() {
  if [ ! -d $sourcepath ]; then
    echo -e "${style_error}Your source path is not a valid directory!${style_reset}"
    read_sourcepath
  fi
}

# If a single argument is given, this is the source path
#   Else, check for source/flags and values, prompt to enter missing ones

sourcepath=''
targetpath=''
create_flag='false'
update_flag='false'

check_arguments() {
  case $# in
  0)
    read_sourcepath
    select_mode
    ;;
  1)
    sourcepath=$1
    validate_sourcepath
    select_mode
    ;;
  *)
    while getopts 'c:u:' flag; do
      case "${flag}" in
      c)
        create_flag='true'
        sourcepath="${OPTARG}"
        ;;
      u)
        update_flag='true'
        sourcepath="${OPTARG}"
        ;;
      *)
        exit 1
        ;;
      esac
    done
    ;;
  esac
}

# check_arguments

print_target_stats() {
  targetpath=$1
  available=$2

  if [ $available == 'true' ]; then
    echo -e "\n${style_ok}The target location has enough space available:${style_reset}"
  else
    echo -e "\n${style_warn}The target location has not enough space available:${style_reset}"
  fi

  list_els_displayed=${#target_stats_keys[@]}
  if [ $create_flag == 'true' ]; then
    list_els_displayed=$((${#target_stats_keys[@]} - 1)) # Hide "Existing Target"
  fi

  for ((i = 0; i < $list_els_displayed; ++i)); do
    printf "%-16s  %-16d\n" "${target_stats_keys[$i]}" "${target_stats_values[$i]}"
  done

  echo -en "\n${style_heading}"
  df --human-readable --output=target,size,used,avail,pcent $targetpath | head -1
  echo -en "${style_reset}"
  df --human-readable --output=target,size,used,avail,pcent $targetpath | tail --lines=1
  echo
}

check_free_target_space() {
  targetpath=$1
  target_stats_values=$2
  block_size=512

  size_source=$(du --block-size=$block_size --summarize $sourcepath | awk '{print $1}')
  avail_target=$(df --block-size=$block_size --output=avail $targetpath | tail --lines=1 | awk '{print $1}')

  if [ $create_flag == 'true' ]; then
    free_space=$(($avail_target - $size_source))
  fi

  if [ $update_flag == 'true' ]; then
    size_existing=$(du --block-size=$block_size --summarize $targetpath | awk '{print $1}')
    free_space=$(($avail_target + $size_existing - $size_source))
  fi

  target_stats_values[0]=$size_source
  target_stats_values[1]=$avail_target
  target_stats_values[2]=$size_existing

  if [ $free_space -gt 0 ]; then
    backup_possible='true'
  else
    backup_possible='false'
  fi
}

get_targetpath() {
  if [ $create_flag == 'true' ]; then
    hint='directory will be created there'
  fi
  if [ $update_flag == 'true' ]; then
    hint='directory will be replaced/updated'
  fi
  echo -en ${style_menu}
  read -p "Enter target location on drive ($hint): " targetpath_on_drive
  echo -en ${style_reset}

  targetpath="$drivepath/$targetpath_on_drive"
  echo -e "\nTargetpath is $targetpath"

  if [[ $update_flag == 'true' && ! -d $targetpath ]]; then
    echo -e "${style_error}Your target path is not a valid directory!${style_reset}\n"
    get_targetpath
  fi
}

reselect_drive() {
  PS3="$(echo -en ${style_reset})Select an answer (number): "
  options=("Select another drive" "Exit")

  echo -en "${style_menu}"

  select answer in "${options[@]}"; do
    case $answer in
    ${options[0]}) select_target ;;
    ${options[1]}) exit ;;
    esac
  done
}

# Get drive selection
# Print top-level directory of selected drive
# Check mode

select_target() {
  clear
  PS3="$(echo -en ${style_reset})Select the target drive (number): "
  add_options=('Scan drives again')
  options=($(ls /media/$USER) "${add_options[@]}")

  echo -en "${style_menu}"

  select option in "${options[@]}"; do
    clear

    case $option in
    ${add_options[0]})
      select_target
      break
      ;;
    *)
      drivepath="/media/$USER/$option"

      echo -e "${style_heading}This is the root directory of your target:${style_reset}"
      ls -l --all --color=auto $drivepath
      echo

      # If creating
      #   Check if there is enough free space at target location and print stats
      #     If yes, prompt to enter target location on drive (directory will be created there)
      #       Validate directory
      #         If valid, proceed
      #         Else, prompt to enter again
      #     Else, ask if user wants to select another drive or quit
      #       If yes, go back to drive selection
      #       Else exit

      create_flag='true'
      update_flag='false'

      target_stats_keys=('Source' 'Free on Drive' 'Existing Target')
      target_stats_values=(0 0 0)

      backup_possible='null'

      if [ $create_flag == 'true' ]; then
        check_free_target_space $drivepath $target_stats_values
        print_target_stats $drivepath $backup_possible

        if [ $backup_possible == 'true' ]; then
          get_targetpath
        else
          reselect_drive
        fi
      fi

      # If updating
      #   Prompt to enter target location on drive (must point to existing backup directory)
      #     Validate directory
      #       If valid
      #         Check if there is enough free space (difference existing/source) and print stats
      #           If yes, proceed
      #           Else, print result and ask if user wants to select another drive or quit
      #            If drive, go back to drive selection
      #            Else exit
      #       Else, prompt to enter again

      if [ $update_flag == 'true' ]; then
        get_targetpath
        check_free_target_space $targetpath
        print_target_stats $targetpath $backup_possible

        if [ $backup_possible == 'false' ]; then
          reselect_drive
        fi
      fi
      break
      ;;
    esac
  done
}

select_target

# Set backup-directory name format
#   (same as source)
#   ("<user>@<host>:<directory>")
#   ("<user>@<host>:<directory>_<iso-date>")
#   ("<user>@<host>:<directory>_<iso-date-time>")
#     Check if it already exists
#       If yes, print warning and ask if to proceed
#         If yes, overwrite
#         Else, remove current option from list and prompt to choose option again

# Select transfer/compression options
# Start copying and show progress
#   echo 'Scarab starts rolling...'
# Notify when finished and print copied size again
