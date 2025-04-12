# 主量子区块链(MQB)主页开发文档

> 量子基因编码: QG-SOM01-DOC-20250402-C4D23A-ENT9876

## 概述

主量子区块链(Main Quantum Blockchain, MQB)是QSM项目的核心组件，提供量子链浏览和管理功能。本文档详细说明MQB主页的设计规范、功能需求和开发指南。

## 功能需求

### 1. 主要功能

- **量子状态监控** - 实时展示量子链状态和健康度
- **量子块浏览** - 浏览和查看量子区块详情
- **交易查询** - 查询和验证量子交易记录
- **节点管理** - 管理量子链节点和连接状态
- **量子存储统计** - 展示存储状态和使用情况
- **系统控制面板** - 管理员操作和配置接口

### 2. 用户界面要求

- 遵循QSM统一设计语言
- 采用响应式设计，适配不同设备
- 提供暗色主题和亮色主题切换
- 使用量子可视化元素展示区块链状态
- 集成量子态阵图交互功能

## 页面结构

```
+------------------------------------------------------+
|                   统一导航栏                          |
+------------------------------------------------------+
|                                                      |
|  +------------------+  +-------------------------+   |
|  |                  |  |                         |   |
|  |  量子链状态仪表盘  |  |      最新量子块          |   |
|  |                  |  |                         |   |
|  +------------------+  +-------------------------+   |
|                                                      |
|  +------------------+  +-------------------------+   |
|  |                  |  |                         |   |
|  |   节点分布地图    |  |      量子存储统计        |   |
|  |                  |  |                         |   |
|  +------------------+  +-------------------------+   |
|                                                      |
|  +--------------------------------------------------+|
|  |                                                  ||
|  |                高级功能面板                      ||
|  |                                                  ||
|  +--------------------------------------------------+|
|                                                      |
+------------------------------------------------------+
|                   统一底部栏                          |
+------------------------------------------------------+
```

## 组件详情

### 1. 量子链状态仪表盘

- **TPS指标** - 每秒交易处理量
- **当前高度** - 最新区块高度
- **节点数量** - 活跃节点计数
- **量子链健康度** - 综合健康评分
- **量子纠缠强度** - 纠缠信道质量指标

### 2. 最新量子块

- 显示最近生成的5个量子区块
- 包含区块高度、时间戳、区块哈希、交易数量
- 提供区块详情链接
- 实时更新新区块

### 3. 节点分布地图

- 全球节点分布可视化
- 节点类型和状态标记
- 节点连接和纠缠可视化
- 交互式节点信息查看

### 4. 量子存储统计

- 总存储容量和使用量
- 按数据类型的存储分布
- 存储效率和冗余度
- 历史存储增长趋势

### 5. 高级功能面板

- 交易查询工具
- 区块浏览器入口
- 量子合约管理
- 系统参数配置（仅管理员）
- 性能监控工具

## 技术实现

### 1. 前端技术栈

- HTML5 + CSS3 + JavaScript
- 响应式布局框架
- 数据可视化库（D3.js、Chart.js）
- WebSocket实时数据更新
- 符合QSM统一设计规范

### 2. 数据接口

```javascript
// 获取量子链状态API
GET /api/som/mqb/status
Response: {
  tps: 1240,
  blockHeight: 3458921,
  activeNodes: 156,
  healthScore: 97.2,
  entanglementStrength: 0.87
}

// 获取最新区块API
GET /api/som/mqb/blocks/latest?limit=5
Response: {
  blocks: [
    {
      height: 3458921,
      timestamp: "2025-04-02T01:02:35Z",
      hash: "q7f8e9d5c6b3a2...",
      transactionCount: 235
    },
    // ... 其他区块
  ]
}

// 获取节点分布API
GET /api/som/mqb/nodes/distribution
Response: {
  nodes: [
    {
      id: "node_2e3f4d5a",
      type: "validator",
      location: {
        lat: 39.9042,
        lng: 116.4074
      },
      status: "active",
      connections: ["node_7c8d9e0f", "node_1a2b3c4d"]
    },
    // ... 其他节点
  ]
}

// 获取存储统计API
GET /api/som/mqb/storage/stats
Response: {
  totalCapacity: 256000,
  usedCapacity: 142376,
  distribution: {
    "transactions": 58623,
    "contracts": 35481,
    "states": 48272
  },
  redundancyFactor: 3.2,
  growthRate: 4.7
}
```

