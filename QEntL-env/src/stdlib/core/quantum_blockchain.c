/**
 * 量子区块链模块 - 实现基于量子纠缠的区块链系统
 * 
 * 该模块利用量子纠缠特性实现安全、不可篡改且自动同步的分布式账本
 * 
 * @作者：QEntL开发团队
 * @版本：1.0.0
 * @日期：2023-06-18
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../../quantum_state.h"
#include "../../quantum_entanglement.h"
#include "../../quantum_gene.h"

// 量子交易结构
typedef struct {
    char transaction_id[64];           // 交易ID
    char sender[64];                   // 发送方
    char recipient[64];                // 接收方
    double amount;                     // 交易金额
    char data[256];                    // 交易数据
    quantum_state_t* quantum_signature; // 量子签名
    time_t timestamp;                  // 时间戳
} quantum_transaction_t;

// 量子区块结构
typedef struct quantum_block {
    unsigned int index;                // 区块索引
    char previous_hash[65];            // 前一区块哈希
    char current_hash[65];             // 当前区块哈希
    time_t timestamp;                  // 时间戳
    unsigned int nonce;                // 工作量证明随机数
    quantum_transaction_t** transactions; // 交易列表
    unsigned int transaction_count;    // 交易数量
    quantum_state_t* quantum_state;    // 区块量子状态
    quantum_entanglement_t* chain_entanglement; // 与前一区块的纠缠
    struct quantum_block* next;        // 指向下一区块
} quantum_block_t;

// 量子区块链结构
typedef struct {
    quantum_block_t* genesis_block;    // 创世区块
    quantum_block_t* latest_block;     // 最新区块
    unsigned int block_count;          // 区块数量
    unsigned int difficulty;           // 挖矿难度
    char chain_id[64];                 // 链ID
    quantum_entanglement_t* global_entanglement; // 全局纠缠状态
} quantum_blockchain_t;

// 量子共识节点结构
typedef struct {
    char node_id[64];                  // 节点ID
    quantum_state_t* node_state;       // 节点量子状态
    quantum_entanglement_t* network_entanglement; // 与网络的纠缠
    int is_validator;                  // 是否为验证节点
    int is_miner;                      // 是否为挖矿节点
    quantum_blockchain_t* blockchain;  // 本地区块链副本
} quantum_consensus_node_t;

// 创建新的量子交易
quantum_transaction_t* quantum_transaction_create(const char* sender, const char* recipient, double amount, const char* data) {
    quantum_transaction_t* transaction = (quantum_transaction_t*)malloc(sizeof(quantum_transaction_t));
    if (!transaction) return NULL;
    
    // 生成随机交易ID
    sprintf(transaction->transaction_id, "TX%016lx", (unsigned long)rand() * (unsigned long)rand());
    
    strncpy(transaction->sender, sender, 63);
    transaction->sender[63] = '\0';
    
    strncpy(transaction->recipient, recipient, 63);
    transaction->recipient[63] = '\0';
    
    transaction->amount = amount;
    
    strncpy(transaction->data, data, 255);
    transaction->data[255] = '\0';
    
    // 创建量子签名（使用4个量子比特）
    transaction->quantum_signature = quantum_state_create(4);
    
    // 基于交易详情初始化量子状态
    char combined[512];
    sprintf(combined, "%s%s%s%.8f%s", 
            transaction->transaction_id, 
            transaction->sender, 
            transaction->recipient, 
            transaction->amount, 
            transaction->data);
    
    quantum_state_init_from_string(transaction->quantum_signature, combined);
    
    // 设置时间戳
    transaction->timestamp = time(NULL);
    
    return transaction;
}

// 销毁量子交易
void quantum_transaction_destroy(quantum_transaction_t* transaction) {
    if (!transaction) return;
    
    quantum_state_destroy(transaction->quantum_signature);
    free(transaction);
}

// 验证量子交易
int quantum_transaction_verify(quantum_transaction_t* transaction) {
    if (!transaction) return 0;
    
    // 重新计算量子签名并比较
    quantum_state_t* verification = quantum_state_create(4);
    
    char combined[512];
    sprintf(combined, "%s%s%s%.8f%s", 
            transaction->transaction_id, 
            transaction->sender, 
            transaction->recipient, 
            transaction->amount, 
            transaction->data);
    
    quantum_state_init_from_string(verification, combined);
    
    // 对比两个量子状态是否相同
    int is_valid = quantum_state_equals(verification, transaction->quantum_signature);
    
    quantum_state_destroy(verification);
    return is_valid;
}

// 创建创世区块
quantum_block_t* quantum_block_create_genesis() {
    quantum_block_t* genesis = (quantum_block_t*)malloc(sizeof(quantum_block_t));
    if (!genesis) return NULL;
    
    genesis->index = 0;
    strcpy(genesis->previous_hash, "0000000000000000000000000000000000000000000000000000000000000000");
    genesis->timestamp = time(NULL);
    genesis->nonce = 0;
    
    // 分配交易列表内存
    genesis->transactions = NULL;
    genesis->transaction_count = 0;
    
    // 创建区块量子状态（使用8个量子比特）
    genesis->quantum_state = quantum_state_create(8);
    
    // 初始化量子状态为叠加态
    quantum_state_hadamard_all(genesis->quantum_state);
    
    // 初始没有与前一区块的纠缠
    genesis->chain_entanglement = NULL;
    
    // 计算区块哈希
    char block_data[512];
    sprintf(block_data, "%u%s%lu%u", 
            genesis->index, 
            genesis->previous_hash, 
            (unsigned long)genesis->timestamp, 
            genesis->nonce);
    
    quantum_gene_hash(block_data, genesis->current_hash);
    
    genesis->next = NULL;
    
    return genesis;
}

// 创建新区块
quantum_block_t* quantum_block_create(quantum_block_t* previous_block, quantum_transaction_t** transactions, unsigned int transaction_count) {
    if (!previous_block) return NULL;
    
    quantum_block_t* new_block = (quantum_block_t*)malloc(sizeof(quantum_block_t));
    if (!new_block) return NULL;
    
    new_block->index = previous_block->index + 1;
    strcpy(new_block->previous_hash, previous_block->current_hash);
    new_block->timestamp = time(NULL);
    new_block->nonce = 0;
    
    // 分配并复制交易
    new_block->transaction_count = transaction_count;
    new_block->transactions = (quantum_transaction_t**)malloc(sizeof(quantum_transaction_t*) * transaction_count);
    
    if (!new_block->transactions) {
        free(new_block);
        return NULL;
    }
    
    for (unsigned int i = 0; i < transaction_count; i++) {
        new_block->transactions[i] = transactions[i];
    }
    
    // 创建区块量子状态（使用8个量子比特）
    new_block->quantum_state = quantum_state_create(8);
    
    // 将新区块的量子状态与前一区块的量子状态纠缠
    new_block->chain_entanglement = quantum_entangle(previous_block->quantum_state, new_block->quantum_state);
    
    // 哈希值将在挖矿过程中设置
    strcpy(new_block->current_hash, "0000000000000000000000000000000000000000000000000000000000000000");
    
    new_block->next = NULL;
    
    return new_block;
}

// 销毁区块
void quantum_block_destroy(quantum_block_t* block) {
    if (!block) return;
    
    // 释放所有交易
    for (unsigned int i = 0; i < block->transaction_count; i++) {
        quantum_transaction_destroy(block->transactions[i]);
    }
    
    if (block->transactions) {
        free(block->transactions);
    }
    
    quantum_state_destroy(block->quantum_state);
    
    if (block->chain_entanglement) {
        quantum_entanglement_destroy(block->chain_entanglement);
    }
    
    free(block);
}

// 计算区块哈希
void quantum_block_calculate_hash(quantum_block_t* block) {
    if (!block) return;
    
    // 构建区块数据字符串
    char block_data[4096] = {0};
    
    // 添加区块头数据
    sprintf(block_data, "%u%s%lu%u", 
            block->index, 
            block->previous_hash, 
            (unsigned long)block->timestamp, 
            block->nonce);
    
    // 添加所有交易数据
    for (unsigned int i = 0; i < block->transaction_count; i++) {
        char tx_data[512];
        sprintf(tx_data, "%s%s%s%.8f", 
                block->transactions[i]->transaction_id,
                block->transactions[i]->sender,
                block->transactions[i]->recipient,
                block->transactions[i]->amount);
        strcat(block_data, tx_data);
    }
    
    // 计算量子哈希
    quantum_gene_hash(block_data, block->current_hash);
}

// 挖矿（工作量证明）
int quantum_block_mine(quantum_block_t* block, unsigned int difficulty) {
    if (!block) return 0;
    
    char target[65] = {0};
    memset(target, '0', difficulty);
    target[difficulty] = '\0';
    
    do {
        block->nonce++;
        quantum_block_calculate_hash(block);
    } while (strncmp(block->current_hash, target, difficulty) != 0);
    
    return 1;
}

// 验证区块
int quantum_block_verify(quantum_block_t* block, unsigned int difficulty) {
    if (!block) return 0;
    
    // 验证哈希
    char temp_hash[65];
    strcpy(temp_hash, block->current_hash);
    
    quantum_block_calculate_hash(block);
    
    if (strcmp(temp_hash, block->current_hash) != 0) {
        return 0;
    }
    
    // 验证难度
    char target[65] = {0};
    memset(target, '0', difficulty);
    target[difficulty] = '\0';
    
    if (strncmp(block->current_hash, target, difficulty) != 0) {
        return 0;
    }
    
    // 验证所有交易
    for (unsigned int i = 0; i < block->transaction_count; i++) {
        if (!quantum_transaction_verify(block->transactions[i])) {
            return 0;
        }
    }
    
    return 1;
}

// 创建量子区块链
quantum_blockchain_t* quantum_blockchain_create(const char* chain_id, unsigned int difficulty) {
    quantum_blockchain_t* blockchain = (quantum_blockchain_t*)malloc(sizeof(quantum_blockchain_t));
    if (!blockchain) return NULL;
    
    strncpy(blockchain->chain_id, chain_id, 63);
    blockchain->chain_id[63] = '\0';
    
    blockchain->difficulty = difficulty;
    
    // 创建创世区块
    blockchain->genesis_block = quantum_block_create_genesis();
    blockchain->latest_block = blockchain->genesis_block;
    blockchain->block_count = 1;
    
    // 创建全局纠缠态
    blockchain->global_entanglement = NULL;
    
    return blockchain;
}

// 销毁量子区块链
void quantum_blockchain_destroy(quantum_blockchain_t* blockchain) {
    if (!blockchain) return;
    
    // 释放所有区块
    quantum_block_t* current = blockchain->genesis_block;
    while (current) {
        quantum_block_t* next = current->next;
        quantum_block_destroy(current);
        current = next;
    }
    
    if (blockchain->global_entanglement) {
        quantum_entanglement_destroy(blockchain->global_entanglement);
    }
    
    free(blockchain);
}

// 添加区块到区块链
int quantum_blockchain_add_block(quantum_blockchain_t* blockchain, quantum_transaction_t** transactions, unsigned int transaction_count) {
    if (!blockchain) return 0;
    
    // 创建新区块
    quantum_block_t* new_block = quantum_block_create(blockchain->latest_block, transactions, transaction_count);
    if (!new_block) return 0;
    
    // 挖矿
    if (!quantum_block_mine(new_block, blockchain->difficulty)) {
        quantum_block_destroy(new_block);
        return 0;
    }
    
    // 验证区块
    if (!quantum_block_verify(new_block, blockchain->difficulty)) {
        quantum_block_destroy(new_block);
        return 0;
    }
    
    // 添加到链
    blockchain->latest_block->next = new_block;
    blockchain->latest_block = new_block;
    blockchain->block_count++;
    
    return 1;
}

// 验证整个区块链
int quantum_blockchain_verify(quantum_blockchain_t* blockchain) {
    if (!blockchain) return 0;
    
    quantum_block_t* current = blockchain->genesis_block;
    quantum_block_t* next = current->next;
    
    while (next) {
        // 验证前一个哈希
        if (strcmp(next->previous_hash, current->current_hash) != 0) {
            return 0;
        }
        
        // 验证当前区块
        if (!quantum_block_verify(next, blockchain->difficulty)) {
            return 0;
        }
        
        // 验证量子纠缠
        if (!quantum_entanglement_verify(next->chain_entanglement)) {
            return 0;
        }
        
        current = next;
        next = current->next;
    }
    
    return 1;
}

// 创建共识节点
quantum_consensus_node_t* quantum_consensus_node_create(const char* node_id, int is_validator, int is_miner) {
    quantum_consensus_node_t* node = (quantum_consensus_node_t*)malloc(sizeof(quantum_consensus_node_t));
    if (!node) return NULL;
    
    strncpy(node->node_id, node_id, 63);
    node->node_id[63] = '\0';
    
    node->is_validator = is_validator;
    node->is_miner = is_miner;
    
    // 创建节点量子状态
    node->node_state = quantum_state_create(4);
    
    // 初始化为随机量子态
    quantum_state_init_random(node->node_state);
    
    // 初始暂无区块链
    node->blockchain = NULL;
    
    // 初始暂无网络纠缠
    node->network_entanglement = NULL;
    
    return node;
}

// 销毁共识节点
void quantum_consensus_node_destroy(quantum_consensus_node_t* node) {
    if (!node) return;
    
    quantum_state_destroy(node->node_state);
    
    if (node->network_entanglement) {
        quantum_entanglement_destroy(node->network_entanglement);
    }
    
    // 注意：不销毁blockchain，因为它可能被其他节点共享
    
    free(node);
}

// 节点加入区块链网络
int quantum_consensus_node_join_network(quantum_consensus_node_t* node, quantum_blockchain_t* blockchain, quantum_consensus_node_t** other_nodes, unsigned int node_count) {
    if (!node || !blockchain) return 0;
    
    // 复制区块链引用
    node->blockchain = blockchain;
    
    // 与其他节点创建量子纠缠
    if (node_count > 0 && other_nodes) {
        // 收集所有节点的量子状态
        quantum_state_t** states = (quantum_state_t**)malloc(sizeof(quantum_state_t*) * (node_count + 1));
        if (!states) return 0;
        
        states[0] = node->node_state;
        for (unsigned int i = 0; i < node_count; i++) {
            states[i + 1] = other_nodes[i]->node_state;
        }
        
        // 创建多方纠缠
        node->network_entanglement = quantum_entangle_multiple(node_count + 1, states[0], states[1], NULL);
        
        free(states);
    }
    
    return 1;
}

// 打印区块链信息
void quantum_blockchain_print(quantum_blockchain_t* blockchain) {
    if (!blockchain) return;
    
    printf("===== 量子区块链信息 =====\n");
    printf("链ID: %s\n", blockchain->chain_id);
    printf("区块数量: %u\n", blockchain->block_count);
    printf("挖矿难度: %u\n", blockchain->difficulty);
    
    printf("\n区块链内容:\n");
    quantum_block_t* current = blockchain->genesis_block;
    int block_index = 0;
    
    while (current) {
        printf("\n区块 #%d:\n", block_index++);
        printf("  索引: %u\n", current->index);
        printf("  哈希: %.10s...\n", current->current_hash);
        printf("  前一区块哈希: %.10s...\n", current->previous_hash);
        printf("  时间戳: %ld\n", (long)current->timestamp);
        printf("  随机数: %u\n", current->nonce);
        printf("  交易数量: %u\n", current->transaction_count);
        
        for (unsigned int i = 0; i < current->transaction_count; i++) {
            printf("    交易 #%u:\n", i);
            printf("      ID: %s\n", current->transactions[i]->transaction_id);
            printf("      发送方: %s\n", current->transactions[i]->sender);
            printf("      接收方: %s\n", current->transactions[i]->recipient);
            printf("      金额: %.8f\n", current->transactions[i]->amount);
        }
        
        current = current->next;
    }
    
    printf("\n===========================\n");
}

// 查找特定交易
quantum_transaction_t* quantum_blockchain_find_transaction(quantum_blockchain_t* blockchain, const char* transaction_id) {
    if (!blockchain || !transaction_id) return NULL;
    
    quantum_block_t* current = blockchain->genesis_block;
    
    while (current) {
        for (unsigned int i = 0; i < current->transaction_count; i++) {
            if (strcmp(current->transactions[i]->transaction_id, transaction_id) == 0) {
                return current->transactions[i];
            }
        }
        
        current = current->next;
    }
    
    return NULL;
}

// 计算账户余额
double quantum_blockchain_get_balance(quantum_blockchain_t* blockchain, const char* account) {
    if (!blockchain || !account) return 0.0;
    
    double balance = 0.0;
    quantum_block_t* current = blockchain->genesis_block;
    
    while (current) {
        for (unsigned int i = 0; i < current->transaction_count; i++) {
            if (strcmp(current->transactions[i]->recipient, account) == 0) {
                balance += current->transactions[i]->amount;
            }
            
            if (strcmp(current->transactions[i]->sender, account) == 0) {
                balance -= current->transactions[i]->amount;
            }
        }
        
        current = current->next;
    }
    
    return balance;
} 