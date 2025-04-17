/**
 * @file entanglement_channel_embedder.c
 * @brief 纠缠信道嵌入器实现
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
#include "../../include/quantum_entanglement.h"

/**
 * @brief 纠缠信道类型枚举
 */
typedef enum {
    CHANNEL_TYPE_BELL,         /* 贝尔信道 */
    CHANNEL_TYPE_GHZ,          /* GHZ信道 */
    CHANNEL_TYPE_CLUSTER,      /* 簇信道 */
    CHANNEL_TYPE_ADAPTIVE      /* 自适应信道 */
} EntanglementChannelType;

/**
 * @brief 纠缠信道结构体定义
 */
typedef struct {
    EntanglementChannelType type;   /* 信道类型 */
    int qubit_count;                /* 量子比特数量 */
    int active;                     /* 是否活跃 */
    double fidelity;                /* 信道保真度 */
    double noise_level;             /* 噪声级别 */
    QuantumEntanglement *entanglement; /* 底层纠缠对象 */
    void *metadata;                 /* 元数据 */
} EntanglementChannel;

/**
 * @brief 纠缠嵌入配置结构体
 */
typedef struct {
    int error_correction;           /* 是否使用错误校正 */
    int compression_level;          /* 压缩级别 */
    double encoding_density;        /* 编码密度 */
    int use_superposition;          /* 是否使用叠加态 */
} EmbeddingConfig;

/**
 * @brief 纠缠信道嵌入器结构体定义
 */
typedef struct {
    EntanglementChannel **channels;   /* 信道数组 */
    int channel_count;                /* 信道数量 */
    EmbeddingConfig config;           /* 嵌入配置 */
    int total_capacity;               /* 总容量(比特) */
    int used_capacity;                /* 已用容量(比特) */
    void *embedder_context;           /* 嵌入器上下文 */
} EntanglementChannelEmbedder;

/**
 * @brief 创建纠缠信道
 * 
 * @param type 信道类型
 * @param qubit_count 量子比特数量
 * @return EntanglementChannel* 信道指针
 */
static EntanglementChannel* create_entanglement_channel(EntanglementChannelType type, int qubit_count) {
    if (qubit_count < 2) {
        fprintf(stderr, "错误: 信道至少需要2个量子比特\n");
        return NULL;
    }
    
    EntanglementChannel *channel = (EntanglementChannel*)malloc(sizeof(EntanglementChannel));
    if (!channel) {
        fprintf(stderr, "错误: 无法分配信道内存\n");
        return NULL;
    }
    
    channel->type = type;
    channel->qubit_count = qubit_count;
    channel->active = 1;
    channel->fidelity = 0.95;
    channel->noise_level = 0.01;
    channel->metadata = NULL;
    
    // 创建底层纠缠对象
    channel->entanglement = quantum_entanglement_create(qubit_count);
    if (!channel->entanglement) {
        fprintf(stderr, "错误: 无法创建纠缠态\n");
        free(channel);
        return NULL;
    }
    
    // 根据类型初始化信道
    switch (type) {
        case CHANNEL_TYPE_BELL:
            // 创建贝尔态信道
            if (qubit_count == 2) {
                quantum_entanglement_create_bell_state(channel->entanglement, 0, 1);
            } else {
                // 如果比特数 > 2，创建多个贝尔对
                for (int i = 0; i < qubit_count - 1; i += 2) {
                    quantum_entanglement_create_bell_state(channel->entanglement, i, i + 1);
                }
            }
            break;
            
        case CHANNEL_TYPE_GHZ:
            // 创建GHZ态信道
            {
                int qubits[qubit_count];
                for (int i = 0; i < qubit_count; i++) {
                    qubits[i] = i;
                }
                quantum_entanglement_create_ghz_state(channel->entanglement, qubits, qubit_count);
            }
            break;
            
        case CHANNEL_TYPE_CLUSTER:
            // 创建簇态信道
            {
                int qubits[qubit_count];
                for (int i = 0; i < qubit_count; i++) {
                    qubits[i] = i;
                }
                quantum_entanglement_create_cluster_state(channel->entanglement, qubits, qubit_count);
            }
            break;
            
        case CHANNEL_TYPE_ADAPTIVE:
            // 创建自适应信道
            // 简化实现：首先创建一个GHZ态，然后对部分比特进行局部操作
            {
                int qubits[qubit_count];
                for (int i = 0; i < qubit_count; i++) {
                    qubits[i] = i;
                }
                quantum_entanglement_create_ghz_state(channel->entanglement, qubits, qubit_count);
                
                // 对部分比特应用Hadamard门
                for (int i = 0; i < qubit_count; i += 2) {
                    quantum_entanglement_apply_gate(channel->entanglement, i, "H");
                }
            }
            break;
    }
    
    printf("创建了类型为 %d 的纠缠信道，包含 %d 个量子比特\n", type, qubit_count);
    
    return channel;
}

