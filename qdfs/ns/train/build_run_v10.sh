#!/bin/bash
# ============================================================================
# build_run_v10.sh - 构建 qcl.qbc/qvm.qbc/v10.qbc 并运行 v10 训练
# 用法:
#   bash qdfs/ns/train/build_run_v10.sh <smoke_limit> <batch> <state> <epoch>
#   bash qdfs/ns/train/build_run_v10.sh 5 0 0 1     # 冒烟 5样本 1epoch
#   bash qdfs/ns/train/build_run_v10.sh 0 0 0 3     # 正式 batch0 态0 3epoch
# ============================================================================
set -u
cd /root/QSM/QLife || exit 1

SM="${1:-5}"
B="${2:-0}"
S="${3:-0}"
EP="${4:-1}"

echo "===== 0. 控制文件 ====="
echo "$B" > qdfs/ns/train/current_batch.txt
echo "$S" > qdfs/ns/train/current_state.txt
echo "$SM" > qdfs/ns/train/smoke_limit.txt
grep -n '^var g_epoch' qdfs/ns/train/qscl_32x32_v10.qentl
sed -i "s|^var g_epoch = [0-9]*.*|var g_epoch = $EP             # 由 build_run_v10.sh 设定: 冒烟1/正式3|" qdfs/ns/train/qscl_32x32_v10.qentl
grep -n '^var g_epoch' qdfs/ns/train/qscl_32x32_v10.qentl

echo ""
echo "===== 1. 重建 run/qcl.qbc (从 qcl.qentl) ====="
cp run/qcl.qbc run/qcl.qbc.bak_v10
cp qcl.qentl input.qentl
OUT1=$(bin/qvm_boot run run/qcl.qbc 2>&1)
echo "$OUT1"
ERRS=$(grep -o 'errors=[0-9]*' <<<"$OUT1" | head -1 | cut -d= -f2)
if [ -z "$ERRS" ] || [ "$ERRS" != "0" ]; then
  echo "!!! qcl.qbc 编译失败 errors=$ERRS, 中止"
  exit 2
fi
cp output.qbc run/qcl.qbc
echo "qcl.qbc md5=$(md5sum run/qcl.qbc | cut -d' ' -f1) size=$(wc -c < run/qcl.qbc)"

echo ""
echo "===== 2. 重建 run/qvm.qbc (从 qvm.qentl) ====="
cp run/qvm.qbc run/qvm.qbc.bak_v10
cp qvm.qentl input.qentl
OUT2=$(bin/qvm_boot run run/qcl.qbc 2>&1)
echo "$OUT2"
ERRS=$(grep -o 'errors=[0-9]*' <<<"$OUT2" | head -1 | cut -d= -f2)
if [ -z "$ERRS" ] || [ "$ERRS" != "0" ]; then
  echo "!!! qvm.qbc 编译失败 errors=$ERRS, 中止"
  exit 2
fi
cp output.qbc run/qvm.qbc
echo "qvm.qbc md5=$(md5sum run/qvm.qbc | cut -d' ' -f1) size=$(wc -c < run/qvm.qbc)"

echo ""
echo "===== 3. 编译 v10.qentl → run/qscl_32x32_v10.qbc ====="
cp qdfs/ns/train/qscl_32x32_v10.qentl input.qentl
OUT3=$(bin/qvm_boot run run/qcl.qbc 2>&1)
echo "$OUT3"
ERRS=$(grep -o 'errors=[0-9]*' <<<"$OUT3" | head -1 | cut -d= -f2)
if [ -z "$ERRS" ] || [ "$ERRS" != "0" ]; then
  echo "!!! v10 编译失败 errors=$ERRS, 中止"
  exit 2
fi
cp output.qbc run/qscl_32x32_v10.qbc
cp output.qbc target.qbc
echo "v10.qbc md5=$(md5sum run/qscl_32x32_v10.qbc | cut -d' ' -f1) size=$(wc -c < run/qscl_32x32_v10.qbc)"

echo ""
echo "===== 4. 运行 (smoke_limit=$SM batch=$B state=$S epoch=$EP) ====="
STREAM=qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w
LOG=run/train_b${B}_s${S}.log
TMF=run/train_b${B}_s${S}_time.txt
ALL=run/qvm_b${B}_s${S}.all
rm -f "$STREAM" "$LOG" "$TMF" "$ALL"

T0=$(date +%s)
/usr/bin/time -v bin/qvm_boot run run/qvm.qbc > "$ALL" 2> "$TMF"
RC=$?
T1=$(date +%s)

echo "exit=$RC 耗时=$((T1-T0))s"
echo "--- /usr/bin/time 计时/RSS ---"
grep -E 'Maximum resident|Elapsed \(wall|User time|Exit status|Command being' "$TMF"

echo "--- 权重流大小 & 头 ---"
wc -c "$ALL"
head -c 300 "$ALL"; echo

echo "--- 分流 (哨兵 === 日志截断 === 之后是权重流) ---"
awk -v logf="$LOG" 'BEGIN{p=0} /=== 日志截断 ===/{p=1;next} p{print; next} {print > logf}' "$ALL" > "$STREAM"
echo "--- 训练日志 ---"
cat "$LOG"
echo "--- 权重流大小 & 头 ---"
wc -c "$STREAM"
head -c 200 "$STREAM"; echo

if [ -f "$ALL" ]; then
  echo "--- 全 stdout 尾部 500 字节 ---"
  tail -c 500 "$ALL"; echo
fi

echo "===== DONE 耗时=$((T1-T0))s ====="
