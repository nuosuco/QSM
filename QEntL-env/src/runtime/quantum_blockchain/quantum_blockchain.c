/**
 * @file quantum_blockchain.c
 * @brief 量子区块链模块实现 - 整合版
 * @author QEntL开发团队
 * @version 1.1
 * @date 2024-06-05
 * 
 * 该模块利用量子纠缠特性实现安全、不可篡改且自动同步的分布式账本
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include "../../../include/quantum_blockchain.h"
#include "../../../include/quantum_state.h"
#include "../../../include/quantum_entanglement.h"

/**
 * @brief 量子区块链结构体定义
 */
struct QuantumBlockchain {
    uint64_t block_count;           /* 区块数量 */
    Block **blocks;                 /* 区块数组 */
    uint32_t difficulty;            /* 当前挖矿难度 */
    uint32_t pending_tx_count;      /* 待处理交易数量 */
    Transaction **pending_txs;      /* 待处理交易数组 */
    QuantumState *chain_state;      /* 区块链的量子状态 */
    time_t creation_time;           /* 创建时间 */
    char chain_id[64];              /* 链标识符 */
    quantum_entanglement_t* global_entanglement; // 全局量子纠缠状态，用于区块同步
};

// 从旧版本保留的量子共识节点结构，用于网络共识
typedef struct {
    char node_id[64];                  /* 节点ID */
    QuantumState* node_state;          /* 节点量子状态 */
    quantum_entanglement_t* network_entanglement; /* 与网络的纠缠 */
    int is_validator;                  /* 是否为验证节点 */
    int is_miner;                      /* 是否为挖矿节点 */
    struct QuantumBlockchain* blockchain;  /* 本地区块链副本 */
} quantum_consensus_node_t;

/**
 * @brief 计算交易的哈希值
 * 
 * @param tx 交易指针
 * @param hash_out 输出哈希值的缓冲区，至少64字节
 */
static void calculate_transaction_hash(const Transaction *tx, uint8_t *hash_out) {
    // 创建一个缓冲区存储交易数据
    char buffer[1024];
    sprintf(buffer, "%lu|%d|%s|%s|%lu|%lu", 
            tx->id, tx->type, tx->sender, tx->receiver, 
            tx->amount, tx->timestamp);
    
    // 简化实现：使用简单哈希函数
    uint8_t hash[64] = {0};
    uint32_t hash_val = 0;
    
    for(size_t i = 0; i < strlen(buffer); i++) {
        hash_val = ((hash_val << 5) + hash_val) + buffer[i];
    }
    
    // 将哈希值转换为十六进制字符串
    for(int i = 0; i < 16; i++) {
        sprintf((char*)hash + (i*2), "%02x", (hash_val >> (i*8)) & 0xFF);
    }
    
    memcpy(hash_out, hash, 64);
}

/**
 * @brief 计算区块的哈希值
 * 
 * @param block 区块指针
 * @param hash_out 输出哈希值的缓冲区，至少128字节
 */
static void calculate_block_hash(const Block *block, uint8_t *hash_out) {
    // 创建一个缓冲区存储区块头数据
    char buffer[2048];
    sprintf(buffer, "%u|%lu|%lu|%lu", 
            block->header.version,
            (unsigned long)block->header.timestamp,
            block->header.difficulty,
            block->header.nonce);
    
    // 添加前一个区块哈希
    strcat(buffer, "|");
    strncat(buffer, (char*)block->header.prev_hash, 64);
    
    // 添加默克尔根
    strcat(buffer, "|");
    strncat(buffer, (char*)block->header.merkle_root, 64);
    
    // 简化实现：使用简单哈希函数
    uint8_t hash[128] = {0};
    uint64_t hash_val = 0;
    
    for(size_t i = 0; i < strlen(buffer); i++) {
        hash_val = ((hash_val << 5) + hash_val) + buffer[i];
        hash_val = hash_val * 17 + buffer[i]; // 多重混合
    }
    
    // 将哈希值转换为十六进制字符串
    for(int i = 0; i < 32; i++) {
        sprintf((char*)hash + (i*2), "%02x", (uint8_t)((hash_val >> (i*8)) & 0xFF));
    }
    
    memcpy(hash_out, hash, 128);
}

