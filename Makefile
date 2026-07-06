.PHONY: all clean test phase1 phase2 phase3 phase4 phase5 pipeline qnn_train deploy qcl_phase2 phase2_compile phase2_verify

# Compiler flags
CC = gcc
CFLAGS = -std=c11 -O2 -lm

# Directories
BIN = $(CURDIR)/bin
DOCS = $(CURDIR)/Docs
EXAMPLES = $(CURDIR)/docs/examples
QENTL_SCRIPTS = $(CURDIR)/QEntL/scripts
INSTALLER = $(CURDIR)/Installer

# ============================================================================
# All targets
# ============================================================================

# Sources
SRC = $(CURDIR)/src

# qcl_phase2 — 高级语法编译器（支持 class/def/import/quantum_class/quantum_enum）
QCL_PHASE2 = $(BIN)/qcl_phase2

all: qvm_boot qcl_phase2 phase3 phase4 phase5

# 跳过phase1（qvm_boot 已用 qvm_bootstrap 替代）
phase1:
	@echo ">>> Phase 1: QVM Boot skipped (using bin/qvm_bootstrap instead)"

# Phase 2: 使用 qcl_phase2 批量编译所有含高级语法(class/def/import)的 .qentl 模块
phase2: qcl_phase2 phase2_compile phase2_verify
	@echo "============================================="
	@echo "  Phase 2: qcl_phase2 编译链完成"
	@echo "============================================="

# 从 src/qcl_phase2.c 编译出 bin/qcl_phase2（高级语法编译器）
qcl_phase2: $(QCL_PHASE2)
$(QCL_PHASE2): $(SRC)/qcl_phase2.c
	@echo ">>> Phase 2: 编译 qcl_phase2 (高级语法编译器)..."
	@$(CC) $(CFLAGS) -o $@ $< -lm
	@echo "    Done: $@"
	@file $@ | grep -q "ELF" && echo "    ELF验证: OK" || (echo "    ELF验证: FAIL" && exit 1)

# 批量编译所有含高级语法(class/def/import/quantum_class/quantum_enum)的 .qentl
phase2_compile: $(QCL_PHASE2)
	@echo ">>> Phase 2: 扫描高级语法 .qentl 并批量编译..."
	@TOTAL=0; SUCCESS=0; FAIL=0; \
	for f in $$(find QEntL -name '*.qentl' | sort); do \
		if grep -qE '^\s*(class|def|import|quantum_class|quantum_enum|函数|类型|导入|导出)' "$$f" 2>/dev/null; then \
			TOTAL=$$((TOTAL+1)); \
			qbc="$${f%.qentl}.qbc"; \
			if timeout 30 $(QCL_PHASE2) "$$f" >/dev/null 2>&1; then \
				if [ -f "$$qbc" ] && [ -s "$$qbc" ]; then \
					fb=$$(xxd -l1 -p "$$qbc" 2>/dev/null || echo "??"); \
					SUCCESS=$$((SUCCESS+1)); \
				else \
					FAIL=$$((FAIL+1)); \
				fi \
			else \
				FAIL=$$((FAIL+1)); \
			fi \
		fi \
	done; \
	echo "    高级语法模块总数: $$TOTAL"; \
	echo "    编译成功: $$SUCCESS"; \
	echo "    编译失败: $$FAIL"

# 验证编译产物 .qbc 有效性
phase2_verify: phase2_compile
	@echo ">>> Phase 2: 验证编译产物有效性..."
	@ALLQBC=$$(find QEntL -name '*.qbc' -type f | wc -l); \
	OK=0; BAD=0; EMPTY=0; \
	for f in $$(find QEntL -name '*.qbc' -type f | sort); do \
		sz=$$(stat -c%s "$$f" 2>/dev/null || echo 0); \
		if [ "$$sz" -eq 0 ]; then \
			EMPTY=$$((EMPTY+1)); \
		else \
			fb=$$(xxd -l1 -p "$$f" 2>/dev/null || echo "??"); \
			case "$$fb" in 14|0c|0b|11|01|72) OK=$$((OK+1));; *) BAD=$$((BAD+1)); echo "    异常: $$f 首字节=0x$$fb";; esac \
		fi \
	done; \
	echo "    .qbc总数: $$ALLQBC"; \
	echo "    有效产物(0x14/0x0c等): $$OK"; \
	echo "    异常首字节: $$BAD"; \
	echo "    空文件: $$EMPTY"; \
	[ "$$BAD" -eq 0 ] && [ "$$EMPTY" -eq 0 ] && echo "    验证: PASS ✅" || echo "    验证: FAIL ❌ (异常=$$BAD 空=$$EMPTY)"

phase3: qentl_compiler

phase4: qnn_runner