/**
 * @brief 销毁纠缠信道
 * 
 * @param channel 信道指针
 */
static void destroy_entanglement_channel(EntanglementChannel *channel) {
    if (!channel) return;
    
    if (channel->entanglement) {
        quantum_entanglement_destroy(channel->entanglement);
    }
    
    if (channel->metadata) {
        free(channel->metadata);
    }
    
    free(channel);
}

/**
 * @brief 创建纠缠信道嵌入器
 * 
 * @param initial_channels 初始信道数量
 * @return EntanglementChannelEmbedder* 嵌入器指针
 */
EntanglementChannelEmbedder* entanglement_channel_embedder_create(int initial_channels) {
    if (initial_channels < 0) {
        initial_channels = 0;
    }
    
    EntanglementChannelEmbedder *embedder = (EntanglementChannelEmbedder*)malloc(sizeof(EntanglementChannelEmbedder));
    if (!embedder) {
        fprintf(stderr, "错误: 无法分配嵌入器内存\n");
        return NULL;
    }
    
    embedder->channel_count = 0;
    embedder->total_capacity = 0;
    embedder->used_capacity = 0;
    embedder->embedder_context = NULL;
    
    // 设置默认配置
    embedder->config.error_correction = 1;
    embedder->config.compression_level = 2;
    embedder->config.encoding_density = 0.8;
    embedder->config.use_superposition = 1;
    
    // 分配信道数组
    if (initial_channels > 0) {
        embedder->channels = (EntanglementChannel**)malloc(initial_channels * sizeof(EntanglementChannel*));
        if (!embedder->channels) {
            fprintf(stderr, "错误: 无法分配信道数组内存\n");
            free(embedder);
            return NULL;
        }
        
        memset(embedder->channels, 0, initial_channels * sizeof(EntanglementChannel*));
    } else {
        embedder->channels = NULL;
    }
    
    printf("创建了纠缠信道嵌入器，初始容量: %d 个信道\n", initial_channels);
    
    return embedder;
}

/**
 * @brief 销毁纠缠信道嵌入器
 * 
 * @param embedder 嵌入器指针
 */
void entanglement_channel_embedder_destroy(EntanglementChannelEmbedder *embedder) {
    if (!embedder) return;
    
    // 销毁所有信道
    for (int i = 0; i < embedder->channel_count; i++) {
        if (embedder->channels[i]) {
            destroy_entanglement_channel(embedder->channels[i]);
        }
    }
    
    // 释放信道数组
    if (embedder->channels) {
        free(embedder->channels);
    }
    
    // 释放上下文
    if (embedder->embedder_context) {
        free(embedder->embedder_context);
    }
    
    free(embedder);
    printf("销毁了纠缠信道嵌入器\n");
}

/**
 * @brief 添加新的纠缠信道
 * 
 * @param embedder 嵌入器指针
 * @param type 信道类型
 * @param qubit_count 量子比特数量
 * @return int 成功返回信道索引，失败返回-1
 */
int entanglement_channel_embedder_add_channel(EntanglementChannelEmbedder *embedder, 
                                            EntanglementChannelType type, 
                                            int qubit_count) {
    if (!embedder) {
        return -1;
    }
    
    // 创建新信道
    EntanglementChannel *channel = create_entanglement_channel(type, qubit_count);
    if (!channel) {
        return -1;
    }
    
    // 扩展信道数组
    EntanglementChannel **new_channels = (EntanglementChannel**)realloc(
        embedder->channels, 
        (embedder->channel_count + 1) * sizeof(EntanglementChannel*)
    );
    
    if (!new_channels) {
        fprintf(stderr, "错误: 无法重新分配信道数组内存\n");
        destroy_entanglement_channel(channel);
        return -1;
    }
    
    embedder->channels = new_channels;
    embedder->channels[embedder->channel_count] = channel;
    
    // 更新总容量
    int channel_capacity = qubit_count - 1; // 有效信息容量比特数
    embedder->total_capacity += channel_capacity;
    
    printf("添加了一个容量为 %d 比特的信道，当前总容量: %d 比特\n", 
           channel_capacity, embedder->total_capacity);
    
    return embedder->channel_count++;
}

