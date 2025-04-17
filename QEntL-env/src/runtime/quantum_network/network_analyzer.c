/**
 * @file network_analyzer.c
 * @brief 量子网络分析器实现
 * @version 1.0
 * @date 2024-05-20
 * 
 * 本模块提供量子网络分析功能，用于评估网络健康状态、拓扑结构和性能指标
 */

#include "network_analyzer.h"
#include "node_manager.h"
#include "../common/logger.h"
#include "../common/memory_manager.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

// 内部函数声明
static bool validate_analyzer_parameters(NetworkAnalyzerConfig* config);
static void log_analyzer_action(NetworkAnalyzer* analyzer, const char* action, const char* details);
static int** calculate_shortest_paths(NetworkAnalyzer* analyzer, int* node_count);
static int* detect_clusters_dfs(NetworkAnalyzer* analyzer, int node_count);
static void dfs_visit(NetworkAnalyzer* analyzer, int node_index, int* visited, int* cluster_ids, int cluster_id);

/**
 * @brief 初始化网络分析器
 * 
 * @param node_manager 节点管理器指针
 * @param config 分析器配置
 * @return NetworkAnalyzer* 初始化的分析器，失败返回NULL
 */
NetworkAnalyzer* initialize_network_analyzer(NodeManager* node_manager, NetworkAnalyzerConfig* config) {
    if (!node_manager || !config) {
        qentl_log_error("网络分析器初始化失败：参数无效");
        return NULL;
    }
    
    if (!validate_analyzer_parameters(config)) {
        qentl_log_error("网络分析器初始化失败：配置参数无效");
        return NULL;
    }
    
    NetworkAnalyzer* analyzer = (NetworkAnalyzer*)allocate_memory(sizeof(NetworkAnalyzer));
    if (!analyzer) {
        qentl_log_error("网络分析器初始化失败：内存分配失败");
        return NULL;
    }
    
    // 初始化分析器属性
    analyzer->node_manager = node_manager;
    analyzer->config = *config;
    analyzer->last_analysis_time = 0;
    analyzer->analysis_count = 0;
    
    // 初始化健康指标
    analyzer->health_metrics.overall_health = 0.0;
    analyzer->health_metrics.active_node_ratio = 0.0;
    analyzer->health_metrics.connectivity = 0.0;
    analyzer->health_metrics.stability = 0.0;
    analyzer->health_metrics.entanglement_level = 0.0;
    
    // 如果配置中启用了日志，打开日志文件
    if (config->enable_logging) {
        analyzer->log_enabled = true;
        log_analyzer_action(analyzer, "初始化", "网络分析器已成功初始化");
    } else {
        analyzer->log_enabled = false;
    }
    
    qentl_log_info("网络分析器初始化成功");
    return analyzer;
}

/**
 * @brief 获取默认网络分析器配置
 * 
 * @return NetworkAnalyzerConfig 默认配置
 */
NetworkAnalyzerConfig get_default_network_analyzer_config() {
    NetworkAnalyzerConfig config;
    
    config.analysis_interval_ms = 5000;  // 5秒
    config.health_threshold_warning = 0.6;
    config.health_threshold_critical = 0.4;
    config.enable_logging = true;
    config.enable_auto_recovery = true;
    config.topology_analysis_depth = 3;
    
    return config;
}

/**
 * @brief 分析网络状态
 * 
 * @param analyzer 网络分析器指针
 * @return NetworkAnalysisResult 分析结果
 */
