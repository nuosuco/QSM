#!/bin/bash
# Audit QEntL files for platform (5 OS) and deployment (3 modes) references

WORKDIR="/root/QSM"
cd "$WORKDIR"

TOTAL=0
HAS_PLATFORM=0
HAS_DEPLOY=0
MISSING_PLATFORM=()
MISSING_DEPLOY=()
MISSING_BOTH=()
EXISTS_PLATFORM=()
EXISTS_DEPLOY=()

# Exclude the platform/deployment definition files themselves from audit? 
# Per task: ALL .qentl files must contain platform AND deployment references.
# We'll include them but note they're the source modules.

while IFS= read -r f; do
    TOTAL=$((TOTAL + 1))
    basename_f=$(basename "$f")
    
    has_p=0
    has_d=0
    
    # Platform: Windows/macOS/iOS/Android/Linux OR platform_types/import Platform
    if grep -qiE '(windows|macos|ios|android|linux|platform_types|Platform/platform|System/Platform)' "$f" 2>/dev/null; then
        has_p=1
        HAS_PLATFORM=$((HAS_PLATFORM + 1))
        EXISTS_PLATFORM+=("$f")
    else
        MISSING_PLATFORM+=("$f")
    fi
    
    # Deployment: development/production/specialized (mode)
    if grep -qiE '(development_mode|production_mode|specialized_mode|System/Deployment|deployment_mode|deploy.*mode)' "$f" 2>/dev/null; then
        has_d=1
        HAS_DEPLOY=$((HAS_DEPLOY + 1))
        EXISTS_DEPLOY+=("$f")
    else
        MISSING_DEPLOY+=("$f")
    fi
    
    if [ $has_p -eq 0 ] && [ $has_d -eq 0 ]; then
        MISSING_BOTH+=("$f")
    fi
done < <(find "$WORKDIR/QEntL" -name '*.qentl' | sort)

echo "============================================="
echo "QEntL AUDIT: Platform(5 OS) + Deployment(3 modes)"
echo "============================================="
echo "Total .qentl files:       $TOTAL"
echo "With platform reference:  $HAS_PLATFORM"
echo "With deployment reference: $HAS_DEPLOY"
echo "Missing BOTH:             ${#MISSING_BOTH[@]}"
echo "Missing platform only:    $((${#MISSING_PLATFORM[@]} - ${#MISSING_BOTH[@]}))"
echo "Missing deployment only:  $((${#MISSING_DEPLOY[@]} - ${#MISSING_BOTH[@]}))"
echo ""
echo "=== FILES MISSING PLATFORM REFERENCE (${#MISSING_PLATFORM[@]} total) ==="
for f in "${MISSING_PLATFORM[@]}"; do
    echo "  $f"
done
echo ""
echo "=== FILES MISSING DEPLOYMENT REFERENCE (${#MISSING_DEPLOY[@]} total) ==="
for f in "${MISSING_DEPLOY[@]}"; do
    echo "  $f"
done
echo ""
echo "=== FILES MISSING BOTH (${#MISSING_BOTH[@]} total) ==="
for f in "${MISSING_BOTH[@]}"; do
    echo "  $f"
done
