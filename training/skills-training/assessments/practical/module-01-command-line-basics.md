# 模块1：命令行操作基础 - 实践操作考核

## 考核说明

### 基本信息
- **考核模块**：命令行操作基础
- **考核类型**：实践操作
- **考核时间**：60分钟
- **总分**：100分
- **通过分数**：70分及以上

### 考核环境
- 操作系统：Linux/Unix环境
- 终端：Bash或兼容Shell
- 工作目录：`~/cli_assessment`
- 允许命令：所有标准命令行工具
- 禁止：互联网搜索、外部帮助

### 考核规则
1. 在规定时间内完成所有任务
2. 按照要求准确执行命令
3. 注意操作安全和伦理要求
4. 保持文件结构和命名规范
5. 考核结束后提交工作目录

### 伦理要求
所有操作必须符合三大圣律：
1. 不执行破坏性操作
2. 保护数据和系统安全
3. 遵循规范操作流程

## 考核任务

### 任务1：环境准备（10分）

#### 要求
1. 在家目录创建考核工作目录：`~/cli_assessment`
2. 进入该目录作为工作目录
3. 创建任务记录文件：`task_log.txt`

#### 评分标准
- 目录创建正确：3分
- 成功进入目录：2分
- 记录文件创建：3分
- 操作规范：2分

#### 预期结果
```
~/cli_assessment/
└── task_log.txt
```

### 任务2：文件系统操作（20分）

#### 要求
1. 创建以下目录结构：
   ```
   ~/cli_assessment/
   ├── documents/
   ├── data/
   │   ├── raw/
   │   └── processed/
   ├── scripts/
   └── backup/
   ```
2. 在 `documents/` 目录中创建文件：`notes.md`
3. 在 `data/raw/` 目录中创建三个数据文件：`data1.csv`, `data2.csv`, `data3.csv`
4. 将 `data/raw/` 中的所有文件复制到 `backup/` 目录
5. 将 `data/raw/data2.csv` 移动到 `data/processed/` 目录并重命名为 `processed_data.csv`

#### 评分标准
- 目录结构完整：5分
- 文件创建正确：5分
- 复制操作正确：5分
- 移动和重命名正确：5分

#### 预期结果
```
~/cli_assessment/
├── documents/
│   └── notes.md
├── data/
│   ├── raw/
│   │   ├── data1.csv
│   │   └── data3.csv
│   └── processed/
│       └── processed_data.csv
├── scripts/
├── backup/
│   ├── data1.csv
│   ├── data2.csv
│   └── data3.csv
└── task_log.txt
```

### 任务3：文件内容操作（20分）

#### 要求
1. 在 `documents/notes.md` 中添加以下内容：
   ```
   # 学习笔记
   日期：2026-02-07
   
   今天学习了命令行操作，包括：
   - 目录导航
   - 文件操作
   - 权限管理
   
   明天计划学习Shell脚本基础。
   ```
2. 创建文件 `documents/todo.txt` 并添加以下任务列表：
   ```
   1. 复习命令行基础
   2. 练习管道操作
   3. 学习环境变量
   4. 完成实践项目
   ```
3. 将两个文件的内容合并到 `documents/combined.txt`
4. 统计 `documents/combined.txt` 的行数、字数和字符数

#### 评分标准
- 文件内容正确：5分
- 文件创建和编辑：5分
- 文件合并正确：5分
- 统计信息正确：5分

#### 验证命令
```bash
wc documents/combined.txt
```

### 任务4：搜索和过滤（15分）

#### 要求
1. 在 `documents/` 目录中创建测试文件 `search_test.txt` 并添加以下内容：
   ```
   apple
   banana
   cherry
   date
   elderberry
   fig
   grape
   apple juice
   banana bread
   cherry pie
   ```
2. 使用 `grep` 查找包含 "apple" 的行
3. 使用 `grep` 查找以 "b" 开头的行
4. 使用 `grep -c` 统计包含 "cherry" 的行数
5. 使用 `grep -v` 排除包含 "berry" 的行

#### 评分标准
- 测试文件创建：3分
- 搜索操作正确：每个3分，共12分

#### 预期输出示例
```bash
# 任务2输出
apple
apple juice

# 任务3输出
banana
banana bread

# 任务4输出
2

# 任务5输出
apple
banana
date
fig
grape
apple juice
banana bread
cherry pie
```

### 任务5：权限管理（15分）

#### 要求
1. 在 `scripts/` 目录中创建脚本文件：`hello.sh`
2. 脚本内容：
   ```bash
   #!/bin/bash
   echo "Hello from CLI Assessment!"
   ```
3. 查看脚本文件的当前权限
4. 给脚本添加执行权限
5. 运行脚本验证权限设置
6. 将权限设置为：用户可读写执行，组可读执行，其他只读（权限数字表示）

#### 评分标准
- 脚本创建正确：3分
- 权限查看：3分
- 添加执行权限：3分
- 脚本运行：3分
- 权限数字设置：3分

#### 验证命令
```bash
ls -l scripts/hello.sh
./scripts/hello.sh
```

