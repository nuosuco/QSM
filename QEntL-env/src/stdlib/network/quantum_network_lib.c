/**
 * QEntL标准库网络函数实现
 * 
 * 量子基因编码: QG-STDLIB-NET-A1B5
 * 
 * @文件: quantum_network_lib.c
 * @描述: 实现QEntL标准库中的网络功能，包括量子节点管理和纠缠通信
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-15
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 网络节点和通信信道自动包含量子基因编码和量子纠缠信道
 * - 能根据运行环境自适应调整量子比特处理能力
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../../quantum_state.h"
#include "../../quantum_gene.h"
#include "../../quantum_entanglement.h"
#include "../../quantum_network.h"
#include "../../runtime/quantum_runtime.h"
#include "quantum_network_lib.h"

/* 量子纠缠激活 */
#define QUANTUM_ENTANGLEMENT_ACTIVE 1
#define MAX_NODE_CONNECTIONS 128
#define DEFAULT_CONNECTION_STRENGTH 0.75

/* 内部量子基因 */
static QGene* stdlib_network_gene = NULL;

/* 全局节点列表 */
static QNetworkNode** global_nodes = NULL;
static size_t global_node_count = 0;
static size_t global_node_capacity = 0;

/**
 * 量子网络节点结构
 */
struct QNetworkNode {
    char* id;                     /* 节点ID */
    char* name;                   /* 节点名称 */
    char* type;                   /* 节点类型 */
    char* address;                /* 网络地址 */
    int active;                   /* 激活状态 */
    QGene* gene;                  /* 量子基因 */
    QEntanglement** connections;  /* 与其他节点的连接 */
    size_t connection_count;      /* 连接数量 */
    time_t creation_time;         /* 创建时间 */
    time_t last_active_time;      /* 最后活动时间 */
    QState* state;                /* 节点量子态 */
    void* user_data;              /* 用户数据 */
    void (*cleanup_callback)(void*); /* 清理回调 */
};

/**
 * 量子通信信道结构
 */
struct QNetworkChannel {
    char* id;                  /* 信道ID */
    QNetworkNode* source;      /* 源节点 */
    QNetworkNode* target;      /* 目标节点 */
    double strength;           /* 纠缠强度 */
    QGene* gene;               /* 量子基因 */
    QEntanglement* entanglement; /* 量子纠缠 */
    int active;                /* 激活状态 */
    int error_rate;            /* 错误率 (0-100) */
    int bandwidth;             /* 带宽 (量子比特/秒) */
    time_t creation_time;      /* 创建时间 */
    time_t last_used_time;     /* 最后使用时间 */
};

/**
 * 生成唯一ID
 */
static char* generate_unique_id(const char* prefix) {
    static unsigned int counter = 0;
    char* id = (char*)malloc(64);
    if (!id) return NULL;
    
    unsigned int timestamp = (unsigned int)time(NULL);
    snprintf(id, 64, "%s-%u-%u", prefix, timestamp, counter++);
    return id;
}

/**
 * 初始化标准库网络组件
 */
