/**
 * 量子基因编码器头文件
 * 
 * 该文件定义了量子基因编码器的数据结构和函数接口，用于实现各种类型数据的量子基因编码。
 * 基因编码是QEntL环境中的核心功能之一，将多种信息编码为量子基因结构。
 *
 * @file gene_encoder.h
 * @version 1.0
 * @date 2024-05-15
 */

#ifndef QENTL_GENE_ENCODER_H
#define QENTL_GENE_ENCODER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "../../quantum_gene.h"
#include "../quantum_state/state_manager.h"

/**
 * 基因编码错误码
 */
typedef enum {
    GENE_ENCODER_ERROR_NONE = 0,                   // 无错误
    GENE_ENCODER_ERROR_INVALID_ARGUMENT = 1,       // 无效参数
    GENE_ENCODER_ERROR_MEMORY_ALLOCATION = 2,      // 内存分配错误
    GENE_ENCODER_ERROR_UNSUPPORTED_FORMAT = 3,     // 不支持的格式
    GENE_ENCODER_ERROR_ENCODING_FAILED = 4,        // 编码失败
    GENE_ENCODER_ERROR_DECODING_FAILED = 5,        // 解码失败
    GENE_ENCODER_ERROR_DATA_TOO_LARGE = 6,         // 数据过大
    GENE_ENCODER_ERROR_GENE_CORRUPTED = 7,         // 基因损坏
    GENE_ENCODER_ERROR_OPERATION_FAILED = 8,       // 操作失败
    GENE_ENCODER_ERROR_NOT_IMPLEMENTED = 9,        // 功能未实现
    GENE_ENCODER_ERROR_INTERNAL = 10               // 内部错误
} GeneEncoderError;

/**
 * 编码数据类型
 */
typedef enum {
    GENE_DATA_TYPE_TEXT = 0,             // 文本数据
    GENE_DATA_TYPE_BINARY = 1,           // 二进制数据
    GENE_DATA_TYPE_IMAGE = 2,            // 图像数据
    GENE_DATA_TYPE_AUDIO = 3,            // 音频数据
    GENE_DATA_TYPE_NUMERIC = 4,          // 数值数据
    GENE_DATA_TYPE_MIXED = 5,            // 混合数据
    GENE_DATA_TYPE_JSON = 6,             // JSON数据
    GENE_DATA_TYPE_XML = 7,              // XML数据
    GENE_DATA_TYPE_CUSTOM = 8            // 自定义数据
} GeneDataType;

/**
 * 编码选项标志
 */
typedef enum {
    GENE_ENCODE_FLAG_NONE = 0,                   // 无特殊选项
    GENE_ENCODE_FLAG_COMPRESSION = (1 << 0),     // 启用压缩
    GENE_ENCODE_FLAG_ENCRYPTION = (1 << 1),      // 启用加密
    GENE_ENCODE_FLAG_ERROR_CORRECTION = (1 << 2),// 启用错误修正
    GENE_ENCODE_FLAG_METADATA = (1 << 3),        // 包含元数据
    GENE_ENCODE_FLAG_VERSIONING = (1 << 4),      // 包含版本信息
    GENE_ENCODE_FLAG_CHECKSUM = (1 << 5),        // 包含校验和
    GENE_ENCODE_FLAG_REDUNDANCY = (1 << 6),      // 包含冗余信息
    GENE_ENCODE_FLAG_HIGH_FIDELITY = (1 << 7)    // 高保真度模式
} GeneEncodeFlag;

/**
 * 基因编码级别
 */
typedef enum {
    GENE_ENCODING_LEVEL_BASIC = 0,       // 基础编码 (低复杂度)
    GENE_ENCODING_LEVEL_STANDARD = 1,    // 标准编码 (平衡)
    GENE_ENCODING_LEVEL_ADVANCED = 2,    // 高级编码 (高保真)
    GENE_ENCODING_LEVEL_QUANTUM = 3      // 量子级编码 (最高复杂度)
} GeneEncodingLevel;

/**
 * 编码选项结构体
 */
typedef struct {
    GeneDataType data_type;              // 数据类型
    GeneEncodingLevel encoding_level;    // 编码级别
    unsigned int flags;                  // 选项标志
    int gene_dimensions;                 // 基因维度
    double min_fidelity;                 // 最小保真度
    char* encryption_key;                // 加密密钥
    void* custom_params;                 // 自定义参数
} GeneEncodingOptions;

