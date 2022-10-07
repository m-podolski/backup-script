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

source_path=''
target_path=''
create_flag='false'
update_flag='false'

select_mode() {
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
  echo
}

read_source_path() {
  echo -en "${style_menu}"
  read -p "Enter your source directory: " source_path
  echo -en "${style_reset}\n"

  source_path=${source_path/#\~/$HOME}
  validate_source_path
}

validate_source_path() {
  if [ ! -d $source_path ]; then
    echo -e "${style_error}Your source path is not a valid directory!${style_reset}\n"
    read_source_path
  fi
}

# If a single argument is given, this is the source path
# Else, check for source/flags and values
#   Prompt to enter any missing ones
# Check if source is a valid directory
#   If not, prompt to enter again

check_arguments() {
  case $# in
  0)
    read_source_path
    select_mode
    ;;
  1)
    source_path=$1
    validate_source_path
    select_mode
    ;;
  *)
    while getopts 'c:u:' flag; do
      case "${flag}" in
      c)
        create_flag='true'
        source_path="${OPTARG}"
        ;;
      u)
        update_flag='true'
        source_path="${OPTARG}"
        ;;
      *)
        exit 1
        ;;
      esac
    done
    ;;
  esac
}

check_arguments

get_target_path() {
  if [ $create_flag == 'true' ]; then
    echo -en "\n${style_heading}Your are in Create-Mode\n${style_reset}The backup will be created under the selected directory. Press RETURN for the root directory."
  fi
  if [ $update_flag == 'true' ]; then
    echo -en "\n${style_heading}Your are in Update-Mode\n${style_reset}The selected directory will be replaced/updated"
  fi
  echo -en "\n${style_menu}"
  read -p "Enter target location on drive: " path_at_target
  echo -en ${style_reset}

  target_path="$drivepath/$path_at_target"
  echo -e "\nTargetpath is $target_path"

  if [[ $update_flag == 'true' && ! -d $target_path ]]; then
    echo -e "${style_error}Your target path is not a valid directory!${style_reset}\n"
    get_target_path
  fi
}

check_free_target_space() {
  target_path=$1
  target_stats_values=$2
  block_size=512

  size_source=$(du --block-size=$block_size --summarize $source_path | awk '{print $1}')
  avail_target=$(df --block-size=$block_size --output=avail $target_path | tail --lines=1 | awk '{print $1}')

  if [ $create_flag == 'true' ]; then
    free_space=$(($avail_target - $size_source))
  fi

  if [ $update_flag == 'true' ]; then
    size_existing=$(du --block-size=$block_size --summarize $target_path | awk '{print $1}')
    free_space=$(($avail_target + $size_existing - $size_source))
  fi

  target_stats_values[0]=$size_source
  target_stats_values[1]=$avail_target
  target_stats_values[2]=$size_existing
  target_stats_values[3]=$free_space

  if [ $free_space -gt 0 ]; then
    backup_possible='true'
  else
    backup_possible='false'
  fi
}