/**
 * @brief 计算默克尔树根哈希
 * 
 * @param txs 交易数组
 * @param tx_count 交易数量
 * @param merkle_root 输出默克尔根的缓冲区，至少64字节
 */
static void calculate_merkle_root(const Transaction **txs, uint32_t tx_count, uint8_t *merkle_root) {
    if (tx_count == 0) {
        memset(merkle_root, 0, 64);
        return;
    }
    
    // 为每个交易计算哈希
    uint8_t **tx_hashes = (uint8_t**)malloc(tx_count * sizeof(uint8_t*));
    for (uint32_t i = 0; i < tx_count; i++) {
        tx_hashes[i] = (uint8_t*)malloc(64);
        calculate_transaction_hash(txs[i], tx_hashes[i]);
    }
    
    // 简化的默克尔树实现，仅用于演示
    uint8_t tmp_hash[64];
    if (tx_count == 1) {
        memcpy(merkle_root, tx_hashes[0], 64);
    } else {
        // 组合所有哈希
        memset(tmp_hash, 0, 64);
        for (uint32_t i = 0; i < tx_count; i++) {
            for (int j = 0; j < 64; j++) {
                tmp_hash[j] ^= tx_hashes[i][j];
            }
        }
        memcpy(merkle_root, tmp_hash, 64);
    }
    
    // 释放内存
    for (uint32_t i = 0; i < tx_count; i++) {
        free(tx_hashes[i]);
    }
    free(tx_hashes);
}

/**
 * @brief 验证工作量证明
 * 
 * @param hash 区块哈希
 * @param difficulty 挖矿难度
 * @return int 验证成功返回1，失败返回0
 */
static int verify_proof_of_work(const uint8_t *hash, uint32_t difficulty) {
    // 验证哈希前difficulty位是否为0
    for (uint32_t i = 0; i < difficulty / 4; i++) {
        if (hash[i] != 0) {
            return 0;
        }
    }
    
    if (difficulty % 4) {
        uint8_t mask = 0xF0 >> (difficulty % 4);
        if ((hash[difficulty / 4] & mask) != 0) {
            return 0;
        }
    }
    
    return 1;
}

/**
 * @brief 创建一个新的量子区块链
 * 
 * @param difficulty 初始挖矿难度
 * @param genesis_data 创世区块数据
 * @return QuantumBlockchain* 创建的区块链指针
 */
QuantumBlockchain* blockchain_create(uint32_t difficulty, const char *genesis_data) {
    QuantumBlockchain *chain = (QuantumBlockchain*)malloc(sizeof(QuantumBlockchain));
    if (!chain) {
        fprintf(stderr, "错误: 无法分配区块链内存\n");
        return NULL;
    }
    
    // 初始化区块链
    chain->block_count = 0;
    chain->blocks = NULL;
    chain->difficulty = difficulty;
    chain->pending_tx_count = 0;
    chain->pending_txs = NULL;
    chain->creation_time = time(NULL);
    chain->global_entanglement = NULL;
    
    // 生成链ID
    snprintf(chain->chain_id, sizeof(chain->chain_id), "QBC%lX", 
            (unsigned long)chain->creation_time ^ (unsigned long)rand());
    
    // 创建链的量子状态 (8个量子比特)
    chain->chain_state = quantum_state_create(8);
    if (chain->chain_state) {
        // 初始化量子状态为叠加态
        quantum_state_hadamard_all(chain->chain_state);
    }
    
    // 创建创世区块
    Transaction *genesis_tx = transaction_create(
        TRANSACTION_TYPE_NORMAL, 
        "SYSTEM", 
        "GENESIS", 
        0, 
        genesis_data, 
        strlen(genesis_data) + 1
    );
    
    if (!genesis_tx) {
        if (chain->chain_state) {
            quantum_state_destroy(chain->chain_state);
        }
        free(chain);
        return NULL;
    }
    
    // 将创世交易添加到区块链
    blockchain_add_transaction(chain, genesis_tx);
    
    // 挖掘创世区块
    Block *genesis_block = blockchain_mine_block(chain, "SYSTEM");
    if (!genesis_block) {
        transaction_destroy(genesis_tx);
        if (chain->chain_state) {
            quantum_state_destroy(chain->chain_state);
        }
        free(chain);
        return NULL;
    }
    
    printf("量子区块链创建成功，链ID: %s\n", chain->chain_id);
    
    return chain;
}

