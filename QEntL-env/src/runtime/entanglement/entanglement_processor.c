/**
 * 量子纠缠处理器实现文件
 * 实现量子纠缠通道的创建、管理、度量和处理功能
 * 版本: 1.0
 * 最后更新: 2024-05-15
 */

#include "entanglement_processor.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>

/**
 * 创建一个新的纠缠处理器实例
 */
EntanglementProcessor* create_entanglement_processor(void) {
    EntanglementProcessor* processor = (EntanglementProcessor*)malloc(sizeof(EntanglementProcessor));
    if (processor == NULL) {
        return NULL;
    }
    
    processor->max_channels = DEFAULT_MAX_CHANNELS;
    processor->channel_count = 0;
    processor->channels = (EntanglementChannel**)malloc(sizeof(EntanglementChannel*) * processor->max_channels);
    
    if (processor->channels == NULL) {
        free(processor);
        return NULL;
    }
    
    processor->last_error_code = ERROR_NONE;
    processor->debug_mode = 0;
    processor->timestamp = time(NULL);
    
    return processor;
}

/**
 * 销毁纠缠处理器实例并释放所有相关资源
 */
void destroy_entanglement_processor(EntanglementProcessor* processor) {
    if (processor == NULL) {
        return;
    }
    
    // 释放所有通道
    for (int i = 0; i < processor->channel_count; i++) {
        if (processor->channels[i] != NULL) {
            free(processor->channels[i]->metadata);
            free(processor->channels[i]);
        }
    }
    
    // 释放通道数组和处理器本身
    free(processor->channels);
    free(processor);
}

/**
 * 创建一个新的纠缠通道
 */
ChannelReference create_entanglement(
    EntanglementProcessor* processor,
    QuantumStateReference source_state,
    QuantumStateReference target_state,
    EntanglementType type,
    double initial_strength
) {
    if (processor == NULL || source_state == NULL || target_state == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return NULL;
    }
    
    // 检查是否达到最大通道数
    if (processor->channel_count >= processor->max_channels) {
        // 动态增加容量
        int new_max = processor->max_channels * 2;
        EntanglementChannel** new_channels = (EntanglementChannel**)realloc(
            processor->channels, 
            sizeof(EntanglementChannel*) * new_max
        );
        
        if (new_channels == NULL) {
            processor->last_error_code = ERROR_MEMORY_ALLOCATION;
            return NULL;
        }
        
        processor->channels = new_channels;
        processor->max_channels = new_max;
    }
    
    // 创建新通道
    EntanglementChannel* channel = (EntanglementChannel*)malloc(sizeof(EntanglementChannel));
    if (channel == NULL) {
        processor->last_error_code = ERROR_MEMORY_ALLOCATION;
        return NULL;
    }
    
    // 生成唯一ID
    static unsigned int next_id = 1;
    channel->id = next_id++;
    
    // 初始化通道属性
    channel->source = source_state;
    channel->target = target_state;
    channel->type = type;
    channel->strength = initial_strength;
    channel->creation_time = time(NULL);
    channel->last_update_time = channel->creation_time;
    channel->stability = 1.0;
    channel->is_active = 1;
    
    // 分配并初始化元数据
    channel->metadata = (ChannelMetadata*)malloc(sizeof(ChannelMetadata));
    if (channel->metadata == NULL) {
        free(channel);
        processor->last_error_code = ERROR_MEMORY_ALLOCATION;
        return NULL;
    }
    
    memset(channel->metadata, 0, sizeof(ChannelMetadata));
    
    // 添加到处理器的通道列表
    processor->channels[processor->channel_count] = channel;
    processor->channel_count++;
    
    if (processor->debug_mode) {
        printf("创建纠缠通道: ID=%u, 类型=%d, 强度=%.2f\n", 
               channel->id, channel->type, channel->strength);
    }
    
    return (ChannelReference)channel;
}

/**
 * 获取通道引用
 */
