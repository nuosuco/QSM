/**
 * @file quantum_gene_encoder.c
 * @brief 量子基因编码器实现
 * @author Claude
 * @version 1.0
 * @date 2024-05-31
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "../../include/quantum_gene.h"
#include "../../include/quantum_state.h"
#include "../output/quantum_gene_encoder.h"

/**
 * @brief 量子基因编码器结构体
 */
struct QuantumGeneEncoder {
    int encoding_level;           /* 编码级别 (1-3) */
    int error_correction;         /* 是否启用错误校正 */
    int compression_factor;       /* 压缩因子 */
    int use_entanglement;         /* 是否使用纠缠态 */
    double encoding_quality;      /* 编码质量系数 (0.0-1.0) */
    
    QuantumGene *last_gene;       /* 上一个生成的基因 */
    
    size_t total_encoded_bytes;   /* 统计：已编码的总字节数 */
    int total_genes_created;      /* 统计：已创建的基因总数 */
};

/**
 * @brief 基因编码策略
 */
typedef enum {
    ENCODING_SIMPLE,              /* 简单编码 - 只使用基本量子态 */
    ENCODING_ADVANCED,            /* 高级编码 - 使用纠缠态 */
    ENCODING_QUANTUM_HYBRID       /* 混合编码 - 组合多种量子特性 */
} EncodingStrategy;

/**
 * @brief 创建量子基因编码器
 * 
 * @param encoding_level 编码级别 (1-3)
 * @param error_correction 是否启用错误校正
 * @return QuantumGeneEncoder* 编码器指针
 */
QuantumGeneEncoder* quantum_gene_encoder_create(int encoding_level, int error_correction) {
    // 验证参数
    if (encoding_level < 1 || encoding_level > 3) {
        fprintf(stderr, "错误: 编码级别必须在1-3范围内\n");
        return NULL;
    }
    
    // 分配内存
    QuantumGeneEncoder *encoder = (QuantumGeneEncoder*)malloc(sizeof(QuantumGeneEncoder));
    if (!encoder) {
        fprintf(stderr, "错误: 无法分配量子基因编码器内存\n");
        return NULL;
    }
    
    // 初始化编码器
    encoder->encoding_level = encoding_level;
    encoder->error_correction = error_correction ? 1 : 0;
    encoder->last_gene = NULL;
    encoder->total_encoded_bytes = 0;
    encoder->total_genes_created = 0;
    
    // 根据编码级别设置参数
    switch (encoding_level) {
        case 1: // 基础级别
            encoder->compression_factor = 1;
            encoder->use_entanglement = 0;
            encoder->encoding_quality = 0.9;
            break;
            
        case 2: // 中级
            encoder->compression_factor = 2;
            encoder->use_entanglement = 1;
            encoder->encoding_quality = 0.8;
            break;
            
        case 3: // 高级
            encoder->compression_factor = 4;
            encoder->use_entanglement = 1;
            encoder->encoding_quality = 0.75;
            break;
    }
    
    printf("创建了量子基因编码器：级别=%d, 错误校正=%s\n", 
           encoding_level, error_correction ? "开启" : "关闭");
    
    return encoder;
}

/**
 * @brief 销毁量子基因编码器
 * 
 * @param encoder 编码器指针
 */
void quantum_gene_encoder_destroy(QuantumGeneEncoder *encoder) {
    if (!encoder) return;
    
    // 清理最后一个基因
    if (encoder->last_gene) {
        quantum_gene_destroy(encoder->last_gene);
    }
    
    // 释放编码器内存
    free(encoder);
    
    printf("销毁了量子基因编码器\n");
}

/**
 * @brief 设置编码器参数
 * 
 * @param encoder 编码器指针
 * @param param_name 参数名
 * @param param_value 参数值指针
 * @return int 成功返回0，失败返回非0值
 */