NetworkAnalysisResult analyze_network(NetworkAnalyzer* analyzer) {
    NetworkAnalysisResult result = {0};
    
    if (!analyzer || !analyzer->node_manager) {
        result.success = false;
        result.error_code = ANALYZER_ERROR_INVALID_PARAMS;
        strcpy(result.error_message, "分析器或节点管理器无效");
        return result;
    }
    
    log_analyzer_action(analyzer, "分析开始", "开始执行网络分析");
    
    // 更新分析计数和时间
    analyzer->analysis_count++;
    analyzer->last_analysis_time = get_current_time_ms();
    
    // 分析网络拓扑
    result.topology.total_nodes = get_total_node_count(analyzer->node_manager);
    result.topology.active_nodes = get_active_node_count(analyzer->node_manager);
    result.topology.inactive_nodes = get_inactive_node_count(analyzer->node_manager);
    result.topology.error_nodes = get_error_node_count(analyzer->node_manager);
    
    // 计算活跃节点比例
    if (result.topology.total_nodes > 0) {
        analyzer->health_metrics.active_node_ratio = 
            (double)result.topology.active_nodes / result.topology.total_nodes;
    } else {
        analyzer->health_metrics.active_node_ratio = 0.0;
    }
    
    // 计算连接度
    result.topology.total_connections = get_total_connection_count(analyzer->node_manager);
    if (result.topology.active_nodes > 1) {
        analyzer->health_metrics.connectivity = 
            (double)result.topology.total_connections / 
            ((result.topology.active_nodes * (result.topology.active_nodes - 1)) / 2.0);
    } else {
        analyzer->health_metrics.connectivity = 0.0;
    }
    
    // 计算平均稳定性
    analyzer->health_metrics.stability = calculate_average_stability(analyzer->node_manager);
    
    // 计算纠缠水平
    analyzer->health_metrics.entanglement_level = 
        calculate_network_entanglement(analyzer->node_manager);
    
    // 计算整体健康度 (加权平均)
    analyzer->health_metrics.overall_health = 
        (analyzer->health_metrics.active_node_ratio * 0.3) +
        (analyzer->health_metrics.connectivity * 0.25) +
        (analyzer->health_metrics.stability * 0.25) +
        (analyzer->health_metrics.entanglement_level * 0.2);
    
    // 记录分析结果
    result.health_metrics = analyzer->health_metrics;
    result.success = true;
    
    // 根据健康状态确定警告级别
    if (analyzer->health_metrics.overall_health < analyzer->config.health_threshold_critical) {
        result.health_status = NETWORK_HEALTH_CRITICAL;
    } else if (analyzer->health_metrics.overall_health < analyzer->config.health_threshold_warning) {
        result.health_status = NETWORK_HEALTH_WARNING;
    } else {
        result.health_status = NETWORK_HEALTH_GOOD;
    }
    
    // 尝试自动恢复 (如果启用且健康状态为警告或危急)
    if (analyzer->config.enable_auto_recovery && 
        result.health_status != NETWORK_HEALTH_GOOD) {
        log_analyzer_action(analyzer, "自动恢复", "检测到网络健康状况不佳，尝试自动恢复");
        attempt_network_recovery(analyzer);
    }
    
    log_analyzer_action(analyzer, "分析完成", "网络分析已完成");
    return result;
}

/**
 * @brief 获取网络健康指标
 * 
 * @param analyzer 网络分析器指针
 * @return NetworkHealthMetrics 健康指标
 */
NetworkHealthMetrics get_network_health_metrics(NetworkAnalyzer* analyzer) {
    NetworkHealthMetrics empty_metrics = {0};
    
    if (!analyzer) {
        qentl_log_error("获取网络健康指标失败：分析器无效");
        return empty_metrics;
    }
    
    return analyzer->health_metrics;
}

/**
 * @brief 关闭网络分析器
 * 
 * @param analyzer 网络分析器指针
 * @return bool 成功返回true，失败返回false
 */
bool shutdown_network_analyzer(NetworkAnalyzer* analyzer) {
    if (!analyzer) {
        qentl_log_error("关闭网络分析器失败：分析器无效");
        return false;
    }
    
    log_analyzer_action(analyzer, "关闭", "网络分析器正在关闭");
    
    // 清理资源
    free_memory(analyzer);
    
    qentl_log_info("网络分析器已成功关闭");
    return true;
}

/**
 * @brief 计算网络密度
 * 
 * @param analyzer 网络分析器指针
 * @return double 网络密度(0-1)，失败时返回负值
 */
double calculate_network_density(NetworkAnalyzer* analyzer) {
    if (!analyzer || !analyzer->node_manager) {
        qentl_log_error("计算网络密度失败：参数无效");
        return -1.0;
    }
    
    log_analyzer_action(analyzer, "计算密度", "开始计算网络密度");
    
    int total_nodes = get_total_node_count(analyzer->node_manager);
    int active_nodes = get_active_node_count(analyzer->node_manager);
    int total_connections = get_total_connection_count(analyzer->node_manager);
    
    // 检查节点数量
    if (active_nodes <= 1) {
        qentl_log_warning("计算网络密度：活跃节点数量不足");
        return 0.0;
    }
    
    // 计算最大可能连接数
    int max_possible_connections = (active_nodes * (active_nodes - 1)) / 2;
    
    // 计算密度
    double density = (double)total_connections / max_possible_connections;
    
    log_analyzer_action(analyzer, "计算密度完成", "网络密度计算完毕");
    return density;
}

/**
 * @brief 计算平均路径长度
 * 
 * @param analyzer 网络分析器指针
 * @return double 平均路径长度，失败时返回负值
 */