/**
 * @brief 设置嵌入配置
 * 
 * @param embedder 嵌入器指针
 * @param error_correction 是否启用错误校正
 * @param compression_level 压缩级别(1-3)
 * @param encoding_density 编码密度(0.0-1.0)
 * @param use_superposition 是否使用叠加态
 * @return int 成功返回0，失败返回非0值
 */
int entanglement_channel_embedder_set_config(EntanglementChannelEmbedder *embedder,
                                          int error_correction,
                                          int compression_level,
                                          double encoding_density,
                                          int use_superposition) {
    if (!embedder) {
        return -1;
    }
    
    // 验证参数
    if (compression_level < 1 || compression_level > 3) {
        fprintf(stderr, "错误: 压缩级别必须在1-3范围内\n");
        return -1;
    }
    
    if (encoding_density < 0.0 || encoding_density > 1.0) {
        fprintf(stderr, "错误: 编码密度必须在0.0-1.0范围内\n");
        return -1;
    }
    
    // 设置配置
    embedder->config.error_correction = error_correction ? 1 : 0;
    embedder->config.compression_level = compression_level;
    embedder->config.encoding_density = encoding_density;
    embedder->config.use_superposition = use_superposition ? 1 : 0;
    
    printf("更新了嵌入配置: 错误校正=%d, 压缩级别=%d, 编码密度=%.2f, 使用叠加态=%d\n",
           error_correction, compression_level, encoding_density, use_superposition);
    
    return 0;
}

/**
 * @brief 将数据嵌入到纠缠信道
 * 
 * @param embedder 嵌入器指针
 * @param data 输入数据
 * @param data_size 数据大小
 * @return int 成功返回嵌入的比特数，失败返回-1
 */
int entanglement_channel_embedder_embed_data(EntanglementChannelEmbedder *embedder,
                                          const uint8_t *data,
                                          size_t data_size) {
    if (!embedder || !data || data_size == 0) {
        return -1;
    }
    
    // 检查嵌入容量
    int required_bits = data_size * 8 / embedder->config.compression_level;
    int available_bits = embedder->total_capacity - embedder->used_capacity;
    
    if (required_bits > available_bits) {
        fprintf(stderr, "错误: 没有足够的容量嵌入数据，需要 %d 比特，可用 %d 比特\n",
                required_bits, available_bits);
        return -1;
    }
    
    // 计算嵌入后的比特数
    int embedded_bits = 0;
    
    // 循环嵌入数据到可用信道
    int current_channel = 0;
    int current_qubit = 0;
    int bits_processed = 0;
    
    while (bits_processed < data_size * 8 && current_channel < embedder->channel_count) {
        EntanglementChannel *channel = embedder->channels[current_channel];
        
        // 如果当前信道已满或不活跃，跳到下一个信道
        if (!channel || !channel->active || current_qubit >= channel->qubit_count) {
            current_channel++;
            current_qubit = 0;
            continue;
        }
        
        // 处理一个比特的数据
        if (bits_processed < data_size * 8) {
            int byte_index = bits_processed / 8;
            int bit_index = bits_processed % 8;
            int bit_value = (data[byte_index] >> bit_index) & 0x1;
            
            // 根据比特值修改量子态
            if (embedder->config.use_superposition) {
                // 使用叠加态编码
                // 如果是1，应用Hadamard门，否则保持基态
                if (bit_value) {
                    quantum_entanglement_apply_gate(channel->entanglement, current_qubit, "H");
                }
            } else {
                // 使用计算基编码
                // 如果是1，应用X门，否则保持基态
                if (bit_value) {
                    quantum_entanglement_apply_gate(channel->entanglement, current_qubit, "X");
                }
            }
            
            embedded_bits++;
            bits_processed += embedder->config.compression_level;
            current_qubit++;
            
            // 如果启用了错误校正，添加奇偶校验位
            if (embedder->config.error_correction && current_qubit < channel->qubit_count && 
                (bits_processed % (8 * embedder->config.compression_level)) == 0) {
                // 简单奇偶校验：计算前几位的奇偶性
                int parity = 0;
                for (int i = 1; i <= embedder->config.compression_level; i++) {
                    int prev_bit_index = bits_processed - i;
                    int prev_byte_index = prev_bit_index / 8;
                    int prev_bit_pos = prev_bit_index % 8;
                    parity ^= ((data[prev_byte_index] >> prev_bit_pos) & 0x1);
                }
                
                // 设置奇偶校验位
                if (parity) {
                    quantum_entanglement_apply_gate(channel->entanglement, current_qubit, "X");
                }
                
                current_qubit++;
                embedded_bits++;
            }
        }
    }
    
    // 更新已用容量
    embedder->used_capacity += embedded_bits;
    
    printf("成功嵌入 %d 比特的数据，当前已用容量: %d/%d 比特\n",
           embedded_bits, embedder->used_capacity, embedder->total_capacity);
    
    return embedded_bits;
}

