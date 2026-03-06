# 模块1：命令行操作基础

## 模块概述

本模块介绍命令行界面（CLI）的基本概念和常用操作，帮助学员掌握通过命令行高效完成日常任务的能力。所有内容符合三大圣律，强调安全、合规的操作习惯。

### 学习目标
- 理解命令行界面的基本概念和作用
- 掌握常用命令的语法和参数
- 能够独立完成文件系统导航和操作
- 培养安全、规范的命令行操作习惯

### 预计学习时间
- 理论学习：2小时
- 实践练习：3小时
- 综合练习：1小时
- 总计：6小时

### 先决条件
- 无特定技术要求
- 基本的计算机操作知识
- 积极的学习态度

## 核心内容

### 1.1 命令行基础概念

#### 什么是命令行？
命令行界面（Command Line Interface，CLI）是一种通过文本命令与计算机交互的方式。与图形界面（GUI）相比，CLI更加高效、灵活，适合自动化和批量处理任务。

#### 为什么学习命令行？
- **效率**：快速完成复杂操作
- **自动化**：编写脚本批量处理任务
- **远程操作**：通过SSH管理远程服务器
- **开发必备**：大多数开发工具依赖命令行

#### 伦理考量：安全操作
- 谨慎执行未知命令
- 确认命令目的和影响
- 避免执行可能破坏系统的命令
- 遵守系统权限和安全策略

### 1.2 基本命令

#### 导航命令
```bash
# 显示当前目录
pwd

# 列出目录内容
ls
ls -l    # 详细列表
ls -a    # 包括隐藏文件

# 切换目录
cd /path/to/directory
cd ..    # 返回上级目录
cd ~     # 返回家目录
```

#### 文件操作命令
```bash
# 创建文件
touch filename.txt

# 创建目录
mkdir directory_name
mkdir -p parent/child  # 创建多层目录

# 复制文件或目录
cp source.txt destination.txt
cp -r source_dir destination_dir  # 复制目录

# 移动或重命名
mv oldname.txt newname.txt
mv file.txt /target/directory/

# 删除文件或目录
rm file.txt
rm -r directory_name  # 删除目录
```

#### 查看文件内容
```bash
# 查看完整文件
cat file.txt

# 分页查看
less file.txt
more file.txt

# 查看开头几行
head -n 10 file.txt

# 查看结尾几行
tail -n 10 file.txt
```

### 1.3 命令参数和选项

#### 命令结构
```
command [options] [arguments]
```

#### 常见选项类型
- `-a`：短选项，单字母
- `--all`：长选项，描述性
- `-h` 或 `--help`：获取帮助

#### 获取帮助
```bash
# 查看命令手册
man ls

# 查看命令简要帮助
ls --help
```

### 1.4 管道和重定向

#### 管道（Pipe）
将一个命令的输出作为另一个命令的输入：
```bash
# 统计文件行数
cat file.txt | wc -l

# 查找包含特定内容的行
cat file.txt | grep "pattern"
```

#### 重定向（Redirection）
```bash
# 输出重定向到文件
ls -l > list.txt

# 追加到文件
echo "new line" >> list.txt

# 错误输出重定向
command 2> error.log

# 输入重定向
sort < input.txt
```

### 1.5 权限管理基础

#### 查看权限
```bash
ls -l
# 输出示例：-rw-r--r-- 1 user group 1234 Feb 7 11:00 file.txt
```

#### 权限解释
- `r`：读权限（4）
- `w`：写权限（2）
- `x`：执行权限（1）
- 三组权限：用户、组、其他

#### 修改权限
```bash
# 添加执行权限
chmod +x script.sh

# 设置具体权限
chmod 755 script.sh  # rwxr-xr-x
```

### 1.6 环境变量

#### 查看环境变量
```bash
# 查看所有环境变量
env

# 查看特定变量
echo $PATH
echo $HOME
```

#### 设置环境变量
```bash
# 临时设置
export MY_VAR="value"

# 永久设置（添加到~/.bashrc）
echo 'export MY_VAR="value"' >> ~/.bashrc
source ~/.bashrc
```

## 实践练习

### 练习1：基本导航
1. 打开命令行终端
2. 使用 `pwd` 查看当前目录
3. 使用 `ls` 查看目录内容
4. 创建一个新目录：`mkdir practice`
5. 进入该目录：`cd practice`
6. 返回家目录：`cd ~`

### 练习2：文件操作
1. 在家目录创建练习目录：`mkdir ~/cli_practice`
2. 进入该目录：`cd ~/cli_practice`
3. 创建三个文本文件：`touch file1.txt file2.txt file3.txt`
4. 创建子目录：`mkdir subdir`
5. 移动一个文件到子目录：`mv file1.txt subdir/`
6. 复制另一个文件：`cp file2.txt file2_copy.txt`
7. 重命名文件：`mv file3.txt renamed.txt`
8. 查看目录结构：`ls -R`