double calculate_average_path_length(NetworkAnalyzer* analyzer) {
    if (!analyzer || !analyzer->node_manager) {
        qentl_log_error("计算平均路径长度失败：参数无效");
        return -1.0;
    }
    
    log_analyzer_action(analyzer, "计算路径", "开始计算平均路径长度");
    
    // 获取节点数量
    int node_count = 0;
    int** shortest_paths = calculate_shortest_paths(analyzer, &node_count);
    
    if (!shortest_paths || node_count <= 1) {
        if (shortest_paths) {
            // 清理已分配的内存
            for (int i = 0; i < node_count; i++) {
                free(shortest_paths[i]);
            }
            free(shortest_paths);
        }
        qentl_log_warning("计算平均路径长度：节点数量不足或计算失败");
        return node_count <= 1 ? 0.0 : -1.0;
    }
    
    // 计算所有有效路径的总和
    int valid_path_count = 0;
    int total_path_length = 0;
    
    for (int i = 0; i < node_count; i++) {
        for (int j = i + 1; j < node_count; j++) {
            // 如果路径存在（不是无穷大），则累加
            if (shortest_paths[i][j] != INT_MAX && shortest_paths[i][j] > 0) {
                total_path_length += shortest_paths[i][j];
                valid_path_count++;
            }
        }
    }
    
    // 清理内存
    for (int i = 0; i < node_count; i++) {
        free(shortest_paths[i]);
    }
    free(shortest_paths);
    
    // 检查是否有有效路径
    if (valid_path_count == 0) {
        qentl_log_warning("计算平均路径长度：没有有效路径");
        return -1.0;
    }
    
    // 计算平均路径长度
    double average_path_length = (double)total_path_length / valid_path_count;
    
    log_analyzer_action(analyzer, "计算路径完成", "平均路径长度计算完毕");
    return average_path_length;
}

/**
 * @brief 计算最短路径矩阵（Floyd-Warshall算法）
 * 
 * @param analyzer 网络分析器指针
 * @param node_count 输出参数，返回网络中的节点数量
 * @return int** 最短路径矩阵，失败时返回NULL
 */
static int** calculate_shortest_paths(NetworkAnalyzer* analyzer, int* node_count) {
    if (!analyzer || !analyzer->node_manager || !node_count) {
        return NULL;
    }
    
    // 获取节点数量
    *node_count = get_active_node_count(analyzer->node_manager);
    if (*node_count <= 0) {
        return NULL;
    }
    
    // 分配距离矩阵内存
    int** distances = (int**)malloc(sizeof(int*) * (*node_count));
    if (!distances) {
        return NULL;
    }
    
    for (int i = 0; i < *node_count; i++) {
        distances[i] = (int*)malloc(sizeof(int) * (*node_count));
        if (!distances[i]) {
            // 清理已分配的内存
            for (int j = 0; j < i; j++) {
                free(distances[j]);
            }
            free(distances);
            return NULL;
        }
        
        // 初始化距离
        for (int j = 0; j < *node_count; j++) {
            if (i == j) {
                distances[i][j] = 0;  // 自己到自己的距离为0
            } else {
                distances[i][j] = INT_MAX;  // 初始化为无穷大
            }
        }
    }
    
    // 填充直接连接的距离
    // 注意：这里的实现简化了，实际实现需要从node_manager获取节点和连接信息
    // 通过node_manager的API获取节点和连接信息，并填充distances矩阵
    
    // Floyd-Warshall算法计算最短路径
    for (int k = 0; k < *node_count; k++) {
        for (int i = 0; i < *node_count; i++) {
            for (int j = 0; j < *node_count; j++) {
                if (distances[i][k] != INT_MAX && distances[k][j] != INT_MAX) {
                    int potential_distance = distances[i][k] + distances[k][j];
                    if (potential_distance < distances[i][j]) {
                        distances[i][j] = potential_distance;
                    }
                }
            }
        }
    }
    
    return distances;
}

/**
 * @brief 检测网络集群
 * 
 * @param analyzer 网络分析器指针
 * @param algorithm 聚类算法
 * @return int 集群数量，失败时返回负值
 */
int detect_network_clusters(NetworkAnalyzer* analyzer, ClusteringAlgorithm algorithm) {
    if (!analyzer || !analyzer->node_manager) {
        qentl_log_error("检测网络集群失败：参数无效");
        return -1;
    }
    
    log_analyzer_action(analyzer, "检测集群", "开始检测网络集群");
    
    int node_count = get_active_node_count(analyzer->node_manager);
    if (node_count <= 0) {
        qentl_log_warning("检测网络集群：没有活跃节点");
        return 0;
    }
    
    int* cluster_ids = NULL;
    int cluster_count = 0;
    
    // 根据指定的算法选择不同的聚类方法
    switch (algorithm) {
        case CLUSTERING_DFS:
            cluster_ids = detect_clusters_dfs(analyzer, node_count);
            break;
            
        case CLUSTERING_COMMUNITY:
            // 社区检测算法（未实现）
            qentl_log_error("社区检测算法尚未实现");
            return -1;
            
        case CLUSTERING_SPECTRAL:
            // 谱聚类算法（未实现）
            qentl_log_error("谱聚类算法尚未实现");
            return -1;
            
        case CLUSTERING_HIERARCHICAL:
            // 层次聚类算法（未实现）
            qentl_log_error("层次聚类算法尚未实现");
            return -1;
            
        default:
            qentl_log_error("未知的聚类算法");
            return -1;
    }
    
    if (!cluster_ids) {
        qentl_log_error("聚类算法执行失败");
        return -1;
    }
    
    // 计算集群数量
    int max_cluster_id = 0;
    for (int i = 0; i < node_count; i++) {
        if (cluster_ids[i] > max_cluster_id) {
            max_cluster_id = cluster_ids[i];
        }
    }
    cluster_count = max_cluster_id + 1;
    
    // 统计每个集群的大小
    char details[256];
    sprintf(details, "检测到%d个集群", cluster_count);
    log_analyzer_action(analyzer, "检测集群完成", details);
    
    // 清理内存
    free(cluster_ids);
    
    return cluster_count;
}

