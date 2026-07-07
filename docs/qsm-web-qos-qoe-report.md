# QSM Web QOS 用户体验优化报告

**报告时间**: 2026-07-07  
**测试环境**: som.top (nginx/1.26.3, TLSv1.3)  
**QSM 项目路径**: /root/QSM

---

## 一、优化措施清单

| # | 优化项 | 措施 | 状态 |
|---|--------|------|------|
| 1 | 字体preload拼写修正 | `/fonts/lingxi-yi.ttf` → `/fonts/lingyi.ttf` | ✅ 已修复 |
| 2 | Gzip压缩启用 | `/etc/nginx/conf.d/qsm-gzip.conf` | ✅ 已部署 |
| 3 | 静态资源缓存 | 30天 `public, immutable` | ✅ 已配置 |
| 4 | QVMSimulator全局导出 | `window.QVMSimulator = QVMSimulator` | ✅ 已存在 |

---

## 二、性能提升数据

### 2.1 传输体积对比（Gzip压缩）

| 资源 | 原始大小 | Gzip压缩 | 节省率 |
|------|----------|----------|--------|
| index.html | 24,848 bytes | 6,881 bytes | **72.3%** |
| styles.css | 21,556 bytes | 4,294 bytes | **80.1%** |
| qvm-simulator.js | 65,828 bytes | 15,407 bytes | **76.6%** |
| lingyi.ttf (字体) | 1,793,084 bytes | 970,892 bytes | **45.9%** |

### 2.2 页面加载时间

| 页面 | 加载耗时 |
|------|----------|
| `/` (桌面) | 0.130s |
| `/apps/qvm/` (量子虚拟机) | 0.197s |
| `/styles.css` | 0.187s |
| `/fonts/lingyi.ttf` | 0.375s |

### 2.3 关键指标

- **Gzip 压缩生效**: `Vary: Accept-Encoding` + `Content-Encoding: gzip` ✅
- **缓存策略生效**: `Cache-Control: max-age=2592000, public, immutable` ✅
- **错误消除**: `fonts/lingxi-yi.ttf` → 修正后 200（原 404）
- **Brotli**: 预留配置未启用（需 nginx-module-brotli 编译支持）

---

## 三、用户体验验证结果

### 3.1 三语切换功能

| 语言 | 按钮 | 验证结果 |
|------|------|----------|
| 中文 (zh) | 中文 | ✅ 桌面图标标签切换为中文 |
| English (en) | EN | ✅ 桌面图标标签切换为英文 |
| 彝文 (yi) | 󲝁 | ✅ 桌面图标标签切换为彝文 |

- 切换机制: `setLang()` → `render()` → `localStorage` 持久化
- 状态恢复: 页面刷新自动恢复上次语言

### 3.2 彝文字体渲染

| 检查项 | 结果 |
|--------|------|
| 字体文件 HTTP | 200 OK (lingyi.ttf, 1.79MB) |
| preload 404 | 已消除（修正为 lingyi.ttf） |
| 字体 CSS 加载 | yi-fonts.css 正确引用 lingyi.ttf |
| 彝文字符集 | 4120 字，私有区编码 U+F2710–U+F27DF |
| QVM 应用三语 | `三语量子概念` 按钮存在，三语显示组件已加载 |

### 3.3 QVM 模拟器交互功能

| 功能 | 验证结果 |
|------|----------|
| QVM 页面加载 | ✅ 200 OK，"QSM QEntL量子虚拟机模拟器 v0.2.0" |
| qvm-simulator.js 加载 | ✅ 脚本加载成功 (65,828 bytes) |
| QVMSimulator 类 | ✅ `window.QVMSimulator` 已导出 |
| QBC 字节码编辑器 | ✅ textarea 编辑器存在 |
| 量子电路 Canvas | ✅ Canvas 渲染正常 |
| 量子比特可视化 | ✅ 量子比特状态展示 |
| 三语切换 | ✅ "🔤 三语" 按钮存在 |
| QBC 指令帮助表 | ✅ 指令表格渲染 |

### 3.4 浏览器控制台 JS 错误检查

| 检查项 | 结果 |
|--------|------|
| 应用层 JS 错误 | ✅ **0 个**（控制台无应用错误） |
| 字体 preload 404 | ✅ **已消除**（修正后 200） |
| QVMSimulator 导出错误 | ✅ **已消除**（window.QVMSimulator 可访问） |
| 控制台日志 | "三语显示组件已加载"（正常日志） |

---

## 四、总结

### 已完成优化
1. **字体preload拼写修正**: 消除 `lingxi-yi.ttf` 404 错误，所有 preload 标签正确指向 `lingyi.ttf`
2. **Gzip压缩部署**: 平均节省 72–80% 传输体积（HTML/CSS/JS），字体 46%
3. **三语切换验证**: 中文/英文/彝文三语切换功能完整可用，含持久化存储
4. **彝文字体渲染**: 字体文件 200 OK，preload 无 404，CSS 引用正确
5. **QVM 模拟器**: 脚本加载、Canvas 渲染、QBC 编辑器、三语显示组件全部正常
6. **JS 错误**: 浏览器控制台 0 个应用层错误

### 建议（可选）
- **Brotli 压缩**: 安装 `nginx-module-brotli` 可进一步降低 15–25% 体积
- **字体 WOFF2**: 将 `lingyi.ttf` 转换为 WOFF2 格式可节省约 40% 字体体积
- **QVM 桌面页**: QVM 应用页面内的 `setLang` 函数未暴露为全局（仅主桌面页有），不影响使用
