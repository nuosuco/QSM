#!/bin/bash
# QVM Quantum Virtual Machine - Environment Verification Script
# QVM量子虚拟机环境验证脚本
# Version: 1.0.0
# Created: 2026-07-03
# Author: QSM Team
#
# Usage: bash qvm_verify.sh
#
# 功能：
#   1. 验证C语言启动器存在并可用
#   2. 验证配置文件存在
#   3. 验证QEntL源码完整性
#   4. 验证21个有效量子电路
#   5. CNOT回归测试
#   6. 输出验证报告

set -e

QSM_ROOT="/root/QSM"
QVM_BIN="${QSM_ROOT}/bin/qvm_bootstrap"
QCL_BIN="${QSM_ROOT}/bin/qcl_bootstrap"
QENTL_ROOT="${QSM_ROOT}/QEntL"
CONF_FILE="${QSM_ROOT}/qvm_env.conf"

cd "${QSM_ROOT}"

echo "=============================================="
echo "QVM 环境验证"
echo "=============================================="
echo ""

PASS=0
FAIL=0

check() {
    local name="$1"
    local result="$2"
    
    if [ "${result}" -eq 0 ]; then
        echo "✅ ${name}"
        PASS=$((PASS + 1))
    else
        echo "❌ ${name}"
        FAIL=$((FAIL + 1))
    fi
}

# -----------------------------------------------------------------------------
# 1. C语言启动器
# -----------------------------------------------------------------------------
echo "1. C语言启动器"
[ -x "${QVM_BIN}" ] && check "qvm_bootstrap 存在且可执行" 0 || check "qvm_bootstrap 存在且可执行" 1
[ -x "${QCL_BIN}" ] && check "qcl_bootstrap 存在且可执行" 0 || check "qcl_bootstrap 存在且可执行" 1

QVM_FILE=$(file "${QVM_BIN}" 2>/dev/null)
echo "${QVM_FILE}" | grep -q "ELF" && check "qvm_bootstrap 是ELF格式" 0 || check "qvm_bootstrap 是ELF格式" 1

QCL_FILE=$(file "${QCL_BIN}" 2>/dev/null)
echo "${QCL_FILE}" | grep -q "ELF" && check "qcl_bootstrap 是ELF格式" 0 || check "qcl_bootstrap 是ELF格式" 1

echo ""

# -----------------------------------------------------------------------------
# 2. 配置文件
# -----------------------------------------------------------------------------
echo "2. 配置文件"
[ -f "${CONF_FILE}" ] && check "qvm_env.conf 存在" 0 || check "qvm_env.conf 存在" 1
[ -f "${QSM_ROOT}/qvm_env_init.sh" ] && check "qvm_env_init.sh 存在" 0 || check "qvm_env_init.sh 存在" 1
[ -f "${QSM_ROOT}/qvm_run_21_circuits.sh" ] && check "qvm_run_21_circuits.sh 存在" 0 || check "qvm_run_21_circuits.sh 存在" 1
echo ""

# -----------------------------------------------------------------------------
# 3. QEntL源码
# -----------------------------------------------------------------------------
echo "3. QEntL源码"
QENTL_COUNT=$(find "${QENTL_ROOT}" -name '*.qentl' | wc -l)
echo "  .qentl文件数: ${QENTL_COUNT}"
[ "${QENTL_COUNT}" -eq 220 ] && check ".qentl文件数=220" 0 || check ".qentl文件数=220" 1

QBC_COUNT=$(find "${QENTL_ROOT}" -name '*.qbc' | wc -l)
echo "  .qbc文件数: ${QBC_COUNT}"
[ "${QBC_COUNT}" -eq 220 ] && check ".qbc文件数=220" 0 || check ".qbc文件数=220" 1

MISSING=0
for f in $(find "${QENTL_ROOT}" -name '*.qentl'); do
    if [ ! -f "${f%.qentl}.qbc" ]; then
        MISSING=$((MISSING + 1))
    fi
done
echo "  缺失.qbc: ${MISSING}"
[ "${MISSING}" -eq 0 ] && check "无缺失.qbc" 0 || check "无缺失.qbc" 1

EMPTY=0
for f in $(find "${QENTL_ROOT}" -name '*.qbc' -empty); do
    EMPTY=$((EMPTY + 1))
done
echo "  空.qbc: ${EMPTY}"
[ "${EMPTY}" -eq 0 ] && check "无空.qbc" 0 || check "无空.qbc" 1
echo ""

# -----------------------------------------------------------------------------
# 4. 21个有效量子电路
# -----------------------------------------------------------------------------
echo "4. 有效量子电路（头部0x14）"

VALID=0
while IFS= read -r line; do
    VALID=$((VALID + 1))
done < <(find "${QENTL_ROOT}" -name '*.qbc' -type f | while read -r f; do
    first=$(xxd -l1 -p "$f" 2>/dev/null)
    if [ "$first" = "14" ]; then
        echo "VALID"
    fi
done)

echo "  有效电路数: ${VALID}"
[ "${VALID}" -eq 21 ] && check "有效电路数=21" 0 || check "有效电路数=21" 1

# 检查各模块电路
QSM_VALID=$(find "${QENTL_ROOT}/Models/QSM" -name '*.qbc' | while read -r f; do
    first=$(xxd -l1 -p "$f" 2>/dev/null)
    [ "$first" = "14" ] && echo "OK"
done | wc -l)
echo "  QSM有效电路: ${QSM_VALID}/5"
[ "${QSM_VALID}" -eq 5 ] && check "QSM电路数=5" 0 || check "QSM电路数=5" 1

