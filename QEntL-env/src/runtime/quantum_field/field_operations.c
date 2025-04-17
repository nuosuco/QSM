/**
 * 量子场操作实现
 * 
 * 实现了量子场的高级操作函数，提供交互、演化、分析和可视化等功能。
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include "field_operations.h"

/* 内部辅助函数声明 */
static QField* get_field_from_reference(FieldReference* reference);
static char* generate_timestamp();
static FieldOperationResult create_operation_result(int success, const char* description);
static void set_operation_result_energy_entropy(FieldOperationResult* result, QField* field);

/**
 * 应用操作到量子场
 */
FieldOperationResult apply_field_operation(FieldManager* manager, 
                                          FieldReference* reference,
                                          FieldOperationType operation,
                                          FieldOperationParams params) {
    if (!manager || !reference) {
        FieldOperationResult result = create_operation_result(0, "无效参数");
        result.error = FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
        return result;
    }
    
    QField* field = get_field_from_reference(reference);
    if (!field) {
        FieldOperationResult result = create_operation_result(0, "无效场引用");
        result.error = FIELD_MANAGER_ERROR_INVALID_REFERENCE;
        return result;
    }
    
    // 获取操作前能量和熵
    double energy_before = calculate_field_energy(field);
    double entropy_before = calculate_field_entropy(field);
    
    // 准备结果结构
    FieldOperationResult result;
    result.success = 0;
    result.operation_description = NULL;
    result.effect_magnitude = 0.0;
    result.energy_before = energy_before;
    result.entropy_before = entropy_before;
    result.energy_after = 0.0;
    result.entropy_after = 0.0;
    result.timestamp = generate_timestamp();
    result.error = FIELD_MANAGER_ERROR_NONE;
    
    // 中心坐标，应用于多种操作
    FieldCoordinate center = {params.param1, params.param2, params.param3, 0.0};
    
    // 根据操作类型执行不同操作
    switch (operation) {
        case FIELD_OP_AMPLIFY: {
            // 创建场效应参数
            FieldEffectParameters effect_params;
            effect_params.type = EFFECT_AMPLIFICATION;
            effect_params.strength = params.param1;  // 使用param1作为强度
            effect_params.range = params.param2;     // 使用param2作为范围
            effect_params.duration = params.param3;  // 使用param3作为持续时间
            effect_params.custom_parameters = params.custom_params;
            
            // 应用效应
            apply_field_effect(field, center, effect_params);
            
            result.success = 1;
            result.operation_description = strdup("振幅放大");
            result.effect_magnitude = params.param1;
            break;
        }
        
        case FIELD_OP_ATTENUATE: {
            // 创建场效应参数
            FieldEffectParameters effect_params;
            effect_params.type = EFFECT_ATTENUATION;
            effect_params.strength = params.param1;  // 使用param1作为强度
            effect_params.range = params.param2;     // 使用param2作为范围
            effect_params.duration = params.param3;  // 使用param3作为持续时间
            effect_params.custom_parameters = params.custom_params;
            
            // 应用效应
            apply_field_effect(field, center, effect_params);
            
            result.success = 1;
            result.operation_description = strdup("振幅衰减");
            result.effect_magnitude = params.param1;
            break;
        }
        
        case FIELD_OP_PHASE_SHIFT: {
            // 创建场效应参数
            FieldEffectParameters effect_params;
            effect_params.type = EFFECT_PHASE_SHIFT;
            effect_params.strength = params.param1;  // 使用param1作为强度
            effect_params.range = params.param2;     // 使用param2作为范围
            effect_params.duration = params.param3;  // 使用param3作为持续时间
            effect_params.custom_parameters = params.custom_params;
            
            // 应用效应
            apply_field_effect(field, center, effect_params);
            
            result.success = 1;
            result.operation_description = strdup("相位偏移");
            result.effect_magnitude = params.param1;
            break;
        }
        
        case FIELD_OP_ENTANGLE: {
            // 创建场效应参数
            FieldEffectParameters effect_params;
            effect_params.type = EFFECT_ENTANGLEMENT_BOOST;
            effect_params.strength = params.param1;  // 使用param1作为强度
            effect_params.range = params.param2;     // 使用param2作为范围
            effect_params.duration = params.param3;  // 使用param3作为持续时间
            effect_params.custom_parameters = params.custom_params;
            
            // 应用效应
            apply_field_effect(field, center, effect_params);
            
            result.success = 1;
            result.operation_description = strdup("纠缠增强");
            result.effect_magnitude = params.param1;
            break;
        }
        
        case FIELD_OP_DECOHERE: {
            // 创建场效应参数
            FieldEffectParameters effect_params;
            effect_params.type = EFFECT_DECOHERENCE;
            effect_params.strength = params.param1;  // 使用param1作为强度
            effect_params.range = params.param2;     // 使用param2作为范围
            effect_params.duration = params.param3;  // 使用param3作为持续时间
            effect_params.custom_parameters = params.custom_params;
            
            // 应用效应
            apply_field_effect(field, center, effect_params);
            
            result.success = 1;
            result.operation_description = strdup("退相干");
            result.effect_magnitude = params.param1;
            break;
        }
        
        case FIELD_OP_TRANSFORM:
            // 可以添加变换操作的实现
            result.success = 0;
            result.operation_description = strdup("变换操作未实现");
            result.error = FIELD_MANAGER_ERROR_NOT_IMPLEMENTED;
            break;
            
        case FIELD_OP_ANALYZE:
            // 分析操作应该通过专门的分析函数实现
            result.success = 0;
            result.operation_description = strdup("分析操作应使用专门的分析函数");
            result.error = FIELD_MANAGER_ERROR_OPERATION_FAILED;
            break;
            
        case FIELD_OP_VISUALIZE:
            // 可视化操作应该通过专门的可视化函数实现
            result.success = 0;
            result.operation_description = strdup("可视化操作应使用专门的可视化函数");
            result.error = FIELD_MANAGER_ERROR_OPERATION_FAILED;
            break;
            
        case FIELD_OP_CUSTOM:
            // 自定义操作，需要额外的自定义参数
            if (!params.custom_params) {
                result.success = 0;
                result.operation_description = strdup("自定义操作缺少必要参数");
                result.error = FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
            } else {
                // 此处应该根据自定义参数执行操作
                // 示例：您可以在custom_params中传入一个函数指针
                result.success = 0;
                result.operation_description = strdup("自定义操作未实现");
                result.error = FIELD_MANAGER_ERROR_NOT_IMPLEMENTED;
            }
            break;
            
        default:
            result.success = 0;
            result.operation_description = strdup("未知操作类型");
            result.error = FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
            break;
    }
    
    // 获取操作后能量和熵
    result.energy_after = calculate_field_energy(field);
    result.entropy_after = calculate_field_entropy(field);
    
    // 记录日志
    if (manager->config.enable_logging) {
        printf("[%s] 执行量子场操作: %s, 场ID: %s, 成功: %d\n", 
               result.timestamp, 
               result.operation_description,
               field->id.readable_id,
               result.success);
    }
    
    return result;
}

