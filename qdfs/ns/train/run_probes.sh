#!/bin/bash
# 内存归属探针: a=仅训练热路径, b=仅保存循环。分别测 VmHWM/耗时, 判定泄漏来源。
cd /root/QSM/QLife || exit 1
for tag in a b; do
  SRC=qdfs/ns/train/rss_probe_$tag.qentl
  echo "########## PROBE $tag : $SRC ##########"
  cp "$SRC" input.qentl
  OUT=$(bin/qvm_boot run run/qcl.qbc 2>&1)
  E=$(grep -o 'errors=[0-9]*' <<<"$OUT" | head -1 | cut -d= -f2)
  echo "compile errors=${E:-none}"
  [ "${E:-x}" != "0" ] && { echo "!!! 编译失败, 跳过 $tag"; continue; }
  cp output.qbc target.qbc
  rm -f run/probe_$tag.out
  T0=$(date +%s)
  /usr/bin/time -v bin/qvm_boot run run/qvm.qbc > run/probe_$tag.out 2> run/probe_$tag.tmf
  RC=$?
  T1=$(date +%s)
  echo "exit=$RC wall=$((T1-T0))s"
  echo "-- stdout tail --"; tail -3 run/probe_$tag.out
  echo "-- time -v key --"
  grep -E 'Maximum resident|Elapsed \(wall|User time|System time' run/probe_$tag.tmf
done
echo "########## 汇总 ##########"
for tag in a b; do
  H=$(grep 'Maximum resident' run/probe_$tag.tmf | awk '{print $NF}')
  W=$(grep 'Elapsed (wall clock)' run/probe_$tag.tmf | sed 's/.*: //')
  echo "probe_$tag VmHWM=${H}kB wall=$W"
done