ChannelReference get_channel_reference(
    EntanglementProcessor* processor,
    unsigned int channel_id
) {
    if (processor == NULL) {
        return NULL;
    }
    
    for (int i = 0; i < processor->channel_count; i++) {
        if (processor->channels[i]->id == channel_id) {
            return (ChannelReference)processor->channels[i];
        }
    }
    
    processor->last_error_code = ERROR_CHANNEL_NOT_FOUND;
    return NULL;
}

/**
 * 更新通道属性
 */
int update_channel(
    EntanglementProcessor* processor,
    ChannelReference channel_ref,
    EntanglementUpdateParams params
) {
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    
    // 更新强度 (如果请求)
    if (params.update_flags & UPDATE_STRENGTH) {
        channel->strength = params.new_strength;
    }
    
    // 更新稳定性 (如果请求)
    if (params.update_flags & UPDATE_STABILITY) {
        channel->stability = params.new_stability;
    }
    
    // 更新活动状态 (如果请求)
    if (params.update_flags & UPDATE_ACTIVITY) {
        channel->is_active = params.is_active;
    }
    
    // 更新类型 (如果请求)
    if (params.update_flags & UPDATE_TYPE) {
        channel->type = params.new_type;
    }
    
    // 更新元数据 (如果请求)
    if (params.update_flags & UPDATE_METADATA && params.metadata != NULL) {
        memcpy(channel->metadata, params.metadata, sizeof(ChannelMetadata));
    }
    
    // 更新时间戳
    channel->last_update_time = time(NULL);
    
    if (processor->debug_mode) {
        printf("更新纠缠通道: ID=%u, 强度=%.2f, 稳定性=%.2f\n", 
               channel->id, channel->strength, channel->stability);
    }
    
    return 1;
}

/**
 * 删除纠缠通道
 */
int delete_channel(
    EntanglementProcessor* processor,
    ChannelReference channel_ref
) {
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    int found = 0;
    int found_index = -1;
    
    // 查找通道索引
    for (int i = 0; i < processor->channel_count; i++) {
        if (processor->channels[i] == channel) {
            found = 1;
            found_index = i;
            break;
        }
    }
    
    if (!found) {
        processor->last_error_code = ERROR_CHANNEL_NOT_FOUND;
        return 0;
    }
    
    if (processor->debug_mode) {
        printf("删除纠缠通道: ID=%u\n", channel->id);
    }
    
    // 释放通道资源
    free(channel->metadata);
    free(channel);
    
    // 从数组中移除 (通过将最后一个元素移到被删除的位置)
    if (found_index < processor->channel_count - 1) {
        processor->channels[found_index] = processor->channels[processor->channel_count - 1];
    }
    
    processor->channel_count--;
    return 1;
}

/**
 * 获取通道强度
 */
double get_channel_strength(
    EntanglementProcessor* processor,
    ChannelReference channel_ref
) {
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0.0;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    return channel->strength;
}

/**
 * 获取通道稳定性
 */
double get_channel_stability(
    EntanglementProcessor* processor,
    ChannelReference channel_ref
) {
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0.0;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    return channel->stability;
}

/**
 * 获取通道类型
 */
EntanglementType get_channel_type(
    EntanglementProcessor* processor,
    ChannelReference channel_ref
) {
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return ENTANGLEMENT_TYPE_UNKNOWN;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    return channel->type;
}

/**
 * 检查通道是否活跃
 */
int is_channel_active(
    EntanglementProcessor* processor,
    ChannelReference channel_ref
) {
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    return channel->is_active;
}

/**
 * 获取源量子状态
 */
QuantumStateReference get_source_state(
    EntanglementProcessor* processor,
    ChannelReference channel_ref
) {
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return NULL;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    return channel->source;
}

/**
 * 获取目标量子状态
 */
QuantumStateReference get_target_state(
    EntanglementProcessor* processor,
    ChannelReference channel_ref
) {
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return NULL;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    return channel->target;
}

/**
 * 查找两个量子态之间的所有通道
 */