### 练习3：查看和搜索
1. 创建一个示例文件：`echo -e "line1\nline2\nline3\napple\nbanana\ncherry" > fruits.txt`
2. 查看完整文件：`cat fruits.txt`
3. 查看前3行：`head -n 3 fruits.txt`
4. 查看后3行：`tail -n 3 fruits.txt`
5. 搜索包含"apple"的行：`grep "apple" fruits.txt`
6. 统计行数：`wc -l fruits.txt`

### 练习4：管道和重定向
1. 创建两个文件：`echo "first file" > file1.txt` 和 `echo "second file" > file2.txt`
2. 合并文件：`cat file1.txt file2.txt > combined.txt`
3. 查看合并结果：`cat combined.txt`
4. 使用管道排序：`echo -e "banana\napple\ncherry" | sort`
5. 重定向排序结果：`echo -e "banana\napple\ncherry" | sort > sorted.txt`

## 综合项目

### 项目：文件整理脚本
创建一个简单的文件整理脚本，实现以下功能：

#### 需求
1. 在指定目录创建以下结构：
   ```
   project/
   ├── docs/
   ├── data/
   ├── scripts/
   └── logs/
   ```
2. 在每个目录中创建示例文件
3. 生成目录结构报告
4. 清理测试文件

#### 步骤指导
1. 创建项目目录
2. 创建子目录结构
3. 创建示例文件
4. 生成结构报告
5. 验证和清理

#### 示例代码
```bash
#!/bin/bash

# 创建项目目录
mkdir -p my_project
cd my_project

# 创建子目录
mkdir docs data scripts logs

# 创建示例文件
echo "# Documentation" > docs/README.md
echo "sample data" > data/sample.txt
echo "echo 'Hello World'" > scripts/hello.sh
echo "log entry" > logs/app.log

# 生成结构报告
tree . > structure.txt
echo "Directory structure saved to structure.txt"

# 显示创建的内容
echo "Project created successfully:"
ls -R
```

## 伦理与安全注意事项

### 安全操作原则
1. **确认再执行**：特别是删除、移动重要文件时
2. **权限最小化**：只授予必要的权限
3. **备份重要数据**：操作前备份关键文件
4. **了解命令作用**：不执行不了解的命令

### 伦理使用指南
1. **正当目的**：只用于合法、正当的工作任务
2. **尊重隐私**：不访问未授权的文件或目录
3. **保护系统**：不执行可能破坏系统稳定性的命令
4. **承担责任**：对自己的操作负责，及时纠正错误

### 常见风险与防范
1. **误删除文件**：
   - 使用 `rm -i` 交互模式
   - 先使用 `ls` 确认文件
   - 重要文件先备份

2. **权限错误**：
   - 理解权限设置
   - 谨慎使用 `chmod 777`
   - 遵循最小权限原则

3. **系统破坏**：
   - 不在根目录执行危险操作
   - 理解命令的系统影响
   - 在测试环境练习

## 考核标准

### 理论知识考核（30分）
- 选择题：10题，每题2分，共20分
- 简答题：2题，每题5分，共10分

### 实践操作考核（70分）
- 基本操作：5个任务，每题6分，共30分
- 综合任务：2个任务，每题20分，共40分

### 通过标准
- 总分 ≥ 90分（总分100分）
- 实践操作 ≥ 60分
- 伦理相关题目必须全部正确

### 考核题目示例
1. 选择题：哪个命令用于查看当前目录？
   A) ls  B) pwd  C) cd  D) where

2. 简答题：解释 `rm -rf /` 命令的危险性及伦理考量。

3. 实践题：创建目录结构并完成指定文件操作。

## 扩展学习

### 推荐资源
- **在线教程**：
  - Linux命令行基础（中文）
  - Bash脚本入门指南
- **参考书籍**：
  - 《Linux命令行与Shell脚本编程大全》
  - 《鸟哥的Linux私房菜》
- **练习平台**：
  - Linux命令行在线模拟器
  - 交互式Shell学习网站

### 进阶主题
- Shell脚本编程
- 正则表达式
- 进程管理
- 网络命令

### 实用技巧
- 命令历史搜索（Ctrl+R）
- 命令补全（Tab键）
- 别名设置（alias）
- 快捷键操作

## 模块总结

### 关键知识点
1. 命令行基本概念和优势
2. 常用命令的语法和使用
3. 管道和重定向机制
4. 文件权限管理基础
5. 环境变量概念

### 核心技能
1. 文件系统导航和操作
2. 文件内容查看和搜索
3. 批量处理和自动化基础
4. 安全操作习惯

### 伦理收获
1. 安全意识的建立
2. 责任感的培养
3. 合规操作的重视
4. 系统保护的意识

## 下一步学习建议

完成本模块后，建议：
1. 继续学习模块2：文件系统操作
2. 在实际工作中应用命令行
3. 练习常用命令的组合使用
4. 探索更多命令行工具和技巧

---
**模块版本**: v0.1.0
**创建日期**: 2026-02-07
**更新日期**: 2026-02-07
**开发状态**: 草案
**伦理审查状态**: 待审查
**审查要求**: 必须通过伦理监察代理审查