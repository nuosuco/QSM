#!/bin/bash
# QVM Quantum Virtual Machine - Run 21 Quantum Circuits
# QVM量子虚拟机 - 运行21个量子电路脚本
# Version: 1.0.0
# Created: 2026-07-03
# Author: QSM Team
#
# Usage: bash qvm_run_21_circuits.sh [--epoch N] [--report]
#
# Options:
#   --epoch N     运行N个epoch的训练循环（默认1）
#   --report      生成详细运行报告
#   --quiet       只输出统计信息，不显示每个电路输出
#
# 功能：
#   1. 扫描所有有效量子电路（头部0x14）
#   2. 按模块分类运行
#   3. 统计周期和门数
#   4. 生成运行报告

set -e

# -----------------------------------------------------------------------------
# 路径定义
# -----------------------------------------------------------------------------
QSM_ROOT="/root/QSM"
QVM_BIN="${QSM_ROOT}/bin/qvm_bootstrap"
QENTL_ROOT="${QSM_ROOT}/QEntL"

cd "${QSM_ROOT}"

# -----------------------------------------------------------------------------
# 参数解析
# -----------------------------------------------------------------------------
EPOCH=1
REPORT=0
QUIET=0

for arg in "$@"; do
    case "$arg" in
        --epoch) EPOCH="$2"; shift 2 ;;
        --report) REPORT=1 ;;
        --quiet) QUIET=1 ;;
    esac
done

echo "=============================================="
echo "QVM - 运行21个量子电路"
echo "=============================================="
echo "  QVM: ${QVM_BIN}"
echo "  QEntL: ${QENTL_ROOT}"
echo "  Epochs: ${EPOCH}"
echo ""

# -----------------------------------------------------------------------------
# 扫描有效量子电路
# -----------------------------------------------------------------------------
VALID_QBCS=()
while IFS= read -r line; do
    VALID_QBCS+=("${line#VALID|}")
done < <(find "${QENTL_ROOT}" -name '*.qbc' -type f | sort | while read -r f; do
    first=$(xxd -l1 -p "$f" 2>/dev/null)
    if [ "$first" = "14" ]; then
        echo "VALID|$f"
    fi
done)