/**
 * 叠加两个量子场
 */
FieldReference* superpose_fields(FieldManager* manager,
                               FieldReference* reference1,
                               FieldReference* reference2,
                               double weight1,
                               double weight2,
                               FieldCreationOptions result_options) {
    if (!manager || !reference1 || !reference2) {
        return NULL;
    }
    
    QField* field1 = get_field_from_reference(reference1);
    QField* field2 = get_field_from_reference(reference2);
    
    if (!field1 || !field2) {
        return NULL;
    }
    
    // 创建新场来存储叠加结果
    FieldReference* result_ref = create_field(manager, FIELD_TYPE_COMPOSITE, result_options);
    if (!result_ref) {
        return NULL;
    }
    
    QField* result_field = get_field_from_reference(result_ref);
    
    // 对于field1中的每个节点
    for (int i = 0; i < field1->node_count; i++) {
        FieldNode* node1 = field1->nodes[i];
        
        // 尝试在field2中找到相应位置的节点
        FieldNode* node2 = find_field_node(field2, node1->coordinate);
        
        // 创建新状态
        QuantumState* new_state = NULL;
        
        if (node2) {
            // 如果在field2中找到了对应节点，则叠加两个状态
            new_state = superpose_quantum_states(node1->state, node2->state, weight1, weight2);
        } else {
            // 如果没有找到对应节点，则只使用field1的状态（乘以权重）
            new_state = clone_quantum_state(node1->state);
            scale_quantum_state(new_state, weight1);
        }
        
        // 将新状态添加到结果场
        add_field_node(result_field, node1->coordinate, new_state);
    }
    
    // 对于field2中的节点（仅处理field1中没有的节点）
    for (int i = 0; i < field2->node_count; i++) {
        FieldNode* node2 = field2->nodes[i];
        
        // 检查结果场中是否已有该节点（通过field1添加的）
        FieldNode* existing_node = find_field_node(result_field, node2->coordinate);
        
        if (!existing_node) {
            // 如果结果场中尚无该节点，则添加（仅包含field2的贡献）
            QuantumState* new_state = clone_quantum_state(node2->state);
            scale_quantum_state(new_state, weight2);
            add_field_node(result_field, node2->coordinate, new_state);
        }
    }
    
    // 记录日志
    if (manager->config.enable_logging) {
        printf("叠加量子场: %s 和 %s 创建新场: %s, 权重: %.2f, %.2f\n", 
               field1->id.readable_id, 
               field2->id.readable_id,
               result_field->id.readable_id,
               weight1, weight2);
    }
    
    return result_ref;
}

