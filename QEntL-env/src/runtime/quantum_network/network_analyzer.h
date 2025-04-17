/**
 * 量子网络分析器头文件
 * 
 * 该文件定义了量子网络分析器的数据结构和函数接口，用于分析量子网络的拓扑结构和性能指标。
 *
 * @file network_analyzer.h
 * @version 1.0
 * @date 2024-05-15
 */

#ifndef QENTL_NETWORK_ANALYZER_H
#define QENTL_NETWORK_ANALYZER_H

#include <stdio.h>
#include <stdlib.h>
#include "node_manager.h"

/**
 * 中心性度量类型
 */
typedef enum {
    CENTRALITY_DEGREE = 0,        // 度中心性
    CENTRALITY_CLOSENESS = 1,     // 接近中心性
    CENTRALITY_BETWEENNESS = 2,   // 中介中心性
    CENTRALITY_EIGENVECTOR = 3    // 特征向量中心性
} CentralityType;

/**
 * 网络聚类算法
 */
typedef enum {
    CLUSTERING_DFS = 0,           // 深度优先搜索
    CLUSTERING_COMMUNITY = 1,     // 社区检测
    CLUSTERING_SPECTRAL = 2,      // 谱聚类
    CLUSTERING_HIERARCHICAL = 3   // 层次聚类
} ClusteringAlgorithm;

/**
 * 路径类型
 */
typedef enum {
    PATH_SHORTEST = 0,            // 最短路径
    PATH_MOST_RELIABLE = 1,       // 最可靠路径
    PATH_HIGHEST_BANDWIDTH = 2,   // 最高带宽路径
    PATH_LOWEST_LATENCY = 3       // 最低延迟路径
} PathType;

/**
 * 网络健康指标
 */
typedef struct {
    double active_node_ratio;     // 活动节点比例
    double connectivity_score;    // 连接性得分
    double average_stability;     // 平均稳定性
    double entanglement_level;    // 纠缠水平
    double error_node_ratio;      // 错误节点比例
    double energy_efficiency;     // 能量效率
    double routing_efficiency;    // 路由效率
    double overall_health;        // 总体健康度
} NetworkHealthMetrics;

/**
 * 节点重要性指标
 */
typedef struct {
    unsigned int node_id;         // 节点ID
    double degree_centrality;     // 度中心性
    double closeness_centrality;  // 接近中心性
    double betweenness_centrality;// 中介中心性
    double eigenvector_centrality;// 特征向量中心性
    double importance_score;      // 重要性综合得分
} NodeImportanceMetrics;

/**
 * 连接质量指标
 */
typedef struct {
    unsigned int connection_id;   // 连接ID
    double strength;              // 强度
    double stability;             // 稳定性
    double bandwidth;             // 带宽
    double latency;               // 延迟
    double quality_score;         // 质量综合得分
} ConnectionQualityMetrics;

/**
 * 网络分析选项
 */
typedef struct {
    int calculate_centrality;     // 是否计算中心性
    CentralityType centrality_type;// 中心性类型
    int detect_clusters;          // 是否检测集群
    ClusteringAlgorithm clustering_algorithm;// 聚类算法
    int calculate_paths;          // 是否计算路径
    PathType path_type;           // 路径类型
    int analyze_health;           // 是否分析健康状况
    int identify_bottlenecks;     // 是否识别瓶颈
    int rank_nodes;               // 是否对节点排序
    int evaluate_robustness;      // 是否评估鲁棒性
} NetworkAnalysisOptions;

/**
 * 网络分析结果
 */
typedef struct {
    NetworkTopologyAnalysis* topology;      // 拓扑分析结果
    NetworkHealthMetrics* health;           // 健康指标
    NodeImportanceMetrics** node_importance;// 节点重要性数组
    int node_importance_count;              // 节点重要性数量
    ConnectionQualityMetrics** conn_quality;// 连接质量数组
    int conn_quality_count;                 // 连接质量数量
    int** shortest_paths;                   // 最短路径矩阵
    int** clusters;                         // 集群数据
    int cluster_count;                      // 集群数量
    double* bottleneck_scores;              // 瓶颈分数
    double robustness_score;                // 鲁棒性得分
    char* analysis_timestamp;               // 分析时间戳
} NetworkAnalysisResult;

/**
 * 网络分析器配置
 */
typedef struct {
    int enable_logging;                     // 是否启用日志
    char* log_file_path;                    // 日志文件路径
    int max_path_calculation_size;          // 路径计算的最大网络大小
    int max_iterations;                     // 最大迭代次数
    double convergence_threshold;           // 收敛阈值
    int use_approximate_algorithms;         // 是否使用近似算法
    int cache_results;                      // 是否缓存结果
    int cache_timeout;                      // 缓存超时时间(秒)
} NetworkAnalyzerConfig;

/**
 * 网络分析器
 */
typedef struct {
    NetworkAnalyzerConfig config;           // 配置
    NodeManager* node_manager;              // 节点管理器
    FILE* log_file;                         // 日志文件
    void* cache;                            // 结果缓存
    time_t last_analysis_time;              // 最后分析时间
    char* analyzer_id;                      // 分析器ID
} NetworkAnalyzer;

