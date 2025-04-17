#!/bin/bash
# 量子模型集成框架构建脚本
#
# 用于编译和链接QEntL环境中的量子模型集成框架组件
#
# 作者: QEntL核心开发团队
# 日期: 2024-05-21
# 版本: 1.0

# 设置颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # 无颜色

# 设置目录
ROOT_DIR=$(pwd)
SRC_DIR="$ROOT_DIR/src"
BIN_DIR="$ROOT_DIR/bin"
LIB_DIR="$ROOT_DIR/lib"
TEST_DIR="$ROOT_DIR/tests"

# 创建必要的目录
mkdir -p $BIN_DIR
mkdir -p $LIB_DIR

# 编译标志
CFLAGS="-I$SRC_DIR -std=c99 -Wall -O2"
LDFLAGS="-L$LIB_DIR"

echo -e "${GREEN}===== 构建量子模型集成框架 =====${NC}"

# 编译集成框架
echo -e "${YELLOW}编译集成管理器...${NC}"
gcc -c $SRC_DIR/stdlib/integration/quantum_model_integration.c -I$SRC_DIR $CFLAGS

if [ $? -ne 0 ]; then
    echo -e "${RED}编译集成管理器失败${NC}"
    exit 1
fi

# 编译QSM适配器
echo -e "${YELLOW}编译QSM适配器...${NC}"
gcc -c $SRC_DIR/stdlib/integration/qsm_adapter.c -I$SRC_DIR $CFLAGS

if [ $? -ne 0 ]; then
    echo -e "${RED}编译QSM适配器失败${NC}"
    exit 1
fi

# 编译其他适配器
# 如果其他适配器文件存在，则编译它们
if [ -f "$SRC_DIR/stdlib/integration/som_adapter.c" ]; then
    echo -e "${YELLOW}编译SOM适配器...${NC}"
    gcc -c $SRC_DIR/stdlib/integration/som_adapter.c -I$SRC_DIR $CFLAGS
fi

if [ -f "$SRC_DIR/stdlib/integration/ref_adapter.c" ]; then
    echo -e "${YELLOW}编译REF适配器...${NC}"
    gcc -c $SRC_DIR/stdlib/integration/ref_adapter.c -I$SRC_DIR $CFLAGS
fi

if [ -f "$SRC_DIR/stdlib/integration/weq_adapter.c" ]; then
    echo -e "${YELLOW}编译WeQ适配器...${NC}"
    gcc -c $SRC_DIR/stdlib/integration/weq_adapter.c -I$SRC_DIR $CFLAGS
fi

# 创建静态库
echo -e "${YELLOW}创建集成框架静态库...${NC}"
ar rcs $LIB_DIR/libqentl_integration.a quantum_model_integration.o qsm_adapter.o

if [ $? -ne 0 ]; then
    echo -e "${RED}创建静态库失败${NC}"
    exit 1
fi

# 添加其他适配器到静态库（如果存在）
if [ -f "som_adapter.o" ]; then
    ar rcs $LIB_DIR/libqentl_integration.a som_adapter.o
fi

if [ -f "ref_adapter.o" ]; then
    ar rcs $LIB_DIR/libqentl_integration.a ref_adapter.o
fi

if [ -f "weq_adapter.o" ]; then
    ar rcs $LIB_DIR/libqentl_integration.a weq_adapter.o
fi

# 编译测试程序
echo -e "${YELLOW}编译集成框架测试程序...${NC}"
gcc -o $BIN_DIR/test_model_integration $TEST_DIR/test_model_integration.c \
    quantum_model_integration.o qsm_adapter.o \
    -I$SRC_DIR $CFLAGS

if [ $? -ne 0 ]; then
    echo -e "${RED}编译测试程序失败${NC}"
    exit 1
fi

# 清理目标文件
echo -e "${YELLOW}清理临时文件...${NC}"
rm -f *.o

echo -e "${GREEN}===== 量子模型集成框架构建完成 =====${NC}"
echo -e "${GREEN}测试程序位置: $BIN_DIR/test_model_integration${NC}"
echo -e "${GREEN}静态库位置: $LIB_DIR/libqentl_integration.a${NC}"

# 询问是否运行测试
echo -e "${YELLOW}是否运行集成框架测试程序? (y/n)${NC}"
read -r run_test

if [[ $run_test == "y" || $run_test == "Y" ]]; then
    echo -e "${GREEN}===== 运行集成框架测试 =====${NC}"
    $BIN_DIR/test_model_integration
fi

exit 0 