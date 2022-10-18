#! /bin/bash

# malte.podolski AT web DOT de
# github.com/m-podolski/scarab-backup

version='0.3.1'

style_ok='\e[0;32m\e[1m'
style_warn='\e[0;33m\e[1mWarning: '
style_error='\e[0;91m\e[1mError: '
style_menu='\e[0;34m\e[1m'
style_heading='\e[1m'
style_reset='\e[0m'

select_mode() {
  PS3="$(echo -en "${style_reset}")Select the backup-mode (number): "
  options=('Create new' 'Update existing')
  echo -en "${style_menu}"

  select answer in "${options[@]}"; do
    case $answer in
    "${options[0]}")
      mode_flag='create'
      break
      ;;
    "${options[1]}")
      mode_flag='update'
      break
      ;;
    esac
  done
  echo
}

read_source_path() {
  echo -en "${style_menu}"
  read -p "Enter your source directory (absolute path): " source_path
  echo -en "${style_reset}\n"

  source_path=${source_path/#\~/$HOME}
  validate_source_path
}

validate_source_path() {
  if [[ ! -d "$source_path" ]]; then
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
        mode_flag='create'
        source_path="${OPTARG}"
        ;;
      u)
        mode_flag='update'
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

# Check if folder called "[Bb]ackup[s]*" exists at drive
#   If yes, append to drivepath and print subdirectories as menu
#   If not, prompt for path

get_destination_path() {
  drive_path=$1
  backup_dir_matches=()

  for file in "$drive_path"/*; do
    if [[ $file =~ [Bb]ackup[s]* ]]; then
      backup_dir_matches+=("$file")
    fi
  done
  echo "${backup_dir_matches[@]}"

  if ((${#backup_dir_matches[@]})); then
    backup_dir="${backup_dir_matches[0]}"

    if [[ $mode_flag == 'create' ]]; then
      destination_path=$backup_dir
    fi
    if [[ $mode_flag == 'update' ]]; then
      PS3="$(echo -en "${style_reset}")Select the destination directory. (number): "
      mapfile -t options < <(ls "$backup_dir")
      echo -en "${style_menu}"

      select option in "${options[@]}"; do
        case $option in
        *) destination_path="$backup_dir/$option" ;;
        esac
        break
      done
      echo
    fi
  else
    if [ -x "$(command -v tree)" ]; then
      echo -e "${style_heading}These are the top 2 levels of your destination:${style_reset}"
      tree -dL 2 "$drive_path"
    else
      echo -e "${style_heading}This is the root directory of your destination:${style_reset}"
      ls -l --all --color=auto "$drive_path"
    fi

    if [[ $mode_flag == 'create' ]]; then
      echo -en "\n${style_heading}Your are in Create-Mode\n${style_reset}The backup will be created under the selected directory. Press RETURN for the root directory."
    fi
    if [[ $mode_flag == 'update' ]]; then
      echo -en "\n${style_heading}Your are in Update-Mode\n${style_reset}The selected directory will be replaced/updated"
    fi
    echo -en "\n${style_menu}"
    read -p "Enter destination on drive: " path_at_destination
    echo -en "${style_reset}"

    destination_path="$drive_path/$path_at_destination"
    echo -e "\nDestination is ${style_heading}$destination_path${style_reset}"

    if [[ $mode_flag == 'update' && ! -d $destination_path ]]; then
      echo -e "${style_error}Your destination path is not a valid directory!${style_reset}\n"
      get_destination_path "$drive_path"
    fi
  fi
}

check_free_drive_space() {
  destination_path=$1
  destination_stats_values=$2
  block_size=512

  echo -e "${style_heading}Checking your free drive space. Please wait.${style_reset}"

  size_source=$(du --block-size=$block_size --summarize "$source_path" | awk '{print $1}')
  avail_destination=$(df --block-size=$block_size --output=avail "$destination_path" | tail --lines=1 | awk '{print $1}')

  if [[ $mode_flag == 'create' ]]; then
    free_space=$((avail_destination - size_source))
  fi

  if [[ $mode_flag == 'update' ]]; then
    size_existing=$(du --block-size=$block_size --summarize "$destination_path" | awk '{print $1}')
    free_space=$((avail_destination + size_existing - size_source))
  fi

  destination_stats_values[0]=$size_source
  destination_stats_values[1]=$avail_destination
  destination_stats_values[2]=$size_existing
  destination_stats_values[3]=$free_space

  if [[ $free_space -gt 0 ]]; then
    backup_possible='true'
  else
    backup_possible='false'
  fi
}

print_destination_stats() {
  destination_path=$1
  available=$2

  if [[ "$available" == 'true' ]]; then
    echo -e "\n${style_ok}The destination has enough space available:${style_reset}"
  else
    echo -e "\n${style_warn}The destination has not enough space available:${style_reset}"
  fi

  list_els_displayed=${#destination_stats_keys[@]}
  if [[ $mode_flag == 'create' ]]; then
    list_els_displayed=$((${#destination_stats_keys[@]} - 2))
  fi

  for ((i = 0; i < "$list_els_displayed"; ++i)); do
    printf "%-16s  %-16d\n" "${destination_stats_keys[$i]}" "${destination_stats_values[$i]}"
  done

  echo -en "\n${style_heading}"
  df --human-readable --output=target,size,used,avail,pcent "$destination_path" | head -1
  echo -en "${style_reset}"
  df --human-readable --output=target,size,used,avail,pcent "$destination_path" | tail --lines=1
}

reselect_drive() {
  PS3="$(echo -en "${style_reset}")Select an answer (number): "
  options=('Select another drive' 'Exit')
  echo -en "\n${style_menu}"

  select answer in "${options[@]}"; do
    case $answer in
    "${options[0]}") select_destination ;;
    "${options[1]}") exit ;;
    esac
  done
}

# Get drive selection
# Print top-level directory of selected drive
# Check mode

select_destination() {
  PS3="$(echo -en "${style_reset}")Select the destination drive. Backup directories will be detected automatically (number): "
  mapfile -t options < <(ls "/media/$USER")
  rescan='Scan drives again'
  options+=("$rescan")

  echo -en "${style_menu}"

  select option in "${options[@]}"; do
    case $option in
    "$rescan")
      echo
      select_destination
      ;;
    *)
      echo
      drive_path="/media/$USER/$option"
      # clear

      # If creating
      #   Check if there is enough free space at destination and print stats
      #     If yes, prompt to enter destination on drive (directory will be created there)
      #       Validate directory
      #         If valid, proceed
      #         Else, prompt to enter again
      #     Else, ask if user wants to select another drive or quit
      #       If yes, go back to drive selection
      #       Else exit

      destination_stats_keys=('Source' 'Free on Drive' 'Existing Target' 'Existing Diff')
      destination_stats_values=(0 0 0 0)
      backup_possible=''

      if [[ $mode_flag == 'create' ]]; then
        check_free_drive_space "$drive_path" "${destination_stats_values[@]}"
        print_destination_stats "$drive_path" "$backup_possible"

        if [[ "$backup_possible" == 'true' ]]; then
          get_destination_path "$drive_path"
        else
          reselect_drive
        fi
      fi

      # If updating
      #   Prompt to enter destination on drive (must point to existing backup directory)
      #     Validate directory
      #       If valid
      #         Check if there is enough free space (difference existing/source) and print stats
      #           If yes, proceed
      #           Else, print result and ask if user wants to select another drive or quit
      #            If drive, go back to drive selection
      #            Else exit
      #       Else, prompt to enter again

      if [[ $mode_flag == 'update' ]]; then
        get_destination_path "$drive_path"
        check_free_drive_space "$destination_path"
        print_destination_stats "$destination_path" "$backup_possible"

        if [[ "$backup_possible" == 'false' ]]; then
          reselect_drive
        fi
      fi
      ;;
    esac
    break
  done
}

# Set backup-directory name format
#   Check mode and if dir already exists
#     If creating and dir exists
#       Prompt to change format, rescan, replace or exit
#     If creating and dir exists not
#       Proceed
#     If updating
#       Proceed
#     ("If updating and dir exists not" cannot happen; already validated path)

handle_create_destination_conflict() {
  if [[ $mode_flag == 'create' && $dest_name_has_time == 'false' && -d "$destination_path/$destination_name" ]]; then
    if [[ "$has_destination_conflict" == 'false' ]]; then
      echo -e "\n${style_warn}A directory with the selected name already exists!${style_reset}\nYou can first change the name of the existing directory manually and then use the 'Rescan' option to proceed with your current settings\n"
    fi

    PS3="$(echo -en "${style_reset}")Select an answer (number): "
    options=('Rescan' 'Change name format' 'Replace (Switch to Update-Mode)' 'Exit')
    echo -en "${style_menu}"

    select answer in "${options[@]}"; do
      case $answer in
      "${options[0]}")
        if [[ -d "$destination_path/$destination_name" ]]; then
          echo -en "\n${style_error}Rescan still found directory of the same name.${style_reset}\n"
          has_destination_conflict='true'
          handle_create_destination_conflict
        else
          echo -e "\n${style_ok}Directory conflict has been resolved. Proceeding...${style_reset}\n"
        fi
        ;;
      "${options[1]}") select_destination_name ;;
      "${options[2]}")
        mode_flag='update'
        echo -e "\n${style_ok}You have switched into update-mode. The destination directory will be replaced.${style_reset}\n"
        ;;
      "${options[3]}") exit ;;
      esac
      break
    done
  fi
}

select_destination_name() {
  clear
  printf "${style_heading}%-16s${style_reset} %-16s\n" '<source-dir>' 'The original directory name'
  printf "${style_heading}%-16s${style_reset} %-16s\n" '<date>' 'YYYY-MM-DD'
  printf "${style_heading}%-16s${style_reset} %-16s\n\n" '<date-time>' 'YYYY-MM-DD_HH-MM-SS'

  PS3="$(echo -en "${style_reset}")Select a name format for the backup directory (number): "
  options=(
    '<source-dir>'
    '<source-dir>_<date>'
    '<source-dir>_<date-time>'
    '<user>@<host>_<source-dir>'
    '<user>@<host>_<source-dir>_<date>'
    '<user>@<host>_<source-dir>_<date-time>'
  )

  destination_name=''
  dest_name_has_time='false'
  source_dir_last_seg=$(grep --only-matching '/[^/]\+$' <<<"$source_path")
  source_dir=${source_dir_last_seg:1}
  date=$(date +'%Y-%m-%d')
  echo -en "${style_menu}"

  select answer in "${options[@]}"; do
    case $answer in
    "${options[0]}") destination_name="${source_dir}" ;;
    "${options[1]}") destination_name="${source_dir}_${date}" ;;
    "${options[2]}")
      destination_name="${source_dir}_${date}"
      dest_name_has_time='true'
      ;;
    "${options[3]}") destination_name="${USER}@${HOSTNAME}_${source_dir}" ;;
    "${options[4]}") destination_name="${USER}@${HOSTNAME}_${source_dir}_${date}" ;;
    " ${options[5]}")
      destination_name="${USER}@${HOSTNAME}_${source_dir}_${date}"
      dest_name_has_time='true'
      ;;
    esac
    break
  done

  if [[ $dest_name_has_time == 'true' ]]; then
    dummy_time="_00:00:00 ${style_reset}(time will be set at the end)"
  fi
  echo -e "\nYour backup directory will be called ${style_heading}$destination_name$dummy_time${style_reset}"

  has_destination_conflict='false'
  handle_create_destination_conflict
}

# Check if source root contains prepare-file (.scarabprepare.sh)
#   If yes, execute
# Check if source root contains exclude-file (.scarabignore)
#   If yes, use for --exclude-from
# Select transfer/compression options
#   Regular Rsync Archive
#   Scarab Archive
#   Scarab Archive with Hardlinks
#   (Dry Run) Regular Rsync Archive
#   (Dry Run) Scarab Archive
#   (Dry Run) Scarab Archive with Hardlinks
#   Custom
#     Prompt to enter options as one string
# Start copying and show progress

select_archive_mode() {
  PS3="$(echo -en "${style_reset}")Select the archive mode for rsync (number): "
  options=(
    'Scarab Archive'
    'Scarab Archive (Hardlinks)'
    '(Dry Run) Scarab Archive'
    '(Dry Run) Scarab Archive (Hardlinks)'
    'Custom'
  )
  printf "${style_heading}%-32s${style_reset} %s\n" "${options[0]}" 'Same as rsync archive, also keeps access-times. Deletes missing and excluded files.'
  printf "${style_heading}%-32s${style_reset} %s\n" "${options[1]}" 'Same as above, also keeps hardlinks. May be slower.'
  printf "${style_heading}%-32s${style_reset} %s\n" '(Dry Run) *' 'Uses respective configuration only for logging.'
  printf "${style_heading}%-32s${style_reset} %s\n\n" "${options[4]}" 'Rsync with custom options. You will be prompted.'

  # --archive is equal to the following options:
  # --recursive --links --perms --times --group --owner --devices --specials
  rsync_options_scarab='--itemize-changes --stats --progress --human-readable --filter=dir-merge_/.rsync-filter --archive --atimes --delete --delete-excluded'
  rsync_options_scarab_hardlinks='--itemize-changes --stats --progress --human-readable --filter=dir-merge_/.rsync-filter --archive --atimes --hard-links --delete --delete-excluded'
  echo -en "${style_menu}"

  select answer in "${options[@]}"; do
    case $answer in
    "${options[0]}") rsync_options=$rsync_options_scarab ;;
    "${options[1]}") rsync_options=$rsync_options_scarab_hardlinks ;;
    "${options[2]}") rsync_options="--dry-run $rsync_options_scarab " ;;
    "${options[3]}") rsync_options="--dry-run $rsync_options_scarab_hardlinks" ;;
    "${options[4]}")
      echo
      read -p "Enter your rsync options: " rsync_options
      ;;
    esac
    break
  done

  echo -e "\nRsync will be run with the following options: ${style_heading}$rsync_options${style_reset}\n"
}

run_scarabprepare() {
  clear
  scarabprepare_path="$source_path/.scarabprepare.sh"
  if [[ -e "$scarabprepare_path" ]]; then
    echo -e "${style_ok}Found .scarabprepare.sh and executing it${style_reset}"
    # shellcheck source=/dev/null
    source "$scarabprepare_path"
  fi
}

transfer_data() {
  echo -e "Your source directory is ${style_heading}$source_path${style_reset}"
  echo -e "Your destination directory is ${style_heading}$destination_path${style_reset}\n"

  run_scarabprepare
  echo -e "${style_ok}Scarab starts rolling...${style_reset}\n"

  if [[ $mode_flag == 'create' ]]; then
    destination_path="$destination_path/$destination_name"

    destination_rename=$destination_path
    rsync "$rsync_options" "$source_path" "$destination_path"
  fi
  if [[ $mode_flag == 'update' ]]; then
    destination_path_last_seg=$(grep --only-matching '/[^/]\+$' <<<"$destination_path")
    destination_dir=${destination_path:0:$((-${#destination_path_last_seg}))}

    destination_rename="$destination_dir/$destination_name"
    rsync "$rsync_options" "$source_path/" "$destination_path"
  fi

  if [[ $dest_name_has_time == 'true' ]]; then
    time=$(date +'%H-%M-%S')
    destination_rename="${destination_rename}_$time"
  fi
  mv "$destination_path" "$destination_rename"
}

main() {
  source_path='null'
  destination_path='null'
  mode_flag='null'

  clear
  script_dir="$(cd "$(dirname "$0")" && pwd)"
  cat "$script_dir/welcome-art.txt"
  echo -e "${style_heading}You are running Scarab Backup ${version} (2022 by Malte Podolski)${style_reset}\n"

  check_arguments "$@"
  select_destination
  select_destination_name
  select_archive_mode
  transfer_data
}

main "$@"
