# QSM项目统一导航栏设计文档

> 量子基因编码: QG-QSM01-DOC-20250402-F7E23D-ENT8765

## 导航栏概述

QSM项目采用统一的导航栏和底部栏设计，确保用户在QSM、SOM、WeQ和Ref各子系统间无缝切换体验。导航栏在所有子系统中保持一致的样式、结构和交互方式，提供全面的功能访问和系统切换能力。

## 导航栏组件结构

```
+----------------------------------------------------------------------------------------------------+
|  QSM Logo  |  主量子区块链  |  小趣模块  |  松麦模块  |  自反省模块  |  开发者中心  |  [量子态阵]  [用户] |
+----------------------------------------------------------------------------------------------------+
```

## 导航元素

### 1. 系统切换链接

导航栏中心区域包含了QSM生态系统的五大核心组件链接：

- **主量子区块链** - 链接到QSM核心功能和管理界面
  - 量子状态监控
  - 量子链浏览器
  - 系统控制面板
  
- **小趣模块(WeQ)** - 链接到量子交互系统
  - 多模态交互
  - 量子可视化
  - 生物信号处理
  
- **松麦模块(SOM)** - 链接到量子经济系统
  - 松麦子链
  - 松麦钱包
  - 松麦币
  - 生态商城
  - 追溯系统
  
- **自反省模块(Ref)** - 链接到系统自管理功能
  - 量子基因管理
  - 系统监控
  - 自动修复
  - 备份管理
  
- **开发者中心** - 链接到开发工具和文档
  - API文档
  - SDK下载
  - 开发指南
  - 示例项目

### 2. 量子态阵图

位于导航栏右侧的量子态阵图是一个交互式按钮，点击后会展开九个多模态交互选项：

```
+-------------------+
| [量子态阵] [用户]  |
+-------------------+
        |
        v
+-------------------+
| 文本 | 点击 | 声音 |
+-------------------+
| 图像 | 动作 | 视频 |
+-------------------+
| 脑波 | 文件 | 向量 |
+-------------------+
```

这些模态对应的功能：

1. **文本模式** - 自然语言对话界面，支持指令和查询
2. **点击模式** - 高级交互式界面元素和可视化控制面板
3. **声音模式** - 语音识别和控制界面
4. **图像模式** - 图像上传、分析和处理
5. **动作模式** - 手势识别和体感交互控制面板
6. **视频模式** - 视频分析和实时处理界面
7. **脑波模式** - 脑机接口实验性功能（需要专用设备）
8. **文件模式** - 文件上传和批处理工具
9. **向量模式** - 向量空间查询和相似性检索工具

## 底部栏设计

底部栏提供辅助导航和附加信息：

```
+----------------------------------------------------------------------------------------------------+
|  关于QSM  |  隐私政策  |  使用条款  |  帮助中心  |  量子基因文档  |  联系我们  |  ©2025 QSM Project  |
+----------------------------------------------------------------------------------------------------+
```

## 技术实现

### 1. 共享组件架构

导航栏和底部栏作为共享组件实现，每个子系统引用相同的源文件：

```
/QSM/templates/shared/
  ├── navigation.html      # 导航栏HTML模板
  ├── footer.html          # 底部栏HTML模板
  ├── js/
  │   ├── navigation.js    # 导航栏交互逻辑
  │   └── quantum_matrix.js # 量子态阵图交互逻辑
  └── css/
      ├── navigation.css   # 导航栏样式
      └── footer.css       # 底部栏样式
```

### 2. 实现技术规范

#### HTML结构

