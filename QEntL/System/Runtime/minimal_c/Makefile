# QEntL Minimal C Runtime Makefile
# 为QEntL量子语言提供最小化C语言运行时
# 实现目标：运行QEntL编译器代码，实现自举循环

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2 -g -Iinclude
LDFLAGS = -lm

TARGET = qentl_runtime
SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin

# 核心源文件
SRCS = \
	$(SRC_DIR)/main.c \
	$(SRC_DIR)/memory.c \
	$(SRC_DIR)/types.c \
	$(SRC_DIR)/value.c \
	$(SRC_DIR)/vm.c \
	$(SRC_DIR)/bytecode.c \
	$(SRC_DIR)/compiler_support.c

OBJS = $(SRCS:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)

.PHONY: all clean dirs test

all: dirs $(BIN_DIR)/$(TARGET)

$(BIN_DIR)/$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

dirs:
	mkdir -p $(OBJ_DIR) $(BIN_DIR)

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)

test: all
	@echo "运行基本测试..."
	$(BIN_DIR)/$(TARGET) --test

# 开发辅助
debug: CFLAGS += -DDEBUG -O0
debug: clean all

valgrind: debug
	valgrind --leak-check=full $(BIN_DIR)/$(TARGET) --test