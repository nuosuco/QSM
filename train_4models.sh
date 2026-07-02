#!/bin/bash
# 四大模型协调训练: QSM / SOM / WeQ / Ref × 3 epoch
# 仅处理 0x14 头部的 .qbc (find + xxd 过滤)
cd /root/QSM

run_model() {
  local model="$1" dir="$2"
  # dynamic: find 0x14-header .qbc only
  local files=()
  while IFS= read -r f; do
    files+=("$f")
  done < <(find "$dir" -name '*.qbc' -exec sh -c 'xxd -l1 -p "$1" | grep -q 14 && echo "$1"' _ {} \;)
  # add integration test to QSM
  if [ "$model" = "QSM" ]; then
    if [ -f QEntL/Models/Models_QNS_Integration_Test.qbc ]; then
      files+=("QEntL/Models/Models_QNS_Integration_Test.qbc")
    fi
  fi
  echo "======================================================================"
  echo "  模型: $model  (${#files[@]} 个电路)"
  echo "======================================================================"
  for F in "${files[@]}"; do
    BASE=$(basename "$F" .qbc)
    TCYC=0; TGAT=0; OK=0
    for E in 1 2 3; do
      LINE=$(bin/qvm_bootstrap "$F" 2>&1 | grep -E '执行完成:.*周期.*门操作')
      if [ -n "$LINE" ]; then
        CYC=$(echo "$LINE" | grep -o '[0-9]\+ 周期' | grep -o '[0-9]\+')
        GAT=$(echo "$LINE" | grep -o '[0-9]\+ 门操作' | grep -o '[0-9]\+')
        printf "  Epoch %d | %-55s %s cycles, %s gates\n" "$E" "$BASE" "$CYC" "$GAT"
        TCYC=$((TCYC+CYC)); TGAT=$((TGAT+GAT)); OK=$((OK+1))
      else
        printf "  Epoch %d | %-55s FAILED\n" "$E" "$BASE"
      fi
    done
    if [ $OK -gt 0 ]; then
      printf "  %-55s 均值: %d 周期, %d 门操作  (成功 %d/3)\n" "$BASE" $((TCYC/OK)) $((TGAT/OK)) $OK
    fi
    echo ""
  done
}

run_model QSM QEntL/Models/QSM
run_model SOM QEntL/Models/SOM
run_model WeQ QEntL/Models/WeQ
run_model Ref QEntL/Models/Ref
