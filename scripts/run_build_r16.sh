#!/bin/bash
# R16: Full remaining compilation + QVM verification
# Covers: QNS, QDFS, Compiler, Kernel, Services, GUI + docs/examples
set -e
cd /root/QSM
echo "=== R16 Full Build ==="

# Count function
build_dir() {
  local d="$1" label="$2"
  [ ! -d "$d" ] && return
  local cnt=0 ok=0 miss=0 qvm_ok=0 qvm_fail=0
  for f in "$d"/*.qentl; do [ -f "$f" ] || continue
    qbc="${f%.qentl}.qbc"
    bin/qcl_bootstrap "$f" "$qbc" >/dev/null 2>&1 && ok=$((ok+1)) || miss=$((miss+1))
    cnt=$((cnt+1))
  done
  for qbc in "$d"/*.qbc; do [ -f "$qbc" ] || continue
    bin/qvm_boot "$qbc" >/dev/null 2>&1 && qvm_ok=$((qvm_ok+1)) || qvm_fail=$((qvm_fail+1))
  done
  echo "$label: compile $ok/$cnt QVM $qvm_ok/$((qvm_ok+qvm_fail))"
}

echo "--- QNS ---"
build_dir QEntL/System/Kernel/neural "QNS"

echo "--- QDFS ---"
build_dir QEntL/System/Kernel/filesystem "QDFS"

echo "--- Compiler CLI ---"
build_dir QEntL/System/Compiler/bin/cli "Compiler_CLI"
echo "--- Compiler Platform ---"
build_dir QEntL/System/Compiler/bin/platform "Compiler_Platform"
echo "--- Compiler Root ---"
for f in QEntL/System/Compiler/qentl_debug.qentl QEntL/System/Compiler/qentl_profiler.qentl QEntL/System/Compiler/src/compiler.qentl; do
  [ -f "$f" ] || continue
  qbc="${f%.qentl}.qbc"
  bin/qcl_bootstrap "$f" "$qbc" >/dev/null 2>&1
  bin/qvm_boot "$qbc" >/dev/null 2>&1 && echo "OK $f" || echo "FAIL $f"
done
echo "--- Compiler src subdirs ---"
for d in QEntL/System/Compiler/src/backend/build \
         QEntL/System/Compiler/src/backend/bytecode/generator \
         QEntL/System/Compiler/src/backend/bytecode/optimizer \
         QEntL/System/Compiler/src/backend/debug \
         QEntL/System/Compiler/src/backend/debug_info \
         QEntL/System/Compiler/src/backend/ir \
         QEntL/System/Compiler/src/backend/linker \
         QEntL/System/Compiler/src/backend/optimizer \
         QEntL/System/Compiler/src/diagnostic \
         QEntL/System/Compiler/src/frontend/lexer \
         QEntL/System/Compiler/src/frontend/parser \
         QEntL/System/Compiler/src/frontend/semantic \
         QEntL/System/Compiler/src/testing \
         QEntL/System/Compiler/src/utils; do
  build_dir "$d" "$(basename $d)"
done

echo "--- Kernel core ---"
build_dir QEntL/System/Kernel/kernel "Kernel"
echo "--- Kernel top-level ---"
for f in QEntL/System/Kernel/qns_qdfs_dataflow.qentl QEntL/System/Kernel/qns_qdfs_reverse_flow_circuit.qentl; do
  [ -f "$f" ] || continue
  qbc="${f%.qentl}.qbc"
  bin/qcl_bootstrap "$f" "$qbc" >/dev/null 2>&1
  bin/qvm_boot "$qbc" >/dev/null 2>&1 && echo "OK $f" || echo "FAIL $f"
done
echo "--- Services ---"
build_dir QEntL/System/Kernel/services "Services"
echo "--- GUI ---"
build_dir QEntL/System/Kernel/gui "GUI"

echo "--- Scripts ---"
build_dir QEntL/scripts "Scripts"

echo "--- Models doc subdirs ---"
for d in QEntL/Models/QSM/docs QEntL/Models/QSM/docs/project_plan \
         QEntL/Models/Ref/docs QEntL/Models/Ref/docs/project_plan \
         QEntL/Models/SOM/docs QEntL/Models/SOM/docs/project_plan \
         QEntL/Models/WeQ/docs QEntL/Models/WeQ/docs/project_plan; do
  build_dir "$d" "$(echo $d | sed 's|QEntL/||')"
done

echo "--- QNS Integration Test ---"
[ -f QEntL/Models/Models_QNS_Integration_Test.qentl ] && {
  bin/qcl_bootstrap QEntL/Models/Models_QNS_Integration_Test.qentl QEntL/Models/Models_QNS_Integration_Test.qbc >/dev/null 2>&1
  bin/qvm_boot QEntL/Models/Models_QNS_Integration_Test.qbc >/dev/null 2>&1 && echo "QNS_Int_Test OK" || echo "QNS_Int_Test FAIL"
}

echo "--- QEntL bin/qentl.qentl ---"
[ -f QEntL/System/Compiler/bin/qentl.qentl ] && {
  bin/qcl_bootstrap QEntL/System/Compiler/bin/qentl.qentl QEntL/System/Compiler/bin/qentl.qbc >/dev/null 2>&1
  bin/qvm_boot QEntL/System/Compiler/bin/qentl.qbc >/dev/null 2>&1 && echo "qentl.qentl OK" || echo "qentl.qentl FAIL"
}

echo "=== TOTAL SUMMARY ==="
echo "qentl: $(find QEntL -name '*.qentl' | wc -l)"
echo "qbc:   $(find QEntL -name '*.qbc' | wc -l)"
echo "uncompiled: $(find QEntL -name '*.qentl' -exec sh -c 'f=${1%.qentl}; [ ! -f "${f}.qbc" ] && echo "$1"' _ {} \; | wc -l)"
echo "R16 done"