/**
 * 编码结果结构体
 */
typedef struct {
    QuantumGene* gene;                   // 量子基因
    double encoding_fidelity;            // 编码保真度
    unsigned int data_size;              // 原始数据大小
    unsigned int gene_size;              // 基因数据大小
    double compression_ratio;            // 压缩比率
    GeneEncoderError error;              // 错误码
    char* error_message;                 // 错误消息
} GeneEncodingResult;

/**
 * 基因相似度比较结果
 */
typedef struct {
    double similarity_score;             // 相似度得分 (0-1)
    double confidence;                   // 置信度 (0-1)
    int matching_segments;               // 匹配片段数
    int total_segments;                  // 总片段数
    double* segment_scores;              // 每段的得分
    char* details;                       // 详细比较信息
} GeneSimilarityResult;

/**
 * 基因编码器配置
 */
typedef struct {
    int max_gene_dimensions;             // 最大基因维度
    int default_encoding_level;          // 默认编码级别
    unsigned int default_flags;          // 默认选项标志
    double default_min_fidelity;         // 默认最小保真度
    int enable_caching;                  // 是否启用缓存
    int enable_logging;                  // 是否启用日志
    char* log_file_path;                 // 日志文件路径
    void* custom_config;                 // 自定义配置
} GeneEncoderConfig;

/**
 * 基因编码器结构体
 */
typedef struct {
    GeneEncoderConfig config;            // 配置
    StateManager* state_manager;         // 状态管理器
    void* cache;                         // 缓存
    FILE* log_file;                      // 日志文件
    GeneEncoderError last_error;         // 最后的错误码
    char* encoder_id;                    // 编码器ID
    time_t creation_time;                // 创建时间
} GeneEncoder;

/* 函数声明 */

/**
 * 初始化基因编码器
 * 
 * @param config 编码器配置
 * @param state_manager 状态管理器
 * @return 基因编码器指针，失败时返回NULL
 */
GeneEncoder* initialize_gene_encoder(GeneEncoderConfig config, StateManager* state_manager);

/**
 * 获取默认基因编码器配置
 * 
 * @return 默认配置
 */
GeneEncoderConfig get_default_gene_encoder_config();

/**
 * 关闭基因编码器
 * 
 * @param encoder 基因编码器
 */
void shutdown_gene_encoder(GeneEncoder* encoder);

/**
 * 编码文本数据为量子基因
 * 
 * @param encoder 基因编码器
 * @param text 文本数据
 * @param text_length 文本长度
 * @param options 编码选项
 * @return 编码结果
 */
GeneEncodingResult encode_text(GeneEncoder* encoder, const char* text, size_t text_length, GeneEncodingOptions options);

/**
 * 解码量子基因为文本数据
 * 
 * @param encoder 基因编码器
 * @param gene 量子基因
 * @param buffer 输出缓冲区
 * @param buffer_size 缓冲区大小
 * @return 实际解码的字节数，失败时返回负值
 */
int decode_text(GeneEncoder* encoder, QuantumGene* gene, char* buffer, size_t buffer_size);

/**
 * 编码二进制数据为量子基因
 * 
 * @param encoder 基因编码器
 * @param data 二进制数据
 * @param data_length 数据长度
 * @param options 编码选项
 * @return 编码结果
 */
GeneEncodingResult encode_binary(GeneEncoder* encoder, const void* data, size_t data_length, GeneEncodingOptions options);

/**
 * 解码量子基因为二进制数据
 * 
 * @param encoder 基因编码器
 * @param gene 量子基因
 * @param buffer 输出缓冲区
 * @param buffer_size 缓冲区大小
 * @return 实际解码的字节数，失败时返回负值
 */
int decode_binary(GeneEncoder* encoder, QuantumGene* gene, void* buffer, size_t buffer_size);

/**
 * 编码图像数据为量子基因
 * 
 * @param encoder 基因编码器
 * @param image_data 图像数据
 * @param width 图像宽度
 * @param height 图像高度
 * @param channels 图像通道数
 * @param options 编码选项
 * @return 编码结果
 */
GeneEncodingResult encode_image(GeneEncoder* encoder, const void* image_data, int width, int height, int channels, GeneEncodingOptions options);

/**
 * 解码量子基因为图像数据
 * 
 * @param encoder 基因编码器
 * @param gene 量子基因
 * @param buffer 输出缓冲区
 * @param buffer_size 缓冲区大小
 * @param width 输出参数，图像宽度
 * @param height 输出参数，图像高度
 * @param channels 输出参数，图像通道数
 * @return 实际解码的字节数，失败时返回负值
 */
