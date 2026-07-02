/**
 * QSM - QEntL量子虚拟机Web模拟器 - 算法统计增强版
 * 版本: v0.2.1-alpha
 * 量子基因编码: QGC-QVM-SIMULATOR-20260303
 * 
 * 新增功能：量子算法成功率追踪系统
 */

// 算法成功率追踪类
class AlgorithmStatsTracker {
    constructor() {
        this.stats = new Map();
        this.sessionId = Date.now();
    }
    
    // 记录算法执行结果
    recordExecution(algorithmName, success, executionTime, details = {}) {
        if (!this.stats.has(algorithmName)) {
            this.stats.set(algorithmName, {
                totalRuns: 0,
                successfulRuns: 0,
                totalExecutionTime: 0,
                avgSuccessRate: 0,
                lastRun: null,
                history: []
            });
        }
        
        const stat = this.stats.get(algorithmName);
        stat.totalRuns++;
        if (success) stat.successfulRuns++;
        stat.totalExecutionTime += executionTime;
        stat.avgSuccessRate = (stat.successfulRuns / stat.totalRuns * 100).toFixed(1);
        stat.lastRun = { success, executionTime, details, timestamp: new Date().toISOString() };
        
        // 保持最近20次历史
        stat.history.push(stat.lastRun);
        if (stat.history.length > 20) stat.history.shift();
        
        return this.getAlgorithmStats(algorithmName);
    }
    
    // 获取单个算法统计
    getAlgorithmStats(algorithmName) {
        const stat = this.stats.get(algorithmName);
        if (!stat) return null;
        
        return {
            name: algorithmName,
            totalRuns: stat.totalRuns,
            successfulRuns: stat.successfulRuns,
            failedRuns: stat.totalRuns - stat.successfulRuns,
            successRate: stat.avgSuccessRate + '%',
            avgTime: (stat.totalExecutionTime / stat.totalRuns).toFixed(2) + 'ms',
            lastRun: stat.lastRun
        };
    }
    
    // 获取所有算法统计
    getAllStats() {
        const result = [];
        this.stats.forEach((value, key) => {
            result.push(this.getAlgorithmStats(key));
        });
        return result;
    }
    
    // 获取总体统计
    getSummary() {
        let totalRuns = 0;
        let totalSuccess = 0;
        let algorithms = 0;
        
        this.stats.forEach(stat => {
            totalRuns += stat.totalRuns;
            totalSuccess += stat.successfulRuns;
            algorithms++;
        });
        
        return {
            algorithmsUsed: algorithms,
            totalExecutions: totalRuns,
            successfulExecutions: totalSuccess,
            overallSuccessRate: totalRuns > 0 ? (totalSuccess / totalRuns * 100).toFixed(1) + '%' : 'N/A',
            sessionId: this.sessionId
        };
    }
    
    // 重置统计
    reset() {
        this.stats.clear();
        this.sessionId = Date.now();
    }
    
    // 导出为JSON
    export() {
        return JSON.stringify({
            sessionId: this.sessionId,
            summary: this.getSummary(),
            algorithms: this.getAllStats()
        }, null, 2);
    }
}

// 导出给全局使用
if (typeof window !== 'undefined') {
    window.AlgorithmStatsTracker = AlgorithmStatsTracker;
}