/**
 * @brief 销毁区块链并释放资源
 * 
 * @param chain 区块链指针
 */
void blockchain_destroy(QuantumBlockchain *chain) {
    if (!chain) return;
    
    // 释放所有区块
    for (uint64_t i = 0; i < chain->block_count; i++) {
        Block *block = chain->blocks[i];
        
        // 释放所有交易
        for (uint32_t j = 0; j < block->tx_count; j++) {
            transaction_destroy(block->transactions[j]);
        }
        
        // 释放交易数组
        if (block->transactions) {
            free(block->transactions);
        }
        
        // 释放区块量子状态
        if (block->block_state) {
            quantum_state_destroy(block->block_state);
        }
        
        free(block);
    }
    
    // 释放区块数组
    if (chain->blocks) {
        free(chain->blocks);
    }
    
    // 释放待处理交易
    for (uint32_t i = 0; i < chain->pending_tx_count; i++) {
        transaction_destroy(chain->pending_txs[i]);
    }
    
    // 释放待处理交易数组
    if (chain->pending_txs) {
        free(chain->pending_txs);
    }
    
    // 释放链的量子状态
    if (chain->chain_state) {
        quantum_state_destroy(chain->chain_state);
    }
    
    // 释放全局纠缠状态
    if (chain->global_entanglement) {
        quantum_entanglement_destroy(chain->global_entanglement);
    }
    
    free(chain);
    printf("量子区块链已销毁\n");
}

/**
 * @brief 向区块链添加一个新交易
 * 
 * @param chain 区块链指针
 * @param tx 交易指针
 * @return int 成功返回交易索引，失败返回-1
 */
int blockchain_add_transaction(QuantumBlockchain *chain, Transaction *tx) {
    if (!chain || !tx) {
        return -1;
    }
    
    // 验证交易
    if (!transaction_verify(tx, NULL)) { // 公钥验证暂时不实现
        fprintf(stderr, "错误: 交易验证失败\n");
        return -1;
    }
    
    // 分配或重新分配待处理交易数组
    if (chain->pending_tx_count == 0) {
        chain->pending_txs = (Transaction**)malloc(sizeof(Transaction*));
        if (!chain->pending_txs) {
            fprintf(stderr, "错误: 无法分配交易内存\n");
            return -1;
        }
    } else {
        Transaction **new_txs = (Transaction**)realloc(
            chain->pending_txs, 
            (chain->pending_tx_count + 1) * sizeof(Transaction*)
        );
        
        if (!new_txs) {
            fprintf(stderr, "错误: 无法重新分配交易内存\n");
            return -1;
        }
        
        chain->pending_txs = new_txs;
    }
    
    // 添加交易
    chain->pending_txs[chain->pending_tx_count] = tx;
    int index = chain->pending_tx_count;
    chain->pending_tx_count++;
    
    printf("交易已添加到区块链，等待挖掘\n");
    
    return index;
}

/**
 * @brief 挖掘一个新区块
 * 
 * @param chain 区块链指针
 * @param miner_address 矿工地址
 * @return Block* 成功返回新区块指针，失败返回NULL
 */
