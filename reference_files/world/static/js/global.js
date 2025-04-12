/**
 * 全局JavaScript - 量子叠加态模型系统
 * 提供所有页面共用的功能和量子纠缠信道管理
 */

// 全局命名空间
window.QSM = window.QSM || {};

// 量子纠缠信道管理
QSM.QuantumChannel = (function() {
  // 私有变量
  let isReady = false;
  let isConnecting = false;
  let channelId = null;
  let retryCount = 0;
  const maxRetries = 5;
  
  // 配置
  const config = {
    reconnectDelay: 3000, // 3秒
    heartbeatInterval: 30000, // 30秒
    debugMode: false
  };
  
  // 日志函数
  function log(...args) {
    if (config.debugMode) {
      console.log('[QSM.QuantumChannel]', ...args);
    }
  }
  
  // 错误处理
  function error(...args) {
    console.error('[QSM.QuantumChannel]', ...args);
  }
  
  // 初始化量子纠缠信道
  function init() {
    log('初始化量子纠缠信道');
    
    // 检查是否已经连接或正在连接
    if (isReady || isConnecting) {
      log('量子纠缠信道已经就绪或正在连接中');
      return;
    }
    
    isConnecting = true;
    
    // 等待WebQuantum客户端准备就绪
    waitForWebQuantum()
      .then(() => {
        log('WebQuantum客户端就绪');
        return createChannel();
      })
      .then(id => {
        log('量子纠缠信道创建成功', id);
        channelId = id;
        isReady = true;
        isConnecting = false;
        
        // 触发就绪事件
        document.dispatchEvent(new CustomEvent('quantum:ready', {
          detail: { 
            component: 'QuantumChannel',
            channelId: channelId
          }
        }));
        
        // 启动心跳
        startHeartbeat();
      })
      .catch(err => {
        error('初始化量子纠缠信道失败', err);
        isConnecting = false;
        
        // 触发错误事件
        document.dispatchEvent(new CustomEvent('quantum:error', {
          detail: { 
            component: 'QuantumChannel',
            error: err.message
          }
        }));
        
        // 尝试重连
        if (retryCount < maxRetries) {
          retryCount++;
          log(`连接失败，${config.reconnectDelay / 1000}秒后尝试重连 (${retryCount}/${maxRetries})`);
          setTimeout(init, config.reconnectDelay);
        }
      });
  }
  
  // 等待WebQuantum客户端就绪
  function waitForWebQuantum() {
    return new Promise((resolve, reject) => {
      // 如果WebQuantum已经就绪，直接返回
      if (window.webQuantumInstance && window.webQuantumInstance.isReady) {
        resolve();
        return;
      }
      
      // 设置超时
      const timeout = setTimeout(() => {
        document.removeEventListener('webquantum:entanglement:established', onWebQuantumReady);
        reject(new Error('等待WebQuantum客户端超时'));
      }, 10000);
      
      // 监听WebQuantum就绪事件
      function onWebQuantumReady() {
        clearTimeout(timeout);
        document.removeEventListener('webquantum:entanglement:established', onWebQuantumReady);
        resolve();
      }
      
      document.addEventListener('webquantum:entanglement:established', onWebQuantumReady);
    });
  }
  
  // 创建量子纠缠信道
  function createChannel() {
    return new Promise((resolve, reject) => {
      try {
        if (!window.webQuantumInstance) {
          reject(new Error('WebQuantum客户端未初始化'));
          return;
        }
        
        // 通过WebQuantum创建主纠缠信道
        window.webQuantumInstance.createEntanglementChannel('main', {
          persistent: true,
          priority: 'high',
          encryption: 'quantum'
        })
        .then(id => {
          resolve(id);
        })
        .catch(err => {
          reject(err);
        });
      } catch (err) {
        reject(err);
      }
    });
  }
  
  // 启动心跳
  function startHeartbeat() {
    if (!isReady || !channelId) {
      error('无法启动心跳，量子纠缠信道未就绪');
      return;
    }
    
    log('启动量子纠缠信道心跳');
    
    setInterval(() => {
      try {
        if (window.webQuantumInstance) {
          window.webQuantumInstance.sendThroughChannel(channelId, {
            type: 'heartbeat',
            timestamp: Date.now()
          })
          .then(() => {
            log('心跳发送成功');
          })
          .catch(err => {
            error('心跳发送失败', err);
            
            // 如果发送失败，可能信道已断开，尝试重新连接
            if (isReady) {
              isReady = false;
              channelId = null;
              retryCount = 0;
              init();
            }
          });
        }
      } catch (err) {
        error('心跳处理异常', err);
      }
    }, config.heartbeatInterval);
  }
  
  // 发送数据
  function send(data) {
    return new Promise((resolve, reject) => {
      if (!isReady || !channelId) {
        reject(new Error('量子纠缠信道未就绪'));
        return;
      }
      
      try {
        window.webQuantumInstance.sendThroughChannel(channelId, {
          type: 'message',
          data: data,
          timestamp: Date.now()
        })
        .then(result => {
          resolve(result);
        })
        .catch(err => {
          reject(err);
        });
      } catch (err) {
        reject(err);
      }
    });
  }
  
  // 接收数据处理
  function setupReceiver() {
    if (!window.webQuantumInstance) {
      error('WebQuantum客户端未初始化，无法设置接收器');
      return;
    }
    
    window.webQuantumInstance.onMessage = function(message) {
      log('收到信道消息', message);
      
      // 触发消息事件
      document.dispatchEvent(new CustomEvent('quantum:message', {
        detail: message
      }));
    };
  }
  
  // 获取状态
  function getStatus() {
    return {
      isReady: isReady,
      isConnecting: isConnecting,
      channelId: channelId
    };
  }
  
  // 公开API
  return {
    init: init,
    getStatus: getStatus,
    send: send,
    setupReceiver: setupReceiver
  };
})();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
  // 初始化量子纠缠信道
  QSM.QuantumChannel.init();
  QSM.QuantumChannel.setupReceiver();
  
  // 初始化页面导航
  initNavigation();
  
  // 初始化暗色模式切换
  initDarkModeToggle();
});