int qentl_stdlib_network_initialize(void) {
    /* 如果已经初始化，返回成功 */
    if (stdlib_network_gene) {
        return 1;
    }
    
    /* 创建标准库网络量子基因 */
    stdlib_network_gene = quantum_gene_create("STDLIB-NETWORK", "A1B5");
    if (!stdlib_network_gene) {
        return 0;
    }
    
    /* 设置量子基因属性 */
    quantum_gene_add_metadata(stdlib_network_gene, "STDLIB_VERSION", "1.0");
    quantum_gene_add_metadata(stdlib_network_gene, "INITIALIZATION_TIME", 
                             (const char*)(size_t)time(NULL));
    quantum_gene_set_strength(stdlib_network_gene, 0.85);
    
    /* 创建量子纠缠 */
    if (QUANTUM_ENTANGLEMENT_ACTIVE) {
        /* 创建与运行时的纠缠 */
        QEntanglement* ent_runtime = quantum_entanglement_create();
        if (ent_runtime) {
            quantum_entanglement_set_source(ent_runtime, "STDLIB-NETWORK");
            quantum_entanglement_set_target(ent_runtime, "RUNTIME-CORE");
            quantum_entanglement_set_strength(ent_runtime, 0.8);
            quantum_gene_add_entanglement(stdlib_network_gene, ent_runtime);
            quantum_entanglement_destroy(ent_runtime);
        }
        
        /* 创建与其他标准库模块的纠缠 */
        QEntanglement* ent_core = quantum_entanglement_create();
        if (ent_core) {
            quantum_entanglement_set_source(ent_core, "STDLIB-NETWORK");
            quantum_entanglement_set_target(ent_core, "STDLIB-CORE");
            quantum_entanglement_set_strength(ent_core, 0.9);
            quantum_gene_add_entanglement(stdlib_network_gene, ent_core);
            quantum_entanglement_destroy(ent_core);
        }
    }
    
    /* 初始化全局节点列表 */
    global_nodes = (QNetworkNode**)malloc(sizeof(QNetworkNode*) * 16);
    if (!global_nodes) {
        quantum_gene_destroy(stdlib_network_gene);
        stdlib_network_gene = NULL;
        return 0;
    }
    
    global_node_capacity = 16;
    global_node_count = 0;
    
    return 1;
}

/**
 * 清理标准库网络组件
 */
void qentl_stdlib_network_cleanup(void) {
    if (stdlib_network_gene) {
        quantum_gene_destroy(stdlib_network_gene);
        stdlib_network_gene = NULL;
    }
    
    /* 释放全局节点列表 */
    if (global_nodes) {
        for (size_t i = 0; i < global_node_count; i++) {
            if (global_nodes[i]) {
                qentl_destroy_network_node(global_nodes[i]);
            }
        }
        free(global_nodes);
        global_nodes = NULL;
        global_node_count = 0;
        global_node_capacity = 0;
    }
}

/**
 * 添加节点到全局列表
 */
static int add_node_to_global_list(QNetworkNode* node) {
    if (!node || !global_nodes) {
        return 0;
    }
    
    /* 检查容量并扩展如果需要 */
    if (global_node_count >= global_node_capacity) {
        size_t new_capacity = global_node_capacity * 2;
        QNetworkNode** new_nodes = (QNetworkNode**)realloc(global_nodes, 
                                                         sizeof(QNetworkNode*) * new_capacity);
        if (!new_nodes) {
            return 0;
        }
        
        global_nodes = new_nodes;
        global_node_capacity = new_capacity;
    }
    
    /* 添加节点 */
    global_nodes[global_node_count++] = node;
    return 1;
}

/**
 * 从全局列表移除节点
 */
static void remove_node_from_global_list(QNetworkNode* node) {
    if (!node || !global_nodes || global_node_count == 0) {
        return;
    }
    
    /* 查找节点 */
    for (size_t i = 0; i < global_node_count; i++) {
        if (global_nodes[i] == node) {
            /* 移动后续节点 */
            if (i < global_node_count - 1) {
                memmove(&global_nodes[i], &global_nodes[i + 1], 
                       sizeof(QNetworkNode*) * (global_node_count - i - 1));
            }
            
            global_node_count--;
            break;
        }
    }
}

/**
 * 创建量子网络节点
 */