/**
 * @brief 使用DFS算法检测集群
 * 
 * @param analyzer 网络分析器指针
 * @param node_count 节点数量
 * @return int* 集群ID数组，每个节点对应的集群ID，失败时返回NULL
 */
static int* detect_clusters_dfs(NetworkAnalyzer* analyzer, int node_count) {
    if (!analyzer || node_count <= 0) {
        return NULL;
    }
    
    // 分配集群ID数组
    int* cluster_ids = (int*)malloc(sizeof(int) * node_count);
    if (!cluster_ids) {
        return NULL;
    }
    
    // 初始化为-1，表示尚未访问
    for (int i = 0; i < node_count; i++) {
        cluster_ids[i] = -1;
    }
    
    // 分配访问标记数组
    int* visited = (int*)malloc(sizeof(int) * node_count);
    if (!visited) {
        free(cluster_ids);
        return NULL;
    }
    
    // 初始化访问标记
    for (int i = 0; i < node_count; i++) {
        visited[i] = 0;
    }
    
    // 执行DFS
    int cluster_id = 0;
    for (int i = 0; i < node_count; i++) {
        if (!visited[i]) {
            dfs_visit(analyzer, i, visited, cluster_ids, cluster_id);
            cluster_id++;
        }
    }
    
    // 清理访问标记数组
    free(visited);
    
    return cluster_ids;
}

/**
 * @brief DFS访问节点及其邻居
 * 
 * @param analyzer 网络分析器指针
 * @param node_index 当前节点索引
 * @param visited 访问标记数组
 * @param cluster_ids 集群ID数组
 * @param cluster_id 当前集群ID
 */
static void dfs_visit(NetworkAnalyzer* analyzer, int node_index, int* visited, int* cluster_ids, int cluster_id) {
    visited[node_index] = 1;
    cluster_ids[node_index] = cluster_id;
    
    // 遍历邻居节点
    // 注意：这里的实现简化了，实际实现需要从node_manager获取邻居节点信息
    // 通过node_manager的API获取节点的邻居信息，并递归调用dfs_visit
}

/**
 * @brief 计算节点中心性
 * 
 * @param analyzer 网络分析器指针
 * @param node_id 节点ID
 * @param centrality_type 中心性类型
 * @return double 中心性值，失败时返回负值
 */
double calculate_node_centrality(NetworkAnalyzer* analyzer, unsigned int node_id, CentralityType centrality_type) {
    if (!analyzer || !analyzer->node_manager) {
        qentl_log_error("计算节点中心性失败：参数无效");
        return -1.0;
    }
    
    // 检查节点是否存在
    QuantumNetworkNode* node = get_node(analyzer->node_manager, node_id);
    if (!node) {
        qentl_log_error("计算节点中心性失败：节点不存在");
        return -1.0;
    }
    
    char details[256];
    sprintf(details, "开始计算节点%u的中心性", node_id);
    log_analyzer_action(analyzer, "计算中心性", details);
    
    double centrality = 0.0;
    
    // 根据中心性类型选择不同的计算方法
    switch (centrality_type) {
        case CENTRALITY_DEGREE: {
            // 度中心性是节点的连接数
            int connection_count = node->connection_count;
            int active_node_count = get_active_node_count(analyzer->node_manager);
            
            // 归一化处理，除以最大可能的连接数
            if (active_node_count > 1) {
                centrality = (double)connection_count / (active_node_count - 1);
            } else {
                centrality = 0.0;
            }
            break;
        }
        
        case CENTRALITY_CLOSENESS: {
            // 接近中心性需要计算节点到所有其他节点的最短路径
            // 实现略，需要使用calculate_shortest_paths的结果
            qentl_log_error("接近中心性计算尚未实现");
            return -1.0;
        }
        
        case CENTRALITY_BETWEENNESS: {
            // 中介中心性需要计算通过该节点的最短路径数量
            // 实现略，需要使用calculate_shortest_paths的结果
            qentl_log_error("中介中心性计算尚未实现");
            return -1.0;
        }
        
        case CENTRALITY_EIGENVECTOR: {
            // 特征向量中心性需要计算邻接矩阵的主特征向量
            // 实现略，需要复杂的矩阵运算
            qentl_log_error("特征向量中心性计算尚未实现");
            return -1.0;
        }
        
        default:
            qentl_log_error("未知的中心性类型");
            return -1.0;
    }
    
    sprintf(details, "节点%u的%s中心性为%.4f", node_id, 
           centrality_type == CENTRALITY_DEGREE ? "度" : 
           centrality_type == CENTRALITY_CLOSENESS ? "接近" : 
           centrality_type == CENTRALITY_BETWEENNESS ? "中介" : "特征向量", 
           centrality);
    log_analyzer_action(analyzer, "计算中心性完成", details);
    
    return centrality;
}