### 3. 代码结构

```
/SOM/templates/MQB/
  ├── index.html            # 主页HTML
  ├── js/
  │   ├── dashboard.js      # 仪表盘组件
  │   ├── blocks.js         # 区块展示组件
  │   ├── node-map.js       # 节点地图组件
  │   ├── storage-stats.js  # 存储统计组件
  │   └── advanced-panel.js # 高级功能面板
  └── css/
      ├── mqb-main.css      # 主样式文件
      ├── dashboard.css     # 仪表盘样式
      └── node-map.css      # 节点地图样式
```

## 实现示例

### HTML结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>主量子区块链 - QSM</title>
  <!-- 导航栏和底部栏样式 -->
  <link rel="stylesheet" href="/QSM/templates/shared/css/navigation.css">
  <link rel="stylesheet" href="/QSM/templates/shared/css/footer.css">
  <!-- MQB特定样式 -->
  <link rel="stylesheet" href="/SOM/templates/MQB/css/mqb-main.css">
  <link rel="stylesheet" href="/SOM/templates/MQB/css/dashboard.css">
  <link rel="stylesheet" href="/SOM/templates/MQB/css/node-map.css">
</head>
<body data-system="mqb">
  <!-- 统一导航栏 -->
  {% include "shared/navigation.html" %}
  
  <main class="mqb-container">
    <h1 class="mqb-title">主量子区块链</h1>
    
    <div class="mqb-dashboard-row">
      <!-- 量子链状态仪表盘 -->
      <section class="mqb-panel" id="status-dashboard">
        <h2 class="panel-title">量子链状态</h2>
        <div class="dashboard-grid">
          <div class="dashboard-item">
            <div class="item-value" id="tps">--</div>
            <div class="item-label">每秒交易数</div>
          </div>
          <div class="dashboard-item">
            <div class="item-value" id="block-height">--</div>
            <div class="item-label">区块高度</div>
          </div>
          <div class="dashboard-item">
            <div class="item-value" id="node-count">--</div>
            <div class="item-label">活跃节点数</div>
          </div>
          <div class="dashboard-item">
            <div class="item-value" id="health-score">--</div>
            <div class="item-label">健康度</div>
          </div>
          <div class="dashboard-item">
            <div class="item-value" id="entanglement-strength">--</div>
            <div class="item-label">纠缠强度</div>
          </div>
        </div>
      </section>
      
      <!-- 最新量子块 -->
      <section class="mqb-panel" id="latest-blocks">
        <h2 class="panel-title">最新量子块</h2>
        <table class="blocks-table">
          <thead>
            <tr>
              <th>高度</th>
              <th>时间</th>
              <th>哈希</th>
              <th>交易数</th>
            </tr>
          </thead>
          <tbody id="blocks-tbody">
            <!-- 动态填充区块数据 -->
          </tbody>
        </table>
        <a href="/mqb/blocks" class="view-all-btn">查看全部区块</a>
      </section>
    </div>
    
    <div class="mqb-dashboard-row">
      <!-- 节点分布地图 -->
      <section class="mqb-panel" id="node-map-panel">
        <h2 class="panel-title">节点分布</h2>
        <div id="node-map" class="node-map-container"></div>
        <div class="node-stats">
          <div class="node-type validator">验证节点: <span id="validator-count">--</span></div>
          <div class="node-type observer">观察节点: <span id="observer-count">--</span></div>
          <div class="node-type relay">中继节点: <span id="relay-count">--</span></div>
        </div>
      </section>
      
      <!-- 量子存储统计 -->
      <section class="mqb-panel" id="storage-stats">
        <h2 class="panel-title">量子存储统计</h2>
        <div class="storage-overview">
          <div class="storage-chart-container">
            <canvas id="storage-chart"></canvas>
          </div>
          <div class="storage-metrics">
            <div class="metric">
              <div class="metric-label">总容量</div>
              <div class="metric-value" id="total-capacity">--</div>
            </div>
            <div class="metric">
              <div class="metric-label">已使用</div>
              <div class="metric-value" id="used-capacity">--</div>
            </div>
            <div class="metric">
              <div class="metric-label">冗余度</div>
              <div class="metric-value" id="redundancy">--</div>
            </div>
            <div class="metric">
              <div class="metric-label">增长率</div>
              <div class="metric-value" id="growth-rate">--</div>
            </div>
          </div>
        </div>
      </section>
    </div>
    
    <!-- 高级功能面板 -->
    <section class="mqb-panel full-width" id="advanced-panel">
      <h2 class="panel-title">高级功能</h2>
      <div class="advanced-tools">
        <div class="tool-card" id="transaction-search">
          <div class="tool-icon transaction-icon"></div>
          <h3 class="tool-title">交易查询</h3>
          <p class="tool-desc">查询和验证链上交易记录</p>
        </div>
        <div class="tool-card" id="block-explorer">
          <div class="tool-icon block-icon"></div>
          <h3 class="tool-title">区块浏览</h3>
          <p class="tool-desc">全功能区块浏览器</p>
        </div>
        <div class="tool-card" id="contract-manager">
          <div class="tool-icon contract-icon"></div>
          <h3 class="tool-title">量子合约</h3>
          <p class="tool-desc">管理和部署量子智能合约</p>
        </div>
        <div class="tool-card" id="system-config">
          <div class="tool-icon config-icon"></div>
          <h3 class="tool-title">系统配置</h3>
          <p class="tool-desc">调整和优化系统参数</p>
        </div>
        <div class="tool-card" id="performance-monitor">
          <div class="tool-icon monitor-icon"></div>
          <h3 class="tool-title">性能监控</h3>
          <p class="tool-desc">实时监控系统性能指标</p>
        </div>
      </div>
    </section>
  </main>
  
  <!-- 统一底部栏 -->
  {% include "shared/footer.html" %}
  
  <!-- 导航栏脚本 -->
  <script src="/QSM/templates/shared/js/navigation.js"></script>
  <script src="/QSM/templates/shared/js/quantum_matrix.js"></script>
  <!-- 可视化库 -->
  <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1"></script>
  <!-- MQB特定脚本 -->
  <script src="/SOM/templates/MQB/js/dashboard.js"></script>
  <script src="/SOM/templates/MQB/js/blocks.js"></script>
  <script src="/SOM/templates/MQB/js/node-map.js"></script>
  <script src="/SOM/templates/MQB/js/storage-stats.js"></script>
  <script src="/SOM/templates/MQB/js/advanced-panel.js"></script>