Block* blockchain_mine_block(QuantumBlockchain *chain, const char *miner_address) {
    if (!chain || !miner_address || chain->pending_tx_count == 0) {
        return NULL;
    }
    
    // 创建新区块
    Block *new_block = (Block*)malloc(sizeof(Block));
    if (!new_block) {
        fprintf(stderr, "错误: 无法分配区块内存\n");
        return NULL;
    }
    
    // 初始化区块头
    new_block->header.version = 1;
    new_block->header.timestamp = time(NULL);
    new_block->header.difficulty = chain->difficulty;
    new_block->header.nonce = 0;
    
    // 设置前一个区块的哈希
    if (chain->block_count == 0) {
        // 创世区块
        memset(new_block->header.prev_hash, 0, 64);
    } else {
        // 使用前一个区块的哈希
        memcpy(new_block->header.prev_hash, chain->blocks[chain->block_count-1]->header.quantum_hash, 64);
    }
    
    // 复制待处理交易
    new_block->tx_count = chain->pending_tx_count;
    new_block->transactions = (Transaction**)malloc(new_block->tx_count * sizeof(Transaction*));
    if (!new_block->transactions) {
        fprintf(stderr, "错误: 无法分配交易数组内存\n");
        free(new_block);
        return NULL;
    }
    
    for (uint32_t i = 0; i < chain->pending_tx_count; i++) {
        new_block->transactions[i] = chain->pending_txs[i];
    }
    
    // 计算默克尔根
    calculate_merkle_root((const Transaction**)new_block->transactions, new_block->tx_count, new_block->header.merkle_root);
    
    printf("开始挖掘区块...\n");
    
    // 挖掘区块 (工作量证明)
    uint8_t hash[128];
    bool found = false;
    
    while (!found) {
        // 计算区块哈希
        calculate_block_hash(new_block, hash);
        
        // 检查是否满足难度要求
        if (verify_proof_of_work(hash, chain->difficulty)) {
            found = true;
        } else {
            new_block->header.nonce++;
        }
    }
    
    // 保存区块哈希
    memcpy(new_block->header.quantum_hash, hash, 128);
    
    // 创建区块的量子状态 (8个量子比特)
    new_block->block_state = quantum_state_create(8);
    if (new_block->block_state) {
        // 初始化为与区块数据有关的状态
        char block_data[256];
        sprintf(block_data, "BLOCK%lu", (unsigned long)chain->block_count);
        quantum_state_init_from_string(new_block->block_state, block_data);
        
        // 如果不是创世区块，创建与前一个区块的量子纠缠
        if (chain->block_count > 0 && chain->blocks[chain->block_count-1]->block_state) {
            // 创建纠缠态
            quantum_entanglement_t* entanglement = quantum_entangle(
                chain->blocks[chain->block_count-1]->block_state,
                new_block->block_state
            );
            
            // 将纠缠信息保存在链的全局纠缠状态中
            if (entanglement) {
                if (chain->global_entanglement) {
                    quantum_entanglement_destroy(chain->global_entanglement);
                }
                chain->global_entanglement = entanglement;
            }
        }
    }
    
    // 计算区块的量子状态哈希
    memcpy(new_block->quantum_state_hash, new_block->header.quantum_hash, 64);
    
    // 将新区块添加到区块链
    if (chain->block_count == 0) {
        chain->blocks = (Block**)malloc(sizeof(Block*));
        if (!chain->blocks) {
            fprintf(stderr, "错误: 无法分配区块数组内存\n");
            if (new_block->transactions) free(new_block->transactions);
            if (new_block->block_state) quantum_state_destroy(new_block->block_state);
            free(new_block);
            return NULL;
        }
    } else {
        Block **new_blocks = (Block**)realloc(
            chain->blocks, 
            (chain->block_count + 1) * sizeof(Block*)
        );
        
        if (!new_blocks) {
            fprintf(stderr, "错误: 无法重新分配区块数组内存\n");
            if (new_block->transactions) free(new_block->transactions);
            if (new_block->block_state) quantum_state_destroy(new_block->block_state);
            free(new_block);
            return NULL;
        }
        
        chain->blocks = new_blocks;
    }
    
    chain->blocks[chain->block_count] = new_block;
    chain->block_count++;
    
    // 清空待处理交易
    free(chain->pending_txs);
    chain->pending_txs = NULL;
    chain->pending_tx_count = 0;
    
    printf("区块成功挖掘，哈希: %.16s...\n", (char*)new_block->header.quantum_hash);
    
    return new_block;
}