```html
<!-- 导航栏HTML结构 -->
<nav class="qsm-navigation">
  <div class="qsm-nav-logo">
    <a href="/"><img src="/QSM/templates/images/qsm-logo.svg" alt="QSM Logo"></a>
  </div>
  
  <div class="qsm-nav-links">
    <a href="/qsm/blockchain" class="qsm-nav-item">主量子区块链</a>
    <a href="/weq" class="qsm-nav-item">小趣模块</a>
    <a href="/som" class="qsm-nav-item">松麦模块</a>
    <a href="/ref" class="qsm-nav-item">自反省模块</a>
    <a href="/developer" class="qsm-nav-item">开发者中心</a>
  </div>
  
  <div class="qsm-nav-controls">
    <button id="quantum-matrix-btn" class="quantum-matrix-toggle">
      <span class="matrix-icon"></span>
    </button>
    <div class="user-controls">
      <a href="/login" id="login-btn" class="login-btn">登录</a>
      <div id="user-profile" class="user-profile hidden">
        <img src="/QSM/templates/images/default-avatar.png" alt="用户头像">
        <span class="username">用户名</span>
      </div>
    </div>
  </div>
</nav>

<!-- 量子态阵图HTML结构 -->
<div id="quantum-matrix-panel" class="quantum-matrix-panel hidden">
  <div class="matrix-grid">
    <div class="matrix-item" data-mode="text">文本</div>
    <div class="matrix-item" data-mode="click">点击</div>
    <div class="matrix-item" data-mode="voice">声音</div>
    <div class="matrix-item" data-mode="image">图像</div>
    <div class="matrix-item" data-mode="motion">动作</div>
    <div class="matrix-item" data-mode="video">视频</div>
    <div class="matrix-item" data-mode="brainwave">脑波</div>
    <div class="matrix-item" data-mode="file">文件</div>
    <div class="matrix-item" data-mode="vector">向量</div>
  </div>
</div>

<!-- 底部栏HTML结构 -->
<footer class="qsm-footer">
  <div class="footer-links">
    <a href="/about">关于QSM</a>
    <a href="/privacy">隐私政策</a>
    <a href="/terms">使用条款</a>
    <a href="/help">帮助中心</a>
    <a href="/docs/quantum-gene">量子基因文档</a>
    <a href="/contact">联系我们</a>
  </div>
  <div class="footer-copyright">
    &copy; 2025 QSM Project
  </div>
</footer>
```

#### JavaScript实现

```javascript
// navigation.js
class QSMNavigation {
  constructor() {
    this.matrixButton = document.getElementById('quantum-matrix-btn');
    this.matrixPanel = document.getElementById('quantum-matrix-panel');
    this.loginButton = document.getElementById('login-btn');
    this.userProfile = document.getElementById('user-profile');
    this.matrixItems = document.querySelectorAll('.matrix-item');
    
    this.initialize();
  }
  
  initialize() {
    // 绑定事件监听器
    this.matrixButton.addEventListener('click', this.toggleMatrixPanel.bind(this));
    this.matrixItems.forEach(item => {
      item.addEventListener('click', this.handleModeSelection.bind(this));
    });
    
    // 检查用户登录状态
    this.checkUserAuthentication();
    
    // 同步状态
    this.initializeSyncManager();
  }
  
  toggleMatrixPanel() {
    this.matrixPanel.classList.toggle('hidden');
    
    // 同步到其他面板
    if (window.syncManager) {
      window.syncManager.broadcastEvent({
        type: 'matrix_toggle',
        isOpen: !this.matrixPanel.classList.contains('hidden')
      });
    }
  }
  
  handleModeSelection(event) {
    const mode = event.currentTarget.getAttribute('data-mode');
    console.log(`Switching to ${mode} mode`);
    
    // 激活选中模式的处理器
    if (window.interactionManager) {
      window.interactionManager.activateMode(mode);
    }
    
    // 同步模式选择
    if (window.syncManager) {
      window.syncManager.broadcastEvent({
        type: 'mode_change',
        mode: mode
      });
    }
    
    // 关闭面板
    this.matrixPanel.classList.add('hidden');
  }
  
  checkUserAuthentication() {
    const token = localStorage.getItem('qsm_user_token');
    
    if (token) {
      try {
        // 检查令牌有效性
        const payload = this.decodeToken(token);
        if (payload && payload.exp > Date.now() / 1000) {
          this.loginButton.classList.add('hidden');
          this.userProfile.classList.remove('hidden');
          
          // 设置用户信息
          const username = document.querySelector('.username');
          username.textContent = payload.username || '用户';
          
          // 如果有头像，设置头像
          if (payload.avatar) {
            const avatar = this.userProfile.querySelector('img');
            avatar.src = payload.avatar;
          }
        } else {
          // 令牌过期，清除
          localStorage.removeItem('qsm_user_token');
        }
      } catch (e) {
        console.error('令牌解析错误', e);
        localStorage.removeItem('qsm_user_token');
      }
    }
  }
  
  decodeToken(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      return JSON.parse(window.atob(base64));
    } catch (e) {
      return null;
    }
  }
  
  initializeSyncManager() {
    // 初始化同步管理器
    if (!window.syncManager && window.SyncManager) {
      window.syncManager = new SyncManager('navigation');
      
      // 监听同步事件
      window.syncManager.onEvent((event) => {
        if (event.type === 'matrix_toggle') {
          this.matrixPanel.classList.toggle('hidden', !event.isOpen);
        } else if (event.type === 'mode_change' && window.interactionManager) {
          window.interactionManager.activateMode(event.mode);
        }
      });
    }
  }
}

// 初始化导航
document.addEventListener('DOMContentLoaded', () => {
  window.qsmNavigation = new QSMNavigation();
});
```

