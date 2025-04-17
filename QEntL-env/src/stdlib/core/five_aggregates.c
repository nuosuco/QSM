/**
 * 五蕴状态模块 - 实现佛教五蕴(色受想行识)的量子表示
 * 
 * 该模块将五蕴概念映射到量子状态，使其可以在量子计算环境中表示和操作
 * 
 * @作者：QEntL开发团队
 * @版本：1.0.0
 * @日期：2023-06-15
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "../../quantum_state.h"
#include "../../quantum_entanglement.h"
#include "math_library.h"

// 色蕴(物质形态)结构
typedef struct {
    quantum_state_t* state;         // 底层量子状态
    float solidity;                 // 固态程度
    float resistance;               // 阻力
    float density;                  // 密度
    float visibility;               // 可视性
    char* color_spectrum;           // 色彩谱
} form_aggregate_t;

// 受蕴(感受)结构
typedef struct {
    quantum_state_t* state;         // 底层量子状态
    float pleasure;                 // 愉悦程度
    float pain;                     // 痛苦程度
    float neutrality;               // 中性程度
    float intensity;                // 强度
    float duration;                 // 持续时间
} sensation_aggregate_t;

// 想蕴(认知)结构
typedef struct {
    quantum_state_t* state;         // 底层量子状态
    float clarity;                  // 清晰度
    float distortion;               // 扭曲程度
    float complexity;               // 复杂度
    float abstraction;              // 抽象度
    char* concept_association;      // 概念关联
} perception_aggregate_t;

// 行蕴(意志活动)结构
typedef struct {
    quantum_state_t* state;         // 底层量子状态
    float intention_strength;       // 意图强度
    float decision_certainty;       // 决策确定性
    float action_potency;           // 行动力
    float habit_tendency;           // 习惯倾向
    float karma_weight;             // 业力权重
} volition_aggregate_t;

// 识蕴(意识)结构
typedef struct {
    quantum_state_t* state;         // 底层量子状态
    float awareness_level;          // 觉知水平
    float cognitive_clarity;        // 认知清晰度
    float integration_degree;       // 整合度
    float continuity;               // 连续性
    float transcendence;            // 超越性
} consciousness_aggregate_t;

// 五蕴整体结构
typedef struct {
    form_aggregate_t* form;             // 色蕴
    sensation_aggregate_t* sensation;   // 受蕴
    perception_aggregate_t* perception; // 想蕴
    volition_aggregate_t* volition;     // 行蕴
    consciousness_aggregate_t* consciousness; // 识蕴
    quantum_entanglement_t* entanglement; // 五蕴间的量子纠缠
    float emptiness_measure;           // 空性度量
    float impermanence_rate;           // 无常变化率
    float suffering_potential;         // 苦的潜力
    float non_self_degree;             // 无我程度
} five_aggregates_t;

// 创建色蕴
form_aggregate_t* form_aggregate_create(int qubits) {
    form_aggregate_t* form = (form_aggregate_t*)malloc(sizeof(form_aggregate_t));
    if (!form) return NULL;
    
    form->state = quantum_state_create(qubits);
    form->solidity = 0.5f;
    form->resistance = 0.5f;
    form->density = 0.5f;
    form->visibility = 0.5f;
    form->color_spectrum = strdup("neutral");
    
    return form;
}

// 销毁色蕴
void form_aggregate_destroy(form_aggregate_t* form) {
    if (!form) return;
    
    quantum_state_destroy(form->state);
    free(form->color_spectrum);
    free(form);
}

// 创建受蕴
sensation_aggregate_t* sensation_aggregate_create(int qubits) {
    sensation_aggregate_t* sensation = (sensation_aggregate_t*)malloc(sizeof(sensation_aggregate_t));
    if (!sensation) return NULL;
    
    sensation->state = quantum_state_create(qubits);
    sensation->pleasure = 0.0f;
    sensation->pain = 0.0f;
    sensation->neutrality = 1.0f;
    sensation->intensity = 0.5f;
    sensation->duration = 0.0f;
    
    return sensation;
}

// 销毁受蕴
void sensation_aggregate_destroy(sensation_aggregate_t* sensation) {
    if (!sensation) return;
    
    quantum_state_destroy(sensation->state);
    free(sensation);
}

// 创建想蕴
perception_aggregate_t* perception_aggregate_create(int qubits) {
    perception_aggregate_t* perception = (perception_aggregate_t*)malloc(sizeof(perception_aggregate_t));
    if (!perception) return NULL;
    
    perception->state = quantum_state_create(qubits);
    perception->clarity = 0.5f;
    perception->distortion = 0.0f;
    perception->complexity = 0.5f;
    perception->abstraction = 0.5f;
    perception->concept_association = strdup("undefined");
    
    return perception;
}

// 销毁想蕴
void perception_aggregate_destroy(perception_aggregate_t* perception) {
    if (!perception) return;
    
    quantum_state_destroy(perception->state);
    free(perception->concept_association);
    free(perception);
}

// 创建行蕴
volition_aggregate_t* volition_aggregate_create(int qubits) {
    volition_aggregate_t* volition = (volition_aggregate_t*)malloc(sizeof(volition_aggregate_t));
    if (!volition) return NULL;
    
    volition->state = quantum_state_create(qubits);
    volition->intention_strength = 0.5f;
    volition->decision_certainty = 0.5f;
    volition->action_potency = 0.5f;
    volition->habit_tendency = 0.5f;
    volition->karma_weight = 0.0f;
    
    return volition;
}

// 销毁行蕴
void volition_aggregate_destroy(volition_aggregate_t* volition) {
    if (!volition) return;
    
    quantum_state_destroy(volition->state);
    free(volition);
}

// 创建识蕴
consciousness_aggregate_t* consciousness_aggregate_create(int qubits) {
    consciousness_aggregate_t* consciousness = (consciousness_aggregate_t*)malloc(sizeof(consciousness_aggregate_t));
    if (!consciousness) return NULL;
    
    consciousness->state = quantum_state_create(qubits);
    consciousness->awareness_level = 0.5f;
    consciousness->cognitive_clarity = 0.5f;
    consciousness->integration_degree = 0.5f;
    consciousness->continuity = 1.0f;
    consciousness->transcendence = 0.0f;
    
    return consciousness;
}

// 销毁识蕴
void consciousness_aggregate_destroy(consciousness_aggregate_t* consciousness) {
    if (!consciousness) return;
    
    quantum_state_destroy(consciousness->state);
    free(consciousness);
}

// 创建五蕴系统
five_aggregates_t* five_aggregates_create(int qubits_per_aggregate) {
    five_aggregates_t* aggregates = (five_aggregates_t*)malloc(sizeof(five_aggregates_t));
    if (!aggregates) return NULL;
    
    aggregates->form = form_aggregate_create(qubits_per_aggregate);
    aggregates->sensation = sensation_aggregate_create(qubits_per_aggregate);
    aggregates->perception = perception_aggregate_create(qubits_per_aggregate);
    aggregates->volition = volition_aggregate_create(qubits_per_aggregate);
    aggregates->consciousness = consciousness_aggregate_create(qubits_per_aggregate);
    
    // 创建五蕴间的量子纠缠
    aggregates->entanglement = quantum_entangle_multiple(5, 
        aggregates->form->state,
        aggregates->sensation->state,
        aggregates->perception->state,
        aggregates->volition->state,
        aggregates->consciousness->state
    );
    
    // 初始化四法印
    aggregates->emptiness_measure = 0.0f;
    aggregates->impermanence_rate = 0.0f;
    aggregates->suffering_potential = 0.0f;
    aggregates->non_self_degree = 0.0f;
    
    return aggregates;
}

// 销毁五蕴系统
void five_aggregates_destroy(five_aggregates_t* aggregates) {
    if (!aggregates) return;
    
    form_aggregate_destroy(aggregates->form);
    sensation_aggregate_destroy(aggregates->sensation);
    perception_aggregate_destroy(aggregates->perception);
    volition_aggregate_destroy(aggregates->volition);
    consciousness_aggregate_destroy(aggregates->consciousness);
    quantum_entanglement_destroy(aggregates->entanglement);
    free(aggregates);
}

// 更新五蕴空性度量
void five_aggregates_update_emptiness(five_aggregates_t* aggregates) {
    if (!aggregates) return;
    
    // 基于香农熵计算空性度量
    float form_entropy = quantum_state_entropy(aggregates->form->state);
    float sensation_entropy = quantum_state_entropy(aggregates->sensation->state);
    float perception_entropy = quantum_state_entropy(aggregates->perception->state);
    float volition_entropy = quantum_state_entropy(aggregates->volition->state);
    float consciousness_entropy = quantum_state_entropy(aggregates->consciousness->state);
    
    // 空性与熵和纠缠度相关
    float entanglement_measure = quantum_entanglement_measure(aggregates->entanglement);
    
    // 计算空性度量
    aggregates->emptiness_measure = (form_entropy + sensation_entropy + 
                                   perception_entropy + volition_entropy + 
                                   consciousness_entropy) / 5.0f * entanglement_measure;
}

// 模拟五蕴的无常变化
void five_aggregates_evolve(five_aggregates_t* aggregates, float time_step) {
    if (!aggregates) return;
    
    // 应用无常演化算子到各个蕴
    quantum_state_evolve(aggregates->form->state, time_step);
    quantum_state_evolve(aggregates->sensation->state, time_step);
    quantum_state_evolve(aggregates->perception->state, time_step);
    quantum_state_evolve(aggregates->volition->state, time_step);
    quantum_state_evolve(aggregates->consciousness->state, time_step);
    
    // 更新无常变化率
    aggregates->impermanence_rate = calc_state_flux(
        5,
        aggregates->form->state,
        aggregates->sensation->state,
        aggregates->perception->state,
        aggregates->volition->state,
        aggregates->consciousness->state
    );
    
    // 更新苦的潜力
    // 苦=执着度*无常变化率
    float attachment = (aggregates->sensation->pleasure + aggregates->volition->intention_strength) / 2.0f;
    aggregates->suffering_potential = attachment * aggregates->impermanence_rate;
    
    // 更新无我程度
    aggregates->non_self_degree = 
        (aggregates->emptiness_measure + aggregates->impermanence_rate) / 2.0f;
}

// 获取五蕴的整体量子态
quantum_state_t* five_aggregates_get_combined_state(five_aggregates_t* aggregates) {
    if (!aggregates) return NULL;
    
    return quantum_entanglement_get_combined_state(aggregates->entanglement);
}

// 测量五蕴系统的状态
int five_aggregates_measure(five_aggregates_t* aggregates) {
    if (!aggregates) return -1;
    
    // 测量整体状态并返回结果
    quantum_state_t* combined = five_aggregates_get_combined_state(aggregates);
    int result = quantum_state_measure(combined);
    
    // 更新各蕴的状态以反映测量结果
    quantum_entanglement_update_after_measurement(aggregates->entanglement, result);
    
    return result;
}

// 打印五蕴状态
void five_aggregates_print(five_aggregates_t* aggregates) {
    if (!aggregates) return;
    
    printf("===== 五蕴状态 =====\n");
    
    printf("色蕴 (Form):\n");
    printf("  - 固态程度: %.2f\n", aggregates->form->solidity);
    printf("  - 阻力: %.2f\n", aggregates->form->resistance);
    printf("  - 密度: %.2f\n", aggregates->form->density);
    printf("  - 可视性: %.2f\n", aggregates->form->visibility);
    printf("  - 色彩谱: %s\n\n", aggregates->form->color_spectrum);
    
    printf("受蕴 (Sensation):\n");
    printf("  - 愉悦程度: %.2f\n", aggregates->sensation->pleasure);
    printf("  - 痛苦程度: %.2f\n", aggregates->sensation->pain);
    printf("  - 中性程度: %.2f\n", aggregates->sensation->neutrality);
    printf("  - 强度: %.2f\n", aggregates->sensation->intensity);
    printf("  - 持续时间: %.2f\n\n", aggregates->sensation->duration);
    
    printf("想蕴 (Perception):\n");
    printf("  - 清晰度: %.2f\n", aggregates->perception->clarity);
    printf("  - 扭曲程度: %.2f\n", aggregates->perception->distortion);
    printf("  - 复杂度: %.2f\n", aggregates->perception->complexity);
    printf("  - 抽象度: %.2f\n", aggregates->perception->abstraction);
    printf("  - 概念关联: %s\n\n", aggregates->perception->concept_association);
    
    printf("行蕴 (Volition):\n");
    printf("  - 意图强度: %.2f\n", aggregates->volition->intention_strength);
    printf("  - 决策确定性: %.2f\n", aggregates->volition->decision_certainty);
    printf("  - 行动力: %.2f\n", aggregates->volition->action_potency);
    printf("  - 习惯倾向: %.2f\n", aggregates->volition->habit_tendency);
    printf("  - 业力权重: %.2f\n\n", aggregates->volition->karma_weight);
    
    printf("识蕴 (Consciousness):\n");
    printf("  - 觉知水平: %.2f\n", aggregates->consciousness->awareness_level);
    printf("  - 认知清晰度: %.2f\n", aggregates->consciousness->cognitive_clarity);
    printf("  - 整合度: %.2f\n", aggregates->consciousness->integration_degree);
    printf("  - 连续性: %.2f\n", aggregates->consciousness->continuity);
    printf("  - 超越性: %.2f\n\n", aggregates->consciousness->transcendence);
    
    printf("整体特性:\n");
    printf("  - 空性度量: %.2f\n", aggregates->emptiness_measure);
    printf("  - 无常变化率: %.2f\n", aggregates->impermanence_rate);
    printf("  - 苦的潜力: %.2f\n", aggregates->suffering_potential);
    printf("  - 无我程度: %.2f\n", aggregates->non_self_degree);
    printf("  - 纠缠度: %.2f\n", quantum_entanglement_measure(aggregates->entanglement));
    printf("===================\n");
}

// 用于测试的辅助函数，创建一个示例五蕴配置
five_aggregates_t* five_aggregates_create_example() {
    five_aggregates_t* example = five_aggregates_create(3); // 每个蕴使用3个量子比特
    
    // 设置各蕴的特性
    example->form->solidity = 0.8f;
    example->form->visibility = 0.9f;
    free(example->form->color_spectrum);
    example->form->color_spectrum = strdup("vibrant");
    
    example->sensation->pleasure = 0.7f;
    example->sensation->pain = 0.1f;
    example->sensation->neutrality = 0.2f;
    
    example->perception->clarity = 0.85f;
    example->perception->complexity = 0.6f;
    free(example->perception->concept_association);
    example->perception->concept_association = strdup("nature");
    
    example->volition->intention_strength = 0.75f;
    example->volition->action_potency = 0.8f;
    
    example->consciousness->awareness_level = 0.9f;
    example->consciousness->transcendence = 0.4f;
    
    // 更新整体特性
    five_aggregates_update_emptiness(example);
    five_aggregates_evolve(example, 0.1f);
    
    return example;
}

// 计算五蕴间的相互作用
void five_aggregates_interact(five_aggregates_t* aggregates) {
    if (!aggregates) return;
    
    // 色蕴影响受蕴
    aggregates->sensation->intensity = 
        (aggregates->form->density + aggregates->form->solidity) / 2.0f;
    
    // 受蕴影响想蕴
    aggregates->perception->clarity = 
        aggregates->sensation->intensity * (1.0f - aggregates->sensation->pain);
    
    // 想蕴影响行蕴
    aggregates->volition->decision_certainty = 
        aggregates->perception->clarity * (1.0f - aggregates->perception->distortion);
    
    // 行蕴影响识蕴
    aggregates->consciousness->cognitive_clarity = 
        aggregates->volition->decision_certainty * aggregates->volition->intention_strength;
    
    // 识蕴影响色蕴
    aggregates->form->visibility = 
        aggregates->consciousness->awareness_level * aggregates->consciousness->cognitive_clarity;
    
    // 更新纠缠
    quantum_entanglement_update_correlation(aggregates->entanglement);
    
    // 更新四法印
    five_aggregates_update_emptiness(aggregates);
} 