/**
 * @brief 尝试恢复网络
 * 
 * @param analyzer 网络分析器指针
 * @return bool 成功返回true，失败返回false
 */
bool attempt_network_recovery(NetworkAnalyzer* analyzer) {
    if (!analyzer || !analyzer->node_manager) {
        qentl_log_error("网络恢复失败：参数无效");
        return false;
    }
    
    log_analyzer_action(analyzer, "恢复", "开始执行网络恢复操作");
    
    // 尝试重启错误节点
    int restarted_count = restart_error_nodes(analyzer->node_manager);
    
    // 尝试恢复暂停的节点
    int resumed_count = resume_suspended_nodes(analyzer->node_manager);
    
    // 尝试重建断开的连接
    int reconnected_count = reconnect_broken_connections(analyzer->node_manager);
    
    char details[256];
    sprintf(details, "恢复结果：重启%d个错误节点，恢复%d个暂停节点，重建%d个连接", 
            restarted_count, resumed_count, reconnected_count);
    log_analyzer_action(analyzer, "恢复完成", details);
    
    return (restarted_count > 0 || resumed_count > 0 || reconnected_count > 0);
}

/**
 * @brief 验证分析器参数
 * 
 * @param config 配置参数
 * @return bool 有效返回true，无效返回false
 */
static bool validate_analyzer_parameters(NetworkAnalyzerConfig* config) {
    if (!config) return false;
    
    // 验证各参数是否在合理范围内
    if (config->analysis_interval_ms < 1000) return false;  // 至少1秒
    if (config->health_threshold_warning <= config->health_threshold_critical) return false;
    if (config->health_threshold_warning <= 0.0 || config->health_threshold_warning >= 1.0) return false;
    if (config->health_threshold_critical <= 0.0 || config->health_threshold_critical >= 1.0) return false;
    if (config->topology_analysis_depth < 1) return false;
    
    return true;
}

/**
 * @brief 记录分析器操作
 * 
 * @param analyzer 分析器指针
 * @param action 操作名称
 * @param details 详细信息
 */
static void log_analyzer_action(NetworkAnalyzer* analyzer, const char* action, const char* details) {
    if (!analyzer || !analyzer->log_enabled) return;
    
    char log_message[512];
    sprintf(log_message, "[网络分析器] 操作: %s, 详情: %s", action, details);
    qentl_log_info(log_message);
}

/**
 * @brief 寻找网络关键节点
 * 
 * @param analyzer 网络分析器指针
 * @param count 最大节点数
 * @param importance_metrics 输出重要性指标数组
 * @return int 关键节点数量，失败时返回负值
 */
int find_critical_nodes(NetworkAnalyzer* analyzer, int count, NodeImportanceMetrics** importance_metrics) {
    if (!analyzer || !analyzer->node_manager || count <= 0 || !importance_metrics) {
        qentl_log_error("寻找关键节点失败：参数无效");
        return -1;
    }
    
    log_analyzer_action(analyzer, "关键节点", "开始寻找网络关键节点");
    
    int node_count = get_active_node_count(analyzer->node_manager);
    if (node_count <= 0) {
        qentl_log_warning("寻找关键节点：没有活跃节点");
        return 0;
    }
    
    // 分配NodeImportanceMetrics数组
    NodeImportanceMetrics* metrics = (NodeImportanceMetrics*)allocate_memory(sizeof(NodeImportanceMetrics) * node_count);
    if (!metrics) {
        qentl_log_error("寻找关键节点：内存分配失败");
        return -1;
    }
    
    // 获取节点数据（简化，实际实现需要从node_manager获取）
    QuantumNetworkNode** nodes = NULL;
    int actual_node_count = 0;
    
    // 评估每个节点的重要性指标
    for (int i = 0; i < actual_node_count; i++) {
        if (!nodes[i] || nodes[i]->state != NODE_STATE_ACTIVE) {
            continue;
        }
        
        metrics[i].node_id = nodes[i]->id;
        
        // 计算度中心性
        metrics[i].degree_centrality = calculate_node_centrality(
            analyzer, nodes[i]->id, CENTRALITY_DEGREE);
            
        // 计算接近中心性 (暂未实现，使用-1标记)
        metrics[i].closeness_centrality = -1.0;
        
        // 计算中介中心性 (暂未实现，使用-1标记)
        metrics[i].betweenness_centrality = -1.0;
        
        // 计算特征向量中心性 (暂未实现，使用-1标记)
        metrics[i].eigenvector_centrality = -1.0;
        
        // 加权计算总体重要性得分
        metrics[i].importance_score = 
            metrics[i].degree_centrality * 1.0;  // 目前只使用度中心性
    }
    
    // 按重要性得分排序（降序）
    for (int i = 0; i < actual_node_count - 1; i++) {
        for (int j = 0; j < actual_node_count - i - 1; j++) {
            if (metrics[j].importance_score < metrics[j + 1].importance_score) {
                // 交换
                NodeImportanceMetrics temp = metrics[j];
                metrics[j] = metrics[j + 1];
                metrics[j + 1] = temp;
            }
        }
    }
    
    // 限制返回的节点数量
    int result_count = (count < actual_node_count) ? count : actual_node_count;
    
    // 创建结果数组
    *importance_metrics = (NodeImportanceMetrics*)allocate_memory(sizeof(NodeImportanceMetrics) * result_count);
    if (!(*importance_metrics)) {
        free_memory(metrics);
        qentl_log_error("寻找关键节点：结果内存分配失败");
        return -1;
    }
    
    // 复制结果
    for (int i = 0; i < result_count; i++) {
        (*importance_metrics)[i] = metrics[i];
    }
    
    // 清理临时数组
    free_memory(metrics);
    
    char details[256];
    sprintf(details, "找到%d个关键节点", result_count);
    log_analyzer_action(analyzer, "关键节点完成", details);
    
    return result_count;
}