/**
 * 在量子场中创建波
 */
FieldOperationResult create_wave_in_field(FieldManager* manager,
                                         FieldReference* reference,
                                         double center_x,
                                         double center_y,
                                         double center_z,
                                         double amplitude,
                                         double frequency,
                                         double phase) {
    if (!manager || !reference) {
        FieldOperationResult result = create_operation_result(0, "无效参数");
        result.error = FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
        return result;
    }
    
    QField* field = get_field_from_reference(reference);
    if (!field) {
        FieldOperationResult result = create_operation_result(0, "无效场引用");
        result.error = FIELD_MANAGER_ERROR_INVALID_REFERENCE;
        return result;
    }
    
    // 获取操作前能量和熵
    double energy_before = calculate_field_energy(field);
    double entropy_before = calculate_field_entropy(field);
    
    // 创建中心坐标
    FieldCoordinate center = {center_x, center_y, center_z, 0.0};
    
    // 使用现有函数创建波
    create_field_wave(field, center, amplitude, frequency, phase);
    
    // 创建操作结果
    FieldOperationResult result;
    result.success = 1;
    result.operation_description = strdup("创建量子场波");
    result.effect_magnitude = amplitude;
    result.energy_before = energy_before;
    result.entropy_before = entropy_before;
    result.energy_after = calculate_field_energy(field);
    result.entropy_after = calculate_field_entropy(field);
    result.timestamp = generate_timestamp();
    result.error = FIELD_MANAGER_ERROR_NONE;
    
    // 记录日志
    if (manager->config.enable_logging) {
        printf("[%s] 在量子场 %s 中创建波: 振幅=%.2f, 频率=%.2f, 相位=%.2f\n", 
               result.timestamp, 
               field->id.readable_id,
               amplitude, frequency, phase);
    }
    
    return result;
}

/**
 * 演化量子场并记录轨迹
 */