/**
 * @brief 验证区块链完整性
 * 
 * @param chain 区块链指针
 * @return int 验证成功返回1，失败返回0
 */
int blockchain_verify_consistency(const QuantumBlockchain *chain) {
    if (!chain) return 0;
    
    // 验证区块链中的每个区块
    for (uint64_t i = 0; i < chain->block_count; i++) {
        // 验证当前区块
        const Block *block = chain->blocks[i];
        
        // 验证区块哈希
        uint8_t calculated_hash[128];
        calculate_block_hash(block, calculated_hash);
        
        if (memcmp(calculated_hash, block->header.quantum_hash, 128) != 0) {
            fprintf(stderr, "一致性检查失败: 区块 %lu 哈希不匹配\n", (unsigned long)i);
            return 0;
        }
        
        // 验证与前一个区块的链接
        if (i > 0) {
            const Block *prev_block = chain->blocks[i-1];
            if (memcmp(block->header.prev_hash, prev_block->header.quantum_hash, 64) != 0) {
                fprintf(stderr, "一致性检查失败: 区块 %lu 与前一区块的链接无效\n", (unsigned long)i);
                return 0;
            }
        }
        
        // 验证工作量证明
        if (!verify_proof_of_work(block->header.quantum_hash, block->header.difficulty)) {
            fprintf(stderr, "一致性检查失败: 区块 %lu 工作量证明无效\n", (unsigned long)i);
            return 0;
        }
        
        // 验证默克尔根
        uint8_t merkle_root[64];
        calculate_merkle_root((const Transaction**)block->transactions, block->tx_count, merkle_root);
        
        if (memcmp(merkle_root, block->header.merkle_root, 64) != 0) {
            fprintf(stderr, "一致性检查失败: 区块 %lu 默克尔根不匹配\n", (unsigned long)i);
            return 0;
        }
        
        // 验证所有交易
        for (uint32_t j = 0; j < block->tx_count; j++) {
            if (!transaction_verify(block->transactions[j], NULL)) { // 公钥验证暂时不实现
                fprintf(stderr, "一致性检查失败: 区块 %lu 交易 %u 无效\n", (unsigned long)i, j);
                return 0;
            }
        }
    }
    
    return 1;
}

/**
 * @brief 导出区块链到文件
 * 
 * @param chain 区块链指针
 * @param filename 文件名
 * @return int 成功返回0，失败返回-1
 */