/**
 * @brief 寻找网络瓶颈
 * 
 * @param analyzer 网络分析器指针
 * @param count 最大瓶颈数
 * @param bottleneck_connections 输出瓶颈连接数组
 * @return int 瓶颈数量，失败时返回负值
 */
int find_network_bottlenecks(NetworkAnalyzer* analyzer, int count, unsigned int* bottleneck_connections) {
    if (!analyzer || !analyzer->node_manager || count <= 0 || !bottleneck_connections) {
        qentl_log_error("寻找网络瓶颈失败：参数无效");
        return -1;
    }
    
    log_analyzer_action(analyzer, "瓶颈查找", "开始寻找网络瓶颈");
    
    // 简化的瓶颈检测实现
    // 实际实现应考虑连接的带宽、延迟、负载等因素，以及网络流量分析
    
    // 获取网络连接数据（简化，实际实现需要从node_manager获取）
    int connection_count = 0;
    NetworkConnection** connections = NULL;
    
    // 评估每个连接的瓶颈得分
    double* bottleneck_scores = (double*)allocate_memory(sizeof(double) * connection_count);
    if (!bottleneck_scores) {
        qentl_log_error("寻找网络瓶颈：内存分配失败");
        return -1;
    }
    
    // 初始化索引数组，用于排序
    int* indices = (int*)allocate_memory(sizeof(int) * connection_count);
    if (!indices) {
        free_memory(bottleneck_scores);
        qentl_log_error("寻找网络瓶颈：索引内存分配失败");
        return -1;
    }
    
    for (int i = 0; i < connection_count; i++) {
        indices[i] = i;
    }
    
    // 评估每个连接的瓶颈分数
    for (int i = 0; i < connection_count; i++) {
        if (!connections[i] || connections[i]->state != CONNECTION_STATE_ACTIVE) {
            bottleneck_scores[i] = -1.0;  // 将非活动连接标记为-1
            continue;
        }
        
        // 简化的瓶颈得分计算
        // 在实际实现中，应该考虑多种因素，如带宽利用率、延迟、丢包率等
        double bandwidth_factor = 1.0 / (connections[i]->bandwidth + 1.0);
        double latency_factor = connections[i]->latency;
        double stability_factor = 1.0 - connections[i]->stability;
        
        // 综合评分（越高表示越可能是瓶颈）
        bottleneck_scores[i] = (bandwidth_factor * 0.5) + (latency_factor * 0.3) + (stability_factor * 0.2);
    }
    
    // 按瓶颈得分排序（降序）
    for (int i = 0; i < connection_count - 1; i++) {
        for (int j = 0; j < connection_count - i - 1; j++) {
            if (bottleneck_scores[indices[j]] < bottleneck_scores[indices[j + 1]]) {
                // 交换索引
                int temp = indices[j];
                indices[j] = indices[j + 1];
                indices[j + 1] = temp;
            }
        }
    }
    
    // 获取结果
    int bottleneck_count = 0;
    for (int i = 0; i < connection_count && bottleneck_count < count; i++) {
        int idx = indices[i];
        if (bottleneck_scores[idx] > 0.5) {  // 只返回得分超过阈值的连接
            bottleneck_connections[bottleneck_count++] = connections[idx]->id;
        }
    }
    
    // 清理内存
    free_memory(bottleneck_scores);
    free_memory(indices);
    
    char details[256];
    sprintf(details, "找到%d个网络瓶颈", bottleneck_count);
    log_analyzer_action(analyzer, "瓶颈查找完成", details);
    
    return bottleneck_count;
}

/**
 * @brief 评估网络鲁棒性
 * 
 * @param analyzer 网络分析器指针
 * @param failure_probability 节点失效概率
 * @return double 鲁棒性得分(0-1)，失败时返回负值
 */