REF_VALID=$(find "${QENTL_ROOT}/Models/Ref" -name '*.qbc' | while read -r f; do
    first=$(xxd -l1 -p "$f" 2>/dev/null)
    [ "$first" = "14" ] && echo "OK"
done | wc -l)
echo "  Ref有效电路: ${REF_VALID}/4"
[ "${REF_VALID}" -eq 4 ] && check "Ref电路数=4" 0 || check "Ref电路数=4" 1

SOM_VALID=$(find "${QENTL_ROOT}/Models/SOM" -name '*.qbc' | while read -r f; do
    first=$(xxd -l1 -p "$f" 2>/dev/null)
    [ "$first" = "14" ] && echo "OK"
done | wc -l)
echo "  SOM有效电路: ${SOM_VALID}/2"
[ "${SOM_VALID}" -eq 2 ] && check "SOM电路数=2" 0 || check "SOM电路数=2" 1

WEQ_VALID=$(find "${QENTL_ROOT}/Models/WeQ" -name '*.qbc' | while read -r f; do
    first=$(xxd -l1 -p "$f" 2>/dev/null)
    [ "$first" = "14" ] && echo "OK"
done | wc -l)
echo "  WeQ有效电路: ${WEQ_VALID}/3"
[ "${WEQ_VALID}" -eq 3 ] && check "WeQ电路数=3" 0 || check "WeQ电路数=3" 1

QNS_VALID=$(find "${QENTL_ROOT}/System/Kernel/neural" -name '*.qbc' | while read -r f; do
    first=$(xxd -l1 -p "$f" 2>/dev/null)
    [ "$first" = "14" ] && echo "OK"
done | wc -l)
echo "  QNS有效电路: ${QNS_VALID}/2"
[ "${QNS_VALID}" -eq 2 ] && check "QNS电路数=2" 0 || check "QNS电路数=2" 1

QDFS_VALID=$(find "${QENTL_ROOT}/System/Kernel/filesystem" -name '*.qbc' | while read -r f; do
    first=$(xxd -l1 -p "$f" 2>/dev/null)
    [ "$first" = "14" ] && echo "OK"
done | wc -l)
echo "  QDFS有效电路: ${QDFS_VALID}/2"
[ "${QDFS_VALID}" -eq 2 ] && check "QDFS电路数=2" 0 || check "QDFS电路数=2" 1

# 集成测试（剩余3个）
INTEGRATION_VALID=$((VALID - QSM_VALID - REF_VALID - SOM_VALID - WEQ_VALID - QNS_VALID - QDFS_VALID))
echo "  集成测试电路: ${INTEGRATION_VALID}/3"
[ "${INTEGRATION_VALID}" -eq 3 ] && check "集成测试电路数=3" 0 || check "集成测试电路数=3" 1
echo ""

# -----------------------------------------------------------------------------
# 5. CNOT回归测试
# -----------------------------------------------------------------------------
echo "5. CNOT回归测试"

CNOT_TEST="/tmp/qvm_verify_cnot.qentl"
CNOT_QBC="/tmp/qvm_verify_cnot.qbc"

cat > "${CNOT_TEST}" << 'EOF'
init 3
H 0
X 1
CNOT 0 1
CNOT 1 2
MEASURE 0 0
MEASURE 1 1
MEASURE 2 2
PRINT 0
PRINT 1
PRINT 2
STOP
EOF

"${QCL_BIN}" "${CNOT_TEST}" "${CNOT_QBC}" >/dev/null 2>&1
CNOT_EXIT=$?
[ ${CNOT_EXIT} -eq 0 ] && check "CNOT编译成功" 0 || check "CNOT编译成功" 1

CNOT_OUT=$("${QVM_BIN}" "${CNOT_QBC}" 2>&1)
CNOT_EXIT2=$?
[ ${CNOT_EXIT2} -eq 0 ] && check "CNOT QVM执行成功" 0 || check "CNOT QVM执行成功" 1

# 检查字节码
CNOT_HEX=$(xxd -p "${CNOT_QBC}" | head -1)
echo "  字节码(前12字节): ${CNOT_HEX:0:12}"
echo "${CNOT_HEX}" | grep -q "040001040102" && check "CNOT字节码正确(04 00 01 04 01 02)" 0 || check "CNOT字节码正确" 1

echo ""

# -----------------------------------------------------------------------------
# 6. QVM全量验证
# -----------------------------------------------------------------------------
echo "6. QVM全量验证（21个有效电路）"

QVM_PASS=0
QVM_FAIL=0

while IFS= read -r line; do
    qbc="${line#VALID|}"
    "${QVM_BIN}" "${qbc}" >/dev/null 2>&1 && QVM_PASS=$((QVM_PASS + 1)) || QVM_FAIL=$((QVM_FAIL + 1))
done < <(find "${QENTL_ROOT}" -name '*.qbc' -type f | while read -r f; do
    first=$(xxd -l1 -p "$f" 2>/dev/null)
    if [ "$first" = "14" ]; then
        echo "VALID|$f"
    fi
done)

echo "  PASS: ${QVM_PASS}"
echo "  FAIL: ${QVM_FAIL}"
[ ${QVM_FAIL} -eq 0 ] && check "21个电路QVM全部通过" 0 || check "21个电路QVM全部通过" 1
echo ""

# -----------------------------------------------------------------------------
# 总结
# -----------------------------------------------------------------------------
TOTAL=$((PASS + FAIL))
echo "=============================================="
echo "验证完成"
echo "=============================================="
echo ""
echo "  总计: ${TOTAL}"
echo "  通过: ${PASS}"
echo "  失败: ${FAIL}"
echo ""

if [ ${FAIL} -eq 0 ]; then
    echo "✅ QVM环境验证通过"
else
    echo "⚠️ ${FAIL} 项未通过"
fi

exit ${FAIL}