#### CSS样式规范

```css
/* navigation.css */
.qsm-navigation {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  background: linear-gradient(90deg, #00296B, #3A0CA3, #7209B7);
  color: white;
  padding: 0 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.qsm-nav-logo {
  display: flex;
  align-items: center;
}

.qsm-nav-logo img {
  height: 40px;
}

.qsm-nav-links {
  display: flex;
  align-items: center;
  gap: 20px;
}

.qsm-nav-item {
  color: white;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.qsm-nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.qsm-nav-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.quantum-matrix-toggle {
  background: none;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: rgba(255, 255, 255, 0.1);
  transition: background-color 0.3s;
}

.quantum-matrix-toggle:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.matrix-icon {
  width: 24px;
  height: 24px;
  background-image: url('/QSM/templates/images/quantum-matrix-icon.svg');
  background-size: contain;
  background-repeat: no-repeat;
}

.login-btn {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.15);
  transition: background-color 0.3s;
}

.login-btn:hover {
  background-color: rgba(255, 255, 255, 0.25);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.user-profile img {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.hidden {
  display: none !important;
}

/* 量子态阵图面板 */
.quantum-matrix-panel {
  position: absolute;
  top: 60px;
  right: 20px;
  background: rgba(0, 0, 0, 0.85);
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
  z-index: 1001;
}

.matrix-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 8px;
}

.matrix-item {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.matrix-item:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 底部栏样式 */
.qsm-footer {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: #0a192f;
  color: #c4c4c4;
  gap: 15px;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
}

.footer-links a {
  color: #c4c4c4;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: white;
}

.footer-copyright {
  font-size: 0.9em;
  color: #a0a0a0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .qsm-nav-links {
    display: none;
  }
  
  .qsm-navigation {
    padding: 0 12px;
  }
  
  .mobile-menu-toggle {
    display: block;
  }
  
  .matrix-item {
    width: 60px;
    height: 60px;
    font-size: 0.9em;
  }
}
```

## 使用说明

### 1. 集成到新页面

每个子系统的HTML页面中都应包含统一的导航栏和底部栏：

