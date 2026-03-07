# QEntL运行时库 Makefile
# 版本: 1.0.0

# 配置
CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -O2 -g -I./include
LDFLAGS = 

# 目标
TARGET = libqentl_runtime.a
TEST_TARGET = test_runtime

# 源文件
SRC_DIR = src
SRC_FILES = $(wildcard $(SRC_DIR)/*.c)
OBJ_FILES = $(SRC_FILES:.c=.o)

# 测试文件
TEST_DIR = tests
TEST_SRC = $(TEST_DIR)/test_vm.c
TEST_OBJ = $(TEST_SRC:.c=.o)

# 默认目标
all: $(TARGET) $(TEST_TARGET)

# 静态库
$(TARGET): $(OBJ_FILES)
	ar rcs $@ $^

# 测试程序
$(TEST_TARGET): $(TEST_OBJ) $(TARGET)
	$(CC) $(CFLAGS) -o $@ $(TEST_OBJ) -L. -lqentl_runtime $(LDFLAGS)

# 编译源文件
$(SRC_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# 编译测试文件
$(TEST_DIR)/%.o: $(TEST_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# 运行测试
test: $(TEST_TARGET)
	./$(TEST_TARGET)

# 清理
clean:
	rm -f $(OBJ_FILES) $(TEST_OBJ) $(TARGET) $(TEST_TARGET)
	rm -f *.a *.so

# 安装（系统级）
install: $(TARGET)
	cp $(TARGET) /usr/local/lib/
	cp -r include/qentl_runtime.h /usr/local/include/

# 卸载
uninstall:
	rm -f /usr/local/lib/$(TARGET)
	rm -f /usr/local/include/qentl_runtime.h

# 依赖关系
depend:
	$(CC) -MM $(CFLAGS) $(SRC_FILES) > .depend

-include .depend

# 开发辅助
.PHONY: all clean test install uninstall depend

# 调试信息
info:
	@echo "源文件: $(SRC_FILES)"
	@echo "目标文件: $(OBJ_FILES)"
	@echo "目标库: $(TARGET)"
	@echo "测试程序: $(TEST_TARGET)"