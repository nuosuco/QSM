#!/bin/bash
cd /root/QSM
echo "=== VM core modules ==="
for dir in \
  QEntL/System/VM/src/core/quantum \
  QEntL/System/VM/src/core/debug \
  QEntL/System/VM/src/core/interpreter \
  QEntL/System/VM/src/core/memory \
  QEntL/System/VM/src/core/os_interface \
  QEntL/System/VM/bin/cli \
  QEntL/System/VM; do
  if [ -d "$dir" ]; then
    cnt=0; ok=0; miss=0
    for f in "$dir"/*.qentl; do [ -f "$f" ] || continue
      qbc="${f%.qentl}.qbc"
      bin/qcl_bootstrap "$f" "$qbc" > /dev/null 2>&1
      [ $? -eq 0 ] && ok=$((ok+1)) || miss=$((miss+1))
      cnt=$((cnt+1))
    done
    qvm_ok=0; qvm_fail=0
    for qbc in "$dir"/*.qbc; do [ -f "$qbc" ] || continue
      if bin/qvm_boot "$qbc" > /dev/null 2>&1; then qvm_ok=$((qvm_ok+1)); else qvm_fail=$((qvm_fail+1)); fi
    done
    if [ $cnt -gt 0 ]; then echo "VM/$(basename $dir): compile $ok/$cnt, QVM $qvm_ok/$((qvm_ok+qvm_fail)) ok"; fi
  fi
done

echo "=== Models ==="
for model in QSM Ref WeQ SOM; do
  cnt=0; ok=0
  for f in QEntL/Models/$model/*.qentl; do [ -f "$f" ] || continue
    qbc="${f%.qentl}.qbc"
    bin/qcl_bootstrap "$f" "$qbc" > /dev/null 2>&1
    [ $? -eq 0 ] && ok=$((ok+1))
    cnt=$((cnt+1))
  done
  qvm_ok=0; qvm_fail=0
  for qbc in QEntL/Models/$model/*.qbc; do [ -f "$qbc" ] || continue
    if bin/qvm_boot "$qbc" > /dev/null 2>&1; then qvm_ok=$((qvm_ok+1)); else qvm_fail=$((qvm_fail+1)); fi
  done
  echo "Models/$model: compile $ok/$cnt, QVM $qvm_ok/$((qvm_ok+qvm_fail)) ok"
done
