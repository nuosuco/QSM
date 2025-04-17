CC = gcc
CFLAGS = -Wall -std=c99 -O2 -I../.. -g
LDFLAGS = -lm

# 源文件目录
SRC_DIR = .
TEST_DIR = ./tests
OBJ_DIR = ./obj
BIN_DIR = ../../bin

# 创建目录
$(shell mkdir -p $(OBJ_DIR) $(BIN_DIR))

# 源文件
DEVICE_DETECTOR_SRC = $(SRC_DIR)/device_capability_detector.c
QUANTUM_ADJUSTER_SRC = $(SRC_DIR)/quantum_bit_adjuster.c
RESOURCE_MONITOR_SRC = $(SRC_DIR)/resource_monitor.c

# 测试文件
DEVICE_DETECTOR_TEST = $(TEST_DIR)/test_device_capability_detector.c
QUANTUM_ADJUSTER_TEST = $(TEST_DIR)/test_quantum_bit_adjuster.c
RESOURCE_MONITOR_TEST = $(TEST_DIR)/test_resource_monitor.c

# 目标文件
DEVICE_DETECTOR_OBJ = $(OBJ_DIR)/device_capability_detector.o
QUANTUM_ADJUSTER_OBJ = $(OBJ_DIR)/quantum_bit_adjuster.o
RESOURCE_MONITOR_OBJ = $(OBJ_DIR)/resource_monitor.o

# 测试可执行文件
DEVICE_DETECTOR_BIN = $(BIN_DIR)/test_device_capability_detector
QUANTUM_ADJUSTER_BIN = $(BIN_DIR)/test_quantum_bit_adjuster
RESOURCE_MONITOR_BIN = $(BIN_DIR)/test_resource_monitor

# 默认目标
all: device_detector quantum_adjuster resource_monitor

# 设备能力检测器
device_detector: $(DEVICE_DETECTOR_OBJ)
	@echo "Building device capability detector..."

# 量子比特调整器
quantum_adjuster: $(QUANTUM_ADJUSTER_OBJ) $(DEVICE_DETECTOR_OBJ)
	@echo "Building quantum bit adjuster..."

# 资源监控器
resource_monitor: $(RESOURCE_MONITOR_OBJ)
	@echo "Building resource monitor..."

# 设备能力检测器测试
test_device_detector: $(DEVICE_DETECTOR_OBJ) $(DEVICE_DETECTOR_TEST)
	@echo "Building device capability detector test..."
	$(CC) $(CFLAGS) -o $(DEVICE_DETECTOR_BIN) $(DEVICE_DETECTOR_TEST) $(DEVICE_DETECTOR_OBJ) $(LDFLAGS)

# 量子比特调整器测试
test_quantum_adjuster: $(QUANTUM_ADJUSTER_OBJ) $(DEVICE_DETECTOR_OBJ) $(QUANTUM_ADJUSTER_TEST)
	@echo "Building quantum bit adjuster test..."
	$(CC) $(CFLAGS) -o $(QUANTUM_ADJUSTER_BIN) $(QUANTUM_ADJUSTER_TEST) $(QUANTUM_ADJUSTER_OBJ) $(DEVICE_DETECTOR_OBJ) $(LDFLAGS)

# 资源监控器测试
test_resource_monitor: $(RESOURCE_MONITOR_OBJ) $(RESOURCE_MONITOR_TEST)
	@echo "Building resource monitor test..."
	$(CC) $(CFLAGS) -o $(RESOURCE_MONITOR_BIN) $(RESOURCE_MONITOR_TEST) $(RESOURCE_MONITOR_OBJ) $(LDFLAGS)

# 编译测试所有组件
test: test_device_detector test_quantum_adjuster test_resource_monitor

# 编译所有源文件
$(DEVICE_DETECTOR_OBJ): $(DEVICE_DETECTOR_SRC)
	$(CC) $(CFLAGS) -c $< -o $@

$(QUANTUM_ADJUSTER_OBJ): $(QUANTUM_ADJUSTER_SRC)
	$(CC) $(CFLAGS) -c $< -o $@

$(RESOURCE_MONITOR_OBJ): $(RESOURCE_MONITOR_SRC)
	$(CC) $(CFLAGS) -c $< -o $@

# 运行所有测试
run_tests: test
	@echo "Running device capability detector test..."
	$(DEVICE_DETECTOR_BIN)
	@echo "Running quantum bit adjuster test..."
	$(QUANTUM_ADJUSTER_BIN)
	@echo "Running resource monitor test..."
	$(RESOURCE_MONITOR_BIN)

# 清理
clean:
	rm -f $(OBJ_DIR)/*.o
	rm -f $(DEVICE_DETECTOR_BIN) $(QUANTUM_ADJUSTER_BIN) $(RESOURCE_MONITOR_BIN)
	rm -f *.txt

.PHONY: all clean test run_tests device_detector quantum_adjuster resource_monitor 