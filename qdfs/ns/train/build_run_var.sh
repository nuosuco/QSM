#!/bin/bash
# ============================================================================
# build_run_var.sh - 变体数据训练 (基于 v10-VAR)
# 用法: bash qdfs/ns/train/build_run_var.sh <smoke_limit> <batch> <state> <epoch>
# 数据: qdfs/ns/data/variant_b{B}.comma.data (每类6变体)
# g_ns 从 variant_ns.txt 控制文件读
# 权重流: qdfs/ns/models/variant_b{B}_s{S}_stream.w
# ============================================================================
set -u
cd /root/QSM/QLife || exit 1

SM="${1:-5}"
B="${2:-0}"
S="${3:-0}"
EP="${4:-10}"

# 侧别隔离: A/B 两侧共用 build_run_var.sh 会互踩 current_batch.txt
# 按 batch 范围自动判断侧别 (b0-15=A, b16-41=B), 用不同控制文件
if [ $B -le 15 ]; then
  BATCHFILE=qdfs/ns/train/current_batch_A.txt
  STATEFILE=qdfs/ns/train/current_state_A.txt
  SMOKEFILE=qdfs/ns/train/smoke_limit_A.txt
  NSFILE=qdfs/ns/train/variant_ns_A.txt
  SID=A
else
  BATCHFILE=qdfs/ns/train/current_batch_B.txt
  STATEFILE=qdfs/ns/train/current_state_B.txt
  SMOKEFILE=qdfs/ns/train/smoke_limit_B.txt
  NSFILE=qdfs/ns/train/variant_ns_B.txt
  SID=B
fi
SIDFILE=qdfs/ns/train/current_side.txt

echo "===== 0. 控制文件 (${SID}侧) ====="
echo "$B" > "$BATCHFILE"
echo "$S" > "$STATEFILE"
echo "$SM" > "$SMOKEFILE"
echo "$SID" > "$SIDFILE"
# variant_ns.txt = 该批次行数 (类数×6), 侧别隔离写各自文件
NNS=$(wc -l < "qdfs/ns/data/variant_b${B}.comma.data" 2>/dev/null || echo 0)
echo "$NNS" > "$NSFILE"
echo "g_ns=$NNS ($NSFILE)"
grep -n '^var g_epoch' qdfs/ns/train/qscl_32x32_v10_variant.qentl
sed -i "s|^var g_epoch = [0-9]*.*|var g_epoch = $EP             # 由 build_run_var.sh 设定|" qdfs/ns/train/qscl_32x32_v10_variant.qentl
grep -n '^var g_epoch' qdfs/ns/train/qscl_32x32_v10_variant.qentl

# 空批次跳过
if [ ! -s "qdfs/ns/data/variant_b${B}.comma.data" ]; then
  echo "batch $B 无变体数据, 跳过"
  exit 3
fi

echo ""
echo "===== 1. 重建 run/qcl.qbc (从 qcl.qentl) ====="
cp run/qcl.qbc run/qcl.qbc.bak_var 2>/dev/null
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
cp run/qvm.qbc run/qvm.qbc.bak_var 2>/dev/null
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
echo "===== 3. 编译 v10-VAR.qentl → run/qscl_32x32_v10_var.qbc ====="
cp qdfs/ns/train/qscl_32x32_v10_variant.qentl input.qentl
OUT3=$(bin/qvm_boot run run/qcl.qbc 2>&1)
echo "$OUT3"
ERRS=$(grep -o 'errors=[0-9]*' <<<"$OUT3" | head -1 | cut -d= -f2)
if [ -z "$ERRS" ] || [ "$ERRS" != "0" ]; then
  echo "!!! v10-VAR 编译失败 errors=$ERRS, 中止"
  exit 2
fi
cp output.qbc run/qscl_32x32_v10_var.qbc
cp output.qbc target.qbc
echo "v10-var.qbc md5=$(md5sum run/qscl_32x32_v10_var.qbc | cut -d' ' -f1) size=$(wc -c < run/qscl_32x32_v10_var.qbc)"

echo ""
echo "===== 4. 运行 (smoke_limit=$SM batch=$B state=$S epoch=$EP) ====="
STREAM=qdfs/ns/models/variant_b${B}_s${S}_stream.w
LOG=run/train_var_b${B}_s${S}.log
TMF=run/train_var_b${B}_s${S}_time.txt
ALL=run/qvm_var_b${B}_s${S}.all
rm -f "$STREAM" "$LOG" "$TMF" "$ALL"

T0=$(date +%s)
/usr/bin/time -v bin/qvm_boot run run/qvm.qbc > "$ALL" 2> "$TMF"
RC=$?
T1=$(date +%s)

echo "exit=$RC 耗时=$((T1-T0))s"
echo "--- /usr/bin/time 计时/RSS ---"
grep -E 'Maximum resident|Elapsed \(wall|User time|Exit status|Command being' "$TMF"

echo "--- 分流 (哨兵 === 日志截断 === 之后是权重流) ---"
awk -v logf="$LOG" 'BEGIN{p=0} /=== 日志截断 ===/{p=1;next} p{print; next} {print > logf}' "$ALL" > "$STREAM"
echo "--- 训练日志 ---"
cat "$LOG"
echo "--- 权重流大小 ---"
wc -c "$STREAM"
head -c 200 "$STREAM"; echo

if [ -f "$ALL" ]; then
  echo "--- 全 stdout 尾部 500 字节 ---"
  tail -c 500 "$ALL"; echo
fi

echo "===== DONE 耗时=$((T1-T0))s ====="