```html
<!DOCTYPE html>
<html>
<head>
  <title>QSM - 页面标题</title>
  <!-- 导航栏和底部栏样式 -->
  <link rel="stylesheet" href="/QSM/templates/shared/css/navigation.css">
  <link rel="stylesheet" href="/QSM/templates/shared/css/footer.css">
  <!-- 页面特定样式 -->
  <link rel="stylesheet" href="页面特定样式路径">
</head>
<body>
  <!-- 导航栏 -->
  {% include "shared/navigation.html" %}
  
  <!-- 页面特定内容 -->
  <main class="page-content">
    <!-- 页面内容 -->
  </main>
  
  <!-- 底部栏 -->
  {% include "shared/footer.html" %}
  
  <!-- 导航栏和量子态阵图脚本 -->
  <script src="/QSM/templates/shared/js/navigation.js"></script>
  <script src="/QSM/templates/shared/js/quantum_matrix.js"></script>
  <!-- 页面特定脚本 -->
  <script src="页面特定脚本路径"></script>
</body>
</html>
```

### 2. 子系统导航自定义

每个子系统可以根据需要自定义导航栏下拉菜单，但保持主导航栏结构不变：

```javascript
// 子系统导航自定义示例
window.addEventListener('DOMContentLoaded', () => {
  // 初始化基础导航
  window.qsmNavigation = new QSMNavigation();
  
  // 根据系统类型自定义导航
  const currentSystem = document.body.getAttribute('data-system');
  if (currentSystem === 'weq') {
    // 小趣特定导航设置
  } else if (currentSystem === 'som') {
    // 松麦特定导航设置
  }
});
```

## 多系统状态同步

所有子系统通过WebSocket保持导航栏和量子态阵图的状态同步：

```javascript
// 同步管理器
class SyncManager {
  constructor(sourceId) {
    this.sourceId = sourceId;
    this.socket = new WebSocket('wss://qsm-sync.example.com/ws');
    this.eventHandlers = [];
    
    this.socket.addEventListener('open', this.handleConnection.bind(this));
    this.socket.addEventListener('message', this.handleMessage.bind(this));
    this.socket.addEventListener('close', this.handleDisconnection.bind(this));
  }
  
  handleConnection() {
    console.log('Connected to sync server');
    
    // 注册为特定源
    this.socket.send(JSON.stringify({
      type: 'register',
      sourceId: this.sourceId,
      timestamp: Date.now()
    }));
  }
  
  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      
      // 如果不是自己发的消息，触发事件处理
      if (message.sourceId !== this.sourceId) {
        this.eventHandlers.forEach(handler => handler(message.event));
      }
    } catch (e) {
      console.error('同步消息解析错误', e);
    }
  }
  
  handleDisconnection() {
    console.log('Disconnected from sync server');
    
    // 尝试重连
    setTimeout(() => {
      this.socket = new WebSocket('wss://qsm-sync.example.com/ws');
      this.socket.addEventListener('open', this.handleConnection.bind(this));
      this.socket.addEventListener('message', this.handleMessage.bind(this));
      this.socket.addEventListener('close', this.handleDisconnection.bind(this));
    }, 5000);
  }
  
  broadcastEvent(event) {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({
        type: 'broadcast',
        sourceId: this.sourceId,
        event: event,
        timestamp: Date.now()
      }));
    }
  }
  
  onEvent(handler) {
    this.eventHandlers.push(handler);
  }
}
```

## 开发指南

### 1. 目录规范

统一导航栏和底部栏文件应存放在以下路径：

```
/QSM/templates/shared/  - 主源文件
/WeQ/templates/shared/  - 小趣共享组件（引用主源文件）
/SOM/templates/shared/  - 松麦共享组件（引用主源文件）
/Ref/templates/shared/  - 自反省共享组件（引用主源文件）
```

### 2. 开发流程

1. 对导航栏和底部栏的修改应首先在主源文件中进行
2. 通过自动化脚本将更改同步到各子系统
3. 使用统一的样式变量确保视觉一致性
4. 所有导航链接应经过测试，确保指向正确的目标页面

## 注意事项

1. 导航栏组件仅包含通用导航元素，不应包含特定于某个子系统的功能
2. 子系统特定的导航功能应通过自定义下拉菜单或侧边栏实现
3. 量子态阵图的九个交互模式应在所有子系统中保持一致的功能
4. 用户认证状态在所有子系统间共享，确保一次登录可访问所有功能 