/**
 * @brief 从纠缠信道提取数据
 * 
 * @param embedder 嵌入器指针
 * @param output 输出数据缓冲区
 * @param output_size 缓冲区大小
 * @return int 成功返回提取的比特数，失败返回-1
 */
int entanglement_channel_embedder_extract_data(EntanglementChannelEmbedder *embedder,
                                            uint8_t *output,
                                            size_t output_size) {
    if (!embedder || !output || output_size == 0 || embedder->used_capacity == 0) {
        return -1;
    }
    
    // 计算可以提取的最大字节数
    int extractable_bytes = embedder->used_capacity / (8 * embedder->config.compression_level);
    if (embedder->config.error_correction) {
        // 减去错误校正位占用的空间
        extractable_bytes = extractable_bytes * 8 / 9;
    }
    
    if (output_size < extractable_bytes) {
        fprintf(stderr, "错误: 输出缓冲区太小，需要至少 %d 字节\n", extractable_bytes);
        return -1;
    }
    
    // 清零输出缓冲区
    memset(output, 0, output_size);
    
    // 循环提取数据
    int current_channel = 0;
    int current_qubit = 0;
    int bits_extracted = 0;
    int bytes_extracted = 0;
    
    while (bytes_extracted < extractable_bytes && current_channel < embedder->channel_count) {
        EntanglementChannel *channel = embedder->channels[current_channel];
        
        // 如果当前信道已空或不活跃，跳到下一个信道
        if (!channel || !channel->active || current_qubit >= channel->qubit_count) {
            current_channel++;
            current_qubit = 0;
            continue;
        }
        
        // 处理一个比特的数据
        int bit_value = 0;
        
        // 测量量子态
        if (embedder->config.use_superposition) {
            // 测量叠加态
            double probability = quantum_entanglement_measure_probability(
                channel->entanglement, current_qubit, 1
            );
            bit_value = (probability > 0.5) ? 1 : 0;
        } else {
            // 直接测量计算基
            bit_value = quantum_entanglement_measure(channel->entanglement, current_qubit);
        }
        
        // 写入输出
        int output_bit_index = bits_extracted % 8;
        int output_byte_index = bits_extracted / 8;
        
        if (output_byte_index < output_size) {
            output[output_byte_index] |= (bit_value << output_bit_index);
        }
        
        bits_extracted++;
        current_qubit++;
        
        // 处理错误校正位
        if (embedder->config.error_correction && current_qubit < channel->qubit_count && 
            (bits_extracted % 8) == 0) {
            // 跳过校验位
            current_qubit++;
        }
        
        // 更新已提取字节数
        bytes_extracted = bits_extracted / 8;
    }
    
    // 重置已用容量
    embedder->used_capacity = 0;
    
    printf("成功提取 %d 字节的数据\n", bytes_extracted);
    
    return bits_extracted;
}

/**
 * @brief 检查信道状态
 * 
 * @param embedder 嵌入器指针
 * @param channel_index 信道索引
 * @param fidelity_out 输出保真度的指针
 * @return int 如果信道活跃返回1，否则返回0
 */
int entanglement_channel_embedder_check_channel(EntanglementChannelEmbedder *embedder,
                                             int channel_index,
                                             double *fidelity_out) {
    if (!embedder || channel_index < 0 || channel_index >= embedder->channel_count) {
        return 0;
    }
    
    EntanglementChannel *channel = embedder->channels[channel_index];
    if (!channel) {
        return 0;
    }
    
    if (fidelity_out) {
        *fidelity_out = channel->fidelity;
    }
    
    return channel->active ? 1 : 0;
}

/**
 * @brief 应用噪声到信道
 * 
 * @param embedder 嵌入器指针
 * @param channel_index 信道索引
 * @param noise_level 噪声级别(0.0-1.0)
 * @return int 成功返回0，失败返回非0值
 */
