# 量子UI组件使用示例

## 基础示例

### 创建一个带标签页的量子面板

```html
<template>
  <div class="quantum-panel">
    <quantum-tabs
      :tabs="[
        { label: '量子状态', closable: false },
        { label: '纠缠配置', closable: false },
        { label: '测量结果', closable: true }
      ]"
      :content="[
        '<quantum-state-viewer :data="stateData" />',
        '<quantum-entangle-config :config="entangleConfig" />',
        '<quantum-measurement-results :results="measureResults" />'
      ]"
      @tab-change="handleTabChange"
      @tab-close="handleTabClose"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      stateData: { /* 量子状态数据 */ },
      entangleConfig: { /* 纠缠配置 */ },
      measureResults: { /* 测量结果 */ }
    }
  },
  methods: {
    handleTabChange(index) {
      console.log('切换到标签:', index);
    },
    handleTabClose(index) {
      console.log('关闭标签:', index);
    }
  }
}
</script>
```

### 创建一个量子树形控件

```html
<template>
  <div class="quantum-explorer">
    <quantum-tree
      :data="treeData"
      @node-toggle="handleNodeToggle"
      @node-select="handleNodeSelect"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      treeData: [{
        key: 'qubits',
        label: '量子比特',
        children: [
          {
            key: 'qubit-1',
            label: '比特 #1',
            icon: '⚛'
          },
          {
            key: 'qubit-2',
            label: '比特 #2',
            icon: '⚛'
          }
        ]
      }, {
        key: 'gates',
        label: '量子门',
        children: [
          {
            key: 'gate-h',
            label: 'Hadamard门',
            icon: 'H'
          },
          {
            key: 'gate-x',
            label: 'Pauli-X门',
            icon: 'X'
          }
        ]
      }]
    }
  },
  methods: {
    handleNodeToggle(key) {
      console.log('节点展开/收起:', key);
    },
    handleNodeSelect(key) {
      console.log('节点选中:', key);
    }
  }
}
</script>
```

### 创建一个量子状态图表

```html
<template>
  <div class="quantum-state-chart">
    <quantum-chart
      type="bar"
      :data="chartData"
      :options="chartOptions"
      @data-select="handleDataSelect"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      chartData: {
        labels: ['|00⟩', '|01⟩', '|10⟩', '|11⟩'],
        datasets: [{
          label: '量子态振幅',
          data: [0.5, 0.5, 0.5, 0.5],
          backgroundColor: [
            'rgba(75, 192, 192, 0.2)',
            'rgba(54, 162, 235, 0.2)',
            'rgba(153, 102, 255, 0.2)',
            'rgba(255, 99, 132, 0.2)'
          ],
          borderColor: [
            'rgba(75, 192, 192, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 99, 132, 1)'
          ],
          borderWidth: 1
        }]
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 1
          }
        }
      }
    }
  },
  methods: {
    handleDataSelect(index) {
      console.log('选中状态:', this.chartData.labels[index]);
    }
  }
}
</script>
```

### 创建一个量子计算进度条

```html
<template>
  <div class="quantum-computation">
    <h3>量子计算进度</h3>
    <quantum-progress
      :percentage="computationProgress"
      type="success"
      :text="progressText"
      @change="handleProgressChange"
      @complete="handleComputationComplete"
    />
    
    <div class="computation-stats">
      <p>已完成步骤: {{ completedSteps }}/{{ totalSteps }}</p>
      <p>估计剩余时间: {{ remainingTime }}秒</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      computationProgress: 0,
      completedSteps: 0,
      totalSteps: 100,
      remainingTime: 60
    }
  },
  computed: {
    progressText() {
      return `正在进行量子计算 (${this.completedSteps}/${this.totalSteps})`;
    }
  },
  methods: {
    handleProgressChange(value) {
      this.completedSteps = Math.floor(value * this.totalSteps / 100);
      this.remainingTime = Math.ceil((100 - value) * 0.6);
    },
    handleComputationComplete() {
      console.log('量子计算完成!');
    }
  },
  mounted() {
    // 模拟计算进度
    const interval = setInterval(() => {
      if (this.computationProgress < 100) {
        this.computationProgress += 1;
      } else {
        clearInterval(interval);
      }
    }, 100);
  }
}
</script>
```

## 高级示例

### 量子纠缠通信示例

