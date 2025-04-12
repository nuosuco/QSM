/**
 * 简化版通知系统
 */
class NotificationSystem {
  constructor(options = {}) {
    this.options = {
      containerId: 'notification-container',
      position: 'top-right',
      defaultDuration: 5000,
      maxNotifications: 5,
      ...options
    };
    
    this.notifications = [];
    this.init();
  }
  
  init() {
    // 确保容器存在
    let container = document.getElementById(this.options.containerId);
    
    if (!container) {
      container = document.createElement('div');
      container.id = this.options.containerId;
      container.className = `notification-container ${this.options.position}`;
      document.body.appendChild(container);
    }
    
    this.container = container;
  }
  
  show(message, type = 'info', duration) {
    // 如果超出最大数量，移除最旧的通知
    if (this.notifications.length >= this.options.maxNotifications) {
      this.removeNotification(this.notifications[0]);
    }
    
    // 创建通知元素
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.setAttribute('role', 'alert');
    
    // 设置通知内容
    notification.innerHTML = `
      <div class="notification-content">
        ${message}
      </div>
      <button type="button" class="notification-close" aria-label="关闭">×</button>
    `;
    
    // 添加关闭按钮事件
    const closeButton = notification.querySelector('.notification-close');
    if (closeButton) {
      closeButton.addEventListener('click', () => {
        this.removeNotification(notification);
      });
    }
    
    // 添加到容器
    this.container.appendChild(notification);
    this.notifications.push(notification);
    
    // 添加进入动画
    setTimeout(() => {
      notification.classList.add('notification-show');
    }, 10);
    
    // 设置自动关闭
    const notificationDuration = duration || this.options.defaultDuration;
    if (notificationDuration > 0) {
      notification.timeoutId = setTimeout(() => {
        this.removeNotification(notification);
      }, notificationDuration);
    }
    
    return notification;
  }
  
  removeNotification(notification) {
    if (!notification || !this.container.contains(notification)) return;
    
    // 清除定时器
    if (notification.timeoutId) {
      clearTimeout(notification.timeoutId);
    }
    
    // 添加退出动画
    notification.classList.remove('notification-show');
    notification.classList.add('notification-hide');
    
    // 动画完成后移除元素
    setTimeout(() => {
      if (notification.parentNode === this.container) {
        this.container.removeChild(notification);
        this.notifications = this.notifications.filter(n => n !== notification);
      }
    }, 300);
  }
  
  success(message, duration) {
    return this.show(message, 'success', duration);
  }
  
  error(message, duration) {
    return this.show(message, 'error', duration);
  }
  
  warning(message, duration) {
    return this.show(message, 'warning', duration);
  }
  
  info(message, duration) {
    return this.show(message, 'info', duration);
  }
  
  clear() {
    // 清除所有通知
    this.notifications.forEach(notification => {
      this.removeNotification(notification);
    });
  }
}

// 创建全局通知系统实例
window.notificationSystem = new NotificationSystem();

// 添加一个简便的全局方法
window.showNotification = function(message, type = 'info', duration) {
  if (window.notificationSystem) {
    return window.notificationSystem.show(message, type, duration);
  }
}; 

/*
/*
量子基因编码: QE-NOT-A1DF427D981F
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