int entanglement_channel_embedder_apply_noise(EntanglementChannelEmbedder *embedder,
                                           int channel_index,
                                           double noise_level) {
    if (!embedder || channel_index < 0 || channel_index >= embedder->channel_count) {
        return -1;
    }
    
    EntanglementChannel *channel = embedder->channels[channel_index];
    if (!channel || !channel->active) {
        return -1;
    }
    
    // 验证噪声级别
    if (noise_level < 0.0 || noise_level > 1.0) {
        fprintf(stderr, "错误: 噪声级别必须在0.0-1.0范围内\n");
        return -1;
    }
    
    // 应用噪声
    channel->noise_level = noise_level;
    
    // 降低信道保真度
    channel->fidelity = channel->fidelity * (1.0 - noise_level);
    
    // 如果保真度太低，信道可能变得不可用
    if (channel->fidelity < 0.5) {
        channel->active = 0;
        printf("警告: 信道 %d 的保真度低于阈值，已停用\n", channel_index);
    }
    
    printf("应用了噪声级别 %.2f 到信道 %d，当前保真度: %.4f\n",
           noise_level, channel_index, channel->fidelity);
    
    return 0;
}

/**
 * @brief 尝试恢复信道
 * 
 * @param embedder 嵌入器指针
 * @param channel_index 信道索引
 * @return int 成功返回1，失败返回0
 */
int entanglement_channel_embedder_recover_channel(EntanglementChannelEmbedder *embedder,
                                               int channel_index) {
    if (!embedder || channel_index < 0 || channel_index >= embedder->channel_count) {
        return 0;
    }
    
    EntanglementChannel *channel = embedder->channels[channel_index];
    if (!channel) {
        return 0;
    }
    
    // 如果信道已经活跃，不需要恢复
    if (channel->active) {
        return 1;
    }
    
    // 尝试通过纠缠提纯恢复信道
    printf("尝试恢复信道 %d...\n", channel_index);
    
    // 创建一个新的纠缠对象
    QuantumEntanglement *new_entanglement = quantum_entanglement_create(channel->qubit_count);
    if (!new_entanglement) {
        fprintf(stderr, "错误: 无法创建新的纠缠态\n");
        return 0;
    }
    
    // 根据类型重新初始化信道
    switch (channel->type) {
        case CHANNEL_TYPE_BELL:
            if (channel->qubit_count == 2) {
                quantum_entanglement_create_bell_state(new_entanglement, 0, 1);
            } else {
                for (int i = 0; i < channel->qubit_count - 1; i += 2) {
                    quantum_entanglement_create_bell_state(new_entanglement, i, i + 1);
                }
            }
            break;
            
        case CHANNEL_TYPE_GHZ:
            {
                int qubits[channel->qubit_count];
                for (int i = 0; i < channel->qubit_count; i++) {
                    qubits[i] = i;
                }
                quantum_entanglement_create_ghz_state(new_entanglement, qubits, channel->qubit_count);
            }
            break;
            
        case CHANNEL_TYPE_CLUSTER:
            {
                int qubits[channel->qubit_count];
                for (int i = 0; i < channel->qubit_count; i++) {
                    qubits[i] = i;
                }
                quantum_entanglement_create_cluster_state(new_entanglement, qubits, channel->qubit_count);
            }
            break;
            
        case CHANNEL_TYPE_ADAPTIVE:
            {
                int qubits[channel->qubit_count];
                for (int i = 0; i < channel->qubit_count; i++) {
                    qubits[i] = i;
                }
                quantum_entanglement_create_ghz_state(new_entanglement, qubits, channel->qubit_count);
                
                for (int i = 0; i < channel->qubit_count; i += 2) {
                    quantum_entanglement_apply_gate(new_entanglement, i, "H");
                }
            }
            break;
    }
    
    // 替换旧的纠缠对象
    quantum_entanglement_destroy(channel->entanglement);
    channel->entanglement = new_entanglement;
    
    // 重置信道属性
    channel->active = 1;
    channel->fidelity = 0.95;
    channel->noise_level = 0.01;
    
    printf("成功恢复了信道 %d\n", channel_index);
    
    return 1;
}

/**
 * @brief 获取嵌入器统计信息
 * 
 * @param embedder 嵌入器指针
 * @param active_channels_out 输出活跃信道数的指针
 * @param total_capacity_out 输出总容量的指针
 * @param used_capacity_out 输出已用容量的指针
 */
void entanglement_channel_embedder_get_stats(EntanglementChannelEmbedder *embedder,
                                          int *active_channels_out,
                                          int *total_capacity_out,
                                          int *used_capacity_out) {
    if (!embedder) return;
    
    int active_channels = 0;
    
    // 计算活跃信道数
    for (int i = 0; i < embedder->channel_count; i++) {
        if (embedder->channels[i] && embedder->channels[i]->active) {
            active_channels++;
        }
    }
    
    if (active_channels_out) {
        *active_channels_out = active_channels;
    }
    
    if (total_capacity_out) {
        *total_capacity_out = embedder->total_capacity;
    }
    
    if (used_capacity_out) {
        *used_capacity_out = embedder->used_capacity;
    }
} 