```javascript
// 初始化加密模块
const keyGenerator = new QuantumEncryption.KeyGenerator();
const encryptor = new QuantumEncryption.Encryptor(keyGenerator);
const signature = new QuantumEncryption.Signature(keyGenerator);

// 初始化重连模块
const reconnManager = new QuantumReconnection.ReconnectionManager({
  maxAttempts: 5,
  initialDelay: 1000,
  maxDelay: 30000
});

const heartbeat = new QuantumReconnection.Heartbeat(30000);
const connState = new QuantumReconnection.ConnectionState();

// 初始化消息队列
const queue = new QuantumQueue.MessageQueue({
  maxSize: 1000,
  maxRetries: 3
});

const subscriber = new QuantumQueue.MessageSubscriber();

// 设置连接状态观察者
connState.addObserver((state) => {
  if (state.status === 'disconnected') {
    console.log('连接断开:', state.disconnectReason);
    reconnManager.startReconnection();
  }
});

// 设置重连处理器
reconnManager.setReconnectHandler(async (attempts) => {
  console.log(`第 ${attempts} 次重连尝试`);
  try {
    await connectToQuantumChannel();
    connState.updateState('connected');
    return true;
  } catch (error) {
    console.error('重连失败:', error);
    return false;
  }
});

// 设置心跳处理器
heartbeat.setTimeoutHandler(() => {
  console.log('心跳超时');
  connState.updateState('disconnected', 'heartbeat_timeout');
});

// 注册消息处理器
queue.registerHandler('quantum-state-update', async (data) => {
  try {
    // 验证消息签名
    const isValid = signature.verify(data.payload, data.signature, data.channelId);
    if (!isValid) {
      throw new Error('Invalid message signature');
    }
    
    // 解密消息
    const decrypted = await encryptor.decrypt(data.payload, data.channelId);
    
    // 处理量子态更新
    handleQuantumStateUpdate(decrypted);
  } catch (error) {
    console.error('消息处理失败:', error);
    throw error;
  }
});

// 订阅事件
const unsubscribe = subscriber.subscribe('quantum-measurement', (data) => {
  console.log('收到量子测量结果:', data);
});

// 发送加密消息
async function sendQuantumMessage(channelId, message) {
  try {
    // 生成密钥对
    const { publicKey, privateKey } = keyGenerator.generateKeyPair(channelId);
    
    // 加密消息
    const encrypted = await encryptor.encrypt(message, channelId);
    
    // 生成签名
    const sign = signature.sign(encrypted, channelId);
    
    // 将消息加入队列
    queue.enqueue({
      type: 'quantum-state-update',
      channelId,
      payload: encrypted,
      signature: sign
    }, QuantumQueue.Priority.HIGH);
  } catch (error) {
    console.error('消息发送失败:', error);
    throw error;
  }
}
```

### 完整的量子应用示例

```html
<template>
  <div class="quantum-app">
    <!-- 标签页导航 -->
    <quantum-tabs
      :tabs="tabs"
      :content="tabContents"
      @tab-change="handleTabChange"
    />
    
    <!-- 主要内容区 -->
    <div class="quantum-content">
      <!-- 左侧树形菜单 -->
      <div class="quantum-sidebar">
        <quantum-tree
          :data="menuData"
          @node-select="handleMenuSelect"
        />
      </div>
      
      <!-- 右侧内容区 -->
      <div class="quantum-main">
        <!-- 状态图表 -->
        <quantum-chart
          v-if="showChart"
          :type="chartType"
          :data="chartData"
          :options="chartOptions"
          @data-select="handleDataSelect"
        />
        
        <!-- 进度指示器 -->
        <quantum-progress
          v-if="showProgress"
          :percentage="progress"
          :type="progressType"
          :text="progressText"
          @complete="handleComplete"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { QuantumEncryption, QuantumReconnection, QuantumQueue } from './quantum';

export default {
  data() {
    return {
      // 组件状态
      tabs: [
        { label: '量子态', closable: false },
        { label: '测量', closable: false },
        { label: '设置', closable: false }
      ],
      menuData: [
        {
          key: 'qubits',
          label: '量子比特',
          children: [/* ... */]
        },
        {
          key: 'gates',
          label: '量子门',
          children: [/* ... */]
        }
      ],
      chartData: {/* ... */},
      progress: 0,
      
      // 通信相关
      keyGenerator: null,
      encryptor: null,
      reconnManager: null,
      messageQueue: null
    };
  },
  
  created() {
    // 初始化量子通信
    this.initQuantumCommunication();
  },
  
  methods: {
    // 初始化量子通信
    initQuantumCommunication() {
      // 初始化加密
      this.keyGenerator = new QuantumEncryption.KeyGenerator();
      this.encryptor = new QuantumEncryption.Encryptor(this.keyGenerator);
      
      // 初始化重连
      this.reconnManager = new QuantumReconnection.ReconnectionManager();
      this.reconnManager.setReconnectHandler(this.handleReconnect);
      
      // 初始化消息队列
      this.messageQueue = new QuantumQueue.MessageQueue();
      this.messageQueue.registerHandler('state-update', this.handleStateUpdate);
    },
    
    // 处理重连
    async handleReconnect(attempts) {
      try {
        await this.connectToQuantumBackend();
        return true;
      } catch (error) {
        console.error('重连失败:', error);
        return false;
      }
    },
    
    // 处理状态更新
    async handleStateUpdate(data) {
      try {
        const decrypted = await this.encryptor.decrypt(data.payload, data.channelId);
        this.updateQuantumState(decrypted);
      } catch (error) {
        console.error('状态更新失败:', error);
      }
    },
    
    // 更新量子状态
    updateQuantumState(state) {
      this.chartData = this.transformStateToChartData(state);
      this.progress = this.calculateProgress(state);
    },
    
    // UI事件处理
    handleTabChange(index) {
      // 处理标签页切换
    },
    
    handleMenuSelect(key) {
      // 处理菜单选择
    },
    
    handleDataSelect(index) {
      // 处理数据点选择
    },
    
    handleComplete() {
      // 处理计算完成
    }
  }
};
</script>

<style>
.quantum-app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.quantum-content {
  display: flex;
  flex: 1;
}

.quantum-sidebar {
  width: 250px;
  border-right: 1px solid var(--quantum-border-color);
}

.quantum-main {
  flex: 1;
  padding: 20px;
}
</style>
```

这些示例展示了如何将量子UI组件和量子纠缠通信模块集成到一个完整的应用中。您可以根据实际需求调整和扩展这些示例。 