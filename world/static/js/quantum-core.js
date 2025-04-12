/**
 * 量子核心脚本 - 简化版
 * 用于处理量子状态矩阵和多模态交互功能
 */

// 全局量子核心对象
const quantumCore = {
  // 配置选项
  config: {
    debugMode: true,
    matrixButtonId: 'quantum-matrix-button',
    matrixContainerId: 'quantum-matrix-container',
    matrixCloseId: 'quantum-matrix-close',
    matrixOverlayId: 'quantum-matrix-overlay',
    matrixGridId: 'quantum-matrix-grid',
    statusIndicatorId: 'quantum-channel-status',
    notificationContainerId: 'notification-container'
  },
  
  // 状态变量
  state: {
    isMatrixOpen: false,
    activeMode: null,
    isChannelConnected: false
  },
  
  /**
   * 初始化量子核心
   */
  init: function() {
    if (this.config.debugMode) {
      console.log('量子核心: 初始化开始');
    }
    
    // 绑定矩阵按钮事件
    this.bindMatrixButtonEvents();
    
    // 加载量子通道
    this.loadQuantumChannel();
    
    // 导出全局对象
    window.quantumCore = this;
    
    if (this.config.debugMode) {
      console.log('量子核心: 初始化完成');
    }
  },
  
  /**
   * 绑定量子状态矩阵按钮事件
   */
  bindMatrixButtonEvents: function() {
    // 获取按钮元素
    const matrixButton = document.getElementById(this.config.matrixButtonId);
    if (!matrixButton) {
      if (this.config.debugMode) {
        console.warn('量子核心: 找不到量子状态矩阵按钮');
      }
      return;
    }
    
    // 绑定点击事件
    matrixButton.addEventListener('click', (e) => {
      e.preventDefault();
      this.toggleMatrix();
    });
    
    // 获取关闭按钮
    const closeButton = document.getElementById(this.config.matrixCloseId);
    if (closeButton) {
      closeButton.addEventListener('click', (e) => {
        e.preventDefault();
        this.closeMatrix();
      });
    }
    
    // 获取遮罩层
    const overlay = document.getElementById(this.config.matrixOverlayId);
    if (overlay) {
      overlay.addEventListener('click', () => {
        this.closeMatrix();
      });
    }
    
    // 初始化矩阵单元格事件
    this.initMatrixCells();
  },
  
  /**
   * 初始化矩阵单元格事件
   */
  initMatrixCells: function() {
    const matrixGrid = document.getElementById(this.config.matrixGridId);
    if (!matrixGrid) return;
    
    // 获取所有单元格
    const cells = matrixGrid.querySelectorAll('.matrix-cell');
    cells.forEach(cell => {
      cell.addEventListener('click', () => {
        const mode = cell.getAttribute('data-mode');
        if (mode) {
          this.activateMode(mode);
        }
      });
    });
  },
  
  /**
   * 切换量子状态矩阵显示
   */
  toggleMatrix: function() {
    if (this.state.isMatrixOpen) {
      this.closeMatrix();
    } else {
      this.openMatrix();
    }
  },
  
  /**
   * 打开量子状态矩阵
   */
  openMatrix: function() {
    const container = document.getElementById(this.config.matrixContainerId);
    const overlay = document.getElementById(this.config.matrixOverlayId);
    
    if (!container) return;
    
    container.style.display = 'block';
    if (overlay) overlay.style.display = 'block';
    
    setTimeout(() => {
      container.classList.add('matrix-open');
      if (overlay) overlay.classList.add('overlay-visible');
    }, 10);
    
    this.state.isMatrixOpen = true;
    
    this.showNotification('量子状态矩阵已激活', 'info');
  },
  
  /**
   * 关闭量子状态矩阵
   */
  closeMatrix: function() {
    const container = document.getElementById(this.config.matrixContainerId);
    const overlay = document.getElementById(this.config.matrixOverlayId);
    
    if (!container) return;
    
    container.classList.remove('matrix-open');
    if (overlay) overlay.classList.remove('overlay-visible');
    
    setTimeout(() => {
      container.style.display = 'none';
      if (overlay) overlay.style.display = 'none';
    }, 300); // 与CSS过渡时间一致
    
    this.state.isMatrixOpen = false;
  },
  
  /**
   * 激活特定模式
   * @param {string} mode 模式名称
   */
  activateMode: function(mode) {
    if (this.state.activeMode === mode) return;
    
    // 记录当前激活模式
    this.state.activeMode = mode;
    
    // 更新所有单元格状态
    const matrixGrid = document.getElementById(this.config.matrixGridId);
    if (matrixGrid) {
      const cells = matrixGrid.querySelectorAll('.matrix-cell');
      cells.forEach(cell => {
        const cellMode = cell.getAttribute('data-mode');
        if (cellMode === mode) {
          cell.classList.add('active');
        } else {
          cell.classList.remove('active');
        }
      });
    }
    
    // 显示激活通知
    const modeName = this.getModeDisplayName(mode);
    this.showNotification(`已激活量子模式: ${modeName}`, 'success');
    
    // 关闭矩阵弹窗
    setTimeout(() => {
      this.closeMatrix();
    }, 500);
  },
  
  /**
   * 获取模式显示名称
   * @param {string} mode 模式代码
   * @return {string} 显示名称
   */
  getModeDisplayName: function(mode) {
    const modeNames = {
      'superposition': '叠加态',
      'entanglement': '纠缠态',
      'coherence': '相干态',
      'decoherence': '退相干态',
      'teleportation': '量子隐形传态',
      'tunneling': '量子隧穿',
      'interference': '量子干涉',
      'collapse': '波函数坍缩',
      'measurement': '量子测量'
    };
    
    return modeNames[mode] || mode;
  },
  
  /**
   * 加载量子通道
   */
  loadQuantumChannel: function() {
    // 检查量子通道状态指示器
    const statusIndicator = document.getElementById(this.config.statusIndicatorId);
    if (!statusIndicator) {
      if (this.config.debugMode) {
        console.warn('量子核心: 找不到量子通道状态指示器');
      }
      return;
    }
    
    // 模拟连接过程
    setTimeout(() => {
      this.state.isChannelConnected = true;
      statusIndicator.classList.add('status-connected');
      statusIndicator.classList.add('pulse');
      statusIndicator.setAttribute('title', '量子通道已连接');
      
      this.showNotification('量子通道已连接', 'success');
    }, 2000);
  },
  
  /**
   * 显示通知
   * @param {string} message 通知消息
   * @param {string} type 通知类型 (info, success, warning, error)
   */
  showNotification: function(message, type = 'info') {
    // 使用全局通知系统（如果可用）
    if (window.showNotification) {
      window.showNotification(message, type);
      return;
    }
    
    // 否则创建一个简单的通知
    const container = document.getElementById(this.config.notificationContainerId);
    if (!container) return;
    
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">${message}</div>
      <button class="notification-close">×</button>
    `;
    
    // 添加关闭按钮事件
    const closeButton = notification.querySelector('.notification-close');
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        notification.classList.add('notification-hide');
        setTimeout(() => {
          if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
          }
        }, 300);
      });
    }
    
    // 添加到容器
    container.appendChild(notification);
    
    // 添加进入动画
    setTimeout(() => {
      notification.classList.add('notification-show');
    }, 10);
    
    // 设置自动关闭
    setTimeout(() => {
      notification.classList.add('notification-hide');
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 5000);
  }
};

// 在DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
  quantumCore.init();
}); 

/*
/*
量子基因编码: QE-QUA-AD78A32DE66B
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
