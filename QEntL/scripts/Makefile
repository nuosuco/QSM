# QEntL Bootstrap解释器 Makefile
# 支持Windows、Linux、macOS

# 编译器设置
CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2
TARGET = qentl_bootstrap
SOURCE = qentl_bootstrap.c

# Windows设置
ifeq ($(OS),Windows_NT)
    TARGET := $(TARGET).exe
    RM = del /Q
    MKDIR = mkdir
    TEST_FILE = ..\\..\\tests\\test_hello.qentl
else
    RM = rm -f
    MKDIR = mkdir -p
    TEST_FILE = ../../tests/test_hello.qentl
endif

# 默认目标
all: $(TARGET)

# 编译目标
$(TARGET): $(SOURCE)
	@echo "编译QEntL Bootstrap解释器..."
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE)
	@echo "编译完成: $(TARGET)"

# 测试目标
test: $(TARGET)
	@echo "测试QEntL Bootstrap解释器..."
	@if [ -f "$(TEST_FILE)" ]; then \
		echo "运行测试文件: $(TEST_FILE)"; \
		./$(TARGET) "$(TEST_FILE)"; \
	else \
		echo "创建简单测试..."; \
		echo 'quantum_class HelloWorld {' > test_simple.qentl; \
		echo '    public function main(): Integer {' >> test_simple.qentl; \
		echo '        Console.println("Hello from QEntL Bootstrap!");' >> test_simple.qentl; \
		echo '        return 0;' >> test_simple.qentl; \
		echo '    }' >> test_simple.qentl; \
		echo '}' >> test_simple.qentl; \
		echo "运行简单测试:"; \
		./$(TARGET) test_simple.qentl; \
	fi

# 清理目标
clean:
	$(RM) $(TARGET)
	@if [ -f "test_simple.qentl" ]; then $(RM) test_simple.qentl; fi

# 安装目标（将可执行文件复制到bin目录）
install: $(TARGET)
	@$(MKDIR) ../bin 2>/dev/null || true
	cp $(TARGET) ../bin/

# 帮助
help:
	@echo "QEntL Bootstrap解释器 Makefile"
	@echo "可用目标:"
	@echo "  all      - 编译解释器"
	@echo "  test     - 编译并测试"
	@echo "  clean    - 清理生成的文件"
	@echo "  install  - 安装到bin目录"
	@echo "  help     - 显示此帮助"

.PHONY: all test clean install help
