/**
 * 量子纠缠通信JavaScript
 * 提供跨模块的量子纠缠通信功能
 */

// 量子纠缠通信类
class QuantumEntanglement {
  constructor() {
    // 初始化量子纠缠信息
    this.deviceQuantumGene = this.generateQuantumGene('DEVICE');
    this.sessionQuantumGene = this.generateQuantumGene('SESSION');
    this.registeredChannels = [];
    this.activeModels = ['QSM', 'WeQ', 'SOM', 'Ref'];
    this.connectedModels = [];
    this.isInitialized = false;
    
    // 初始化事件监听器
    this.eventListeners = {};
    
    // 存储UI引用
    this.ui = null;
    
    // 记录当前应用信息
    this.currentModel = this.detectCurrentModel();
    
    // 初始化状态
    this.state = {
      entanglementStatus: 'disconnected', // disconnected, connecting, connected
      signalStrength: 0,
      lastActivity: null,
      entanglementLevel: 0,
      quantumComputing: false,
      parallelComputing: false
    };
  }
  
  /**
   * 初始化量子纠缠通信
   */
  init() {
    if (this.isInitialized) return;
    
    console.log('量子纠缠通信初始化中...');
    
    // 注册量子纠缠信道
    this.registerQuantumChannel();
    
    // 初始化自动重连机制
    this.initReconnection();
    
    // 初始化跨窗口通信
    this.initCrossWindowCommunication();
    
    // 添加页面卸载事件
    window.addEventListener('beforeunload', () => {
      this.disconnectChannel();
    });
    
    this.isInitialized = true;
    
    // 触发初始化完成事件
    this.triggerEvent('initialized', {
      deviceQuantumGene: this.deviceQuantumGene,
      sessionQuantumGene: this.sessionQuantumGene,
      model: this.currentModel
    });
  }
  
  /**
   * 生成量子基因编码
   */
  generateQuantumGene(type) {
    const timestamp = new Date().getTime().toString(36).toUpperCase();
    const randomPart = Math.random().toString(36).substring(2, 10).toUpperCase();
    return `QG-${type}-${timestamp}-${randomPart}`;
  }
  
  /**
   * 检测当前模型
   */
  detectCurrentModel() {
    const path = window.location.pathname;
    
    for (const model of this.activeModels) {
      if (path.includes(`/${model}/`)) {
        return model;
      }
    }
    
    // 默认为QSM
    return 'QSM';
  }
  
  /**
   * 注册量子纠缠信道
   */
  registerQuantumChannel() {
    this.updateState({ entanglementStatus: 'connecting' });
    
    // 模拟API请求
    setTimeout(() => {
      // 模拟成功响应
      const channelId = 'ch-' + Math.random().toString(36).substring(2, 10);
      const channel = {
        id: channelId,
        type: 'quantum_entanglement',
        strength: Math.random() * 0.2 + 0.8,
        established: new Date().toISOString(),
        expires: null,
        source: this.deviceQuantumGene,
        target: `QG-SERVER-${this.currentModel}-${Date.now().toString(36)}`
      };
      
      // 存储信道信息
      this.registeredChannels.push(channel);
      
      // 更新状态
      this.updateState({
        entanglementStatus: 'connected',
        signalStrength: channel.strength,
        lastActivity: channel.established,
        entanglementLevel: this.registeredChannels.length * 0.25
      });
      
      // 触发连接成功事件
      this.triggerEvent('connected', {
        channel: channel,
        model: this.currentModel
      });
      
      // 随机决定是否开启量子计算功能
      if (Math.random() > 0.3) {
        setTimeout(() => {
          this.enableQuantumComputing();
        }, 2000);
      }
      
      // 如果有多个信道，随机决定是否开启并行计算
      if (this.registeredChannels.length > 1 && Math.random() > 0.5) {
        setTimeout(() => {
          this.enableParallelComputing();
        }, 3000);
      }
    }, 1500);
  }
  
