/**
 * @file quantum_contract_manager.h
 * @brief 量子区块链智能合约管理系统头文件
 * @author Claude
 * @version 1.0
 * @date 2024-06-03
 */

#ifndef QUANTUM_CONTRACT_MANAGER_H
#define QUANTUM_CONTRACT_MANAGER_H

#include <stdint.h>
#include <time.h>
#include "quantum_state.h"
#include "quantum_blockchain.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief 智能合约类型枚举
 */
typedef enum {
    CONTRACT_TYPE_BASIC,           /* 基本合约 */
    CONTRACT_TYPE_QUANTUM,         /* 量子合约 */
    CONTRACT_TYPE_HYBRID           /* 混合合约 */
} ContractType;

/**
 * @brief 合约执行状态枚举
 */
typedef enum {
    CONTRACT_STATUS_PENDING,       /* 待执行 */
    CONTRACT_STATUS_EXECUTING,     /* 执行中 */
    CONTRACT_STATUS_COMPLETED,     /* 已完成 */
    CONTRACT_STATUS_FAILED         /* 执行失败 */
} ContractStatus;

/**
 * @brief 合约参数类型枚举
 */
typedef enum {
    PARAM_TYPE_INT,                /* 整数参数 */
    PARAM_TYPE_FLOAT,              /* 浮点数参数 */
    PARAM_TYPE_STRING,             /* 字符串参数 */
    PARAM_TYPE_QUANTUM             /* 量子参数 */
} ContractParamType;

/**
 * @brief 智能合约结构体前向声明
 */
typedef struct QuantumContract QuantumContract;

/**
 * @brief 合约参数结构体
 */
typedef struct {
    char name[32];                 /* 参数名称 */
    ContractParamType type;        /* 参数类型 */
    union {
        int64_t int_value;
        double float_value;
        char *string_value;
        QuantumState *quantum_value;
    } value;                       /* 参数值 */
} ContractParameter;

/**
 * @brief 合约执行结果结构体
 */
typedef struct {
    int success;                   /* 执行成功标志 */
    char message[256];             /* 结果消息 */
    void *data;                    /* 结果数据 */
    size_t data_size;              /* 数据大小 */
    QuantumState *result_state;    /* 结果量子状态 */
} ContractResult;

/**
 * @brief 合约管理器结构体前向声明
 */
typedef struct ContractManager ContractManager;

/**
 * @brief 创建合约管理器
 * 
 * @return ContractManager* 合约管理器指针
 */
ContractManager* contract_manager_create(void);

/**
 * @brief 销毁合约管理器
 * 
 * @param manager 合约管理器指针
 */
void contract_manager_destroy(ContractManager *manager);

/**
 * @brief 创建新合约
 * 
 * @param manager 合约管理器指针
 * @param creator 创建者地址
 * @param type 合约类型
 * @param bytecode 合约字节码
 * @param bytecode_size 字节码大小
 * @return QuantumContract* 创建的合约指针
 */
QuantumContract* contract_create(ContractManager *manager, const char *creator, 
                                ContractType type, const void *bytecode, 
                                size_t bytecode_size);

/**
 * @brief 获取合约信息字符串
 * 
 * @param contract 合约指针
 * @param buffer 输出缓冲区
 * @param buffer_size 缓冲区大小
 * @return int 写入的字符数
 */
int contract_get_info_string(const QuantumContract *contract, char *buffer, size_t buffer_size);

/**
 * @brief 通过地址查找合约
 * 
 * @param manager 合约管理器指针
 * @param address 合约地址
 * @return QuantumContract* 找到的合约指针，没找到返回NULL
 */
QuantumContract* contract_find_by_address(const ContractManager *manager, const char *address);

/**
 * @brief 执行合约
 * 
 * @param manager 合约管理器指针
 * @param contract 合约指针
 * @param method 方法名
 * @param params 参数数组
 * @param param_count 参数个数
 * @param result 执行结果
 * @return int 成功返回0，失败返回非0值
 */
int contract_execute(ContractManager *manager, QuantumContract *contract, 
                    const char *method, ContractParameter *params, 
                    uint32_t param_count, ContractResult *result);