int quantum_gene_encoder_set_param(QuantumGeneEncoder *encoder, 
                                 const char *param_name, 
                                 const void *param_value) {
    if (!encoder || !param_name || !param_value) {
        return -1;
    }
    
    if (strcmp(param_name, "encoding_level") == 0) {
        int level = *((int*)param_value);
        if (level < 1 || level > 3) {
            fprintf(stderr, "错误: 编码级别必须在1-3范围内\n");
            return -1;
        }
        
        encoder->encoding_level = level;
        
        // 更新相关参数
        switch (level) {
            case 1:
                encoder->compression_factor = 1;
                encoder->use_entanglement = 0;
                encoder->encoding_quality = 0.9;
                break;
                
            case 2:
                encoder->compression_factor = 2;
                encoder->use_entanglement = 1;
                encoder->encoding_quality = 0.8;
                break;
                
            case 3:
                encoder->compression_factor = 4;
                encoder->use_entanglement = 1;
                encoder->encoding_quality = 0.75;
                break;
        }
    }
    else if (strcmp(param_name, "error_correction") == 0) {
        encoder->error_correction = *((int*)param_value) ? 1 : 0;
    }
    else if (strcmp(param_name, "compression_factor") == 0) {
        int factor = *((int*)param_value);
        if (factor < 1 || factor > 10) {
            fprintf(stderr, "错误: 压缩因子必须在1-10范围内\n");
            return -1;
        }
        encoder->compression_factor = factor;
    }
    else if (strcmp(param_name, "use_entanglement") == 0) {
        encoder->use_entanglement = *((int*)param_value) ? 1 : 0;
    }
    else if (strcmp(param_name, "encoding_quality") == 0) {
        double quality = *((double*)param_value);
        if (quality < 0.0 || quality > 1.0) {
            fprintf(stderr, "错误: 编码质量必须在0.0-1.0范围内\n");
            return -1;
        }
        encoder->encoding_quality = quality;
    }
    else {
        fprintf(stderr, "错误: 未知参数 '%s'\n", param_name);
        return -1;
    }
    
    return 0;
}

/**
 * @brief 获取编码器参数
 * 
 * @param encoder 编码器指针
 * @param param_name 参数名
 * @param param_value 参数值输出指针
 * @return int 成功返回0，失败返回非0值
 */
int quantum_gene_encoder_get_param(QuantumGeneEncoder *encoder, 
                                 const char *param_name, 
                                 void *param_value) {
    if (!encoder || !param_name || !param_value) {
        return -1;
    }
    
    if (strcmp(param_name, "encoding_level") == 0) {
        *((int*)param_value) = encoder->encoding_level;
    }
    else if (strcmp(param_name, "error_correction") == 0) {
        *((int*)param_value) = encoder->error_correction;
    }
    else if (strcmp(param_name, "compression_factor") == 0) {
        *((int*)param_value) = encoder->compression_factor;
    }
    else if (strcmp(param_name, "use_entanglement") == 0) {
        *((int*)param_value) = encoder->use_entanglement;
    }
    else if (strcmp(param_name, "encoding_quality") == 0) {
        *((double*)param_value) = encoder->encoding_quality;
    }
    else if (strcmp(param_name, "total_encoded_bytes") == 0) {
        *((size_t*)param_value) = encoder->total_encoded_bytes;
    }
    else if (strcmp(param_name, "total_genes_created") == 0) {
        *((int*)param_value) = encoder->total_genes_created;
    }
    else {
        fprintf(stderr, "错误: 未知参数 '%s'\n", param_name);
        return -1;
    }
    
    return 0;
}

/**
 * @brief 计算数据的量子基因模式
 * 
 * @param data 数据指针
 * @param size 数据大小
 * @param pattern 模式输出缓冲区
 * @param pattern_size 模式缓冲区大小
 * @return int 成功返回写入的模式长度，失败返回-1
 */