int blockchain_export(const QuantumBlockchain *chain, const char *filename) {
    if (!chain || !filename) {
        return -1;
    }
    
    FILE *file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "错误: 无法打开文件 %s\n", filename);
        return -1;
    }
    
    // 写入区块链信息
    fprintf(file, "量子区块链导出\n");
    fprintf(file, "链ID: %s\n", chain->chain_id);
    fprintf(file, "创建时间: %s", ctime(&chain->creation_time));
    fprintf(file, "区块数量: %lu\n", (unsigned long)chain->block_count);
    fprintf(file, "当前难度: %u\n\n", chain->difficulty);
    
    // 写入每个区块的信息
    for (uint64_t i = 0; i < chain->block_count; i++) {
        const Block *block = chain->blocks[i];
        
        fprintf(file, "区块 #%lu\n", (unsigned long)i);
        fprintf(file, "  版本: %u\n", block->header.version);
        fprintf(file, "  时间戳: %s", ctime(&block->header.timestamp));
        fprintf(file, "  难度: %u\n", block->header.difficulty);
        fprintf(file, "  Nonce: %lu\n", (unsigned long)block->header.nonce);
        
        fprintf(file, "  前一区块哈希: ");
        for (int j = 0; j < 16; j++) {
            fprintf(file, "%02X", block->header.prev_hash[j]);
        }
        fprintf(file, "...\n");
        
        fprintf(file, "  默克尔根: ");
        for (int j = 0; j < 16; j++) {
            fprintf(file, "%02X", block->header.merkle_root[j]);
        }
        fprintf(file, "...\n");
        
        fprintf(file, "  量子哈希: ");
        for (int j = 0; j < 16; j++) {
            fprintf(file, "%02X", block->header.quantum_hash[j]);
        }
        fprintf(file, "...\n");
        
        fprintf(file, "  交易数量: %u\n", block->tx_count);
        
        // 写入交易信息
        for (uint32_t j = 0; j < block->tx_count; j++) {
            const Transaction *tx = block->transactions[j];
            
            fprintf(file, "    交易 #%u\n", j);
            fprintf(file, "      ID: %lu\n", tx->id);
            fprintf(file, "      类型: %d\n", tx->type);
            fprintf(file, "      发送者: %s\n", tx->sender);
            fprintf(file, "      接收者: %s\n", tx->receiver);
            fprintf(file, "      金额: %lu\n", tx->amount);
            fprintf(file, "      时间戳: %s", ctime(&tx->timestamp));
            
            fprintf(file, "      数据: ");
            uint8_t *data = (uint8_t*)tx->data;
            size_t print_size = tx->data_size > 64 ? 64 : tx->data_size;
            
            for (size_t k = 0; k < print_size; k++) {
                if (data[k] >= 32 && data[k] <= 126) {
                    fputc(data[k], file);
                } else {
                    fprintf(file, "\\%02X", (unsigned char)data[k]);
                }
            }
            
            if (tx->data_size > 64) {
                fprintf(file, "...");
            }
            
            fprintf(file, "\n");
            
            // 写入签名
            fprintf(file, "      签名: ");
            for (int k = 0; k < 16; k++) {
                fprintf(file, "%02X", tx->signature[k]);
            }
            fprintf(file, "...\n");
        }
        
        fprintf(file, "\n");
    }
    
    fclose(file);
    printf("区块链已导出到文件: %s\n", filename);
    
    return 0;
}

/**
 * @brief 从文件导入区块链
 * 
 * @param filename 文件名
 * @return QuantumBlockchain* 导入的区块链指针，失败返回NULL
 */
QuantumBlockchain* blockchain_import(const char *filename) {
    // 这个函数需要详细实现来解析导出的文件格式
    // 由于代码较长且复杂，此处仅提供实现框架
    
    printf("从文件导入区块链功能尚未实现\n");
    return NULL;
}

/**
 * @brief 计算区块链状态熵
 * 
 * @param chain 区块链指针
 * @return double 熵值
 */
double blockchain_calculate_entropy(const QuantumBlockchain *chain) {
    if (!chain) return 0.0;
    
    // 简化实现：计算基于区块数量和交易数量的熵值
    double entropy = 0.0;
    uint64_t total_txs = 0;
    
    for (uint64_t i = 0; i < chain->block_count; i++) {
        total_txs += chain->blocks[i]->tx_count;
    }
    
    // 简单熵计算公式（仅作演示）
    if (total_txs > 0) {
        entropy = log(chain->block_count) * log(total_txs);
    }
    
    return entropy;
}

/**
 * @brief 在区块链上执行智能合约
 * 
 * @param chain 区块链指针
 * @param contract_address 合约地址
 * @param method 方法名
 * @param params 参数
 * @param result 执行结果输出
 * @return int 成功返回0，失败返回-1
 */
int blockchain_execute_contract(QuantumBlockchain *chain, const char *contract_address, 
                               const char *method, const void *params, void *result) {
    // 智能合约执行功能尚未实现
    printf("智能合约执行功能尚未实现\n");
    return -1;
}