  /**
   * 断开信道连接
   */
  disconnectChannel(channelId) {
    if (channelId) {
      // 断开特定信道
      this.registeredChannels = this.registeredChannels.filter(channel => channel.id !== channelId);
    } else {
      // 断开所有信道
      this.registeredChannels = [];
    }
    
    // 更新状态
    if (this.registeredChannels.length === 0) {
      this.updateState({
        entanglementStatus: 'disconnected',
        signalStrength: 0,
        entanglementLevel: 0,
        quantumComputing: false,
        parallelComputing: false
      });
      
      // 触发断开连接事件
      this.triggerEvent('disconnected', {
        model: this.currentModel
      });
    } else {
      // 还有活跃信道，更新状态
      this.updateState({
        entanglementLevel: this.registeredChannels.length * 0.25
      });
    }
  }
  
  /**
   * 初始化重连机制
   */
  initReconnection() {
    // 监听网络状态变化
    window.addEventListener('online', () => {
      if (this.state.entanglementStatus === 'disconnected') {
        this.registerQuantumChannel();
      }
    });
    
    // 周期性检查连接状态
    setInterval(() => {
      if (this.state.entanglementStatus === 'disconnected' && navigator.onLine) {
        this.registerQuantumChannel();
      }
    }, 30000);
  }
  
  /**
   * 初始化跨窗口通信
   */
  initCrossWindowCommunication() {
    // 使用BroadcastChannel API进行跨窗口通信（如果浏览器支持）
    if (typeof BroadcastChannel !== 'undefined') {
      this.broadcastChannel = new BroadcastChannel('quantum_entanglement_channel');
      
      // 监听来自其他窗口的消息
      this.broadcastChannel.onmessage = (event) => {
        this.handleExternalMessage(event.data);
      };
    } else {
      // 降级为使用localStorage进行跨窗口通信
      window.addEventListener('storage', (event) => {
        if (event.key === 'quantum_entanglement_message') {
          try {
            const message = JSON.parse(event.newValue);
            this.handleExternalMessage(message);
          } catch (e) {
            console.error('解析量子纠缠消息失败:', e);
          }
        }
      });
    }
  }
  
  /**
   * 处理外部消息
   */
  handleExternalMessage(message) {
    if (!message || !message.type) return;
    
    switch (message.type) {
      case 'quantum_state_update':
        // 更新本地量子状态
        this.updateState(message.state);
        break;
        
      case 'model_connected':
        // 更新已连接模型列表
        if (!this.connectedModels.includes(message.model)) {
          this.connectedModels.push(message.model);
          this.triggerEvent('model_connected', { model: message.model });
        }
        break;
        
      case 'model_disconnected':
        // 从已连接模型列表中移除
        this.connectedModels = this.connectedModels.filter(model => model !== message.model);
        this.triggerEvent('model_disconnected', { model: message.model });
        break;
        
      case 'quantum_computing_enabled':
        // 开启量子计算
        this.state.quantumComputing = true;
        this.triggerEvent('quantum_computing_enabled');
        break;
        
      case 'parallel_computing_enabled':
        // 开启并行计算
        this.state.parallelComputing = true;
        this.triggerEvent('parallel_computing_enabled');
        break;
    }
  }
  
  /**
   * 发送跨窗口消息
   */
  sendCrossWindowMessage(message) {
    if (typeof BroadcastChannel !== 'undefined' && this.broadcastChannel) {
      this.broadcastChannel.postMessage(message);
    } else {
      // 使用localStorage进行通信
      localStorage.setItem('quantum_entanglement_message', JSON.stringify(message));
      
      // 清除存储，以便下次更新能够触发事件
      setTimeout(() => {
        localStorage.removeItem('quantum_entanglement_message');
      }, 100);
    }
  }
  
