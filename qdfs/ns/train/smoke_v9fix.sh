#!/bin/bash
# 冒烟/正式训练统一入口
#   smoke_limit.txt > 0  → 冒烟 (g_epoch=1, 前N样本)
#   smoke_limit.txt = 0  → 正式 (g_epoch=3, 全129样本)
# QVM二级: run/qcl.qbc = 编译器(读input.qentl→output.qbc), run/qvm.qbc = 虚拟机(读target.qbc)
# 输出路由: QVM printf→stdout(训练日志), 权重流→stderr(2>STREAM), /usr/bin/time 的 stderr 落单独文件
# 用法: bash qdfs/ns/train/smoke_v9fix.sh
cd /root/QSM/QLife || exit 1
set -u

SRC=qdfs/ns/train/qscl_32x32_v9.qentl
B=$(cat qdfs/ns/train/current_batch.txt)
S=$(cat qdfs/ns/train/current_state.txt)
SM=$(cat qdfs/ns/train/smoke_limit.txt)

echo "===== 0. 源码确认: 像素×100 缩放修复点 ====="
grep -n 'v = v \* 100' "$SRC"
echo "   态2椒盐 0<->100: $(grep -c 'g_x\[g_t2_i\] = 100' "$SRC") 处"

if [ "$SM" -gt 0 ]; then
  EPOCH=1; MODE="冒烟(前$SM样本×4态取样)"
else
  EPOCH=3; MODE="正式(全129样本×3ep)"
fi
cp "$SRC" /tmp/v9.bak.qentl
sed -i "s|var g_epoch = [0-9]*.*|var g_epoch = $EPOCH             # 由 smoke_v9fix.sh 按模式设定: 冒烟1/正式3|" "$SRC"
echo "===== 1. g_epoch=$EPOCH ($MODE) 并编译 (QVM二级 run/qcl.qbc) ====="
grep -n '^var g_epoch' "$SRC"
cp "$SRC" input.qentl
OUT=$(bin/qvm_boot run run/qcl.qbc 2>&1)
echo "$OUT"
ERRS=$(grep -o 'errors=[0-9]*' <<<"$OUT" | head -1 | cut -d= -f2)
if [ -z "$ERRS" ] || [ "$ERRS" != "0" ]; then
  echo "!!! 编译 errors!=$ERRS，中止"; exit 2
fi
echo "errors=$ERRS ✓"
cp output.qbc run/qscl_32x32_v9.qbc
cp output.qbc target.qbc
ls -la run/qscl_32x32_v9.qbc target.qbc
echo "qcl.qbc md5=$(md5sum run/qcl.qbc | cut -d' ' -f1) qvm.qbc md5=$(md5sum run/qvm.qbc | cut -d' ' -f1)"

echo "===== 2. 控制文件 ====="
echo "batch=$B state=$S smoke=$SM epoch=$EPOCH"

STREAM=qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w
LOG=run/train_b${B}_s${S}.log
TMF=run/train_b${B}_s${S}_time.txt
echo "===== 3. 清理旧产物 ====="
rm -f "$STREAM" "$LOG" "$TMF"

echo "===== 4. 跑 ($MODE) ====="
# QVM二级: run/qvm.qbc 为运行时, target.qbc 为脚本（qvm_boot 只接受1个参数）
# 输出路由: QVM printf→stderr。训练日志 与 权重流 都走 stderr，
#   用 "=== 日志截断 ===" 哨兵行分流（QVM 内无法区分 fd，故由 shell 切分）。
# 计时: 不用 /usr/bin/time（其统计走外层 stderr 会污染分流），改用 shell time 子串。
# 输出路由（实测,2026-09-13）: QVM printf→stdout；/usr/bin/time -v→stderr。
# 哨兵 "=== 日志截断 ===" 由 v9 在 save_weights_stderr() 起始处打印，
# 用于把 stdout 内的训练日志与权重流分家（两者同为 stdout，QVM 内无法分 fd）。
cp run/qscl_32x32_v9.qbc target.qbc
rm -f "$LOG" "$TMF" run/qvm_b${B}_s${S}.all
T0=$(date +%s)
{ /usr/bin/time -v bin/qvm_boot run run/qvm.qbc > run/qvm_b${B}_s${S}.all ; } 2> "$TMF"
RC=$?
T1=$(date +%s)
# 哨兵切分: 哨兵行之后 = 权重流(标记+515类值)；之前 = 训练日志
awk -v logf="$LOG.2" 'BEGIN{p=0} /=== 日志截断 ===/{p=1;next} p{print; next} {print > logf}' \
    run/qvm_b${B}_s${S}.all > "$STREAM"
mv -f "$LOG.2" "$LOG"
EL=$((T1-T0))
echo "exit=$RC 耗时=${EL}s"
echo "--- 计时/RSS (/usr/bin/time VmHWM) ---"
grep -E 'Maximum resident|Elapsed \(wall|User time|Exit status' "$TMF"
echo "--- 权重流大小 ---"; wc -c "$STREAM"
echo "--- 权重流头 120 字节 ---"; head -c 120 "$STREAM"; echo
echo "--- 训练日志 ---"; cat "$LOG"
echo "===== DONE 耗时=${EL}s ====="