/* 函数声明 */

/**
 * 初始化网络分析器
 * 
 * @param config 分析器配置
 * @param node_manager 节点管理器
 * @return 网络分析器指针，失败时返回NULL
 */
NetworkAnalyzer* initialize_network_analyzer(NetworkAnalyzerConfig config, NodeManager* node_manager);

/**
 * 获取默认网络分析器配置
 * 
 * @return 默认配置
 */
NetworkAnalyzerConfig get_default_network_analyzer_config();

/**
 * 关闭网络分析器
 * 
 * @param analyzer 网络分析器
 */
void shutdown_network_analyzer(NetworkAnalyzer* analyzer);

/**
 * 分析网络拓扑
 * 
 * @param analyzer 网络分析器
 * @param options 分析选项
 * @return 分析结果，失败时返回NULL
 */
NetworkAnalysisResult* analyze_network(NetworkAnalyzer* analyzer, NetworkAnalysisOptions options);

/**
 * 获取网络健康状况
 * 
 * @param analyzer 网络分析器
 * @return 健康指标，失败时返回NULL
 */
NetworkHealthMetrics* get_network_health(NetworkAnalyzer* analyzer);

/**
 * 计算网络密度
 * 
 * @param analyzer 网络分析器
 * @return 网络密度(0-1)，失败时返回负值
 */
double calculate_network_density(NetworkAnalyzer* analyzer);

/**
 * 计算平均路径长度
 * 
 * @param analyzer 网络分析器
 * @return 平均路径长度，失败时返回负值
 */
double calculate_average_path_length(NetworkAnalyzer* analyzer);

/**
 * 检测网络集群
 * 
 * @param analyzer 网络分析器
 * @param algorithm 聚类算法
 * @return 集群数量，失败时返回负值
 */
int detect_network_clusters(NetworkAnalyzer* analyzer, ClusteringAlgorithm algorithm);

/**
 * 计算节点中心性
 * 
 * @param analyzer 网络分析器
 * @param node_id 节点ID
 * @param centrality_type 中心性类型
 * @return 中心性值，失败时返回负值
 */
double calculate_node_centrality(NetworkAnalyzer* analyzer, unsigned int node_id, CentralityType centrality_type);

/**
 * 寻找网络关键节点
 * 
 * @param analyzer 网络分析器
 * @param count 最大节点数
 * @param importance_metrics 输出重要性指标数组
 * @return 关键节点数量，失败时返回负值
 */
int find_critical_nodes(NetworkAnalyzer* analyzer, int count, NodeImportanceMetrics** importance_metrics);

/**
 * 寻找网络瓶颈
 * 
 * @param analyzer 网络分析器
 * @param count 最大瓶颈数
 * @param bottleneck_connections 输出瓶颈连接数组
 * @return 瓶颈数量，失败时返回负值
 */
int find_network_bottlenecks(NetworkAnalyzer* analyzer, int count, unsigned int* bottleneck_connections);

/**
 * 评估网络鲁棒性
 * 
 * @param analyzer 网络分析器
 * @param failure_probability 节点失效概率
 * @return 鲁棒性得分(0-1)，失败时返回负值
 */
double evaluate_network_robustness(NetworkAnalyzer* analyzer, double failure_probability);

/**
 * 模拟网络故障
 * 
 * @param analyzer 网络分析器
 * @param failed_nodes 故障节点ID数组
 * @param failed_count 故障节点数量
 * @return 网络分析结果，失败时返回NULL
 */
NetworkAnalysisResult* simulate_network_failure(NetworkAnalyzer* analyzer, unsigned int* failed_nodes, int failed_count);

/**
 * 获取节点连接性统计
 * 
 * @param analyzer 网络分析器
 * @param node_id 节点ID
 * @param degree 输出度数
 * @param in_degree 输出入度
 * @param out_degree 输出出度
 * @return 错误码
 */
int get_node_connectivity_stats(NetworkAnalyzer* analyzer, unsigned int node_id, int* degree, int* in_degree, int* out_degree);

/**
 * 优化网络结构建议
 * 
 * @param analyzer 网络分析器
 * @param max_suggestions 最大建议数
 * @param suggestions 输出建议数组
 * @return 建议数量，失败时返回负值
 */
int suggest_network_optimizations(NetworkAnalyzer* analyzer, int max_suggestions, char** suggestions);

/**
 * 释放网络分析结果资源
 * 
 * @param result 分析结果
 */
void free_analysis_result(NetworkAnalysisResult* result);

/**
 * 释放网络健康指标资源
 * 
 * @param metrics 健康指标
 */
void free_health_metrics(NetworkHealthMetrics* metrics);

/**
 * 释放节点重要性指标资源
 * 
 * @param metrics 重要性指标
 * @param count 指标数量
 */
void free_importance_metrics(NodeImportanceMetrics** metrics, int count);

#endif /* QENTL_NETWORK_ANALYZER_H */ 