  /**
   * 开启量子计算功能
   */
  enableQuantumComputing() {
    if (this.state.quantumComputing) return;
    
    this.updateState({ quantumComputing: true });
    
    // 触发量子计算开启事件
    this.triggerEvent('quantum_computing_enabled', {
      model: this.currentModel
    });
    
    // 通知其他窗口
    this.sendCrossWindowMessage({
      type: 'quantum_computing_enabled',
      model: this.currentModel
    });
  }
  
  /**
   * 开启并行计算功能
   */
  enableParallelComputing() {
    if (this.state.parallelComputing) return;
    
    this.updateState({ parallelComputing: true });
    
    // 触发并行计算开启事件
    this.triggerEvent('parallel_computing_enabled', {
      model: this.currentModel
    });
    
    // 通知其他窗口
    this.sendCrossWindowMessage({
      type: 'parallel_computing_enabled',
      model: this.currentModel
    });
  }
  
  /**
   * 更新状态
   */
  updateState(newState) {
    // 更新状态
    this.state = { ...this.state, ...newState };
    
    // 如果有UI，更新UI
    if (this.ui) {
      this.ui.updateDisplay(this.state);
    }
    
    // 触发状态更新事件
    this.triggerEvent('state_updated', this.state);
  }
  
  /**
   * 发送量子纠缠消息
   */
  sendMessage(targetModel, message, callback) {
    if (this.state.entanglementStatus !== 'connected') {
      console.error('量子纠缠信道未连接，无法发送消息');
      return false;
    }
    
    // 准备消息数据
    const messageData = {
      channelId: this.registeredChannels[0]?.id,
      sourceModel: this.currentModel,
      targetModel: targetModel,
      content: message,
      timestamp: new Date().toISOString(),
      quantum_signature: this.generateQuantumSignature()
    };
    
    // 模拟消息发送延迟
    setTimeout(() => {
      // 更新最后活动时间
      this.updateState({
        lastActivity: messageData.timestamp
      });
      
      // 触发消息发送事件
      this.triggerEvent('message_sent', messageData);
      
      // 通知其他窗口
      this.sendCrossWindowMessage({
        type: 'quantum_message',
        message: messageData
      });
      
      // 如果提供了回调，调用回调
      if (typeof callback === 'function') {
        callback({
          success: true,
          messageId: `msg-${Date.now().toString(36)}`,
          timestamp: messageData.timestamp
        });
      }
    }, 300);
    
    return true;
  }
  
  /**
   * 生成量子签名
   */
  generateQuantumSignature() {
    const randomBytes = new Uint8Array(16);
    for (let i = 0; i < randomBytes.length; i++) {
      randomBytes[i] = Math.floor(Math.random() * 256);
    }
    
    return Array.from(randomBytes)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }
  
  /**
   * 添加事件监听器
   */
  addEventListener(eventName, callback) {
    if (!this.eventListeners[eventName]) {
      this.eventListeners[eventName] = [];
    }
    
    this.eventListeners[eventName].push(callback);
  }
  
  /**
   * 移除事件监听器
   */
  removeEventListener(eventName, callback) {
    if (!this.eventListeners[eventName]) return;
    
    this.eventListeners[eventName] = this.eventListeners[eventName]
      .filter(cb => cb !== callback);
  }
  
  /**
   * 触发事件
   */
  triggerEvent(eventName, data) {
    if (!this.eventListeners[eventName]) return;
    
    for (const callback of this.eventListeners[eventName]) {
      try {
        callback(data);
      } catch (e) {
        console.error(`量子纠缠事件 ${eventName} 处理出错:`, e);
      }
    }
  }
  
  /**
   * 设置UI引用
   */
  setUI(uiInstance) {
    this.ui = uiInstance;
    
    // 更新UI显示
    if (this.ui) {
      this.ui.updateDisplay(this.state);
    }
  }
  
  /**
   * 获取状态信息
   */
  getStatus() {
    return { ...this.state };
  }
  
  /**
   * 获取连接信息
   */
  getConnectionInfo() {
    return {
      deviceQuantumGene: this.deviceQuantumGene,
      sessionQuantumGene: this.sessionQuantumGene,
      currentModel: this.currentModel,
      channels: [...this.registeredChannels],
      connectedModels: [...this.connectedModels]
    };
  }
}