QNetworkNode* qentl_create_network_node(const char* name, const char* type) {
    if (!name) {
        return NULL;
    }
    
    /* 确保网络库已初始化 */
    if (!stdlib_network_gene) {
        if (!qentl_stdlib_network_initialize()) {
            return NULL;
        }
    }
    
    /* 分配节点结构 */
    QNetworkNode* node = (QNetworkNode*)malloc(sizeof(QNetworkNode));
    if (!node) {
        return NULL;
    }
    
    /* 初始化节点 */
    node->id = generate_unique_id("node");
    node->name = strdup(name);
    node->type = type ? strdup(type) : strdup("default");
    node->address = NULL; /* 稍后设置 */
    node->active = 1; /* 默认为激活状态 */
    node->connections = (QEntanglement**)malloc(sizeof(QEntanglement*) * MAX_NODE_CONNECTIONS);
    node->connection_count = 0;
    node->creation_time = time(NULL);
    node->last_active_time = node->creation_time;
    node->user_data = NULL;
    node->cleanup_callback = NULL;
    
    /* 检查内存分配 */
    if (!node->id || !node->name || !node->type || !node->connections) {
        if (node->id) free(node->id);
        if (node->name) free(node->name);
        if (node->type) free(node->type);
        if (node->connections) free(node->connections);
        free(node);
        return NULL;
    }
    
    /* 生成网络地址 */
    node->address = (char*)malloc(64);
    if (node->address) {
        snprintf(node->address, 64, "qnet://%s/%s", node->type, node->id);
    }
    
    /* 创建节点量子态 */
    node->state = quantum_runtime_create_state(node->name);
    
    /* 应用量子基因 */
    node->gene = quantum_gene_clone(stdlib_network_gene);
    if (node->gene) {
        /* 添加节点特定元数据 */
        quantum_gene_add_metadata(node->gene, "NODE_ID", node->id);
        quantum_gene_add_metadata(node->gene, "NODE_TYPE", node->type);
        quantum_gene_add_metadata(node->gene, "CREATION_TIME", 
                                 (const char*)(size_t)node->creation_time);
        
        /* 应用到节点状态 */
        if (node->state) {
            quantum_state_apply_gene(node->state, node->gene);
        }
    }
    
    /* 添加到全局节点列表 */
    add_node_to_global_list(node);
    
    return node;
}

/**
 * 销毁量子网络节点
 */
void qentl_destroy_network_node(QNetworkNode* node) {
    if (!node) {
        return;
    }
    
    /* 移除全局节点列表 */
    remove_node_from_global_list(node);
    
    /* 释放连接 */
    for (size_t i = 0; i < node->connection_count; i++) {
        if (node->connections[i]) {
            quantum_entanglement_destroy(node->connections[i]);
        }
    }
    
    /* 释放资源 */
    if (node->id) free(node->id);
    if (node->name) free(node->name);
    if (node->type) free(node->type);
    if (node->address) free(node->address);
    if (node->connections) free(node->connections);
    if (node->gene) quantum_gene_destroy(node->gene);
    
    /* 释放量子态 */
    if (node->state) {
        quantum_runtime_destroy_state(node->state);
    }
    
    /* 调用用户清理回调 */
    if (node->user_data && node->cleanup_callback) {
        node->cleanup_callback(node->user_data);
    }
    
    free(node);
}

/**
 * 设置节点活跃状态
 */
void qentl_set_node_active(QNetworkNode* node, int active) {
    if (!node) {
        return;
    }
    
    node->active = active ? 1 : 0;
    
    /* 更新最后活动时间 */
    if (active) {
        node->last_active_time = time(NULL);
    }
}

/**
 * 检查节点是否活跃
 */
int qentl_is_node_active(QNetworkNode* node) {
    return node ? node->active : 0;
}

/**
 * 设置节点用户数据和清理回调
 */
void qentl_set_node_user_data(QNetworkNode* node, void* user_data, 
                            void (*cleanup_callback)(void*)) {
    if (!node) {
        return;
    }
    
    /* 如果有旧的用户数据和回调，先清理 */
    if (node->user_data && node->cleanup_callback) {
        node->cleanup_callback(node->user_data);
    }
    
    node->user_data = user_data;
    node->cleanup_callback = cleanup_callback;
}

/**
 * 获取节点用户数据
 */
