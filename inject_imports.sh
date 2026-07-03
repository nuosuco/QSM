#!/bin/bash
# Add platform + deployment import statements to .qentl files that are missing them.
# Scans the first 30 lines of each file; if no "import" or "//" preamble is present,
# prepends before line 1.  Otherwise, appends the two imports after the last
# existing import line (within first 30 lines).
#
# Excludes the 5 platform definition files and 3 deployment definition files
# themselves — they ARE the source of truth.

WORKDIR="/root/QSM"
cd "$WORKDIR"

PLATFORM_IMPORT='import "QEntL/System/Platform/platform_types.qentl";'
DEPLOY_IMPORT='import "QEntL/System/Deployment/development_mode.qentl";'

# Files that are the platform/deployment definition modules themselves — skip.
SKIP_FILES=(
  "QEntL/System/Platform/platform_types.qentl"
  "QEntL/System/Platform/platform_entry.qentl"
  "QEntL/System/Platform/platform_registry.qentl"
  "QEntL/System/Platform/conversion/binary_converter.qentl"
  "QEntL/System/Platform/formats/pe_format.qentl"
  "QEntL/System/Platform/formats/macho_format.qentl"
  "QEntL/System/Platform/formats/elf_format.qentl"
  "QEntL/System/Platform/formats/harmony_format.qentl"
  "QEntL/System/Deployment/development_mode.qentl"
  "QEntL/System/Deployment/production_mode.qentl"
  "QEntL/System/Deployment/specialized_mode.qentl"
)

skip_file() {
  local rel="$1"
  for s in "${SKIP_FILES[@]}"; do
    [ "$rel" = "$s" ] && return 0
  done
  return 1
}

FIXED=0
FAILED=0

while IFS= read -r f; do
  rel="${f#$WORKDIR/}"
  
  # Skip definition files
  if skip_file "$rel"; then
    continue
  fi
  
  # Check if already has platform AND deployment imports
  has_platform=0
  has_deploy=0
  grep -qE '(System/Platform/platform_types|PLATFORM_WINDOWS|PLATFORM_IOS|PLATFORM_ANDROID|PLATFORM_LINUX|PlatformID)' "$f" 2>/dev/null && has_platform=1
  grep -qE '(System/Deployment/development_mode|System/Deployment/production_mode|System/Deployment/specialized_mode|development_mode|production_mode|specialized_mode)' "$f" 2>/dev/null && has_deploy=1
  
  if [ "$has_platform" -eq 1 ] && [ "$has_deploy" -eq 1 ]; then
    continue  # already compliant
  fi
  
  imports_to_add=""
  [ "$has_platform" -eq 0 ] && imports_to_add="${PLATFORM_IMPORT}"$'\n'
  [ "$has_deploy" -eq 0 ] && imports_to_add="${imports_to_add}${DEPLOY_IMPORT}"
  
  if [ -z "$imports_to_add" ]; then
    continue
  fi
  
  # Find last import line within first 30 lines
  last_import_line=0
  for (( i=1; i<=30; i++ )); do
    line=$(sed -n "${i}p" "$f")
    if echo "$line" | grep -qE '^\s*import\s'; then
      last_import_line=$i
    fi
  done
  
  if [ "$last_import_line" -gt 0 ]; then
    # Insert after the last existing import line
    {
      sed -n "1,${last_import_line}p" "$f"
      echo "$imports_to_add"
      sed -n "$((last_import_line + 1)),$ p" "$f"
    } > "${f}.tmp" && mv "${f}.tmp" "$f"
  else
    # Prepend at the top of the file
    {
      echo "$imports_to_add"
      cat "$f"
    } > "${f}.tmp" && mv "${f}.tmp" "$f"
  fi
  
  FIXED=$((FIXED + 1))
  
  # Verify the fix
  if ! grep -qE '(System/Platform/platform_types)' "$f" 2>/dev/null; then
    FAILED=$((FAILED + 1))
    echo "FAIL verify platform: $rel"
  fi
  if ! grep -qE '(System/Deployment/development_mode|development_mode)' "$f" 2>/dev/null; then
    FAILED=$((FAILED + 1))
    echo "FAIL verify deploy: $rel"
  fi
  
done < <(find "$WORKDIR/QEntL" -name '*.qentl' | sort)

echo ""
echo "=== INJECTION COMPLETE ==="
echo "Files fixed: $FIXED"
echo "Verification failures: $FAILED"