TOTAL=${#VALID_QBCS[@]}
echo "发现 ${TOTAL} 个有效量子电路"
echo ""

# -----------------------------------------------------------------------------
# 运行电路
# -----------------------------------------------------------------------------
if [ ${EPOCH} -eq 1 ]; then
    run_circuit() {
        local qbc="$1"
        local name=$(basename "${qbc}" .qbc)
        local rel="${qbc#${QENTL_ROOT}/}"
        
        # 确定模块
        case "${rel}" in
            Models/QSM/*) module="QSM" ;;
            Models/Ref/*) module="Ref" ;;
            Models/SOM/*) module="SOM" ;;
            Models/WeQ/*) module="WeQ" ;;
            Kernel/neural/*) module="QNS" ;;
            Kernel/filesystem/*) module="QDFS" ;;
            *) module="集成" ;;
        esac
        
        local output=$("${QVM_BIN}" "${qbc}" 2>&1)
        local exit_code=$?
        local cycles=$(echo "${output}" | grep -oP '\d+(?= 周期)' | tail -1 || echo "0")
        local gates=$(echo "${output}" | grep -oP '\d+(?= 门)' | tail -1 || echo "0")
        
        if [ ${QUIET} -eq 0 ]; then
            echo "  [${module}] ${name}: ${cycles}周期/${gates}门 exit=${exit_code}"
        fi
        
        if [ ${exit_code} -eq 0 ]; then
            echo "PASS|${module}|${name}|${cycles}|${gates}"
        else
            echo "FAIL|${module}|${name}|${exit_code}|${exit_code}"
        fi
    }
    
    # 按模块分类运行
    MODULES=("QSM" "Ref" "SOM" "WeQ" "QNS" "QDFS" "集成")
    ALL_RESULTS=""
    TOTAL_CYCLES=0
    TOTAL_GATES=0
    PASS=0
    FAIL=0
    
    for module in "${MODULES[@]}"; do
        if [ ${QUIET} -eq 0 ]; then
            echo "--- ${module} ---"
        fi
        
        for qbc in "${VALID_QBCS[@]}"; do
            rel="${qbc#${QENTL_ROOT}/}"
            circuit_module=""
            case "${rel}" in
                Models/QSM/*) circuit_module="QSM" ;;
                Models/Ref/*) circuit_module="Ref" ;;
                Models/SOM/*) circuit_module="SOM" ;;
                Models/WeQ/*) circuit_module="WeQ" ;;
                Kernel/neural/*) circuit_module="QNS" ;;
                Kernel/filesystem/*) circuit_module="QDFS" ;;
                *) circuit_module="集成" ;;
            esac
            
            if [ "${module}" = "${circuit_module}" ] || ([ "${module}" = "集成" ] && [ "${circuit_module}" = "集成" ]); then
                result=$(run_circuit "${qbc}")
                ALL_RESULTS="${ALL_RESULTS}${result}
"
                
                status=$(echo "${result}" | cut -d'|' -f1)
                cycles=$(echo "${result}" | cut -d'|' -f4)
                gates=$(echo "${result}" | cut -d'|' -f5)
                
                if [ "${status}" = "PASS" ]; then
                    PASS=$((PASS + 1))
                    TOTAL_CYCLES=$((TOTAL_CYCLES + cycles))
                    TOTAL_GATES=$((TOTAL_GATES + gates))
                else
                    FAIL=$((FAIL + 1))
                fi
            fi
        done
        
        if [ ${QUIET} -eq 0 ]; then
            echo ""
        fi
    done
    
    echo "=============================================="
    echo "运行统计"
    echo "=============================================="
    echo "  电路总数: ${TOTAL}"
    echo "  PASS: ${PASS}"
    echo "  FAIL: ${FAIL}"
    echo "  总周期: ${TOTAL_CYCLES}"
    echo "  总门数: ${TOTAL_GATES}"
    echo ""
    
    # 生成报告
    if [ ${REPORT} -eq 1 ]; then
        REPORT_FILE="${QSM_ROOT}/qvm_run_21_report.md"
        cat > "${REPORT_FILE}" << REPORT_EOF
# QVM 21个量子电路运行报告

## 运行参数
- 日期: $(date '+%Y-%m-%d %H:%M:%S')
- Epoch: ${EPOCH}
- QVM: ${QVM_BIN}

## 运行统计
| 指标 | 值 |
|------|-----|
| 电路总数 | ${TOTAL} |
| PASS | ${PASS} |
| FAIL | ${FAIL} |
| 总周期 | ${TOTAL_CYCLES} |
| 总门数 | ${TOTAL_GATES} |

## 详细结果

| 状态 | 模块 | 电路 | 周期 | 门数 |
|------|------|------|------|------|
REPORT_EOF
        
        echo "${ALL_RESULTS}" | while IFS='|' read -r status module name cycles gates; do
            [ -z "${status}" ] && continue
            echo "| ${status} | ${module} | ${name} | ${cycles} | ${gates} |" >> "${REPORT_FILE}"
        done
        
        echo "报告已生成: ${REPORT_FILE}"
    fi
    
    [ ${FAIL} -eq 0 ] && exit 0 || exit 1
    
else
    # 多epoch训练循环
    ALL_RESULTS=""
    TOTAL_RUNS=0
    TOTAL_CYCLES=0
    TOTAL_GATES=0
    PASS=0
    FAIL=0
    
    echo "执行 ${EPOCH} epoch 训练循环..."
    echo ""
    
    for epoch in $(seq 1 ${EPOCH}); do
        echo "=== Epoch ${epoch}/${EPOCH} ==="
        
        for qbc in "${VALID_QBCS[@]}"; do
            name=$(basename "${qbc}" .qbc)
            rel="${qbc#${QENTL_ROOT}/}"
            
            case "${rel}" in
                Models/QSM/*) module="QSM" ;;
                Models/Ref/*) module="Ref" ;;
                Models/SOM/*) module="SOM" ;;
                Models/WeQ/*) module="WeQ" ;;
                Kernel/neural/*) module="QNS" ;;
                Kernel/filesystem/*) module="QDFS" ;;
                *) module="集成" ;;
            esac
            
            output=$("${QVM_BIN}" "${qbc}" 2>&1)
            exit_code=$?
            cycles=$(echo "${output}" | grep -oP '\d+(?= 周期)' | tail -1 || echo "0")
            gates=$(echo "${output}" | grep -oP '\d+(?= 门)' | tail -1 || echo "0")
            
            TOTAL_RUNS=$((TOTAL_RUNS + 1))
            TOTAL_CYCLES=$((TOTAL_CYCLES + cycles))
            TOTAL_GATES=$((TOTAL_GATES + gates))
            
            if [ ${exit_code} -eq 0 ]; then
                PASS=$((PASS + 1))
            else
                FAIL=$((FAIL + 1))
            fi
        done
        
        echo "  Epoch ${epoch}: ${PASS} PASS, ${FAIL} FAIL"
        echo ""
    done
    
    echo "=============================================="
    echo "训练完成"
    echo "=============================================="
    echo "  Epochs: ${EPOCH}"
    echo "  总执行: ${TOTAL_RUNS}"
    echo "  总周期: ${TOTAL_CYCLES}"
    echo "  总门数: ${TOTAL_GATES}"
    echo "  PASS: ${PASS}"
    echo "  FAIL: ${FAIL}"
    echo ""
    
    # 生成报告
    if [ ${REPORT} -eq 1 ]; then
        REPORT_FILE="${QSM_ROOT}/qvm_train_${EPOCH}epoch_report.md"
        cat > "${REPORT_FILE}" << REPORT_EOF
# QVM ${EPOCH} Epoch 训练报告

## 训练参数
- 日期: $(date '+%Y-%m-%d %H:%M:%S')
- Epochs: ${EPOCH}
- 电路数: ${TOTAL}

## 统计
| 指标 | 值 |
|------|-----|
| 总执行次数 | ${TOTAL_RUNS} |
| 总周期 | ${TOTAL_CYCLES} |
| 总门数 | ${TOTAL_GATES} |
| PASS | ${PASS} |
| FAIL | ${FAIL} |
| 成功率 | $(echo "scale=2; ${PASS}*100/${TOTAL_RUNS}" | bc)% |
REPORT_EOF
        
        echo "报告已生成: ${REPORT_FILE}"
    fi
    
    [ ${FAIL} -eq 0 ] && exit 0 || exit 1
fi