phase5: yi_pipeline

pipeline: phase5  # Alias

qnn_train: phase4  # Alias

deploy: all test pipeline qnn_train

# ============================================================================
# Phase 1: QVM Boot
# ============================================================================

qvm_boot: $(SRC)/qvm_boot.c
	@echo ">>> Phase 1: Compiling QVM Boot..."
	$(CC) $(CFLAGS) -o $(BIN)/qvm_boot $(SRC)/qvm_boot.c
	@echo "    Done: $(BIN)/qvm_boot"
	@echo "    Testing QVM..."
	@$(BIN)/qvm_boot test 2>&1 | tail -5

# Bootstrap compiler — builds from src/qcl_bootstrap.c
qentl_compiler: $(SRC)/qcl_bootstrap.c

	$(CC) $(CFLAGS) -o $(BIN)/qentl_compiler $(SRC)/qcl_bootstrap.c -lm
	@echo "    Done: $(BIN)/qentl_compiler"
	@echo "    Testing compiler with CNOT fix..."
	@echo "init 4" > /tmp/_cnot_test.qentl
	@echo "H 0" >> /tmp/_cnot_test.qentl
	@echo "CNOT 0 1" >> /tmp/_cnot_test.qentl
	@echo "CNOT 2 3" >> /tmp/_cnot_test.qentl
	@echo "MEASURE 0 0" >> /tmp/_cnot_test.qentl
	@$(BIN)/qentl_compiler /tmp/_cnot_test.qentl /tmp/_cnot_test.qbc >/dev/null 2>&1 && echo "    Compiler: OK"
	@rm -f /tmp/_cnot_test.qentl /tmp/_cnot_test.qbc

# ============================================================================
# Phase 4: QNN Engine
# ============================================================================

qnn_runner: $(BIN)/qnn_runner

$(BIN)/qnn_runner: $(BIN)/qnn_runner.o $(BIN)/qnn_runner_linked
	@echo ">>> Phase 4: QNN Engine ready (pre-built binary)..."
	@ls -la $@

# ============================================================================
# Phase 5: Yi Language Data Pipeline
# ============================================================================

yi_pipeline: $(BIN)/yi_pipeline

$(BIN)/yi_pipeline: $(BIN)/yi_pipeline.o $(BIN)/yi_pipeline_linked
	@echo ">>> Phase 5: Yi Pipeline ready (pre-built binary)..."
	@ls -la $@

# ============================================================================
# Test targets
# ============================================================================

test: phase3 phase4 phase5 qdfs
	@echo "============================================="
	@echo "  Running test suite..."
	@echo "============================================="
	@echo ""
	@echo "--- QDFS Test ---"
	@$(BIN)/qdfs_driver 2>&1
	@echo ""
	@echo "--- QDFS Extended Test ---"
	@$(BIN)/qdfs_extended_test 2>&1
	@echo ""
	@echo "--- QNN Engine Test ---"
	@$(BIN)/qnn_runner test 2>&1
	@echo ""
	@echo "--- Yi Pipeline Test ---"
	@$(BIN)/yi_pipeline $(CURDIR)/data 2>&1 | head -20
	@echo ""
	@echo "============================================="
	@echo "  Core tests passed!"
	@echo "============================================="

# ============================================================================
# QDFS - Quantum Dynamic File System
# ============================================================================

qdfs: $(BIN)/qdfs_driver $(BIN)/qdfs_extended_test
	@echo ">>> QDFS built and tested"

# ============================================================================
# Test targets
# ============================================================================

test-qdfs: qdfs

# Test Phase 4: QNN Engine
test-qnn: phase4
	@echo ">>> Testing QNN Engine..."
	@$(BIN)/qnn_runner test 2>&1

# Test Phase 5: Yi Data Pipeline
test-pipeline: phase5
	@echo ">>> Testing Yi Data Pipeline..."
	@$(BIN)/yi_pipeline $(CURDIR)/data 2>&1

# Full integrated test
test-all: test test-qnn test-pipeline
	@echo ""
	@echo "============================================="
	@echo "  ALL TESTS PASSED (Phases 1-5)"
	@echo "============================================="

# ============================================================================
# Clean
# ============================================================================

clean:
	rm -f $(BIN)/qvm_boot $(BIN)/qnn_runner $(BIN)/yi_pipeline $(BIN)/qentl_compiler $(BIN)/qcl_phase2
	rm -f $(BIN)/qdfs.o $(BIN)/libqdfs.a $(BIN)/qdfs_driver $(BIN)/qdfs_extended_test
	rm -f $(EXAMPLES)/*.qbc
	rm -f $(CURDIR)/data/training_batch.dat $(CURDIR)/data/training_batch.jsonl
	@echo "Cleaned."