static int calculate_quantum_pattern(const void *data, size_t size, 
                                  uint8_t *pattern, size_t pattern_size) {
    if (!data || !pattern || size == 0 || pattern_size < 16) {
        return -1;
    }
    
    // 简化算法：计算数据的统计特征
    double entropy = 0.0;
    int frequencies[256] = {0};
    
    // 计算字节频率
    const uint8_t *bytes = (const uint8_t*)data;
    for (size_t i = 0; i < size; i++) {
        frequencies[bytes[i]]++;
    }
    
    // 计算熵
    for (int i = 0; i < 256; i++) {
        if (frequencies[i] > 0) {
            double prob = (double)frequencies[i] / size;
            entropy -= prob * log2(prob);
        }
    }
    
    // 生成16字节模式
    // 前8字节基于数据特征
    uint8_t feature_bytes[8];
    
    // 计算最常见的8个字节
    for (int i = 0; i < 8; i++) {
        int max_freq = 0;
        int max_byte = 0;
        
        for (int j = 0; j < 256; j++) {
            if (frequencies[j] > max_freq) {
                max_freq = frequencies[j];
                max_byte = j;
            }
        }
        
        feature_bytes[i] = (uint8_t)max_byte;
        frequencies[max_byte] = 0; // 避免重复选择
    }
    
    // 计算数据序列模式
    uint8_t sequence_pattern = 0;
    for (size_t i = 1; i < size && i < 8; i++) {
        if (bytes[i] > bytes[i-1]) {
            sequence_pattern |= (1 << (i-1));
        }
    }
    
    // 填充模式
    int pos = 0;
    
    // 熵（量化到0-255）
    pattern[pos++] = (uint8_t)(entropy * 25.5); // 最大熵 ~10
    
    // 序列模式
    pattern[pos++] = sequence_pattern;
    
    // 特征字节
    for (int i = 0; i < 8; i++) {
        pattern[pos++] = feature_bytes[i];
    }
    
    // 数据大小特征
    pattern[pos++] = (uint8_t)(size & 0xFF);
    pattern[pos++] = (uint8_t)((size >> 8) & 0xFF);
    pattern[pos++] = (uint8_t)((size >> 16) & 0xFF);
    pattern[pos++] = (uint8_t)((size >> 24) & 0xFF);
    
    // 数据校验和
    uint32_t checksum = 0;
    for (size_t i = 0; i < size; i++) {
        checksum = ((checksum << 5) + checksum) + bytes[i];
    }
    pattern[pos++] = (uint8_t)(checksum & 0xFF);
    pattern[pos++] = (uint8_t)((checksum >> 8) & 0xFF);
    
    return pos;
}

/**
 * @brief 将数据编码为量子基因
 * 
 * @param encoder 编码器指针
 * @param data 数据指针
 * @param size 数据大小
 * @return QuantumGene* 量子基因指针
 */
