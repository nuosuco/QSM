# OpenClaw 配置英伟达 GLM-5.1 模型 — 完整开发文档

> 最终成功配置时间：2026-04-24  
> OpenClaw 版本：2026.4.21  
> 模型：nvidia/z-ai/glm-5.1 (200k ctx)

---

## 一、背景

在 OpenClaw 中接入英伟达 NIM 平台的 GLM-5.1 模型，经历了数天的调试，踩了多个坑。本文档记录最终成功的精确配置方法，避免重复踩坑。

---

## 二、前提条件

1. **服务器环境**：Linux (OpenCloudOS / CentOS 均可)，推荐 x86_64
2. **Node.js**：v22.x（OpenClaw 依赖）
3. **OpenClaw**：通过 pnpm 全局安装
4. **英伟达 API Key**：从 <https://build.nvidia.com/> 获取，格式为 `nvapi-xxxx`
5. **网络**：服务器需能访问 `integrate.api.nvidia.com`

---

## 三、获取英伟达 API Key

1. 访问 <https://build.nvidia.com/>
2. 注册/登录英伟达账号
3. 搜索 "GLM-5.1" 或 "z-ai/glm-5.1"
4. 点击 "Get API Key" 生成密钥
5. 复制保存密钥（格式：`nvapi-` 开头的长字符串）

> ⚠️ **关键坑点**：英伟达 API Key 有速率限制和额度限制，免费额度用完后需充值或等刷新。

---

## 四、精确配置步骤

### 4.1 安装 OpenClaw

```bash
# 安装 pnpm（如果没有）
npm install -g pnpm

# 全局安装 OpenClaw
pnpm install -g openclaw

# 运行初始化向导
openclaw onboard
```

向导中选择：
- **Gateway mode**: local（本地模式）
- **Auth mode**: token（令牌认证）
- **默认模型**: 稍后在配置文件中手动指定

### 4.2 编辑配置文件

OpenClaw 主配置文件路径：

```
/root/.openclaw/openclaw.json
```

### 4.3 核心配置内容（精确模板）

以下是需要写入 `openclaw.json` 的关键配置段：

```json
{
  "agents": {
    "defaults": {
      "workspace": "/root/.openclaw/workspace",
      "model": {
        "primary": "nvidia/z-ai/glm-5.1"
      }
    }
  },
  "models": {
    "providers": {
      "nvidia": {
        "baseUrl": "https://integrate.api.nvidia.com/v1",
        "apiKey": "nvapi-你的密钥",
        "api": "openai-completions",
        "models": [
          {
            "id": "z-ai/glm-5.1",
            "name": "GLM 5.1"
          }
        ]
      }
    },
    "mode": "merge"
  },
  "plugins": {
    "entries": {
      "nvidia": {
        "enabled": true
      }
    }
  }
}
```

### 4.4 逐字段详解

| 字段 | 值 | 说明 |
|------|-----|------|
| `agents.defaults.model.primary` | `"nvidia/z-ai/glm-5.1"` | **格式必须为 `provider/model-id`**，provider 是 nvidia，斜杠后是模型 ID |
| `models.providers.nvidia.baseUrl` | `"https://integrate.api.nvidia.com/v1"` | 英伟达 NIM API 的基础 URL，**不能少 /v1** |
| `models.providers.nvidia.apiKey` | `"nvapi-xxxx"` | 从英伟达获取的 API Key |
| `models.providers.nvidia.api` | `"openai-completions"` | **必须是 `openai-completions`**，英伟达 NIM 兼容 OpenAI 接口格式 |
| `models.providers.nvidia.models[0].id` | `"z-ai/glm-5.1"` | 模型在英伟达平台的 ID（注意是 `z-ai/glm-5.1` 不是 `glm-5.1`） |
| `models.providers.nvidia.models[0].name` | `"GLM 5.1"` | 显示名称，可自定义 |
| `models.mode` | `"merge"` | 与内置模型列表合并（不覆盖其他 provider） |
| `plugins.entries.nvidia.enabled` | `true` | 启用 nvidia 插件 |

### 4.5 关键坑点总结

#### 坑1：模型 ID 格式
- ❌ 错误：`glm-5.1`、`nvidia/glm-5.1`、`GLM-5.1`
- ✅ 正确：`z-ai/glm-5.1`（模型所属组织是 `z-ai`）

