#!/bin/bash
# QEntL Full Stack Test Suite
# 全面测试: 语法检查 → 编译 → QVM运行 → 修复 → 汇报

set -o pipefail

QSM_ROOT="/root/QSM"
COMPILER="$QSM_ROOT/bin/qentl_compiler"
QVM="$QSM_ROOT/bin/qvm_boot"
OUTDIR="$QSM_ROOT/test_output"
mkdir -p "$OUTDIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

TOTAL=0
COMPILE_OK=0
COMPILE_FAIL=0
RUN_OK=0
RUN_FAIL=0
RUN_ERRORS=()

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║          QEntL Full Stack Test Suite v1.0                    ║"
echo "║         全面测试: 语法检查 → 编译 → QVM运行                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: Find all .qentl files ──
echo -e "${CYAN}[$(date +%H:%M:%S)] Step 1: 发现所有 QEntL 文件...${NC}"
mapfile -t QENTL_FILES < <(find "$QSM_ROOT" -name "*.qentl" -type f | sort)
TOTAL=${#QENTL_FILES[@]}
echo "  发现 $TOTAL 个 .qentl 文件"
echo ""

# ── Step 2: Compile all .qentl → .qbc ──
echo -e "${CYAN}[$(date +%H:%M:%S)] Step 2: 编译所有 .qentl 为 .qbc 字节码...${NC}"
echo ""

COMPILED_FILES=()
COMPILE_ERRORS=()

for f in "${QENTL_FILES[@]}"; do
    rel="${f#$QSM_ROOT/}"
    # Output path: preserve directory structure under OUTDIR
    out="$OUTDIR/${rel%.qentl}.qbc"
    mkdir -p "$(dirname "$out")"
    
    # Run compiler
    out_log="$OUTDIR/${rel%.qentl}.compile.log"
    result=$(cd "$QSM_ROOT" && "$COMPILER" "$f" "$out" 2>&1)
    rc=$?
    echo "$result" > "$out_log"
    
    if [ $rc -eq 0 ] && [ -f "$out" ]; then
        COMPILE_OK=$((COMPILE_OK + 1))
        COMPILED_FILES+=("$out")
        printf "  ${GREEN}✓${NC} %s\n" "$rel"
    else
        COMPILE_FAIL=$((COMPILE_FAIL + 1))
        COMPILE_ERRORS+=("$rel")
        printf "  ${RED}✗${NC} %s\n" "$rel"
        # Show first line of error
        first_err=$(head -1 "$out_log" | tr -d '\n' | head -c 120)
        if [ -n "$first_err" ]; then
            echo "         $first_err"
        fi
    fi
done

echo ""
echo -e "  编译结果: ${GREEN}成功 $COMPILE_OK${NC} / ${RED}失败 $COMPILE_FAIL${NC} (共 $TOTAL)"
echo ""

# ── Step 3: Run all compiled .qbc on QVM ──
echo -e "${CYAN}[$(date +%H:%M:%S)] Step 3: 在 QVM 上运行所有 .qbc 文件...${NC}"
echo ""

for qbc in "${COMPILED_FILES[@]}"; do
    rel="${qbc#$OUTDIR/}"
    run_log="$OUTDIR/${rel%.qbc}.run.log"
    
    # Run on QVM with timeout
    result=$(timeout 30 "$QVM" "$qbc" 2>&1)
    rc=$?
    echo "$result" > "$run_log"
    
    if [ $rc -eq 0 ]; then
        RUN_OK=$((RUN_OK + 1))
        printf "  ${GREEN}✓${NC} %s\n" "${rel%.qbc}.qentl"
    else
        RUN_FAIL=$((RUN_FAIL + 1))
        RUN_ERRORS+=("${rel%.qbc}.qentl")
        printf "  ${RED}✗${NC} %s (exit=$rc)\n" "${rel%.qbc}.qentl"
        # Show key error line
        err_line=$(grep -i -E "error|错误|fail|panic|segfault" "$run_log" | head -1 | tr -d '\n' | head -c 120)
        if [ -n "$err_line" ]; then
            echo "         $err_line"
        fi
    fi
done

echo ""
echo -e "  运行结果: ${GREEN}成功 $RUN_OK${NC} / ${RED}失败 $RUN_FAIL${NC} (共 ${#COMPILED_FILES[@]})"
echo ""

# ── Step 4: Summary Report ──
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    测试报告 / Test Report                     ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  总文件数:       $TOTAL"
echo -e "║  编译成功:       ${GREEN}$COMPILE_OK${NC}"
echo -e "║  编译失败:       ${RED}$COMPILE_FAIL${NC}"
echo -e "║  QVM运行成功:    ${GREEN}$RUN_OK${NC}"
echo -e "║  QVM运行失败:    ${RED}$RUN_FAIL${NC}"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── Step 5: Detail failures ──
if [ ${#COMPILE_ERRORS[@]} -gt 0 ]; then
    echo -e "${RED}编译失败的文件 (${#COMPILE_ERRORS[@]} 个):${NC}"
    for f in "${COMPILE_ERRORS[@]}"; do
        echo "  - $f"
    done
    echo ""
fi

if [ ${#RUN_ERRORS[@]} -gt 0 ]; then
    echo -e "${RED}QVM运行失败的文件 (${#RUN_ERRORS[@]} 个):${NC}"
    for f in "${RUN_ERRORS[@]}"; do
        echo "  - $f"
    done
    echo ""
fi

# Save summary
cat > "$OUTDIR/test_summary.txt" <<EOF
QEntL Full Stack Test Report
============================
Date: $(date)
Total files: $TOTAL
Compile OK: $COMPILE_OK
Compile FAIL: $COMPILE_FAIL
QVM Run OK: $RUN_OK
QVM Run FAIL: $RUN_FAIL

Compile Errors:
$(printf '%s\n' "${COMPILE_ERRORS[@]}")

QVM Run Errors:
$(printf '%s\n' "${RUN_ERRORS[@]}")
EOF

echo "详细日志保存在: $OUTDIR/"
echo "测试完成!"
