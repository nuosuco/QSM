# 量子UI组件API文档

## 量子标签页组件 (QuantumTabs)

### 属性
| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| tabs | Array | [] | 标签页配置数组,每项包含label和closable属性 |
| content | Array | [] | 标签页内容数组 |
| allowAdd | Boolean | false | 是否允许添加标签页 |

### 事件
| 事件名 | 参数 | 说明 |
|--------|------|------|
| tab-change | index | 标签页切换时触发 |
| tab-close | index | 关闭标签页时触发 |
| tab-add | - | 点击添加标签页按钮时触发 |

### 示例
```html
<quantum-tabs
  :tabs="[
    { label: '标签1', closable: true },
    { label: '标签2', closable: false }
  ]"
  :content="['内容1', '内容2']"
  :allow-add="true"
  @tab-change="handleTabChange"
  @tab-close="handleTabClose"
  @tab-add="handleTabAdd"
/>
```

## 量子树形控件 (QuantumTree)

### 属性
| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| data | Array | - | 树形数据数组,每项包含key、label、children等属性 |

### 事件
| 事件名 | 参数 | 说明 |
|--------|------|------|
| node-toggle | key | 节点展开/收起时触发 |
| node-select | key | 节点选中时触发 |

### 示例
```html
<quantum-tree
  :data="[{
    key: '1',
    label: '节点1',
    children: [{
      key: '1-1',
      label: '子节点1'
    }]
  }]"
  @node-toggle="handleNodeToggle"
  @node-select="handleNodeSelect"
/>
```

## 量子图表组件 (QuantumChart)

### 属性
| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| type | String | 'line' | 图表类型,支持line/bar/pie等 |
| data | Object | - | 图表数据对象,包含labels和datasets |
| options | Object | {} | 图表配置选项 |

### 事件
| 事件名 | 参数 | 说明 |
|--------|------|------|
| data-select | index | 数据点被选中时触发 |

### 示例
```html
<quantum-chart
  type="line"
  :data="{
    labels: ['A', 'B', 'C'],
    datasets: [{
      data: [10, 20, 30]
    }]
  }"
  :options="{
    responsive: true,
    maintainAspectRatio: false
  }"
  @data-select="handleDataSelect"
/>
```

## 量子进度条组件 (QuantumProgress)

### 属性
| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| percentage | Number | - | 进度百分比(0-100) |
| type | String | 'default' | 进度条类型,支持default/success/warning/error |
| text | String | '' | 自定义显示文本 |
| showInfo | Boolean | true | 是否显示进度信息 |

### 事件
| 事件名 | 参数 | 说明 |
|--------|------|------|
| change | value | 进度变化时触发 |
| complete | - | 进度达到100%时触发 |

### 示例
```html
<quantum-progress
  :percentage="50"
  type="success"
  text="正在处理..."
  :show-info="true"
  @change="handleProgressChange"
  @complete="handleProgressComplete"
/>
```

## 量子纠缠通信

### 加密模块 (QuantumEncryption)

#### KeyGenerator
用于生成和管理量子密钥对:
```javascript
const keyGenerator = new QuantumEncryption.KeyGenerator();
const { publicKey, privateKey } = keyGenerator.generateKeyPair(channelId);
```

#### Encryptor
用于加密和解密消息:
```javascript
const encryptor = new QuantumEncryption.Encryptor(keyGenerator);
const encrypted = await encryptor.encrypt(message, channelId);
const decrypted = await encryptor.decrypt(encrypted, channelId);
```

#### Signature
用于消息签名和验证:
```javascript
const signature = new QuantumEncryption.Signature(keyGenerator);
const sign = signature.sign(message, channelId);
const isValid = signature.verify(message, sign, channelId);
```

### 重连模块 (QuantumReconnection)

#### ReconnectionManager
管理断线重连:
```javascript
const reconnManager = new QuantumReconnection.ReconnectionManager({
  maxAttempts: 5,
  initialDelay: 1000
});

reconnManager.setReconnectHandler(async (attempts) => {
  // 处理重连
});
```

#### Heartbeat
心跳检测:
```javascript
const heartbeat = new QuantumReconnection.Heartbeat(30000);
heartbeat.setTimeoutHandler(() => {
  // 处理心跳超时
});
```

#### ConnectionState
连接状态管理:
```javascript
const connState = new QuantumReconnection.ConnectionState();
connState.addObserver((state) => {
  // 处理状态变化
});
```

### 队列模块 (QuantumQueue)

#### MessageQueue
消息队列管理:
```javascript
const queue = new QuantumQueue.MessageQueue({
  maxSize: 1000,
  maxRetries: 3
});

queue.registerHandler('message-type', async (data) => {
  // 处理消息
});

const messageId = queue.enqueue({
  type: 'message-type',
  data: {}
}, QuantumQueue.Priority.HIGH);
```

#### MessageSubscriber
消息订阅:
```javascript
const subscriber = new QuantumQueue.MessageSubscriber();
const unsubscribe = subscriber.subscribe('event-type', (data) => {
  // 处理事件
});
``` 