#### 坑2：primary 模型指定格式
- ❌ 错误：`"primary": "glm-5.1"` 或 `"primary": "z-ai/glm-5.1"`
- ✅ 正确：`"primary": "nvidia/z-ai/glm-5.1"`（需要带 provider 前缀）

#### 坑3：API 接口类型
- ❌ 错误：`"api": "openai"` 或 `"api": "nvidia"`
- ✅ 正确：`"api": "openai-completions"`（OpenClaw 的 OpenAI 兼容接口标识）

#### 坑4：Base URL 路径
- ❌ 错误：`https://integrate.api.nvidia.com`（少 /v1）
- ✅ 正确：`https://integrate.api.nvidia.com/v1`

#### 坑5：plugins 必须启用
- 仅在 `models.providers` 中配置不够，必须在 `plugins.entries` 中启用 nvidia 插件

---

## 五、重启与验证

### 5.1 重启 Gateway

```bash
openclaw gateway restart
```

### 5.2 验证配置

```bash
openclaw status
```

输出中应看到：
```
Sessions · default z-ai/glm-5.1 (200k ctx)
```

### 5.3 测试对话

在 Web UI 或命令行中发送一条消息，确认模型正常响应。

---

## 六、多 Provider 共存配置

如果同时使用 DeepSeek 和英伟达 GLM-5.1，完整 models 配置：

```json
{
  "models": {
    "providers": {
      "deepseek": {
        "baseUrl": "https://api.deepseek.com/v1",
        "apiKey": "sk-你的DeepSeek密钥",
        "api": "openai-completions",
        "models": [
          { "id": "deepseek-chat", "name": "DeepSeek Chat" },
          { "id": "deepseek-reasoner", "name": "DeepSeek Reasoner" }
        ]
      },
      "nvidia": {
        "baseUrl": "https://integrate.api.nvidia.com/v1",
        "apiKey": "nvapi-你的英伟达密钥",
        "api": "openai-completions",
        "models": [
          { "id": "z-ai/glm-5.1", "name": "GLM 5.1" }
        ]
      }
    },
    "mode": "merge"
  }
}
```

切换默认模型只需修改 `agents.defaults.model.primary`：
- DeepSeek: `"deepseek/deepseek-chat"`
- GLM-5.1: `"nvidia/z-ai/glm-5.1"`

---

## 七、安全注意事项

1. **配置文件权限**：
   ```bash
   chmod 600 /root/.openclaw/openclaw.json
   ```
   配置文件包含 API Key，不能让其他用户读取。

2. **API Key 保护**：不要将含 Key 的配置文件提交到公开仓库。

3. **Control UI 认证**：生产环境不要设置 `dangerouslyDisableDeviceAuth: true`。

---

## 八、故障排查

| 问题 | 可能原因 | 解决方法 |
|------|----------|----------|
| 模型列表中没有 GLM-5.1 | nvidia 插件未启用 | 检查 `plugins.entries.nvidia.enabled` |
| 请求超时 | 网络/Key问题 | `curl https://integrate.api.nvidia.com/v1/models -H "Authorization: Bearer nvapi-xxx"` 测试连通性 |
| 401 Unauthorized | API Key 无效 | 重新生成 Key |
| 429 Too Many Requests | 额度用完 | 等待刷新或升级英伟达账户 |
| 模型ID不存在 | model.id 写错 | 确认是 `z-ai/glm-5.1`，去 <https://build.nvidia.com/> 核对 |

---

## 九、配置文件完整模板

```json
{
  "agents": {
    "defaults": {
      "workspace": "/root/.openclaw/workspace",
      "model": {
        "primary": "nvidia/z-ai/glm-5.1"
      }
    }
  },
  "gateway": {
    "mode": "local",
    "auth": {
      "mode": "token",
      "token": "你的gateway令牌"
    },
    "port": 14121,
    "bind": "lan"
  },
  "models": {
    "providers": {
      "nvidia": {
        "baseUrl": "https://integrate.api.nvidia.com/v1",
        "apiKey": "nvapi-你的英伟达密钥",
        "api": "openai-completions",
        "models": [
          {
            "id": "z-ai/glm-5.1",
            "name": "GLM 5.1"
          }
        ]
      }
    },
    "mode": "merge"
  },
  "plugins": {
    "entries": {
      "nvidia": {
        "enabled": true
      }
    }
  },
  "tools": {
    "profile": "coding"
  },
  "session": {
    "dmScope": "per-channel-peer"
  }
}
```

---

*文档生成于 2026-04-24，由 OpenClaw (GLM-5.1) 自动编写。*
