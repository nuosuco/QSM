#!/bin/bash
cd /root/QSM/QLife
DONE=$(grep -c '\[lr15ep30\]' /tmp/train_full_lr15ep30.log 2>/dev/null)
[ -z "$DONE" ] && DONE=0
NWF=$(find qdfs/ns/models -name 'variant_b*_s*_stream.w' -size +0c 2>/dev/null | wc -l)
PROC=$(ps aux | grep -E 'build_run_var|qvm_boot run run/qvm' | grep -v grep | wc -l)
LATEST=$(grep '\[lr15ep30\]' /tmp/train_full_lr15ep30.log 2>/dev/null | tail -1 | sed 's/  \[lr15ep30\] //')
echo "[$(date '+%m-%d %H:%M')] 进度=${DONE}/168 非零权重流=${NWF} 进程=${PROC} 最新=${LATEST:-无}"
if [ "$PROC" -eq 0 ] && [ "$DONE" -lt 168 ]; then
  echo "  !! 警告: 训练进程死了但没跑完 (${DONE}/168), 需重启全量"
fi
if [ "$DONE" -ge 168 ]; then
  echo "  == 全量训完 (${DONE}/168), 检查合并权重 =="
fi