// 初始化页面导航
function initNavigation() {
  const navLinks = document.querySelectorAll('nav a');
  
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      const target = this.getAttribute('href');
      
      // 如果是锚点链接，滚动到目标位置
      if (target.startsWith('#')) {
        e.preventDefault();
        
        const targetElement = document.querySelector(target);
        if (targetElement) {
          targetElement.scrollIntoView({
            behavior: 'smooth'
          });
        }
        
        // 更新活动链接
        navLinks.forEach(l => l.classList.remove('active'));
        this.classList.add('active');
      }
    });
    
    // 检查当前页面路径，设置当前活动链接
    const currentPath = window.location.pathname;
    const linkPath = link.getAttribute('href');
    
    if (linkPath === currentPath || 
        (currentPath.endsWith('/') && linkPath === currentPath.slice(0, -1)) ||
        (!currentPath.endsWith('/') && linkPath === currentPath + '/')) {
      navLinks.forEach(l => l.classList.remove('active'));
      link.classList.add('active');
    }
  });
}

// 初始化暗色模式切换
function initDarkModeToggle() {
  const darkModeToggle = document.getElementById('dark-mode-toggle');
  
  if (darkModeToggle) {
    // 检查本地存储中的偏好
    const darkModePreference = localStorage.getItem('darkMode');
    
    // 如果之前设置过，应用该设置
    if (darkModePreference === 'true') {
      document.documentElement.classList.add('dark-mode');
      darkModeToggle.checked = true;
    }
    
    // 切换事件处理
    darkModeToggle.addEventListener('change', function() {
      if (this.checked) {
        document.documentElement.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'true');
      } else {
        document.documentElement.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'false');
      }
    });
  }
}



/*
/*
量子基因编码: QE-GLO-97865305F274
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