QuantumGene* quantum_gene_encoder_encode(QuantumGeneEncoder *encoder, 
                                      const void *data, 
                                      size_t size) {
    if (!encoder || !data || size == 0) {
        return NULL;
    }
    
    // 清理上一个基因
    if (encoder->last_gene) {
        quantum_gene_destroy(encoder->last_gene);
        encoder->last_gene = NULL;
    }
    
    // 选择编码策略
    EncodingStrategy strategy;
    if (encoder->encoding_level <= 1) {
        strategy = ENCODING_SIMPLE;
    }
    else if (encoder->encoding_level == 2) {
        strategy = ENCODING_ADVANCED;
    }
    else {
        strategy = ENCODING_QUANTUM_HYBRID;
    }
    
    // 计算基因组大小
    // 基本大小 = 原始大小 / 压缩因子
    size_t gene_size = size / encoder->compression_factor;
    
    // 因错误校正而增加的大小
    if (encoder->error_correction) {
        gene_size += gene_size / 4; // 额外25%用于错误校正
    }
    
    // 最小基因大小
    if (gene_size < 32) {
        gene_size = 32;
    }
    
    // 创建量子基因
    QuantumGene *gene = quantum_gene_create(gene_size);
    if (!gene) {
        fprintf(stderr, "错误: 无法创建量子基因\n");
        return NULL;
    }
    
    // 生成量子基因模式
    uint8_t pattern[16];
    int pattern_length = calculate_quantum_pattern(data, size, pattern, sizeof(pattern));
    
    if (pattern_length < 0) {
        fprintf(stderr, "错误: 无法计算量子模式\n");
        quantum_gene_destroy(gene);
        return NULL;
    }
    
    // 设置基因属性
    quantum_gene_set_property(gene, "data_size", &size, sizeof(size_t));
    quantum_gene_set_property(gene, "encoding_level", &encoder->encoding_level, sizeof(int));
    quantum_gene_set_property(gene, "error_correction", &encoder->error_correction, sizeof(int));
    quantum_gene_set_property(gene, "pattern", pattern, pattern_length);
    
    // 根据策略编码数据
    switch (strategy) {
        case ENCODING_SIMPLE:
            {
                // 简单编码：直接映射数据到量子基因
                const uint8_t *input = (const uint8_t*)data;
                size_t input_pos = 0;
                size_t gene_pos = 0;
                
                // 存储数据模式
                for (int i = 0; i < pattern_length && gene_pos < gene_size; i++) {
                    quantum_gene_set_byte(gene, gene_pos++, pattern[i]);
                }
                
                // 编码头部标记
                uint8_t header[4] = {0xF0, 0xE1, 0xD2, 0xC3};
                for (int i = 0; i < 4 && gene_pos < gene_size; i++) {
                    quantum_gene_set_byte(gene, gene_pos++, header[i]);
                }
                
                // 编码主体数据
                while (input_pos < size && gene_pos < gene_size) {
                    uint8_t current_byte = input[input_pos++];
                    
                    // 简单压缩：合并相邻字节
                    if (input_pos < size && encoder->compression_factor > 1) {
                        uint8_t next_byte = input[input_pos++];
                        current_byte = (current_byte & 0xF0) | ((next_byte >> 4) & 0x0F);
                    }
                    
                    quantum_gene_set_byte(gene, gene_pos++, current_byte);
                }
                
                // 设置尾部标记
                if (gene_pos < gene_size) {
                    quantum_gene_set_byte(gene, gene_pos++, 0xFF);
                }
            }
            break;
            
        case ENCODING_ADVANCED:
            {
                // 高级编码：使用纠缠态编码
                const uint8_t *input = (const uint8_t*)data;
                size_t input_pos = 0;
                
                // 初始化量子态和纠缠态
                QuantumState *q_states[8];
                for (int i = 0; i < 8; i++) {
                    q_states[i] = quantum_state_create(3); // 3量子比特状态
                    if (!q_states[i]) {
                        fprintf(stderr, "错误: 无法创建量子态\n");
                        for (int j = 0; j < i; j++) {
                            quantum_state_destroy(q_states[j]);
                        }
                        quantum_gene_destroy(gene);
                        return NULL;
                    }
                }
                
                // 嵌入模式和标识
                for (int i = 0; i < 8 && i < pattern_length; i++) {
                    uint8_t p = pattern[i];
                    
                    // 设置量子态
                    for (int bit = 0; bit < 3; bit++) {
                        double alpha = ((p >> bit) & 1) ? 0.0 : 1.0;
                        double beta = ((p >> bit) & 1) ? 1.0 : 0.0;
                        quantum_state_set_amplitude(q_states[i], bit, alpha, beta);
                    }
                    
                    // 应用纠缠
                    if (i > 0) {
                        quantum_state_entangle(q_states[i-1], q_states[i]);
                    }
                }
                
                // 编码数据
                int state_index = 0;
                while (input_pos < size) {
                    // 提取4个字节或数据结束
                    uint8_t block[4] = {0};
                    int block_size = 0;
                    
                    for (int i = 0; i < 4 && input_pos < size; i++) {
                        block[i] = input[input_pos++];
                        block_size++;
                    }
                    
                    // 创建量子态表示这4个字节
                    QuantumState *data_state = quantum_state_create(block_size * 2);
                    if (!data_state) {
                        fprintf(stderr, "错误: 无法创建数据量子态\n");
                        for (int i = 0; i < 8; i++) {
                            quantum_state_destroy(q_states[i]);
                        }
                        quantum_gene_destroy(gene);
                        return NULL;
                    }
                    
                    // 设置数据量子态
                    for (int i = 0; i < block_size; i++) {
                        for (int bit = 0; bit < 2; bit++) {
                            int qbit = i * 2 + bit;
                            // 提取2位一组
                            int bit_value = (block[i] >> (bit * 4)) & 0x0F;
                            
                            // 设置振幅
                            double alpha = cos(bit_value * M_PI / 15.0);
                            double beta = sin(bit_value * M_PI / 15.0);
                            quantum_state_set_amplitude(data_state, qbit, alpha, beta);
                        }
                    }
                    
                    // 将数据量子态与模式状态纠缠
                    quantum_state_entangle(q_states[state_index % 8], data_state);
                    
                    // 将量子态保存到基因中
                    quantum_gene_store_state(gene, data_state);
                    
                    // 清理
                    quantum_state_destroy(data_state);
                    state_index++;
                }
                
                // 清理量子态
                for (int i = 0; i < 8; i++) {
                    quantum_state_destroy(q_states[i]);
                }
            }
            break;
            
        case ENCODING_QUANTUM_HYBRID:
            {
                // 混合编码：结合纠缠与叠加编码
                const uint8_t *input = (const uint8_t*)data;
                size_t chunks = (size + 15) / 16; // 每16字节一个区块
                
                // 创建主量子寄存器
                QuantumState *main_register = quantum_state_create(8);
                if (!main_register) {
                    fprintf(stderr, "错误: 无法创建主量子寄存器\n");
                    quantum_gene_destroy(gene);
                    return NULL;
                }
                
                // 设置寄存器为模式状态
                for (int i = 0; i < 8; i++) {
                    uint8_t pattern_byte = (i < pattern_length) ? pattern[i] : 0;
                    double alpha = cos(pattern_byte * M_PI / 255.0);
                    double beta = sin(pattern_byte * M_PI / 255.0);
                    quantum_state_set_amplitude(main_register, i, alpha, beta);
                }
                
                // 存储主寄存器状态
                quantum_gene_store_state(gene, main_register);
                
                // 处理数据块
                for (size_t chunk = 0; chunk < chunks; chunk++) {
                    size_t offset = chunk * 16;
                    size_t remaining = size - offset;
                    size_t chunk_size = (remaining > 16) ? 16 : remaining;
                    
                    // 创建块量子寄存器
                    int qubits_needed = 5 + (chunk_size / 2); // 额外空间用于压缩
                    QuantumState *chunk_register = quantum_state_create(qubits_needed);
                    if (!chunk_register) {
                        fprintf(stderr, "错误: 无法创建块量子寄存器\n");
                        quantum_state_destroy(main_register);
                        quantum_gene_destroy(gene);
                        return NULL;
                    }
                    
                    // 编码块元数据（偏移量和大小）
                    uint8_t meta[2];
                    meta[0] = (uint8_t)(offset & 0xFF);
                    meta[1] = (uint8_t)(chunk_size & 0xFF);
                    
                    // 设置元数据量子态
                    for (int i = 0; i < 2; i++) {
                        double alpha = cos(meta[i] * M_PI / 255.0);
                        double beta = sin(meta[i] * M_PI / 255.0);
                        quantum_state_set_amplitude(chunk_register, i, alpha, beta);
                    }
                    
                    // 编码块数据
                    for (size_t i = 0; i < chunk_size; i += 2) {
                        uint8_t b1 = input[offset + i];
                        uint8_t b2 = (i + 1 < chunk_size) ? input[offset + i + 1] : 0;
                        
                        // 压缩两个字节为一个量子比特
                        int q_idx = 2 + (i / 2);
                        if (q_idx < qubits_needed) {
                            // 计算压缩值 (0-15)
                            uint8_t compressed = (b1 >> 4) ^ (b1 & 0x0F) ^ (b2 >> 4) ^ (b2 & 0x0F);
                            
                            // 设置振幅
                            double alpha = cos(compressed * M_PI / 15.0);
                            double beta = sin(compressed * M_PI / 15.0);
                            quantum_state_set_amplitude(chunk_register, q_idx, alpha, beta);
                        }
                    }
                    
                    // 块寄存器与主寄存器纠缠
                    quantum_state_entangle(main_register, chunk_register);
                    
                    // 存储块寄存器状态
                    quantum_gene_store_state(gene, chunk_register);
                    
                    // 清理块寄存器
                    quantum_state_destroy(chunk_register);
                }
                
                // 清理主寄存器
                quantum_state_destroy(main_register);
            }
            break;
    }
    
    // 更新统计信息
    encoder->total_encoded_bytes += size;
    encoder->total_genes_created++;
    encoder->last_gene = gene;
    
    printf("编码了 %zu 字节的数据，生成了 %zu 字节的量子基因，策略: %d\n",
           size, gene_size, (int)strategy);
    
    return gene;
}

