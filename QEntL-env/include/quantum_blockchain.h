/**
 * @file quantum_blockchain.h
 * @brief 量子区块链模块头文件
 * @author Claude
 * @version 1.0
 * @date 2024-05-31
 */

#ifndef QUANTUM_BLOCKCHAIN_H
#define QUANTUM_BLOCKCHAIN_H

#include <stdint.h>
#include <time.h>
#include "quantum_state.h"
#include "quantum_entanglement.h"

/**
 * @brief 量子区块链中的交易类型
 */
typedef enum {
    TRANSACTION_TYPE_NORMAL,        /* 普通交易 */
    TRANSACTION_TYPE_QUANTUM_STATE, /* 量子状态交易 */
    TRANSACTION_TYPE_ENTANGLEMENT,  /* 量子纠缠交易 */
    TRANSACTION_TYPE_CONTRACT       /* 智能合约交易 */
} TransactionType;

/**
 * @brief 交易结构体
 */
typedef struct {
    uint64_t id;                /* 交易ID */
    TransactionType type;       /* 交易类型 */
    char sender[64];            /* 发送者地址 */
    char receiver[64];          /* 接收者地址 */
    uint64_t amount;            /* 交易金额/数量 */
    void *data;                 /* 交易数据，根据类型可能是量子状态或合约代码 */
    size_t data_size;           /* 数据大小 */
    uint8_t signature[128];     /* 量子签名 */
    time_t timestamp;           /* 时间戳 */
} Transaction;

/**
 * @brief 区块头结构体
 */
typedef struct {
    uint32_t version;           /* 区块版本 */
    uint8_t prev_hash[64];      /* 前一个区块的哈希 */
    uint8_t merkle_root[64];    /* 默克尔树根 */
    time_t timestamp;           /* 时间戳 */
    uint32_t difficulty;        /* 难度目标 */
    uint64_t nonce;             /* 随机数 */
    uint8_t quantum_hash[128];  /* 量子哈希 */
} BlockHeader;

/**
 * @brief 区块结构体
 */
typedef struct {
    BlockHeader header;         /* 区块头 */
    uint32_t tx_count;          /* 交易数量 */
    Transaction *transactions;  /* 交易数组 */
    uint8_t quantum_state_hash[64]; /* 区块的量子状态哈希 */
    QuantumState *block_state;  /* 区块的量子状态 */
} Block;

/**
 * @brief 量子区块链结构体前向声明
 */
typedef struct QuantumBlockchain QuantumBlockchain;

/**
 * @brief 创建一个新的量子区块链
 * 
 * @param difficulty 初始挖矿难度
 * @param genesis_data 创世区块数据
 * @return QuantumBlockchain* 创建的区块链指针
 */
QuantumBlockchain* blockchain_create(uint32_t difficulty, const char *genesis_data);

/**
 * @brief 销毁区块链并释放资源
 * 
 * @param chain 区块链指针
 */
void blockchain_destroy(QuantumBlockchain *chain);

/**
 * @brief 创建一个新交易
 * 
 * @param type 交易类型
 * @param sender 发送者地址
 * @param receiver 接收者地址
 * @param amount 交易金额/数量
 * @param data 交易数据
 * @param data_size 数据大小
 * @return Transaction* 创建的交易指针
 */
Transaction* transaction_create(TransactionType type, const char *sender, const char *receiver, 
                               uint64_t amount, const void *data, size_t data_size);

/**
 * @brief 销毁交易并释放资源
 * 
 * @param tx 交易指针
 */
void transaction_destroy(Transaction *tx);

/**
 * @brief 为交易生成量子签名
 * 
 * @param tx 交易指针
 * @param private_key 私钥
 * @return int 成功返回0，失败返回非0值
 */
int transaction_sign(Transaction *tx, const uint8_t *private_key);

/**
 * @brief 验证交易签名
 * 
 * @param tx 交易指针
 * @param public_key 公钥
 * @return int 验证成功返回1，失败返回0
 */
int transaction_verify(const Transaction *tx, const uint8_t *public_key);

/**
 * @brief 向区块链添加一个新交易
 * 
 * @param chain 区块链指针
 * @param tx 交易指针
 * @return int 成功返回交易索引，失败返回-1
 */
int blockchain_add_transaction(QuantumBlockchain *chain, const Transaction *tx);

/**
 * @brief 挖掘新区块
 * 
 * @param chain 区块链指针
 * @param miner_address 矿工地址(接收奖励)
 * @return Block* 挖出的新区块，失败返回NULL
 */
Block* blockchain_mine_block(QuantumBlockchain *chain, const char *miner_address);

/**
 * @brief 验证区块有效性
 * 
 * @param chain 区块链指针
 * @param block 要验证的区块
 * @return int 验证成功返回1，失败返回0
 */
int blockchain_validate_block(const QuantumBlockchain *chain, const Block *block);

/**
 * @brief 将区块添加到区块链
 * 
 * @param chain 区块链指针
 * @param block 要添加的区块
 * @return int 成功返回0，失败返回-1
 */
int blockchain_add_block(QuantumBlockchain *chain, const Block *block);

/**
 * @brief 获取区块链中的区块数量
 * 
 * @param chain 区块链指针
 * @return uint64_t 区块数量
 */
uint64_t blockchain_get_block_count(const QuantumBlockchain *chain);

/**
 * @brief 获取指定索引的区块
 * 
 * @param chain 区块链指针
 * @param index 区块索引
 * @return const Block* 区块指针，不存在返回NULL
 */
const Block* blockchain_get_block(const QuantumBlockchain *chain, uint64_t index);

/**
 * @brief 获取最新区块
 * 
 * @param chain 区块链指针
 * @return const Block* 最新区块指针
 */
const Block* blockchain_get_latest_block(const QuantumBlockchain *chain);

/**
 * @brief 根据交易ID查找交易
 * 
 * @param chain 区块链指针
 * @param tx_id 交易ID
 * @return const Transaction* 交易指针，不存在返回NULL
 */
const Transaction* blockchain_find_transaction(const QuantumBlockchain *chain, uint64_t tx_id);

/**
 * @brief 导出区块链到文件
 * 
 * @param chain 区块链指针
 * @param filename 文件名
 * @return int 成功返回0，失败返回-1
 */
int blockchain_export(const QuantumBlockchain *chain, const char *filename);

/**
 * @brief 从文件导入区块链
 * 
 * @param filename 文件名
 * @return QuantumBlockchain* 导入的区块链指针，失败返回NULL
 */
QuantumBlockchain* blockchain_import(const char *filename);

/**
 * @brief 计算区块链状态熵
 * 
 * @param chain 区块链指针
 * @return double 熵值
 */
double blockchain_calculate_entropy(const QuantumBlockchain *chain);

/**
 * @brief 量子区块链一致性验证
 * 
 * @param chain 区块链指针
 * @return int 一致性检查通过返回1，失败返回0
 */
int blockchain_verify_consistency(const QuantumBlockchain *chain);

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
                               const char *method, const void *params, void *result);

#endif /* QUANTUM_BLOCKCHAIN_H */ 