### 任务6：综合应用（20分）

#### 要求
创建一个自动化脚本 `scripts/setup_project.sh`，实现以下功能：

1. 在 `~/cli_assessment/` 目录中创建项目结构：
   ```
   my_project/
   ├── src/
   ├── tests/
   ├── docs/
   ├── config/
   └── logs/
   ```
2. 在每个目录中创建 `.gitkeep` 文件（空文件，用于Git跟踪空目录）
3. 在 `docs/` 目录中创建 `README.md`，包含项目名称和创建日期
4. 在 `config/` 目录中创建 `settings.conf`，添加基本配置：
   ```
   # 项目配置
   version=1.0.0
   author=cli_assessment
   created=2026-02-07
   ```
5. 将所有创建的文件列表保存到 `my_project/file_list.txt`
6. 统计项目中的文件和目录数量，保存到 `my_project/stats.txt`

#### 评分标准
- 脚本功能完整：10分
- 项目结构正确：5分
- 文件内容正确：3分
- 统计信息准确：2分

#### 脚本提示
```bash
#!/bin/bash
# 项目目录
project_dir="my_project"

# 创建目录结构
mkdir -p $project_dir/{src,tests,docs,config,logs}

# 创建.gitkeep文件
for dir in src tests docs config logs; do
    touch $project_dir/$dir/.gitkeep
done

# 创建README
echo "# My Project" > $project_dir/docs/README.md
echo "Created on: $(date)" >> $project_dir/docs/README.md

# 创建配置文件
echo "# 项目配置" > $project_dir/config/settings.conf
echo "version=1.0.0" >> $project_dir/config/settings.conf
echo "author=cli_assessment" >> $project_dir/config/settings.conf
echo "created=$(date +%Y-%m-%d)" >> $project_dir/config/settings.conf

# 生成文件列表
find $project_dir -type f > $project_dir/file_list.txt

# 生成统计信息
echo "Files: $(find $project_dir -type f | wc -l)" > $project_dir/stats.txt
echo "Directories: $(find $project_dir -type d | wc -l)" >> $project_dir/stats.txt

echo "Project setup completed!"
```

## 伦理与安全考核

### 伦理检查点（贯穿所有任务）

#### 安全操作
- 是否在安全目录进行操作
- 是否避免使用危险命令（如 `rm -rf /`）
- 是否确认操作目标

#### 数据保护
- 是否备份重要数据
- 是否保护敏感信息
- 是否遵循权限最小化

#### 合规操作
- 是否遵循操作规范
- 是否记录操作步骤
- 是否可追溯和审计

### 伦理违规扣分
- 轻微违规：每次扣5分
- 严重违规：直接考核不合格
- 危险操作：立即终止考核

### 伦理加分项
- 主动添加安全措施
- 优化操作减少风险
- 完善操作记录

## 考核流程

### 考前准备
1. 确认考核环境
2. 阅读考核要求
3. 规划时间分配
4. 备份重要数据

### 考核执行
1. 按顺序完成任务
2. 每完成一个任务检查结果
3. 记录操作步骤到 `task_log.txt`
4. 注意时间管理

### 考核结束
1. 保存所有文件
2. 提交工作目录
3. 填写考核记录
4. 清理临时文件

## 评分记录表

### 任务得分
| 任务 | 满分 | 得分 | 评语 |
|------|------|------|------|
| 任务1 | 10 | | |
| 任务2 | 20 | | |
| 任务3 | 20 | | |
| 任务4 | 15 | | |
| 任务5 | 15 | | |
| 任务6 | 20 | | |
| **小计** | **100** | | |

### 伦理评分
| 检查项 | 扣分 | 说明 |
|--------|------|------|
| 安全操作 | | |
| 数据保护 | | |
| 合规操作 | | |
| **伦理扣分** | | |

### 总分计算
- 任务得分：______ / 100
- 伦理扣分：______
- **最终得分**：______ / 100

### 考核结果
- □ 通过（≥70分且无严重伦理违规）
- □ 未通过（<70分或有严重伦理违规）

### 考核官评语
- 技术表现：_________________________
- 伦理表现：_________________________
- 改进建议：_________________________
- 下一步：___________________________

### 考生确认
- 考生签名：________________
- 日期：________________

### 考核官确认
- 考核官签名：________________
- 日期：________________

## 考核文件提交

### 必须提交的文件
1. 完整的 `~/cli_assessment/` 目录
2. `task_log.txt` 操作记录
3. 所有生成的文件和目录

### 提交方式
1. 打包目录：`tar -czf cli_assessment.tar.gz ~/cli_assessment`
2. 提交压缩文件
3. 附上评分记录表

### 文件验证
考核官将验证：
1. 目录结构是否正确
2. 文件内容是否符合要求
3. 操作记录是否完整
4. 脚本功能是否正常

---
**考核版本**: v0.1.0
**创建日期**: 2026-02-07
**更新日期**: 2026-02-07
**适用模块**: 模块1 - 命令行操作基础
**伦理审查状态**: 待审查
**审查要求**: 必须通过伦理监察代理审查