/**
 * @brief 解码量子基因为原始数据
 * 
 * @param encoder 编码器指针
 * @param gene 量子基因指针
 * @param output 输出数据缓冲区指针
 * @param output_size 输出缓冲区大小
 * @return size_t 成功返回解码的数据大小，失败返回0
 */
size_t quantum_gene_encoder_decode(QuantumGeneEncoder *encoder,
                                QuantumGene *gene,
                                void *output,
                                size_t output_size) {
    if (!encoder || !gene || !output || output_size == 0) {
        return 0;
    }
    
    // 获取原始数据大小
    size_t original_size = 0;
    if (quantum_gene_get_property(gene, "data_size", &original_size, sizeof(size_t)) <= 0) {
        fprintf(stderr, "错误: 无法获取原始数据大小\n");
        return 0;
    }
    
    // 检查输出缓冲区是否足够
    if (output_size < original_size) {
        fprintf(stderr, "错误: 输出缓冲区太小 (%zu < %zu)\n", output_size, original_size);
        return 0;
    }
    
    // 获取编码级别
    int encoding_level = 0;
    if (quantum_gene_get_property(gene, "encoding_level", &encoding_level, sizeof(int)) <= 0) {
        fprintf(stderr, "警告: 无法获取编码级别，假设为1\n");
        encoding_level = 1;
    }
    
    // 选择解码策略
    EncodingStrategy strategy;
    if (encoding_level <= 1) {
        strategy = ENCODING_SIMPLE;
    }
    else if (encoding_level == 2) {
        strategy = ENCODING_ADVANCED;
    }
    else {
        strategy = ENCODING_QUANTUM_HYBRID;
    }
    
    // 输出缓冲区
    uint8_t *out_buffer = (uint8_t*)output;
    size_t decoded_size = 0;
    
    // 解码数据
    switch (strategy) {
        case ENCODING_SIMPLE:
            {
                // 简单解码：直接从基因中提取数据
                size_t gene_size = quantum_gene_get_size(gene);
                size_t gene_pos = 0;
                
                // 跳过模式和头部
                uint8_t pattern[16];
                int pattern_length = quantum_gene_get_property(gene, "pattern", pattern, sizeof(pattern));
                
                if (pattern_length > 0) {
                    gene_pos += pattern_length;
                }
                
                // 跳过标记
                gene_pos += 4;
                
                // 解码数据
                while (gene_pos < gene_size && decoded_size < original_size) {
                    uint8_t current_byte = quantum_gene_get_byte(gene, gene_pos++);
                    
                    // 检查尾部标记
                    if (current_byte == 0xFF) {
                        break;
                    }
                    
                    // 解压缩
                    if (encoder->compression_factor > 1) {
                        // 还原两个字节
                        out_buffer[decoded_size++] = (current_byte & 0xF0);
                        
                        if (decoded_size < original_size) {
                            out_buffer[decoded_size++] = ((current_byte & 0x0F) << 4);
                        }
                    }
                    else {
                        out_buffer[decoded_size++] = current_byte;
                    }
                }
            }
            break;
            
        case ENCODING_ADVANCED:
            {
                // 高级解码：使用纠缠态解码
                // 此示例仅提供简化实现
                size_t states_count = quantum_gene_get_states_count(gene);
                
                // 跳过前8个模式状态
                for (size_t i = 8; i < states_count && decoded_size < original_size; i++) {
                    QuantumState *state = quantum_gene_get_state(gene, i);
                    if (!state) continue;
                    
                    size_t qubits = quantum_state_get_qubits_count(state);
                    size_t data_bytes = qubits / 2;
                    
                    // 从量子态提取数据
                    for (size_t q = 0; q < data_bytes && decoded_size < original_size; q++) {
                        double alpha, beta;
                        uint8_t byte_value = 0;
                        
                        // 提取高4位
                        quantum_state_get_amplitude(state, q * 2, &alpha, &beta);
                        int hi_nibble = (int)(atan2(beta, alpha) * 15.0 / M_PI) & 0x0F;
                        
                        // 提取低4位
                        quantum_state_get_amplitude(state, q * 2 + 1, &alpha, &beta);
                        int lo_nibble = (int)(atan2(beta, alpha) * 15.0 / M_PI) & 0x0F;
                        
                        // 组合为字节
                        byte_value = (hi_nibble << 4) | lo_nibble;
                        out_buffer[decoded_size++] = byte_value;
                    }
                    
                    quantum_state_destroy(state);
                }
            }
            break;
            
        case ENCODING_QUANTUM_HYBRID:
            {
                // 混合解码
                // 这里提供简化实现
                size_t states_count = quantum_gene_get_states_count(gene);
                
                // 跳过主寄存器状态
                for (size_t i = 1; i < states_count; i++) {
                    QuantumState *state = quantum_gene_get_state(gene, i);
                    if (!state) continue;
                    
                    // 提取块元数据
                    double alpha, beta;
                    quantum_state_get_amplitude(state, 0, &alpha, &beta);
                    uint8_t offset_byte = (uint8_t)(atan2(beta, alpha) * 255.0 / M_PI);
                    
                    quantum_state_get_amplitude(state, 1, &alpha, &beta);
                    uint8_t size_byte = (uint8_t)(atan2(beta, alpha) * 255.0 / M_PI);
                    
                    size_t offset = offset_byte;
                    size_t chunk_size = size_byte;
                    
                    // 提取块数据
                    size_t qubits = quantum_state_get_qubits_count(state);
                    
                    for (size_t q = 2; q < qubits && q - 2 < chunk_size / 2; q++) {
                        quantum_state_get_amplitude(state, q, &alpha, &beta);
                        uint8_t compressed = (uint8_t)(atan2(beta, alpha) * 15.0 / M_PI) & 0x0F;
                        
                        // 尝试恢复原始字节（这是近似恢复，非精确）
                        if (offset + (q - 2) * 2 < original_size) {
                            out_buffer[offset + (q - 2) * 2] = (compressed << 4) | compressed;
                        }
                        
                        if (offset + (q - 2) * 2 + 1 < original_size) {
                            out_buffer[offset + (q - 2) * 2 + 1] = (compressed << 4) | compressed;
                        }
                        
                        decoded_size = offset + (q - 2) * 2 + 2;
                    }
                    
                    quantum_state_destroy(state);
                }
                
                // 调整解码大小
                if (decoded_size > original_size) {
                    decoded_size = original_size;
                }
            }
            break;
    }
    
    printf("解码了 %zu 字节的数据\n", decoded_size);
    
    return decoded_size;
}

/**
 * @brief 为编码器注册错误校正功能
 * 
 * @param encoder 编码器指针
 * @param error_correction_func 错误校正函数
 * @return int 成功返回0，失败返回非0值
 */
int quantum_gene_encoder_register_error_correction(
    QuantumGeneEncoder *encoder,
    int (*error_correction_func)(QuantumGene*, void*),
    void *user_data) {
    
    // 注意：此功能尚未实现，仅占位
    fprintf(stderr, "警告: 错误校正功能尚未实现\n");
    return -1;
} 