int find_channels_between_states(
    EntanglementProcessor* processor,
    QuantumStateReference state1,
    QuantumStateReference state2,
    ChannelReference* result_channels,
    int max_results
) {
    if (processor == NULL || state1 == NULL || state2 == NULL || result_channels == NULL || max_results <= 0) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0;
    }
    
    int count = 0;
    
    for (int i = 0; i < processor->channel_count && count < max_results; i++) {
        EntanglementChannel* channel = processor->channels[i];
        
        // 检查是否连接这两个状态 (考虑双向)
        if ((channel->source == state1 && channel->target == state2) ||
            (channel->source == state2 && channel->target == state1)) {
            result_channels[count++] = (ChannelReference)channel;
        }
    }
    
    return count;
}

/**
 * 测量纠缠度
 */
EntanglementMeasurement measure_entanglement(
    EntanglementProcessor* processor,
    ChannelReference channel_ref
) {
    EntanglementMeasurement measurement = {0};
    
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return measurement;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    
    // 计算基本度量
    measurement.strength = channel->strength;
    measurement.stability = channel->stability;
    measurement.duration = difftime(time(NULL), channel->creation_time);
    
    // 计算复合度量
    measurement.quality = measurement.strength * measurement.stability;
    measurement.efficiency = measurement.quality / (1.0 + measurement.duration / 3600.0); // 随时间轻微衰减
    
    if (processor->debug_mode) {
        printf("测量纠缠通道: ID=%u, 强度=%.2f, 稳定性=%.2f, 质量=%.2f\n", 
               channel->id, measurement.strength, measurement.stability, measurement.quality);
    }
    
    return measurement;
}

/**
 * 增强纠缠
 */
int enhance_entanglement(
    EntanglementProcessor* processor,
    ChannelReference channel_ref,
    double enhancement_factor
) {
    if (processor == NULL || channel_ref == NULL || enhancement_factor <= 0) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    
    // 应用增强因子，但确保不超过最大值1.0
    double new_strength = channel->strength * enhancement_factor;
    if (new_strength > 1.0) new_strength = 1.0;
    
    channel->strength = new_strength;
    channel->last_update_time = time(NULL);
    
    if (processor->debug_mode) {
        printf("增强纠缠通道: ID=%u, 新强度=%.2f\n", channel->id, channel->strength);
    }
    
    return 1;
}

/**
 * 降低纠缠
 */
int degrade_entanglement(
    EntanglementProcessor* processor,
    ChannelReference channel_ref,
    double degradation_factor
) {
    if (processor == NULL || channel_ref == NULL || degradation_factor <= 0) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    
    // 应用衰减因子，但确保不低于最小值0.0
    double new_strength = channel->strength / degradation_factor;
    if (new_strength < 0.0) new_strength = 0.0;
    
    channel->strength = new_strength;
    channel->last_update_time = time(NULL);
    
    if (processor->debug_mode) {
        printf("降低纠缠通道: ID=%u, 新强度=%.2f\n", channel->id, channel->strength);
    }
    
    return 1;
}

/**
 * 传播量子状态变化
 */