/**
 * @brief 将合约写入区块链
 * 
 * @param manager 合约管理器指针
 * @param chain 区块链指针
 * @param contract 合约指针
 * @return int 成功返回0，失败返回非0值
 */
int contract_deploy_to_blockchain(ContractManager *manager, 
                                 QuantumBlockchain *chain, 
                                 QuantumContract *contract);

/**
 * @brief 监视合约执行事件
 * 
 * @param manager 合约管理器指针
 * @param event_callback 事件回调函数
 * @param user_data 用户数据
 * @return int 成功返回0，失败返回非0值
 */
int contract_monitor_events(ContractManager *manager, 
                           void (*event_callback)(const char *event_type, 
                                                 const void *event_data, 
                                                 void *user_data), 
                           void *user_data);

/**
 * @brief 生成合约执行报告
 * 
 * @param manager 合约管理器指针
 * @param filename 报告文件名
 * @return int 成功返回0，失败返回非0值
 */
int contract_generate_report(const ContractManager *manager, const char *filename);

/**
 * @brief 创建整数类型的合约参数
 * 
 * @param name 参数名称
 * @param value 整数值
 * @return ContractParameter 创建的参数
 */
ContractParameter contract_param_create_int(const char *name, int64_t value);

/**
 * @brief 创建浮点数类型的合约参数
 * 
 * @param name 参数名称
 * @param value 浮点数值
 * @return ContractParameter 创建的参数
 */
ContractParameter contract_param_create_float(const char *name, double value);

/**
 * @brief 创建字符串类型的合约参数
 * 
 * @param name 参数名称
 * @param value 字符串值
 * @return ContractParameter 创建的参数
 */
ContractParameter contract_param_create_string(const char *name, const char *value);

/**
 * @brief 创建量子状态类型的合约参数
 * 
 * @param name 参数名称
 * @param value 量子状态指针
 * @return ContractParameter 创建的参数
 */
ContractParameter contract_param_create_quantum(const char *name, QuantumState *value);

/**
 * @brief 释放参数资源
 * 
 * @param param 参数指针
 */
void contract_param_free(ContractParameter *param);

/**
 * @brief 释放执行结果资源
 * 
 * @param result 结果指针
 */
void contract_result_free(ContractResult *result);

/**
 * @brief 获取合约ID
 * 
 * @param contract 合约指针
 * @return uint64_t 合约ID
 */
uint64_t contract_get_id(const QuantumContract *contract);

/**
 * @brief 获取合约地址
 * 
 * @param contract 合约指针
 * @return const char* 合约地址
 */
const char* contract_get_address(const QuantumContract *contract);

/**
 * @brief 获取合约创建者
 * 
 * @param contract 合约指针
 * @return const char* 创建者地址
 */
const char* contract_get_creator(const QuantumContract *contract);

/**
 * @brief 获取合约类型
 * 
 * @param contract 合约指针
 * @return ContractType 合约类型
 */
ContractType contract_get_type(const QuantumContract *contract);

/**
 * @brief 获取合约状态
 * 
 * @param contract 合约指针
 * @return ContractStatus 合约状态
 */
ContractStatus contract_get_status(const QuantumContract *contract);

/**
 * @brief 获取合约量子状态
 * 
 * @param contract 合约指针
 * @return QuantumState* 量子状态指针
 */
QuantumState* contract_get_quantum_state(const QuantumContract *contract);

/**
 * @brief 获取管理器中的合约数量
 * 
 * @param manager 合约管理器指针
 * @return uint32_t 合约数量
 */
uint32_t contract_manager_get_contract_count(const ContractManager *manager);

/**
 * @brief 获取管理器中的指定索引的合约
 * 
 * @param manager 合约管理器指针
 * @param index 合约索引
 * @return QuantumContract* 合约指针，超出范围返回NULL
 */
QuantumContract* contract_manager_get_contract_at(const ContractManager *manager, uint32_t index);

#ifdef __cplusplus
}
#endif

#endif /* QUANTUM_CONTRACT_MANAGER_H */ 