double evaluate_network_robustness(NetworkAnalyzer* analyzer, double failure_probability) {
    if (!analyzer || !analyzer->node_manager || failure_probability < 0.0 || failure_probability > 1.0) {
        qentl_log_error("评估网络鲁棒性失败：参数无效");
        return -1.0;
    }
    
    log_analyzer_action(analyzer, "鲁棒性评估", "开始评估网络鲁棒性");
    
    // 获取网络拓扑数据
    int node_count = get_active_node_count(analyzer->node_manager);
    if (node_count <= 0) {
        qentl_log_warning("评估网络鲁棒性：没有活跃节点");
        return 0.0;
    }
    
    // 计算原始网络连通性指标
    double original_connectivity = calculate_network_density(analyzer);
    if (original_connectivity < 0.0) {
        qentl_log_error("评估网络鲁棒性：无法计算原始连通性");
        return -1.0;
    }
    
    // 模拟随机节点失效
    const int simulation_count = 100;  // 模拟次数
    const int failure_step = 5;        // 每次移除5%的节点
    
    // 记录每个失效比例下的连通性
    double robustness_area = 0.0;
    double max_area = 0.0;
    
    // 简化的鲁棒性评估实现（实际实现需要更复杂的模拟和计算）
    for (int i = 0; i <= 100; i += failure_step) {
        double failure_ratio = i / 100.0;
        
        // 估算失效后的连通性（实际实现应该进行真实的模拟）
        double estimated_connectivity = original_connectivity * (1.0 - failure_ratio);
        if (estimated_connectivity < 0.0) estimated_connectivity = 0.0;
        
        // 累计面积（梯形法则）
        if (i > 0) {
            double previous_failure_ratio = (i - failure_step) / 100.0;
            double previous_connectivity = original_connectivity * (1.0 - previous_failure_ratio);
            if (previous_connectivity < 0.0) previous_connectivity = 0.0;
            
            robustness_area += (previous_connectivity + estimated_connectivity) * failure_step / 200.0;
        }
        
        max_area += original_connectivity * failure_step / 100.0;
    }
    
    // 计算鲁棒性得分（面积比）
    double robustness_score = (max_area > 0.0) ? (robustness_area / max_area) : 0.0;
    
    char details[256];
    sprintf(details, "网络鲁棒性得分: %.4f", robustness_score);
    log_analyzer_action(analyzer, "鲁棒性评估完成", details);
    
    return robustness_score;
}

/**
 * @brief 优化网络结构建议
 * 
 * @param analyzer 网络分析器指针
 * @param max_suggestions 最大建议数
 * @param suggestions 输出建议数组
 * @return int 建议数量，失败时返回负值
 */
int suggest_network_optimizations(NetworkAnalyzer* analyzer, int max_suggestions, char** suggestions) {
    if (!analyzer || !analyzer->node_manager || max_suggestions <= 0 || !suggestions) {
        qentl_log_error("网络优化建议失败：参数无效");
        return -1;
    }
    
    log_analyzer_action(analyzer, "优化建议", "开始生成网络优化建议");
    
    // 分析网络状态
    NetworkHealthMetrics health = analyzer->health_metrics;
    double network_density = calculate_network_density(analyzer);
    
    // 创建建议数组
    int suggestion_count = 0;
    
    // 根据健康指标生成建议
    if (health.active_node_ratio < 0.7) {
        if (suggestion_count < max_suggestions) {
            suggestions[suggestion_count] = strdup("提高活跃节点比例，检查或重启非活跃节点");
            suggestion_count++;
        }
    }
    
    if (health.connectivity < 0.3) {
        if (suggestion_count < max_suggestions) {
            suggestions[suggestion_count] = strdup("增加网络连接度，在关键节点之间添加新连接");
            suggestion_count++;
        }
    }
    
    if (health.stability < 0.6) {
        if (suggestion_count < max_suggestions) {
            suggestions[suggestion_count] = strdup("提高节点稳定性，优化资源分配或降低负载");
            suggestion_count++;
        }
    }
    
    if (health.entanglement_level < 0.4) {
        if (suggestion_count < max_suggestions) {
            suggestions[suggestion_count] = strdup("增强量子纠缠水平，在关键节点之间建立纠缠连接");
            suggestion_count++;
        }
    }
    
    // 根据网络密度生成建议
    if (network_density < 0.2) {
        if (suggestion_count < max_suggestions) {
            suggestions[suggestion_count] = strdup("网络密度过低，考虑增加节点间连接以提高可靠性");
            suggestion_count++;
        }
    } else if (network_density > 0.8) {
        if (suggestion_count < max_suggestions) {
            suggestions[suggestion_count] = strdup("网络密度过高，可能导致资源浪费，考虑优化连接结构");
            suggestion_count++;
        }
    }
    
    // 检测瓶颈并提供建议
    unsigned int bottleneck_connections[5];
    int bottleneck_count = find_network_bottlenecks(analyzer, 5, bottleneck_connections);
    
    if (bottleneck_count > 0) {
        if (suggestion_count < max_suggestions) {
            suggestions[suggestion_count] = strdup("发现网络瓶颈，考虑增加带宽或创建备用路径");
            suggestion_count++;
        }
    }
    
    // 提供集群相关建议
    int cluster_count = detect_network_clusters(analyzer, CLUSTERING_DFS);
    if (cluster_count > 1) {
        if (suggestion_count < max_suggestions) {
            char cluster_suggestion[256];
            sprintf(cluster_suggestion, "网络中存在%d个独立集群，考虑增加集群间连接以提高整体连通性", cluster_count);
            suggestions[suggestion_count] = strdup(cluster_suggestion);
            suggestion_count++;
        }
    }
    
    char details[256];
    sprintf(details, "生成了%d条优化建议", suggestion_count);
    log_analyzer_action(analyzer, "优化建议完成", details);
    
    return suggestion_count;
}