int propagate_state_change(
    EntanglementProcessor* processor,
    QuantumStateReference changed_state,
    PropagationConfig config
) {
    if (processor == NULL || changed_state == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0;
    }
    
    int affected_count = 0;
    
    // 遍历所有活跃通道
    for (int i = 0; i < processor->channel_count; i++) {
        EntanglementChannel* channel = processor->channels[i];
        
        // 跳过非活跃通道
        if (!channel->is_active) {
            continue;
        }
        
        // 检查通道是否连接到更改的状态
        if (channel->source == changed_state || channel->target == changed_state) {
            // 获取要影响的另一端
            QuantumStateReference target_state = 
                (channel->source == changed_state) ? channel->target : channel->source;
            
            // 计算传播强度 (基于通道强度和稳定性)
            double prop_strength = channel->strength * channel->stability * config.propagation_factor;
            
            // 如果传播强度低于阈值，则跳过
            if (prop_strength < config.min_propagation_threshold) {
                continue;
            }
            
            // 执行量子态传播 (这需要一个外部函数来处理量子态的实际修改)
            // 此处假设有一个外部函数 apply_state_change() 可以修改目标量子状态
            // apply_state_change(target_state, changed_state, prop_strength);
            
            affected_count++;
            
            // 应用传播后衰减 (如果启用)
            if (config.apply_propagation_decay) {
                channel->strength *= (1.0 - config.propagation_decay_rate);
            }
            
            // 更新通道时间戳
            channel->last_update_time = time(NULL);
            
            // 检查是否已达到最大传播限制
            if (config.max_propagations > 0 && affected_count >= config.max_propagations) {
                break;
            }
        }
    }
    
    if (processor->debug_mode) {
        printf("传播状态变化: 影响了%d个通道\n", affected_count);
    }
    
    return affected_count;
}

/**
 * 获取所有连接到特定量子状态的通道
 */
int get_connected_channels(
    EntanglementProcessor* processor,
    QuantumStateReference state,
    ChannelReference* result_channels,
    int max_results
) {
    if (processor == NULL || state == NULL || result_channels == NULL || max_results <= 0) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return 0;
    }
    
    int count = 0;
    
    for (int i = 0; i < processor->channel_count && count < max_results; i++) {
        EntanglementChannel* channel = processor->channels[i];
        
        // 检查是否连接到目标状态
        if (channel->source == state || channel->target == state) {
            result_channels[count++] = (ChannelReference)channel;
        }
    }
    
    return count;
}

/**
 * 设置处理器调试模式
 */
void set_processor_debug_mode(EntanglementProcessor* processor, int debug_mode) {
    if (processor != NULL) {
        processor->debug_mode = debug_mode;
    }
}

/**
 * 获取处理器错误代码
 */
ErrorCode get_processor_error(EntanglementProcessor* processor) {
    if (processor == NULL) {
        return ERROR_NULL_PROCESSOR;
    }
    return processor->last_error_code;
}

/**
 * 获取错误消息
 */
const char* get_error_message(ErrorCode code) {
    switch (code) {
        case ERROR_NONE:
            return "无错误";
        case ERROR_NULL_PROCESSOR:
            return "处理器为空";
        case ERROR_INVALID_PARAMETER:
            return "无效参数";
        case ERROR_CHANNEL_NOT_FOUND:
            return "找不到通道";
        case ERROR_MEMORY_ALLOCATION:
            return "内存分配失败";
        default:
            return "未知错误";
    }
}

/**
 * 创建通道快照
 */
ChannelSnapshot* create_channel_snapshot(
    EntanglementProcessor* processor,
    ChannelReference channel_ref
) {
    if (processor == NULL || channel_ref == NULL) {
        if (processor != NULL) {
            processor->last_error_code = ERROR_INVALID_PARAMETER;
        }
        return NULL;
    }
    
    EntanglementChannel* channel = (EntanglementChannel*)channel_ref;
    
    ChannelSnapshot* snapshot = (ChannelSnapshot*)malloc(sizeof(ChannelSnapshot));
    if (snapshot == NULL) {
        processor->last_error_code = ERROR_MEMORY_ALLOCATION;
        return NULL;
    }
    
    // 复制通道数据到快照
    snapshot->channel_id = channel->id;
    snapshot->type = channel->type;
    snapshot->strength = channel->strength;
    snapshot->stability = channel->stability;
    snapshot->is_active = channel->is_active;
    snapshot->creation_time = channel->creation_time;
    snapshot->last_update_time = channel->last_update_time;
    snapshot->snapshot_time = time(NULL);
    
    return snapshot;
}

/**
 * 释放通道快照
 */
void free_channel_snapshot(ChannelSnapshot* snapshot) {
    if (snapshot != NULL) {
        free(snapshot);
    }
} 