void* qentl_get_node_user_data(QNetworkNode* node) {
    return node ? node->user_data : NULL;
}

/**
 * 获取节点ID
 */
const char* qentl_get_node_id(QNetworkNode* node) {
    return node ? node->id : NULL;
}

/**
 * 获取节点名称
 */
const char* qentl_get_node_name(QNetworkNode* node) {
    return node ? node->name : NULL;
}

/**
 * 获取节点量子态
 */
QState* qentl_get_node_state(QNetworkNode* node) {
    return node ? node->state : NULL;
}

/**
 * 连接两个节点
 */
QNetworkChannel* qentl_connect_nodes(QNetworkNode* source, QNetworkNode* target, 
                                  double strength) {
    if (!source || !target) {
        return NULL;
    }
    
    /* 检查节点是否活跃 */
    if (!source->active || !target->active) {
        return NULL;
    }
    
    /* 检查连接数量是否已达上限 */
    if (source->connection_count >= MAX_NODE_CONNECTIONS) {
        return NULL;
    }
    
    /* 创建信道 */
    QNetworkChannel* channel = (QNetworkChannel*)malloc(sizeof(QNetworkChannel));
    if (!channel) {
        return NULL;
    }
    
    /* 初始化信道 */
    channel->id = generate_unique_id("channel");
    channel->source = source;
    channel->target = target;
    channel->strength = (strength > 0.0 && strength <= 1.0) ? strength : DEFAULT_CONNECTION_STRENGTH;
    channel->active = 1;
    channel->error_rate = 0;
    channel->bandwidth = 100; /* 默认100量子比特/秒 */
    channel->creation_time = time(NULL);
    channel->last_used_time = channel->creation_time;
    
    /* 检查内存分配 */
    if (!channel->id) {
        free(channel);
        return NULL;
    }
    
    /* 创建量子纠缠 */
    channel->entanglement = quantum_entanglement_create();
    if (!channel->entanglement) {
        free(channel->id);
        free(channel);
        return NULL;
    }
    
    /* 配置纠缠属性 */
    quantum_entanglement_set_source(channel->entanglement, source->id);
    quantum_entanglement_set_target(channel->entanglement, target->id);
    quantum_entanglement_set_strength(channel->entanglement, channel->strength);
    
    /* 应用量子基因 */
    channel->gene = quantum_gene_clone(stdlib_network_gene);
    if (channel->gene) {
        /* 添加信道特定元数据 */
        quantum_gene_add_metadata(channel->gene, "CHANNEL_ID", channel->id);
        quantum_gene_add_metadata(channel->gene, "SOURCE_ID", source->id);
        quantum_gene_add_metadata(channel->gene, "TARGET_ID", target->id);
        quantum_gene_add_metadata(channel->gene, "CREATION_TIME", 
                                 (const char*)(size_t)channel->creation_time);
        
        /* 添加到纠缠 */
        quantum_entanglement_set_gene(channel->entanglement, channel->gene);
    }
    
    /* 添加连接到源节点 */
    source->connections[source->connection_count++] = channel->entanglement;
    
    /* 如果节点状态存在，建立它们之间的纠缠 */
    if (source->state && target->state) {
        quantum_runtime_entangle_states(source->state, target->state, channel->strength);
    }
    
    return channel;
}

/**
 * 销毁量子通信信道
 */
void qentl_destroy_channel(QNetworkChannel* channel) {
    if (!channel) {
        return;
    }
    
    /* 移除源节点中的连接 */
    if (channel->source) {
        for (size_t i = 0; i < channel->source->connection_count; i++) {
            if (channel->source->connections[i] == channel->entanglement) {
                /* 移动后续连接 */
                if (i < channel->source->connection_count - 1) {
                    memmove(&channel->source->connections[i], 
                           &channel->source->connections[i + 1],
                           sizeof(QEntanglement*) * (channel->source->connection_count - i - 1));
                }
                channel->source->connection_count--;
                break;
            }
        }
    }
    
    /* 释放资源 */
    if (channel->id) free(channel->id);
    if (channel->entanglement) quantum_entanglement_destroy(channel->entanglement);
    if (channel->gene) quantum_gene_destroy(channel->gene);
    
    free(channel);
}

