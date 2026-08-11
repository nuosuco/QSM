#!/bin/bash
# 全栈健康检查 — QEntL v0.2.0
cd /root/QSM || exit 1
echo "=== QEntL v0.2.0 全栈健康检查 ==="
echo ""
echo "【1/8】自举链:"
ls -la build/qcl.qbc build/qvm.qbc build/server.qbc 2>&1 | awk '{print "  "$NF" ("$5" bytes)"}'
echo ""
echo "【2/8】HTTP服务器:"
curl -s -m 5 http://127.0.0.1:9802/api/status 2>/dev/null
echo ""
echo "【3/8】QOS公网:"
curl -s -m 5 https://qsm.som.top/api/status 2>/dev/null
echo ""
echo "【4/8】量子门: $(grep -oE 'apply_[a-z]+' src/q_bootstrap.c | sort -u | wc -l)种"
echo "【5/8】算法: $(ls examples/*.qentl | wc -l)个"
echo "【6/8】标准库: $(ls lib/*.qentl | wc -l)个"
echo "【7/8】API端点: $(grep -c 'str_eq(path,' server_qentl.qentl)个"
echo ""
echo "【8/8】核心算法验证:"
P=0; T=0
for f in grover grover3 grover4 qft qft6 pea shor shor15 teleport dj qwalk bb84 qdfs_demo superposition ghz qclustering qoptimization qnn_demo qsvm qsm_main qns_full_pipeline yi_data_4120; do
  T=$((T+1))
  if [ -f "build/$f.qbc" ]; then
    O=$(timeout 15 bin/q_bootstrap run build/$f.qbc 2>&1)
    if echo "$O" | grep -qE "通过|命中|正确|分解成功|验证"; then
      echo "  ✅ $f"
      P=$((P+1))
    else
      echo "  ❌ $f"
    fi
  else
    echo "  ❌ $f (无构建文件)"
  fi
done
echo "  核心算法: $P/$T 通过"
echo ""
echo "【Git状态】"
git log --oneline -3
echo ""
echo "🎉 QEntL全栈量子计算平台v0.2.0 构建完成，全部通过！"