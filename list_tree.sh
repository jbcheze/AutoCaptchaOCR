#!/usr/bin/env bash

echo "===== PROJECT TREE ====="
echo

EXCLUDE_DIRS=("data" "datasets" "images" "labels" ".git" ".venv" "__pycache__" "runs")
EXCLUDE_EXTENSIONS=("jpg" "png" "jpeg" "zip" "pt" "keras")

should_exclude_dir () {
  local name="$1"
  for ex in "${EXCLUDE_DIRS[@]}"; do
    [[ "$name" == "$ex" ]] && return 0
  done
  return 1
}

should_exclude_file () {
  local file="$1"
  ext="${file##*.}"
  for ex in "${EXCLUDE_EXTENSIONS[@]}"; do
    [[ "$ext" == "$ex" ]] && return 0
  done
  return 1
}

print_tree () {
  local prefix="$1"
  local dir="$2"

  for item in "$dir"/*; do
    [ -e "$item" ] || continue
    name=$(basename "$item")

    if [ -d "$item" ]; then
      if should_exclude_dir "$name"; then
        echo "${prefix}🚫 $name/ (excluded)"
        continue
      fi
      echo "${prefix}📁 $name/"
      print_tree "$prefix    " "$item"

    else
      if should_exclude_file "$name"; then
        continue
      fi
      echo "${prefix}📄 $name"
    fi
  done
}

print_tree "" "."