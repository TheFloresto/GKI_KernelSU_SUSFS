#!/usr/bin/env bash
set -euo pipefail

# Quick script to download ALL kernel sources used in test builds and name them properly.
# Folder name format: "<kernel_version>.<sublevel>-<android_version>-lts"
# Usage: ./download.sh [target_root]
# Example: ./download.sh ./kernel_sources_lts

TARGET_ROOT=${1:-"./kernel_sources_lts"}

# Ensure target root exists
mkdir -p "$TARGET_ROOT"

# Require the 'repo' tool to be installed and available in PATH
if ! command -v repo >/dev/null 2>&1; then
  echo "Error: 'repo' tool is required but not found in PATH." >&2
  echo "Install instructions: https://source.android.com/docs/setup/build/downloading\n" >&2
  exit 1
fi

REPO=$(command -v repo)

# Determine CPU count for parallel sync
CPU_COUNT() {
  if command -v nproc >/dev/null 2>&1; then
    nproc
  elif command -v sysctl >/dev/null 2>&1; then
    sysctl -n hw.ncpu
  else
    echo 4
  fi
}

# Branch format used by AOSP kernel manifest
# common-${android_version}-${kernel_version}-${os_patch_level}

download_one() {
  local android_version="$1"   # e.g. android14
  local kernel_version="$2"    # e.g. 6.1
  local os_patch_level="$3"    # e.g. lts

  local formatted_branch="${android_version}-${kernel_version}-${os_patch_level}"
  local work_dir="${TARGET_ROOT}/${kernel_version}.X-${android_version}-${os_patch_level}"

  echo "\n=== Downloading sources for ${kernel_version}.X-${android_version}-${os_patch_level} ==="
  mkdir -p "$work_dir"
  pushd "$work_dir" >/dev/null

  # Initialize manifest
  "$REPO" init --depth=1 \
    --u https://android.googlesource.com/kernel/manifest \
    -b "common-${formatted_branch}" \
    --repo-rev=v2.16

  # Handle deprecated branches (matches build.yml logic)
  local remote_branch
  remote_branch=$(git ls-remote https://android.googlesource.com/kernel/common "${formatted_branch}" || true)
  local default_manifest_path=".repo/manifests/default.xml"
  if echo "$remote_branch" | grep -q deprecated; then
    sed -i "s/\"${formatted_branch}\"/\"deprecated\/${formatted_branch}\"/g" "$default_manifest_path"
  fi

  # Sync
  "$REPO" --trace sync -c -j"$(CPU_COUNT)" --no-tags --fail-fast

  # Extract sublevel from common/Makefile
  local sublevel="X"
  if [ -f "common/Makefile" ]; then
    sublevel=$(grep '^SUBLEVEL = ' common/Makefile | awk '{print $3}') || true
    if [ -z "$sublevel" ]; then
      sublevel="X"
    fi
  fi

  popd >/dev/null

  # Final name with actual sublevel
  local final_dir="${TARGET_ROOT}/${kernel_version}.${sublevel}-${android_version}-${os_patch_level}"
  if [ "$final_dir" != "$work_dir" ]; then
    mv "$work_dir" "$final_dir"
  fi
  echo "Saved to: $final_dir"
}

# All kernel combinations from test build workflow
# Android 12 - 5.10
download_one "android12" "5.10" "2021-08"  # oldest (sub_level: 43)
download_one "android12" "5.10" "lts"      # LTS

# Android 13 - 5.10
download_one "android13" "5.10" "2022-04"  # oldest (sub_level: 107)
download_one "android13" "5.10" "lts"      # LTS

# Android 13 - 5.15
download_one "android13" "5.15" "2022-06"  # oldest (sub_level: 41)
download_one "android13" "5.15" "lts"      # LTS

# Android 14 - 5.15
download_one "android14" "5.15" "2023-06"  # oldest (sub_level: 110)
download_one "android14" "5.15" "lts"      # LTS

# Android 14 - 6.1
download_one "android14" "6.1" "2023-06"   # oldest (sub_level: 25)
download_one "android14" "6.1" "lts"       # LTS
download_one "android14" "6.1" "2025-05"   # specific (sub_level: 134)

# Android 15 - 6.6
download_one "android15" "6.6" "2024-07"   # oldest (sub_level: 30)
download_one "android15" "6.6" "lts"       # LTS

echo "\nAll kernel sources downloaded to: $TARGET_ROOT"