/**
 * @brief 获取节点连接性统计
 * 
 * @param analyzer 网络分析器指针
 * @param node_id 节点ID
 * @param degree 输出度数
 * @param in_degree 输出入度
 * @param out_degree 输出出度
 * @return int 错误码，0表示成功，负值表示错误
 */
int get_node_connectivity_stats(NetworkAnalyzer* analyzer, unsigned int node_id, int* degree, int* in_degree, int* out_degree) {
    if (!analyzer || !analyzer->node_manager || !degree || !in_degree || !out_degree) {
        qentl_log_error("获取节点连接性统计失败：参数无效");
        return -1;
    }
    
    // 检查节点是否存在
    QuantumNetworkNode* node = get_node(analyzer->node_manager, node_id);
    if (!node) {
        qentl_log_error("获取节点连接性统计失败：节点不存在");
        return -2;
    }
    
    char details[256];
    sprintf(details, "开始获取节点%u的连接统计", node_id);
    log_analyzer_action(analyzer, "连接统计", details);
    
    // 初始化计数
    *degree = 0;
    *in_degree = 0;
    *out_degree = 0;
    
    // 简化的连接统计实现
    // 实际实现应该遍历节点的所有连接，并区分入度和出度
    *degree = node->connection_count;
    
    // 简化处理：假设入度和出度相等
    *in_degree = *degree / 2;
    *out_degree = *degree - *in_degree;
    
    sprintf(details, "节点%u的连接统计：总度=%d，入度=%d，出度=%d", 
            node_id, *degree, *in_degree, *out_degree);
    log_analyzer_action(analyzer, "连接统计完成", details);
    
    return 0;
}

/**
 * @brief 释放网络分析结果资源
 * 
 * @param result 分析结果
 */
void free_analysis_result(NetworkAnalysisResult* result) {
    if (!result) {
        return;
    }
    
    // 释放拓扑分析资源
    if (result->topology) {
        if (result->topology->centrality_measures) {
            free_memory(result->topology->centrality_measures);
        }
        if (result->topology->node_degrees) {
            free_memory(result->topology->node_degrees);
        }
        if (result->topology->analysis_timestamp) {
            free_memory(result->topology->analysis_timestamp);
        }
        free_memory(result->topology);
    }
    
    // 释放健康指标资源
    if (result->health) {
        free_memory(result->health);
    }
    
    // 释放节点重要性数组
    if (result->node_importance) {
        for (int i = 0; i < result->node_importance_count; i++) {
            if (result->node_importance[i]) {
                free_memory(result->node_importance[i]);
            }
        }
        free_memory(result->node_importance);
    }
    
    // 释放连接质量数组
    if (result->conn_quality) {
        for (int i = 0; i < result->conn_quality_count; i++) {
            if (result->conn_quality[i]) {
                free_memory(result->conn_quality[i]);
            }
        }
        free_memory(result->conn_quality);
    }
    
    // 释放最短路径矩阵
    if (result->shortest_paths) {
        // 假设shortest_paths的大小与node_importance_count相同
        for (int i = 0; i < result->node_importance_count; i++) {
            if (result->shortest_paths[i]) {
                free_memory(result->shortest_paths[i]);
            }
        }
        free_memory(result->shortest_paths);
    }
    
    // 释放集群数据
    if (result->clusters) {
        for (int i = 0; i < result->cluster_count; i++) {
            if (result->clusters[i]) {
                free_memory(result->clusters[i]);
            }
        }
        free_memory(result->clusters);
    }
    
    // 释放瓶颈分数
    if (result->bottleneck_scores) {
        free_memory(result->bottleneck_scores);
    }
    
    // 释放分析时间戳
    if (result->analysis_timestamp) {
        free_memory(result->analysis_timestamp);
    }
    
    // 释放结果本身
    free_memory(result);
}

/**
 * @brief 释放网络健康指标资源
 * 
 * @param metrics 健康指标
 */
void free_health_metrics(NetworkHealthMetrics* metrics) {
    if (metrics) {
        free_memory(metrics);
    }
}

/**
 * @brief 释放节点重要性指标资源
 * 
 * @param metrics 重要性指标
 * @param count 指标数量
 */
void free_importance_metrics(NodeImportanceMetrics** metrics, int count) {
    if (!metrics) {
        return;
    }
    
    for (int i = 0; i < count; i++) {
        if (metrics[i]) {
            free_memory(metrics[i]);
        }
    }
    
    free_memory(metrics);
} 