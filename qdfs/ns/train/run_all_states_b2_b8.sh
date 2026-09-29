#!/bin/bash
# b1~b8 × 4态 串行训练 runner (2026-09-28 v11 泄漏根治版) — 单QVM串行, RSS 264MB/态
# 每态: 不同起点 seed=1+s*100, LR=500 统一 (2026-09-26 公平叠加态), 24epoch
set -u
cd /root/QSM/QLife || exit 1
echo 0 > qdfs/ns/train/smoke_limit.txt
EP="${EP:-24}"
for B in 1 2 3 4 5 6 7 8; do
  for S in 0 1 2 3; do
    # 跳过已完成的(流文件非空且带 META 头)
    STREAM=qdfs/ns/models/qscl_32x32_b${B}_s${S}_stream.w
    if [ -s "$STREAM" ] && grep -q "META batch=${B} state=${S}" "$STREAM" 2>/dev/null; then
      echo "SKIP b${B}_s${S} (已完成)"
      continue
    fi
    echo "===== START b${B}_s${S} $(date +%H:%M:%S) ====="
    timeout 3600 bash qdfs/ns/train/build_run_v10.sh 0 "$B" "$S" "$EP" > /tmp/train_b${B}_s${S}.summary 2>&1
    RC=$?
    if [ $RC -ne 0 ]; then
      echo "FAIL b${B}_s${S} rc=$RC"
    else
      SZ=$(wc -c < "$STREAM" 2>/dev/null || echo 0)
      EPF=$(grep -oE 'ep[0-9]+: 正确[0-9]+/[0-9]+' /tmp/train_b${B}_s${S}.summary | tail -1)
      echo "OK b${B}_s${S} stream=${SZ}B ${EPF}"
    fi
    # RSS 防线检查
    AV=$(free -b | awk 'NR==2{print $7}')
    if [ "$AV" -lt 800000000 ]; then
      echo "!!! 可用内存<800MB, 停止后续训练"
      exit 3
    fi
  done
done
echo "===== ALL DONE $(date +%H:%M:%S) ====="