int decode_image(GeneEncoder* encoder, QuantumGene* gene, void* buffer, size_t buffer_size, int* width, int* height, int* channels);

/**
 * 编码音频数据为量子基因
 * 
 * @param encoder 基因编码器
 * @param audio_data 音频数据
 * @param data_length 数据长度
 * @param sample_rate 采样率
 * @param channels 通道数
 * @param bits_per_sample 每个样本的位数
 * @param options 编码选项
 * @return 编码结果
 */
GeneEncodingResult encode_audio(GeneEncoder* encoder, const void* audio_data, size_t data_length, int sample_rate, int channels, int bits_per_sample, GeneEncodingOptions options);

/**
 * 解码量子基因为音频数据
 * 
 * @param encoder 基因编码器
 * @param gene 量子基因
 * @param buffer 输出缓冲区
 * @param buffer_size 缓冲区大小
 * @param sample_rate 输出参数，采样率
 * @param channels 输出参数，通道数
 * @param bits_per_sample 输出参数，每个样本的位数
 * @return 实际解码的字节数，失败时返回负值
 */
int decode_audio(GeneEncoder* encoder, QuantumGene* gene, void* buffer, size_t buffer_size, int* sample_rate, int* channels, int* bits_per_sample);

/**
 * 比较两个量子基因的相似度
 * 
 * @param encoder 基因编码器
 * @param gene1 第一个量子基因
 * @param gene2 第二个量子基因
 * @param comparison_mode 比较模式
 * @return 相似度比较结果
 */
GeneSimilarityResult compare_genes(GeneEncoder* encoder, QuantumGene* gene1, QuantumGene* gene2, int comparison_mode);

/**
 * 混合两个量子基因
 * 
 * @param encoder 基因编码器
 * @param gene1 第一个量子基因
 * @param gene2 第二个量子基因
 * @param weight1 第一个基因权重 (0-1)
 * @param options 编码选项
 * @return 混合后的量子基因，失败时返回NULL
 */
QuantumGene* mix_genes(GeneEncoder* encoder, QuantumGene* gene1, QuantumGene* gene2, double weight1, GeneEncodingOptions options);

/**
 * 拆分量子基因
 * 
 * @param encoder 基因编码器
 * @param gene 量子基因
 * @param split_points 分割点数组
 * @param split_count 分割点数量
 * @param results 输出的基因数组
 * @return 实际拆分的基因数量，失败时返回负值
 */
int split_gene(GeneEncoder* encoder, QuantumGene* gene, const double* split_points, int split_count, QuantumGene** results);

/**
 * 提取基因特征
 * 
 * @param encoder 基因编码器
 * @param gene 量子基因
 * @param feature_types 特征类型数组
 * @param feature_count 特征类型数量
 * @param results 输出的特征数组
 * @return 实际提取的特征数量，失败时返回负值
 */
int extract_gene_features(GeneEncoder* encoder, QuantumGene* gene, const int* feature_types, int feature_count, void** results);

/**
 * 验证量子基因的完整性
 * 
 * @param encoder 基因编码器
 * @param gene 量子基因
 * @return 1表示完整，0表示损坏，负值表示错误
 */
int validate_gene(GeneEncoder* encoder, QuantumGene* gene);

/**
 * 修复损坏的量子基因
 * 
 * @param encoder 基因编码器
 * @param gene 损坏的量子基因
 * @return 修复后的量子基因，失败时返回NULL
 */
QuantumGene* repair_gene(GeneEncoder* encoder, QuantumGene* gene);

/**
 * 获取基因编码器错误码
 * 
 * @param encoder 基因编码器
 * @return 错误码
 */
GeneEncoderError get_encoder_error(GeneEncoder* encoder);

/**
 * 获取错误消息
 * 
 * @param error 错误码
 * @return 错误消息
 */
const char* get_encoder_error_message(GeneEncoderError error);

/**
 * 释放编码结果资源
 * 
 * @param result 编码结果
 */
void free_encoding_result(GeneEncodingResult* result);

/**
 * 释放相似度比较结果资源
 * 
 * @param result 相似度比较结果
 */
void free_similarity_result(GeneSimilarityResult* result);

#endif /* QENTL_GENE_ENCODER_H */ 