/**
 * 发送状态通过信道
 */
QState* qentl_transmit_through_channel(QNetworkChannel* channel, QState* state) {
    if (!channel || !state || !channel->active) {
        return NULL;
    }
    
    /* 更新最后使用时间 */
    channel->last_used_time = time(NULL);
    
    /* 创建状态副本 */
    const char* state_name = quantum_state_get_name(state);
    char new_name[128];
    snprintf(new_name, sizeof(new_name), "%s_transmitted", state_name ? state_name : "state");
    
    QState* new_state = quantum_runtime_create_state(new_name);
    if (!new_state) {
        return NULL;
    }
    
    /* 复制状态属性 */
    const char* state_type = quantum_state_get_type(state);
    if (state_type) {
        quantum_state_set_type(new_state, state_type);
    }
    
    /* 应用信道纠缠基因 */
    if (channel->gene) {
        QGene* gene = quantum_gene_clone(channel->gene);
        if (gene) {
            quantum_gene_add_metadata(gene, "TRANSMISSION_TIME", 
                                     (const char*)(size_t)time(NULL));
            quantum_state_apply_gene(new_state, gene);
            quantum_gene_destroy(gene);
        }
    }
    
    /* 如果有目标节点状态，与其建立纠缠 */
    if (channel->target && channel->target->state) {
        quantum_runtime_entangle_states(new_state, channel->target->state, channel->strength);
    }
    
    return new_state;
}

/**
 * 广播状态到所有连接的节点
 */
int qentl_broadcast_state(QNetworkNode* source, QState* state) {
    if (!source || !state || !source->active) {
        return 0;
    }
    
    int success_count = 0;
    
    /* 遍历所有连接 */
    for (size_t i = 0; i < source->connection_count; i++) {
        QEntanglement* ent = source->connections[i];
        if (!ent) continue;
        
        /* 查找目标节点 */
        const char* target_id = quantum_entanglement_get_target(ent);
        QNetworkNode* target = NULL;
        
        /* 在全局节点列表中查找目标 */
        for (size_t j = 0; j < global_node_count; j++) {
            if (global_nodes[j] && 
                strcmp(global_nodes[j]->id, target_id) == 0) {
                target = global_nodes[j];
                break;
            }
        }
        
        if (target && target->active) {
            /* 创建临时信道 */
            QNetworkChannel channel;
            channel.source = source;
            channel.target = target;
            channel.strength = quantum_entanglement_get_strength(ent);
            channel.active = 1;
            channel.entanglement = ent;
            channel.gene = source->gene;
            channel.creation_time = source->creation_time;
            channel.last_used_time = time(NULL);
            
            /* 传输状态 */
            QState* new_state = qentl_transmit_through_channel(&channel, state);
            if (new_state) {
                /* 设置目标节点状态 */
                if (target->state) {
                    quantum_runtime_destroy_state(target->state);
                }
                target->state = new_state;
                success_count++;
            }
        }
    }
    
    return success_count;
}

/**
 * 查找节点
 */
QNetworkNode* qentl_find_node_by_id(const char* node_id) {
    if (!node_id || !global_nodes) {
        return NULL;
    }
    
    /* 在全局节点列表中查找 */
    for (size_t i = 0; i < global_node_count; i++) {
        if (global_nodes[i] && 
            strcmp(global_nodes[i]->id, node_id) == 0) {
            return global_nodes[i];
        }
    }
    
    return NULL;
}

/**
 * 通过名称查找节点
 */