</body>
</html>
```

### JavaScript示例

```javascript
// dashboard.js
class QuantumChainDashboard {
  constructor() {
    this.elements = {
      tps: document.getElementById('tps'),
      blockHeight: document.getElementById('block-height'),
      nodeCount: document.getElementById('node-count'),
      healthScore: document.getElementById('health-score'),
      entanglementStrength: document.getElementById('entanglement-strength')
    };
    
    this.initialize();
  }
  
  async initialize() {
    // 初始数据加载
    await this.fetchAndUpdateData();
    
    // 建立WebSocket连接获取实时更新
    this.connectWebSocket();
    
    // 设置定时刷新（作为WebSocket的备用）
    setInterval(() => this.fetchAndUpdateData(), 30000);
  }
  
  async fetchAndUpdateData() {
    try {
      const response = await fetch('/api/som/mqb/status');
      const data = await response.json();
      
      this.updateDashboard(data);
    } catch (error) {
      console.error('获取量子链状态失败:', error);
    }
  }
  
  updateDashboard(data) {
    this.elements.tps.textContent = data.tps.toLocaleString();
    this.elements.blockHeight.textContent = data.blockHeight.toLocaleString();
    this.elements.nodeCount.textContent = data.activeNodes;
    this.elements.healthScore.textContent = data.healthScore.toFixed(1);
    this.elements.entanglementStrength.textContent = data.entanglementStrength.toFixed(2);
    
    // 根据健康度设置颜色
    this.updateHealthScoreColor(data.healthScore);
  }
  
