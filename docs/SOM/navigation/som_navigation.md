# 松麦系统导航设计

## 导航栏组件结构

> 量子基因编码: QG-QSM01-DOC-20250401204433-28A90D-ENT2298


松麦系统采用统一的导航栏设计，确保用户在各个子系统间无缝切换体验。导航栏在所有松麦子系统中保持一致的样式和交互方式。

```
+----------------------------------------------------------------------------------------------------+
|  松麦Logo  |  主量子区块链  |  松麦子链  |  追溯系统  |  松麦钱包  |  松麦币  |  生态商城  |  [量子态阵]  [登录] |
+----------------------------------------------------------------------------------------------------+
```

## 导航元素

### 1. 系统切换链接

导航栏中心区域包含了松麦生态系统的六大核心组件链接：

- **主量子区块链** - 链接到区块链浏览器和管理界面
- **松麦子链** - 链接到子链运行状态和交易查询
- **追溯系统** - 链接到产品溯源查询和验证界面
- **松麦钱包** - 链接到用户钱包管理界面
- **松麦币** - 链接到币值和经济数据展示界面
- **生态商城** - 链接到松麦生态商品交易平台

### 2. 量子态阵图

位于导航栏右侧的量子态阵图是一个交互式按钮，点击后会展开九个多模态交互选项：

```
+-------------------+
| [量子态阵] [登录]  |
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

## 多模态交互集成

量子态阵图激活后的九个交互模式功能如下：

1. **文本模式** - 自然语言对话界面，支持指令和查询
2. **点击模式** - 高级交互式界面元素和可视化控制面板
3. **声音模式** - 语音识别和控制界面
4. **图像模式** - 图像上传、分析和产品扫描识别
5. **动作模式** - 手势识别和体感交互控制面板
6. **视频模式** - 视频分析和实时处理界面
7. **脑波模式** - 脑机接口实验性功能（需要专用设备）
8. **文件模式** - 文件上传和批处理工具
9. **向量模式** - 向量空间查询和相似性检索工具

## 实现技术规范

### 前端架构

```javascript
// 导航栏组件示例结构
class SomNavigationBar extends Component {
  constructor(props) {
    super(props);
    this.state = {
      currentSystem: props.currentSystem || 'main',
      quantumMatrixOpen: false,
      userLoggedIn: !!localStorage.getItem('som_user_token')
    };
  }
  
  toggleQuantumMatrix = () => {
    this.setState({ quantumMatrixOpen: !this.state.quantumMatrixOpen });
  }
  
  // 其他导航方法...
}
```

### 同步更新机制

导航栏及多模态交互面板在以下三处保持同步：

1. **QSM首页交互面板**
2. **QSM导航栏弹窗**
3. **松麦系统导航栏弹窗**

同步采用基于WebSocket的实时更新机制：

```javascript
// 同步机制示例代码
const syncChannels = [
  'qsm_interaction_panel',
  'qsm_nav_modal',
  'som_nav_modal'
];

function broadcastModalUpdate(update, sourceChannel) {
  syncChannels.forEach(channel => {
    if (channel !== sourceChannel) {
      ws.send(JSON.stringify({
        target: channel,
        action: 'update_modal',
        data: update
      }));
    }
  });
}
```

## 用户身份集成

用户登录状态在QSM和SOM系统间共享，使用JWT令牌实现无缝身份验证：

```javascript
// 身份验证集成
function checkUserAuth() {
  const token = localStorage.getItem('user_token');
  
  if (!token) return false;
  
  // 验证令牌有效性
  try {
    const payload = jwt_decode(token);
    return payload.exp > Date.now() / 1000;
  } catch (e) {
    return false;
  }
}
```

## 导航设计原则

1. **一致性** - 所有子系统保持相同的导航栏位置、样式和交互方式
2. **简洁性** - 导航元素精简、清晰，避免过多选项造成混淆
3. **响应性** - 导航栏适应不同设备屏幕尺寸
4. **交互同步** - 多处交互界面保持状态同步，确保体验一致性
5. **用户中心** - 用户登录状态和偏好设置全局共享 