FieldEvolutionTrajectory evolve_field_with_trajectory(FieldManager* manager,
                                                    FieldReference* reference,
                                                    FieldEvolutionConfig config) {
    FieldEvolutionTrajectory trajectory;
    memset(&trajectory, 0, sizeof(FieldEvolutionTrajectory));
    
    if (!manager || !reference) {
        return trajectory;
    }
    
    QField* field = get_field_from_reference(reference);
    if (!field) {
        return trajectory;
    }
    
    // 设置步数
    int steps = config.steps > 0 ? config.steps : 1;
    trajectory.step_count = steps;
    
    // 分配轨迹数组
    trajectory.time_points = (double*)malloc(sizeof(double) * steps);
    trajectory.energy_trajectory = (double*)malloc(sizeof(double) * steps);
    trajectory.entropy_trajectory = (double*)malloc(sizeof(double) * steps);
    trajectory.coherence_trajectory = (double*)malloc(sizeof(double) * steps);
    trajectory.evolution_id = (char*)malloc(64);
    
    if (!trajectory.time_points || !trajectory.energy_trajectory || 
        !trajectory.entropy_trajectory || !trajectory.coherence_trajectory || 
        !trajectory.evolution_id) {
        // 内存分配失败，释放已分配资源
        if (trajectory.time_points) free(trajectory.time_points);
        if (trajectory.energy_trajectory) free(trajectory.energy_trajectory);
        if (trajectory.entropy_trajectory) free(trajectory.entropy_trajectory);
        if (trajectory.coherence_trajectory) free(trajectory.coherence_trajectory);
        if (trajectory.evolution_id) free(trajectory.evolution_id);
        
        memset(&trajectory, 0, sizeof(FieldEvolutionTrajectory));
        return trajectory;
    }
    
    // 生成演化ID
    snprintf(trajectory.evolution_id, 64, "EVO_%lld_%04d", 
             (long long)time(NULL), rand() % 10000);
    
    // 记录开始时间
    trajectory.start_timestamp = generate_timestamp();
    
    // 设置时间步长
    double time_step = config.time_step > 0 ? config.time_step : 0.1;
    
    // 记录初始状态（步骤0）
    trajectory.time_points[0] = field->current_time;
    trajectory.energy_trajectory[0] = calculate_field_energy(field);
    trajectory.entropy_trajectory[0] = calculate_field_entropy(field);
    trajectory.coherence_trajectory[0] = 1.0; // 假设初始相干性为1.0
    
    // 演化场并记录各时间点状态
    for (int i = 1; i < steps; i++) {
        // 确定当前步长
        double current_step = time_step;
        if (config.adaptive_step) {
            // 如果启用自适应步长，可以根据场的状态调整步长
            double current_energy = trajectory.energy_trajectory[i-1];
            double energy_threshold = 10.0; // 示例阈值
            if (current_energy > energy_threshold) {
                current_step *= 0.5; // 高能量时减小步长
            } else {
                current_step *= 1.2; // 低能量时增大步长
            }
        }
        
        // 演化场
        evolve_field(field, current_step);
        
        // 记录状态
        trajectory.time_points[i] = field->current_time;
        trajectory.energy_trajectory[i] = calculate_field_energy(field);
        trajectory.entropy_trajectory[i] = calculate_field_entropy(field);
        
        // 计算相干性（简化示例）
        double coherence = 0.0;
        if (i > 0) {
            double entropy_change = fabs(trajectory.entropy_trajectory[i] - 
                                        trajectory.entropy_trajectory[i-1]);
            coherence = exp(-entropy_change); // 熵增加越多，相干性下降越快
        }
        trajectory.coherence_trajectory[i] = coherence;
        
        // 检查稳定性
        if (config.stability_threshold > 0) {
            double energy_change = fabs(trajectory.energy_trajectory[i] - 
                                       trajectory.energy_trajectory[i-1]);
            if (energy_change < config.stability_threshold) {
                // 场已稳定，可以提前结束演化
                if (i < steps - 1) {
                    // 调整轨迹数组大小
                    trajectory.step_count = i + 1;
                    trajectory.time_points = realloc(trajectory.time_points, 
                                                   sizeof(double) * trajectory.step_count);
                    trajectory.energy_trajectory = realloc(trajectory.energy_trajectory, 
                                                         sizeof(double) * trajectory.step_count);
                    trajectory.entropy_trajectory = realloc(trajectory.entropy_trajectory, 
                                                          sizeof(double) * trajectory.step_count);
                    trajectory.coherence_trajectory = realloc(trajectory.coherence_trajectory, 
                                                            sizeof(double) * trajectory.step_count);
                    break;
                }
            }
        }
    }
    
    // 记录结束时间
    trajectory.end_timestamp = generate_timestamp();
    
    // 记录日志
    if (manager->config.enable_logging) {
        printf("量子场 %s 演化完成: 步数=%d, 时间步长=%.3f, 演化ID=%s\n", 
               field->id.readable_id, 
               trajectory.step_count, 
               time_step,
               trajectory.evolution_id);
    }
    
    return trajectory;
}

