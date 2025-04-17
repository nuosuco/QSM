/**
 * QEntL任务平衡器与资源自适应引擎集成接口
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月25日
 * 
 * 定义任务平衡器与资源自适应引擎之间的集成接口，
 * 实现资源调度与任务执行的协同优化。
 */

#ifndef QENTL_TASK_BALANCER_INTEGRATION_H
#define QENTL_TASK_BALANCER_INTEGRATION_H

#include <stdbool.h>
#include "resource_adaptive_engine.h"
#include "task_balancer.h"

/**
 * 初始化任务平衡器与资源自适应引擎的集成
 * @param engine 资源自适应引擎实例
 * @param balancer 任务平衡器实例
 * @return 是否成功初始化
 */
bool initialize_task_balancer_integration(
    ResourceAdaptiveEngine* engine,
    TaskBalancer* balancer);

/**
 * 关闭任务平衡器与资源自适应引擎的集成
 * @param engine 资源自适应引擎实例
 * @param balancer 任务平衡器实例
 */
void shutdown_task_balancer_integration(
    ResourceAdaptiveEngine* engine,
    TaskBalancer* balancer);

/**
 * 提交优化任务 - 提交任务并使用自适应引擎进行资源优化
 * @param engine 资源自适应引擎实例
 * @param balancer 任务平衡器实例
 * @param circuit 量子电路
 * @param priority 任务优先级
 * @param task_name 任务名称
 * @param task_id 输出任务ID
 * @return 是否成功提交
 */
bool submit_optimized_task(
    ResourceAdaptiveEngine* engine,
    TaskBalancer* balancer,
    const QuantumCircuit* circuit,
    TaskPriority priority,
    const char* task_name,
    char* task_id);

/**
 * 引擎资源变化时调整任务平衡
 * @param engine 资源自适应引擎实例
 * @param balancer 任务平衡器实例
 * @return 是否成功调整
 */
bool adapt_task_balance_to_resources(
    ResourceAdaptiveEngine* engine,
    TaskBalancer* balancer);

/**
 * 任务执行失败时进行资源自适应重试
 * @param engine 资源自适应引擎实例
 * @param balancer 任务平衡器实例
 * @param task_id 失败的任务ID
 * @param error_code 错误代码
 * @return 是否成功重试
 */
bool retry_task_with_adaptive_resources(
    ResourceAdaptiveEngine* engine,
    TaskBalancer* balancer,
    const char* task_id,
    int error_code);

/**
 * 为即将执行的任务预分配资源
 * @param engine 资源自适应引擎实例
 * @param balancer 任务平衡器实例
 * @param task_id 任务ID
 * @return 是否成功预分配
 */
bool preallocate_resources_for_task(
    ResourceAdaptiveEngine* engine,
    TaskBalancer* balancer,
    const char* task_id);

/**
 * 任务完成后释放并重新平衡资源
 * @param engine 资源自适应引擎实例
 * @param balancer 任务平衡器实例
 * @param task_id 完成的任务ID
 * @return 是否成功释放和重新平衡
 */
bool release_and_rebalance_resources(
    ResourceAdaptiveEngine* engine,
    TaskBalancer* balancer,
    const char* task_id);

/**
 * 生成资源使用与任务执行综合报告
 * @param engine 资源自适应引擎实例
 * @param balancer 任务平衡器实例
 * @param filename 报告文件名
 * @return 是否成功生成
 */
bool generate_integrated_report(
    ResourceAdaptiveEngine* engine,
    TaskBalancer* balancer,
    const char* filename);

/**
 * 预测任务资源需求
 * @param engine 资源自适应引擎实例
 * @param circuit 量子电路
 * @param required_qubits 输出所需量子比特数
 * @param required_memory_bytes 输出所需内存
 * @param estimated_runtime_ms 输出估计运行时间
 * @return 是否成功预测
 */
bool predict_task_resource_requirements(
    ResourceAdaptiveEngine* engine,
    const QuantumCircuit* circuit,
    int* required_qubits,
    uint64_t* required_memory_bytes,
    int* estimated_runtime_ms);

#endif /* QENTL_TASK_BALANCER_INTEGRATION_H */ 