// 量子纠缠UI类
class QuantumEntanglementUI {
  constructor(entanglement) {
    this.entanglement = entanglement;
    this.container = null;
    
    // 初始化时注册到纠缠实例
    if (this.entanglement) {
      this.entanglement.setUI(this);
    }
  }
  
  /**
   * 创建UI
   */
  createUI(targetElement) {
    // 如果已有容器，则返回
    if (this.container) return;
    
    // 创建UI容器
    this.container = document.createElement('div');
    this.container.className = 'quantum-entanglement-ui';
    this.container.style.position = 'fixed';
    this.container.style.bottom = '20px';
    this.container.style.right = '20px';
    this.container.style.zIndex = '9999';
    this.container.style.background = 'rgba(0, 0, 0, 0.7)';
    this.container.style.borderRadius = '5px';
    this.container.style.padding = '10px';
    this.container.style.color = '#fff';
    this.container.style.fontFamily = 'monospace';
    this.container.style.fontSize = '12px';
    this.container.style.boxShadow = '0 0 10px rgba(0, 100, 255, 0.7)';
    this.container.style.transition = 'all 0.3s ease';
    
    // 创建状态指示器
    this.statusIndicator = document.createElement('div');
    this.statusIndicator.className = 'quantum-status-indicator';
    this.statusIndicator.style.width = '10px';
    this.statusIndicator.style.height = '10px';
    this.statusIndicator.style.borderRadius = '50%';
    this.statusIndicator.style.backgroundColor = '#f00';
    this.statusIndicator.style.display = 'inline-block';
    this.statusIndicator.style.marginRight = '5px';
    
    // 创建状态文本
    this.statusText = document.createElement('div');
    this.statusText.className = 'quantum-status-text';
    this.statusText.style.display = 'inline-block';
    this.statusText.textContent = '量子纠缠信道: 未连接';
    
    // 创建详情容器
    this.detailsContainer = document.createElement('div');
    this.detailsContainer.className = 'quantum-details-container';
    this.detailsContainer.style.marginTop = '5px';
    this.detailsContainer.style.display = 'none';
    
    // 添加信号强度
    this.signalStrength = document.createElement('div');
    this.signalStrength.className = 'quantum-signal-strength';
    this.signalStrength.textContent = '信号强度: 0%';
    this.detailsContainer.appendChild(this.signalStrength);
    
    // 添加纠缠级别
    this.entanglementLevel = document.createElement('div');
    this.entanglementLevel.className = 'quantum-entanglement-level';
    this.entanglementLevel.textContent = '纠缠级别: 0';
    this.detailsContainer.appendChild(this.entanglementLevel);
    
    // 添加量子计算状态
    this.quantumComputing = document.createElement('div');
    this.quantumComputing.className = 'quantum-computing-status';
    this.quantumComputing.textContent = '量子计算: 未启用';
    this.detailsContainer.appendChild(this.quantumComputing);
    
    // 添加并行计算状态
    this.parallelComputing = document.createElement('div');
    this.parallelComputing.className = 'parallel-computing-status';
    this.parallelComputing.textContent = '量子并行计算: 未启用';
    this.detailsContainer.appendChild(this.parallelComputing);
    
    // 添加最后活动时间
    this.lastActivity = document.createElement('div');
    this.lastActivity.className = 'quantum-last-activity';
    this.lastActivity.textContent = '最后活动: 无';
    this.detailsContainer.appendChild(this.lastActivity);
    
    // 添加切换按钮
    this.toggleButton = document.createElement('div');
    this.toggleButton.className = 'quantum-toggle-button';
    this.toggleButton.textContent = '显示详情';
    this.toggleButton.style.marginTop = '5px';
    this.toggleButton.style.cursor = 'pointer';
    this.toggleButton.style.textDecoration = 'underline';
    this.toggleButton.style.color = '#3f3';
    this.toggleButton.style.textAlign = 'center';
    
    // 添加事件监听器
    this.toggleButton.addEventListener('click', () => {
      if (this.detailsContainer.style.display === 'none') {
        this.detailsContainer.style.display = 'block';
        this.toggleButton.textContent = '隐藏详情';
      } else {
        this.detailsContainer.style.display = 'none';
        this.toggleButton.textContent = '显示详情';
      }
    });
    
    // 组装UI
    this.container.appendChild(this.statusIndicator);
    this.container.appendChild(this.statusText);
    this.container.appendChild(this.detailsContainer);
    this.container.appendChild(this.toggleButton);
    
    // 添加到目标元素
    if (targetElement) {
      targetElement.appendChild(this.container);
    } else {
      document.body.appendChild(this.container);
    }
    
    // 如果已有状态，更新UI
    if (this.entanglement) {
      this.updateDisplay(this.entanglement.getStatus());
    }
  }
  
