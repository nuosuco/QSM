/**
 * 量子网络节点自动激活与恢复示例
 * 
 * 本演示程序展示了QEntL环境中节点自动激活机制和自动资源检测功能。
 * 在QEntL环境中，所有节点默认处于激活状态，以便自动构建量子纠缠网络。
 * 只有在特殊情况下（如维护、错误等）才需要暂停节点，而后通过恢复功能重新激活。
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

/**
 * 节点状态枚举
 */
typedef enum {
    NODE_STATE_INACTIVE = 0,
    NODE_STATE_ACTIVE = 1,     // 默认激活状态
    NODE_STATE_SUSPENDED = 2,
    NODE_STATE_ERROR = 3
} NodeState;

/**
 * 设备类型枚举
 */
typedef enum {
    DEVICE_TYPE_DESKTOP = 0,
    DEVICE_TYPE_SERVER = 1,
    DEVICE_TYPE_DATACENTER = 2,
    DEVICE_TYPE_QUANTUM_PROCESSOR = 3
} DeviceType;

/**
 * 简化的节点结构
 */
typedef struct {
    unsigned int id;
    NodeState state;
    char name[64];
    int quantum_bits;          // 量子比特数量
    DeviceType device_type;    // 设备类型
    double processing_power;   // 处理能力 (0.0-1.0)
    int connected_nodes;       // 已连接节点数量
} QuantumNode;

/**
 * 自动检测设备资源并调整量子比特数量
 */
void detect_and_adjust_resources(QuantumNode* node) {
    if (!node) {
        return;
    }
    
    printf("正在检测 '%s' 的设备资源...\n", node->name);
    
    // 模拟检测过程
    // 在实际系统中，这将通过硬件API来获取真实资源信息
    switch (node->device_type) {
        case DEVICE_TYPE_DESKTOP:
            node->quantum_bits = 8 + rand() % 20;  // 8-28量子比特
            node->processing_power = 0.3 + ((double)rand() / RAND_MAX) * 0.4;  // 0.3-0.7
            printf("检测到桌面计算设备，资源等级: 基础\n");
            break;
            
        case DEVICE_TYPE_SERVER:
            node->quantum_bits = 32 + rand() % 96;  // 32-128量子比特
            node->processing_power = 0.6 + ((double)rand() / RAND_MAX) * 0.3;  // 0.6-0.9
            printf("检测到服务器环境，资源等级: 中级\n");
            break;
            
        case DEVICE_TYPE_DATACENTER:
            node->quantum_bits = 256 + rand() % 768;  // 256-1024量子比特
            node->processing_power = 0.8 + ((double)rand() / RAND_MAX) * 0.2;  // 0.8-1.0
            printf("检测到数据中心环境，资源等级: 高级\n");
            break;
            
        case DEVICE_TYPE_QUANTUM_PROCESSOR:
            node->quantum_bits = 1024 + rand() % 9216;  // 1024-10240量子比特
            node->processing_power = 0.95 + ((double)rand() / RAND_MAX) * 0.05;  // 0.95-1.0
            printf("检测到专用量子处理器，资源等级: 超级\n");
            break;
    }
    
    printf("资源调整完成: 量子比特数量 = %d, 处理能力 = %.2f\n", 
           node->quantum_bits, node->processing_power);
}

/**
 * 模拟网络自动构建
 */
void simulate_network_building(QuantumNode* nodes, int count) {
    if (!nodes || count <= 0) {
        return;
    }
    
    printf("\n开始模拟量子纠缠网络自动构建...\n");
    
    // 计算总量子比特
    int total_qubits = 0;
    for (int i = 0; i < count; i++) {
        if (nodes[i].state == NODE_STATE_ACTIVE) {
            total_qubits += nodes[i].quantum_bits;
            
            // 模拟节点连接
            nodes[i].connected_nodes = rand() % (count - 1) + 1;
        }
    }
    
    printf("网络自动构建完成:\n");
    printf("- 活跃节点数量: %d\n", count);
    printf("- 总量子比特数: %d\n", total_qubits);
    printf("- 量子纠缠信道: %d\n", count * (count - 1) / 2);
    printf("- 网络计算能力: %.2f QOPS (量子操作/秒)\n", 
           total_qubits * 1000.0 * ((double)rand() / RAND_MAX) * 0.5 + 0.5);
}

/**
 * 演示暂停节点的函数
 */