/**
 * 释放演化轨迹资源
 */
void free_evolution_trajectory(FieldEvolutionTrajectory* trajectory) {
    if (!trajectory) return;
    
    if (trajectory->time_points) free(trajectory->time_points);
    if (trajectory->energy_trajectory) free(trajectory->energy_trajectory);
    if (trajectory->entropy_trajectory) free(trajectory->entropy_trajectory);
    if (trajectory->coherence_trajectory) free(trajectory->coherence_trajectory);
    if (trajectory->evolution_id) free(trajectory->evolution_id);
    if (trajectory->start_timestamp) free(trajectory->start_timestamp);
    if (trajectory->end_timestamp) free(trajectory->end_timestamp);
    
    memset(trajectory, 0, sizeof(FieldEvolutionTrajectory));
}

/**
 * 分析量子场
 */
FieldAnalysisResult analyze_field(FieldManager* manager,
                                 FieldReference* reference,
                                 const char* analysis_type,
                                 void* custom_params) {
    FieldAnalysisResult result;
    memset(&result, 0, sizeof(FieldAnalysisResult));
    
    if (!manager || !reference || !analysis_type) {
        return result;
    }
    
    QField* field = get_field_from_reference(reference);
    if (!field) {
        return result;
    }
    
    // 设置分析类型
    result.analysis_type = strdup(analysis_type);
    result.analysis_timestamp = generate_timestamp();
    
    // 根据分析类型执行不同分析
    if (strcmp(analysis_type, "basic") == 0) {
        // 基本分析：计算能量、熵、节点数和边界尺寸
        result.metric_count = 6;
        result.metric_values = (double*)malloc(sizeof(double) * result.metric_count);
        result.metric_names = (char**)malloc(sizeof(char*) * result.metric_count);
        
        if (result.metric_values && result.metric_names) {
            result.metric_names[0] = strdup("能量");
            result.metric_values[0] = calculate_field_energy(field);
            
            result.metric_names[1] = strdup("熵");
            result.metric_values[1] = calculate_field_entropy(field);
            
            result.metric_names[2] = strdup("节点数");
            result.metric_values[2] = (double)field->node_count;
            
            result.metric_names[3] = strdup("X轴范围");
            result.metric_values[3] = field->boundary.x_max - field->boundary.x_min;
            
            result.metric_names[4] = strdup("Y轴范围");
            result.metric_values[4] = field->boundary.y_max - field->boundary.y_min;
            
            result.metric_names[5] = strdup("Z轴范围");
            result.metric_values[5] = field->boundary.z_max - field->boundary.z_min;
        }
    } 
    else if (strcmp(analysis_type, "distribution") == 0) {
        // 分布分析：分析场中节点的分布情况
        // 此处为简化示例，实际应根据需求实现更复杂分析
        result.metric_count = 3;
        result.metric_values = (double*)malloc(sizeof(double) * result.metric_count);
        result.metric_names = (char**)malloc(sizeof(char*) * result.metric_count);
        
        if (result.metric_values && result.metric_names) {
            // 计算节点密度
            double volume = (field->boundary.x_max - field->boundary.x_min) *
                          (field->boundary.y_max - field->boundary.y_min) *
                          (field->boundary.z_max - field->boundary.z_min);
            
            result.metric_names[0] = strdup("节点密度");
            result.metric_values[0] = field->node_count / volume;
            
            // 计算能量密度
            result.metric_names[1] = strdup("能量密度");
            result.metric_values[1] = calculate_field_energy(field) / volume;
            
            // 计算平均场强度
            double total_intensity = 0.0;
            for (int i = 0; i < field->node_count; i++) {
                total_intensity += field->nodes[i]->field_intensity;
            }
            
            result.metric_names[2] = strdup("平均场强度");
            result.metric_values[2] = total_intensity / field->node_count;
        }
    }
    else if (strcmp(analysis_type, "custom") == 0) {
        // 自定义分析，需要额外参数
        // 此处为示例，实际应根据custom_params实现
        if (custom_params) {
            // 假设custom_params包含自定义分析参数
            // 此处需要根据实际情况实现
        }
    }
    else {
        // 未知分析类型
        if (result.analysis_type) {
            free(result.analysis_type);
            result.analysis_type = NULL;
        }
        if (result.analysis_timestamp) {
            free(result.analysis_timestamp);
            result.analysis_timestamp = NULL;
        }
    }
    
    // 记录日志
    if (manager->config.enable_logging) {
        printf("分析量子场 %s: 类型=%s, 指标数=%d\n", 
               field->id.readable_id, 
               analysis_type,
               result.metric_count);
    }
    
    return result;
}