  /**
   * 更新显示
   */
  updateDisplay(state) {
    if (!this.container) return;
    
    // 更新状态指示器颜色
    switch (state.entanglementStatus) {
      case 'connected':
        this.statusIndicator.style.backgroundColor = '#0f0';
        this.statusText.textContent = '量子纠缠信道: 已连接';
        break;
      case 'connecting':
        this.statusIndicator.style.backgroundColor = '#ff0';
        this.statusText.textContent = '量子纠缠信道: 连接中...';
        break;
      case 'disconnected':
        this.statusIndicator.style.backgroundColor = '#f00';
        this.statusText.textContent = '量子纠缠信道: 未连接';
        break;
    }
    
    // 更新信号强度
    const signalPercent = Math.floor(state.signalStrength * 100);
    this.signalStrength.textContent = `信号强度: ${signalPercent}%`;
    
    // 更新纠缠级别
    const levelPercent = Math.floor(state.entanglementLevel * 100);
    this.entanglementLevel.textContent = `纠缠级别: ${levelPercent}%`;
    
    // 更新量子计算状态
    this.quantumComputing.textContent = `量子计算: ${state.quantumComputing ? '已启用' : '未启用'}`;
    if (state.quantumComputing) {
      this.quantumComputing.style.color = '#0f0';
    } else {
      this.quantumComputing.style.color = '#fff';
    }
    
    // 更新并行计算状态
    this.parallelComputing.textContent = `量子并行计算: ${state.parallelComputing ? '已启用' : '未启用'}`;
    if (state.parallelComputing) {
      this.parallelComputing.style.color = '#0f0';
    } else {
      this.parallelComputing.style.color = '#fff';
    }
    
    // 更新最后活动时间
    if (state.lastActivity) {
      const date = new Date(state.lastActivity);
      const formattedTime = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`;
      this.lastActivity.textContent = `最后活动: ${formattedTime}`;
    } else {
      this.lastActivity.textContent = '最后活动: 无';
    }
    
    // 添加闪烁效果
    if (state.entanglementStatus === 'connected') {
      this.container.style.boxShadow = '0 0 15px rgba(0, 255, 100, 0.7)';
      setTimeout(() => {
        this.container.style.boxShadow = '0 0 10px rgba(0, 100, 255, 0.7)';
      }, 300);
    }
  }
}

// 全局实例
const quantumEntanglement = new QuantumEntanglement();

// 在DOMContentLoaded事件中初始化
document.addEventListener('DOMContentLoaded', function() {
  // 初始化量子纠缠通信
  quantumEntanglement.init();
  
  // 创建UI（如果在非控制台页面）
  if (!window.location.pathname.includes('/quantum_entanglement_comm')) {
    const ui = new QuantumEntanglementUI(quantumEntanglement);
    ui.createUI();
  }
});

// 导出全局实例
window.quantumEntanglement = quantumEntanglement; 

/*
/*
量子基因编码: QE-QUA-810A84702E51
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
