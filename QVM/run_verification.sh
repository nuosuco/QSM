#!/bin/bash
set -e
export QT_QPA_PLATFORM=offscreen
cd /root/QSM
mkdir -p QVM

for m in QSM Ref SOM WeQ; do
  echo ""
  echo "========== $m =========="
  for f in /root/QSM/QEntL/Models/$m/*.qbc; do
    [ ! -f "$f" ] && continue
    echo "=== $f ==="
    timeout 60 /root/QSM/bin/qvm_bootstrap "$f" 2>&1 | tail -15
  done
done