int suspend_node(QuantumNode* node) {
    if (!node) {
        printf("错误: 节点为空\n");
        return 0;
    }
    
    // 检查节点状态
    if (node->state == NODE_STATE_SUSPENDED) {
        printf("节点 [%u] '%s' 已经是暂停状态\n", node->id, node->name);
        return 1;
    }
    
    if (node->state != NODE_STATE_ACTIVE) {
        printf("错误: 节点 [%u] '%s' 不是活动状态 (当前状态: %d)\n", 
               node->id, node->name, node->state);
        return 0;
    }
    
    // 暂停节点
    printf("正在暂停节点 [%u] '%s'...\n", node->id, node->name);
    node->state = NODE_STATE_SUSPENDED;
    printf("节点暂停成功! 当前状态: %d (已暂停)\n", node->state);
    
    return 1;
}

/**
 * 演示恢复节点的函数
 */
int resume_node(QuantumNode* node) {
    if (!node) {
        printf("错误: 节点为空\n");
        return 0;
    }
    
    // 检查节点状态
    if (node->state == NODE_STATE_ACTIVE) {
        printf("节点 [%u] '%s' 已经是活动状态\n", node->id, node->name);
        return 1;
    }
    
    if (node->state != NODE_STATE_SUSPENDED) {
        printf("错误: 节点 [%u] '%s' 不是暂停状态 (当前状态: %d)\n", 
               node->id, node->name, node->state);
        return 0;
    }
    
    // 恢复节点
    printf("正在恢复节点 [%u] '%s'...\n", node->id, node->name);
    node->state = NODE_STATE_ACTIVE;
    printf("节点恢复成功! 当前状态: %d (已激活)\n", node->state);
    
    return 1;
}

int main() {
    // 初始化随机数种子
    srand(time(NULL));
    
    printf("===== 量子网络节点自动激活与资源调整演示 =====\n\n");
    
    // 创建节点 - 所有节点默认为激活状态
    QuantumNode nodes[4] = {
        {
            .id = 101,
            .state = NODE_STATE_ACTIVE,  // 默认为激活状态
            .name = "量子传感器节点",
            .quantum_bits = 28,          // 初始量子比特数
            .device_type = DEVICE_TYPE_DESKTOP,
            .processing_power = 0.5,
            .connected_nodes = 0
        },
        {
            .id = 102,
            .state = NODE_STATE_ACTIVE,
            .name = "量子路由节点",
            .quantum_bits = 64,
            .device_type = DEVICE_TYPE_SERVER,
            .processing_power = 0.7,
            .connected_nodes = 0
        },
        {
            .id = 103,
            .state = NODE_STATE_ACTIVE,
            .name = "量子存储节点",
            .quantum_bits = 512,
            .device_type = DEVICE_TYPE_DATACENTER,
            .processing_power = 0.9,
            .connected_nodes = 0
        },
        {
            .id = 104,
            .state = NODE_STATE_ACTIVE,
            .name = "量子处理器节点",
            .quantum_bits = 2048,
            .device_type = DEVICE_TYPE_QUANTUM_PROCESSOR,
            .processing_power = 0.95,
            .connected_nodes = 0
        }
    };
    
    // 输出节点初始状态
    printf("初始节点状态 (所有节点默认处于激活状态):\n");
    for (int i = 0; i < 4; i++) {
        printf("- 节点 [%u] '%s': 状态 = %d (%s), 量子比特 = %d\n", 
               nodes[i].id, nodes[i].name, nodes[i].state, 
               nodes[i].state == NODE_STATE_ACTIVE ? "已激活" : "未知",
               nodes[i].quantum_bits);
    }
    
    printf("\n");
    
    // 自动检测并调整资源
    printf("示例 1: 自动检测设备资源并调整量子比特数量\n");
    for (int i = 0; i < 4; i++) {
        detect_and_adjust_resources(&nodes[i]);
        printf("\n");
    }
    
    // 模拟网络自动构建
    simulate_network_building(nodes, 4);
    
    // 特殊情况：需要暂停节点进行维护
    printf("\n示例 2: 特殊情况 - 暂停节点进行维护\n");
    printf("(在QEntL环境中，节点默认处于激活状态，只有特殊情况才需要暂停)\n");
    suspend_node(&nodes[0]);
    
    // 再次模拟网络自动构建（少了一个节点）
    printf("\n暂停节点后的网络状态:\n");
    simulate_network_building(nodes, 4);
    
    // 完成维护后恢复节点
    printf("\n示例 3: 维护完成后恢复节点\n");
    resume_node(&nodes[0]);
    
    // 再次模拟网络自动构建（恢复完整网络）
    printf("\n恢复节点后的网络状态:\n");
    simulate_network_building(nodes, 4);
    
    printf("\n===== 演示完成 =====\n");
    printf("结论: QEntL环境中所有节点默认处于激活状态，能够自动构建量子纠缠网络，\n");
    printf("      并根据设备资源自动调整量子比特数量，实现跨设备的计算能力整合。\n");
    
    return 0;
} 