  updateHealthScoreColor(score) {
    const element = this.elements.healthScore;
    element.classList.remove('score-high', 'score-medium', 'score-low');
    
    if (score >= 90) {
      element.classList.add('score-high');
    } else if (score >= 70) {
      element.classList.add('score-medium');
    } else {
      element.classList.add('score-low');
    }
  }
  
  connectWebSocket() {
    const ws = new WebSocket('wss://qsm-ws.example.com/mqb/status');
    
    ws.addEventListener('open', () => {
      console.log('WebSocket连接已建立');
    });
    
    ws.addEventListener('message', (event) => {
      try {
        const data = JSON.parse(event.data);
        this.updateDashboard(data);
      } catch (error) {
        console.error('解析WebSocket消息失败:', error);
      }
    });
    
    ws.addEventListener('close', () => {
      console.log('WebSocket连接已关闭, 10秒后重连');
      setTimeout(() => this.connectWebSocket(), 10000);
    });
    
    ws.addEventListener('error', (error) => {
      console.error('WebSocket错误:', error);
    });
  }
}

// 初始化仪表盘
document.addEventListener('DOMContentLoaded', () => {
  window.quantumChainDashboard = new QuantumChainDashboard();
});
```

### CSS示例

```css
/* mqb-main.css */
.mqb-container {
  max-width: 1200px;
  margin: 80px auto 40px;
  padding: 0 20px;
}

.mqb-title {
  font-size: 2.5rem;
  color: #00296B;
  margin-bottom: 30px;
  text-align: center;
  background: linear-gradient(90deg, #00296B, #3A0CA3, #7209B7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.mqb-dashboard-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.mqb-panel {
  background: white;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  padding: 20px;
  flex: 1;
}

.panel-title {
  margin-top: 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
  color: #3A0CA3;
  font-size: 1.5rem;
}

.full-width {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .mqb-dashboard-row {
    flex-direction: column;
  }
  
  .mqb-panel {
    width: 100%;
  }
}

/* dashboard.css */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 15px;
}

.dashboard-item {
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  background: #f8f9fa;
  transition: transform 0.3s, box-shadow 0.3s;
}

.dashboard-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.item-value {
  font-size: 1.8rem;
  font-weight: bold;
  margin-bottom: 5px;
  color: #3A0CA3;
}

.item-label {
  font-size: 0.9rem;
  color: #6c757d;
}

.score-high {
  color: #28a745;
}

.score-medium {
  color: #ffc107;
}

.score-low {
  color: #dc3545;
}

/* blocks.css */
.blocks-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.blocks-table th,
.blocks-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
  text-align: left;
}

.blocks-table th {
  font-weight: 600;
  color: #495057;
  background-color: #f8f9fa;
}

.blocks-table tbody tr {
  transition: background-color 0.3s;
}

.blocks-table tbody tr:hover {
  background-color: rgba(58, 12, 163, 0.05);
}

.view-all-btn {
  display: block;
  text-align: center;
  margin-top: 15px;
  padding: 8px 16px;
  background-color: #3A0CA3;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  transition: background-color 0.3s;
}

.view-all-btn:hover {
  background-color: #2a0979;
}
```

## 测试标准

1. **功能测试** - 验证所有功能点正常工作
2. **性能测试** - 页面加载和更新速度优化
3. **响应式测试** - 不同设备和屏幕尺寸适配
4. **浏览器兼容性** - 主流浏览器兼容性验证
5. **WebSocket连接** - 实时数据更新可靠性测试

## 开发和部署流程

1. 按照设计规范和功能需求实现前端界面
2. 与后端API集成，确保数据流正确
3. 进行跨浏览器兼容性测试和响应式设计测试
4. 部署到测试环境验证功能
5. 用户体验测试和性能优化
6. 部署到生产环境

## 维护注意事项

1. 定期更新API接口文档
2. 监控WebSocket连接状态和性能
3. 定期检查浏览器兼容性
4. 持续优化页面加载性能
5. 与QSM统一导航栏保持样式同步 