QNetworkNode* qentl_find_node_by_name(const char* node_name) {
    if (!node_name || !global_nodes) {
        return NULL;
    }
    
    /* 在全局节点列表中查找 */
    for (size_t i = 0; i < global_node_count; i++) {
        if (global_nodes[i] && global_nodes[i]->name &&
            strcmp(global_nodes[i]->name, node_name) == 0) {
            return global_nodes[i];
        }
    }
    
    return NULL;
}

/**
 * 获取所有节点
 */
QNetworkNode** qentl_get_all_nodes(size_t* count) {
    if (!count || !global_nodes || global_node_count == 0) {
        if (count) *count = 0;
        return NULL;
    }
    
    /* 克隆节点列表 */
    QNetworkNode** nodes = (QNetworkNode**)malloc(sizeof(QNetworkNode*) * global_node_count);
    if (!nodes) {
        *count = 0;
        return NULL;
    }
    
    memcpy(nodes, global_nodes, sizeof(QNetworkNode*) * global_node_count);
    *count = global_node_count;
    
    return nodes;
}

/**
 * 获取连接到节点的所有信道
 */
QNetworkChannel** qentl_get_node_channels(QNetworkNode* node, size_t* count) {
    if (!node || !count) {
        if (count) *count = 0;
        return NULL;
    }
    
    *count = 0;
    
    /* 分配信道数组 */
    QNetworkChannel** channels = (QNetworkChannel**)malloc(
        sizeof(QNetworkChannel*) * node->connection_count);
    if (!channels) {
        return NULL;
    }
    
    /* 为每个连接创建信道对象 */
    for (size_t i = 0; i < node->connection_count; i++) {
        QEntanglement* ent = node->connections[i];
        if (!ent) continue;
        
        /* 查找目标节点 */
        const char* target_id = quantum_entanglement_get_target(ent);
        QNetworkNode* target = qentl_find_node_by_id(target_id);
        if (!target) continue;
        
        /* 创建信道 */
        QNetworkChannel* channel = (QNetworkChannel*)malloc(sizeof(QNetworkChannel));
        if (!channel) continue;
        
        /* 初始化信道 */
        channel->id = generate_unique_id("channel");
        channel->source = node;
        channel->target = target;
        channel->strength = quantum_entanglement_get_strength(ent);
        channel->entanglement = ent;
        channel->active = 1;
        channel->error_rate = 0;
        channel->bandwidth = 100;
        channel->creation_time = node->creation_time;
        channel->last_used_time = time(NULL);
        
        /* 应用量子基因 */
        channel->gene = quantum_gene_clone(stdlib_network_gene);
        if (channel->gene) {
            /* 添加信道特定元数据 */
            quantum_gene_add_metadata(channel->gene, "CHANNEL_ID", channel->id);
            quantum_gene_add_metadata(channel->gene, "SOURCE_ID", node->id);
            quantum_gene_add_metadata(channel->gene, "TARGET_ID", target_id);
        }
        
        /* 添加到数组 */
        channels[(*count)++] = channel;
    }
    
    return channels;
}

/**
 * 创建量子网络集群
 */
QNetworkNode* qentl_create_network_cluster(const char* name, int node_count) {
    if (!name || node_count <= 0) {
        return NULL;
    }
    
    /* 创建中心节点 */
    QNetworkNode* center = qentl_create_network_node(name, "cluster_center");
    if (!center) {
        return NULL;
    }
    
    /* 创建子节点 */
    for (int i = 0; i < node_count; i++) {
        char node_name[128];
        snprintf(node_name, sizeof(node_name), "%s_node_%d", name, i + 1);
        
        QNetworkNode* node = qentl_create_network_node(node_name, "cluster_node");
        if (node) {
            /* 连接到中心节点 */
            QNetworkChannel* channel = qentl_connect_nodes(center, node, 0.9);
            if (!channel) {
                qentl_destroy_network_node(node);
            }
        }
    }
    
    return center;
} 