/**
 * 释放分析结果资源
 */
void free_analysis_result(FieldAnalysisResult* result) {
    if (!result) return;
    
    if (result->analysis_type) free(result->analysis_type);
    if (result->analysis_timestamp) free(result->analysis_timestamp);
    
    if (result->metric_values) free(result->metric_values);
    
    if (result->metric_names) {
        for (int i = 0; i < result->metric_count; i++) {
            if (result->metric_names[i]) free(result->metric_names[i]);
        }
        free(result->metric_names);
    }
    
    // 自定义分析结果需要根据实际情况释放
    
    memset(result, 0, sizeof(FieldAnalysisResult));
}

/**
 * 可视化量子场
 * 注意：此实现为简化版本，仅生成描述性数据
 */
FieldVisualizationResult visualize_field(FieldManager* manager,
                                        FieldReference* reference,
                                        FieldVisualizationOptions options) {
    FieldVisualizationResult result;
    memset(&result, 0, sizeof(FieldVisualizationResult));
    
    if (!manager || !reference) {
        return result;
    }
    
    QField* field = get_field_from_reference(reference);
    if (!field) {
        return result;
    }
    
    // 设置基本属性
    result.width = options.resolution_x > 0 ? options.resolution_x : 800;
    result.height = options.resolution_y > 0 ? options.resolution_y : 600;
    result.format = strdup(options.visualization_type ? options.visualization_type : "json");
    result.title = strdup("量子场可视化");
    result.description = strdup("量子场可视化结果");
    result.generation_timestamp = generate_timestamp();
    
    // 此处应该实现实际的可视化逻辑
    // 简化示例：生成一个描述性JSON
    const char* json_template = "{"
        "\"field_id\":\"%s\","
        "\"field_type\":%d,"
        "\"node_count\":%d,"
        "\"energy\":%.4f,"
        "\"entropy\":%.4f,"
        "\"visualization_type\":\"%s\","
        "\"timestamp\":\"%s\""
        "}";
    
    // 计算JSON长度
    size_t json_len = snprintf(NULL, 0, json_template,
                             field->id.readable_id,
                             field->type,
                             field->node_count,
                             calculate_field_energy(field),
                             calculate_field_entropy(field),
                             options.visualization_type ? options.visualization_type : "default",
                             result.generation_timestamp) + 1;
    
    // 分配内存并生成JSON
    char* json_data = (char*)malloc(json_len);
    if (json_data) {
        snprintf(json_data, json_len, json_template,
                field->id.readable_id,
                field->type,
                field->node_count,
                calculate_field_energy(field),
                calculate_field_entropy(field),
                options.visualization_type ? options.visualization_type : "default",
                result.generation_timestamp);
        
        result.visualization_data = json_data;
        result.data_size = json_len - 1; // 不包括null终止符
    }
    
    // 记录日志
    if (manager->config.enable_logging) {
        printf("可视化量子场 %s: 类型=%s, 尺寸=%dx%d\n", 
               field->id.readable_id, 
               result.format,
               result.width, result.height);
    }
    
    return result;
}

/**
 * 释放可视化结果资源
 */