print_target_stats() {
  target_path=$1
  available=$2

  if [ $available == 'true' ]; then
    echo -e "\n${style_ok}The target location has enough space available:${style_reset}"
  else
    echo -e "\n${style_warn}The target location has not enough space available:${style_reset}"
  fi

  list_els_displayed=${#target_stats_keys[@]}
  if [ $create_flag == 'true' ]; then
    list_els_displayed=$((${#target_stats_keys[@]} - 2))
  fi

  for ((i = 0; i < $list_els_displayed; ++i)); do
    printf "%-16s  %-16d\n" "${target_stats_keys[$i]}" "${target_stats_values[$i]}"
  done

  echo -en "\n${style_heading}"
  df --human-readable --output=target,size,used,avail,pcent $target_path | head -1
  echo -en "${style_reset}"
  df --human-readable --output=target,size,used,avail,pcent $target_path | tail --lines=1
}

reselect_drive() {
  PS3="$(echo -en ${style_reset})Select an answer (number): "
  options=('Select another drive' 'Exit')
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
  PS3="$(echo -en ${style_reset})Select the target drive (number): "
  add_options=('Scan drives again')
  options=($(ls /media/$USER) "${add_options[@]}")
  echo -en "${style_menu}"

  select option in "${options[@]}"; do
    case $option in
    ${add_options[0]})
      echo
      select_target
      break
      ;;
    *)
      drivepath="/media/$USER/$option"

      clear
      echo -e "${style_heading}This is the root directory of your target:${style_reset}"
      ls -l --all --color=auto $drivepath

      # If creating
      #   Check if there is enough free space at target location and print stats
      #     If yes, prompt to enter target location on drive (directory will be created there)
      #       Validate directory
      #         If valid, proceed
      #         Else, prompt to enter again
      #     Else, ask if user wants to select another drive or quit
      #       If yes, go back to drive selection
      #       Else exit

      target_stats_keys=('Source' 'Free on Drive' 'Existing Target' 'Existing Diff')
      target_stats_values=(0 0 0 0)

      backup_possible=''

      if [ $create_flag == 'true' ]; then
        check_free_target_space $drivepath $target_stats_values
        print_target_stats $drivepath $backup_possible

        if [ $backup_possible == 'true' ]; then
          get_target_path
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
        get_target_path
        check_free_target_space $target_path
        print_target_stats $target_path $backup_possible

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
#   Check mode and if dir already exists
#     If creating and dir exists
#       Prompt to change format, rescan, replace or exit
#     If creating and dir exists not
#       Proceed
#     If updating
#       Proceed
#     ("If updating and dir exists not" cannot happen; already validated path)

handle_create_target_conflict() {
  if [[ $create_flag == 'true' && -d "$target_path/$target_name" ]]; then
    if [ $has_target_conflict == 'false' ]; then
      echo -e "\n${style_warn}A directory with the selected name already exists!${style_reset}\nYou can first change the name of the existing directory manually and then use the 'Rescan' option to proceed with your current settings\n"
    fi

    PS3="$(echo -en ${style_reset})Select an answer (number): "
    options=('Rescan' 'Change name format' 'Replace (Switch to Update-Mode)' 'Exit')
    echo -en "${style_menu}"

    select answer in "${options[@]}"; do
      case $answer in
      ${options[0]})
        if [ -d "$target_path/$target_name" ]; then
          echo -en "\n${style_error}Rescan still found directory of the same name.${style_reset}\n"
          has_target_conflict='true'
          handle_create_target_conflict
        else
          echo -e "\n${style_ok}Directory conflict has been resolved. Proceeding...${style_reset}\n"
        fi
        ;;
      ${options[1]}) select_target_name ;;
      ${options[2]})
        create_flag='false'
        update_flag='true'
        echo -e "\n${style_ok}You have switched into update-mode. The target directory will be replaced.${style_reset}\n"
        ;;
      ${options[3]}) exit ;;
      esac
      break
    done
  fi
}

select_target_name() {
  clear
  echo -e '<source-dir>: The original directory name\n<date>: "YYYY-MM-DD"\n<date-time>: "YYYY-MM-DD_HH:MM:SS"\n'

  PS3="$(echo -en ${style_reset})Select a name format for the backup directory (number): "
  options=(
    '<source-dir>'
    '<source-dir>_<date>'
    '<source-dir>_<date-time>'
    '<user>@<host>:<source-dir>'
    '<user>@<host>:<source-dir>_<date>'
    '<user>@<host>:<source-dir>_<date-time>'
  )

  target_name=''
  source_dir_last_seg=$(grep --only-matching '/[^/]\+$' <<<$source_path)
  source_dir=${source_dir_last_seg:1}
  date=$(date +'%Y-%m-%d')
  date_time=$(date +'%Y-%m-%d_%H:%M:%S')
  echo -en "${style_menu}"

  select answer in "${options[@]}"; do
    case $answer in
    ${options[0]}) target_name="${source_dir}" ;;
    ${options[1]}) target_name="${source_dir}_${date}" ;;
    ${options[2]}) target_name="${source_dir}_${date_time}" ;;
    ${options[3]}) target_name="$USER@$HOSTNAME:${source_dir}" ;;
    ${options[4]}) target_name="$USER@$HOSTNAME:${source_dir}_${date}" ;;
    ${options[5]}) target_name="$USER@$HOSTNAME:${source_dir}_${date_time}" ;;
    esac
    break
  done

  echo -e "\nYour backup directory will be called ${style_heading}$target_name${style_reset}"

  has_target_conflict='false'
  handle_create_target_conflict
}

set_update_target_path() {
  # update_flag check must happen after create_flag + existing directory check
  if [ $update_flag == 'true' ]; then
    target_path_last_seg=$(grep --only-matching '/[^/]\+$' <<<$target_path)
    target_dir=${target_path:0:$((-${#target_path_last_seg}))}
    target_path="$target_dir/$target_name"
  fi
}

select_target_name

echo
echo "select_target_name:"
echo "target_path: $target_path target_name: $target_name"
echo

set_update_target_path

# /home/malte/Desktop/Folder

echo
echo "set_update_target_path:"
echo "target_path: $target_path"
echo

# Select transfer/compression options
# Start copying and show progress
# Notify when finished (give status and print copied size again)

# --stats --progress

transfer_data() {
  echo 'Scarab starts rolling...'
}