/**
 * @brief 计算区块的量子状态哈希
 * 
 * @param block 区块指针
 */
static void calculate_quantum_state_hash(Block *block) {
    // 这里应该使用量子状态计算哈希
    // 此处为演示实现
    
    // 使用块的量子哈希作为量子状态哈希
    memcpy(block->quantum_state_hash, block->header.quantum_hash, 64);
}

/**
 * @brief 创建量子共识节点
 * 
 * @param node_id 节点ID
 * @param is_validator 是否为验证节点
 * @param is_miner 是否为挖矿节点
 * @return quantum_consensus_node_t* 创建的节点指针
 */
quantum_consensus_node_t* quantum_consensus_node_create(const char* node_id, int is_validator, int is_miner) {
    quantum_consensus_node_t* node = (quantum_consensus_node_t*)malloc(sizeof(quantum_consensus_node_t));
    if (!node) return NULL;
    
    strncpy(node->node_id, node_id, 63);
    node->node_id[63] = '\0';
    
    node->is_validator = is_validator;
    node->is_miner = is_miner;
    
    // 创建节点量子状态 (4个量子比特)
    node->node_state = quantum_state_create(4);
    if (node->node_state) {
        // 初始化为随机量子态
        quantum_state_init_random(node->node_state);
    }
    
    // 初始暂无区块链和网络纠缠
    node->blockchain = NULL;
    node->network_entanglement = NULL;
    
    return node;
}

/**
 * @brief 销毁共识节点
 * 
 * @param node 节点指针
 */
void quantum_consensus_node_destroy(quantum_consensus_node_t* node) {
    if (!node) return;
    
    if (node->node_state) {
        quantum_state_destroy(node->node_state);
    }
    
    if (node->network_entanglement) {
        quantum_entanglement_destroy(node->network_entanglement);
    }
    
    // 注意：不销毁blockchain，因为它可能被其他节点共享
    
    free(node);
}

/**
 * @brief 节点加入区块链网络
 * 
 * @param node 节点指针
 * @param chain 区块链指针
 * @param other_nodes 其他节点数组
 * @param node_count 其他节点数量
 * @return int 成功返回1，失败返回0
 */
int quantum_consensus_node_join_network(quantum_consensus_node_t* node, QuantumBlockchain* chain, 
                                       quantum_consensus_node_t** other_nodes, unsigned int node_count) {
    if (!node || !chain) return 0;
    
    // 设置节点的区块链
    node->blockchain = chain;
    
    // 与其他节点建立量子纠缠
    if (other_nodes && node_count > 0) {
        // 在实际实现中，这里应该创建一个多方量子纠缠网络
        // 在这个简化实现中，我们仅与第一个节点建立纠缠
        quantum_consensus_node_t* first_node = other_nodes[0];
        if (first_node && first_node->node_state && node->node_state) {
            node->network_entanglement = quantum_entangle(node->node_state, first_node->node_state);
        }
    }
    
    printf("节点 %s 已加入网络\n", node->node_id);
    return 1;
}

/**
 * @brief 获取账户余额
 * 
 * @param chain 区块链指针
 * @param account 账户地址
 * @return double 账户余额
 */
double blockchain_get_balance(QuantumBlockchain* chain, const char* account) {
    if (!chain || !account) return 0.0;
    
    double balance = 0.0;
    
    // 遍历所有区块和交易
    for (uint64_t i = 0; i < chain->block_count; i++) {
        Block* block = chain->blocks[i];
        
        for (uint32_t j = 0; j < block->tx_count; j++) {
            Transaction* tx = block->transactions[j];
            
            // 如果交易的接收者是指定账户，增加余额
            if (strcmp(tx->receiver, account) == 0) {
                balance += tx->amount;
            }
            
            // 如果交易的发送者是指定账户，减少余额
            if (strcmp(tx->sender, account) == 0) {
                balance -= tx->amount;
            }
        }
    }
    
    return balance;
} 