void free_visualization_result(FieldVisualizationResult* result) {
    if (!result) return;
    
    if (result->visualization_data) free(result->visualization_data);
    if (result->format) free(result->format);
    if (result->title) free(result->title);
    if (result->description) free(result->description);
    if (result->generation_timestamp) free(result->generation_timestamp);
    
    memset(result, 0, sizeof(FieldVisualizationResult));
}

/**
 * 在两个量子场之间创建隧道
 */
FieldOperationResult create_field_tunnel(FieldManager* manager,
                                        FieldReference* reference1,
                                        double x1, double y1, double z1,
                                        FieldReference* reference2,
                                        double x2, double y2, double z2,
                                        double strength) {
    if (!manager || !reference1 || !reference2) {
        FieldOperationResult result = create_operation_result(0, "无效参数");
        result.error = FIELD_MANAGER_ERROR_INVALID_ARGUMENT;
        return result;
    }
    
    QField* field1 = get_field_from_reference(reference1);
    QField* field2 = get_field_from_reference(reference2);
    
    if (!field1 || !field2) {
        FieldOperationResult result = create_operation_result(0, "无效场引用");
        result.error = FIELD_MANAGER_ERROR_INVALID_REFERENCE;
        return result;
    }
    
    // 获取操作前能量和熵
    double energy_before1 = calculate_field_energy(field1);
    double entropy_before1 = calculate_field_entropy(field1);
    double energy_before2 = calculate_field_energy(field2);
    double entropy_before2 = calculate_field_entropy(field2);
    
    // 创建场坐标
    FieldCoordinate point_a = {x1, y1, z1, 0.0};
    FieldCoordinate point_b = {x2, y2, z2, 0.0};
    
    // 创建隧道
    create_field_tunnel(field1, point_a, field2, point_b, strength);
    
    // 创建操作结果
    FieldOperationResult result;
    result.success = 1;
    result.operation_description = strdup("创建量子场隧道");
    result.effect_magnitude = strength;
    
    // 使用第一个场的能量和熵变化作为结果
    result.energy_before = energy_before1;
    result.entropy_before = entropy_before1;
    result.energy_after = calculate_field_energy(field1);
    result.entropy_after = calculate_field_entropy(field1);
    result.timestamp = generate_timestamp();
    result.error = FIELD_MANAGER_ERROR_NONE;
    
    // 记录日志
    if (manager->config.enable_logging) {
        printf("[%s] 创建量子场隧道: 场1=%s, 场2=%s, 强度=%.2f\n", 
               result.timestamp, 
               field1->id.readable_id,
               field2->id.readable_id,
               strength);
    }
    
    return result;
}

/* -------------------- 内部辅助函数实现 -------------------- */

/**
 * 从引用获取量子场
 */
static QField* get_field_from_reference(FieldReference* reference) {
    if (!reference) return NULL;
    return (QField*)reference->field_ptr;
}

/**
 * 生成时间戳
 */
static char* generate_timestamp() {
    time_t now = time(NULL);
    char* timestamp = (char*)malloc(64);
    if (timestamp) {
        strftime(timestamp, 64, "%Y-%m-%d %H:%M:%S", localtime(&now));
    }
    return timestamp;
}

/**
 * 创建操作结果
 */
static FieldOperationResult create_operation_result(int success, const char* description) {
    FieldOperationResult result;
    memset(&result, 0, sizeof(FieldOperationResult));
    result.success = success;
    result.operation_description = description ? strdup(description) : NULL;
    result.timestamp = generate_timestamp();
    return result;
}

/**
 * 设置操作结果的能量和熵
 */
static void set_operation_result_energy_entropy(FieldOperationResult* result, QField* field) {
    // 简单计算场的能量和熵
    double total_energy = 0.0;
    double entropy = 0.0;
    
    for (int i = 0; i < field->node_count; i++) {
        total_energy += field->nodes[i].intensity;
        if (field->nodes[i].intensity > 0) {
            entropy -= field->nodes[i].intensity * log(field->nodes[i].intensity);
        }
    }
    
    result->energy = total_energy;
    result->entropy = entropy;
} 