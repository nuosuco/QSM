# Qwen2.5-0.5B 模型使用指南

## 目录
1. [模型介绍](#模型介绍)
2. [下载模型](#下载模型)
3. [模型存储位置](#模型存储位置)
4. [启动和运行模型](#启动和运行模型)
5. [使用命令行界面](#使用命令行界面)
6. [使用图形用户界面](#使用图形用户界面)
7. [后台运行模型](#后台运行模型)
8. [系统要求](#系统要求)
9. [常见问题排解](#常见问题排解)
10. [高级用法](#高级用法)

## 模型介绍

Qwen2.5-0.5B-Instruct是通义千问的轻量级开源模型，具有5亿参数，支持中英双语，适合在消费级设备上运行。该模型基于Qwen2架构，经过了指令微调(Instruct)，能够理解和执行用户指令。

## 下载模型

### 下载方式1：使用自动化脚本

最简单的方法是使用项目提供的自动下载脚本：

1. 运行 `F:\model\QSM\LM\Qwen\bin\utils\download_qwen.bat` 批处理文件
2. 或者使用总控制台 `F:\model\QSM\LM\Qwen\bin\run_all.bat` 选择选项4

脚本会自动尝试多种下载方式，优先使用国内镜像加速下载。

### 下载方式2：手动下载

如果脚本下载失败，可以通过以下方式手动下载：

1. 访问魔搭社区(ModelScope)：https://modelscope.cn/models/qwen/Qwen2.5-0.5B-Instruct/summary
2. 点击"下载"按钮下载模型文件
3. 解压文件至 `F:\model\QSM\LM\Qwen\qwen\Qwen2.5-0.5B-Instruct` 目录

### 下载链接和镜像

脚本使用的主要镜像链接：
```python
# ModelScope镜像下载链接
modelscope_url = "https://modelscope.cn/api/v1/models/qwen/Qwen2.5-0.5B-Instruct/repo?Revision=master&FilePath=pytorch_model.bin"
```

备用下载源：
1. 魔搭社区镜像：https://hf-mirror.com
2. 百度网盘分享链接(如有更新请查看通义千问官方文档)

## 模型存储位置

模型文件应位于以下目录中的一个：

1. `F:/model/QSM/LM/Qwen/qwen/Qwen2.5-0.5B-Instruct`（首选）
2. `F:/model/QSM/LM/Qwen2.5-0.5B-Instruct-MLX-4bit`
3. `F:/model/QSM/LM/Qwen2.5-0.5B-Instruct`
4. `F:/model/QSM/LM/Qwen`

脚本会自动检查这些路径以加载模型。

## 启动和运行模型

可以通过多种方式启动模型：

### 使用主控制台

运行 `F:\model\QSM\LM\Qwen\bin\run_all.bat`，然后根据菜单选择相应选项：
- 选项1：图形界面
- 选项2：命令行界面
- 选项3：后台运行模型

## 使用命令行界面

1. 运行 `F:\model\QSM\LM\Qwen\bin\cli\run_qwen_cli.bat`
2. 等待模型加载（第一次加载可能需要较长时间）
3. 加载完成后，在命令行界面中输入问题
4. 输入"退出"结束会话

命令行界面使用的核心代码：
```python
# 加载分词器和模型
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path, 
    trust_remote_code=True,
    device_map="auto",
    low_cpu_mem_usage=True
)

# 构建提示
prompt = f"<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"

# 生成回复
generated_text = model.generate(
    tokenizer(prompt, return_tensors="pt").input_ids.to(model.device),
    max_new_tokens=512,
    temperature=0.7,
    top_p=0.9,
    repetition_penalty=1.1
)
```

## 使用图形用户界面

1. 运行 `F:\model\QSM\LM\Qwen\bin\gui\run_qwen_gui.bat`
2. 等待模型加载和GUI初始化
3. 在文本框中输入问题，点击"发送"按钮或按Ctrl+Enter
4. GUI界面支持聊天历史查看和保存

## 后台运行模型

如果需要在后台运行模型，可以：
1. 运行 `F:\model\QSM\LM\Qwen\bin\cli\run_qwen_background.bat`
2. 模型将在新的命令窗口中加载和运行

## 系统要求

最低配置：
- Python 3.9或更高版本
- PyTorch 2.0或更高版本
- Transformers库（版本≥4.37.0）
- 最少4GB系统内存
- 约2GB磁盘空间用于模型存储

推荐配置：
- 8GB+系统内存
- NVIDIA GPU（用于加速）
- CUDA 11.7+（使用GPU时）

## 常见问题排解

### 模型加载错误
- **问题**: "找不到Qwen2.5-0.5B模型目录"
- **解决方案**: 确认模型已正确下载并放置在预期目录

### 内存不足错误
- **问题**: 加载模型时出现内存错误
- **解决方案**: 
  - 添加`load_in_8bit=True`参数降低内存使用
  - 关闭其他占用内存的应用程序
  - 尝试使用GPU而非CPU加载模型

### 安装依赖
如需安装必要的库：
```bash
pip install torch transformers modelscope
```

### trust_remote_code错误
如果遇到trust_remote_code错误，确保在加载模型时使用:
```python
trust_remote_code=True
```

## 高级用法

### 修改模型参数
可以调整下列参数来控制生成文本的质量和多样性：
- `temperature`：值越高，生成文本越随机多样（默认0.7）
- `top_p`：控制词汇选择的概率阈值（默认0.9）
- `repetition_penalty`：避免重复内容的惩罚系数（默认1.1）
- `max_new_tokens`：生成文本的最大长度（默认512）

### 节省内存的加载选项
对于内存受限的设备，可以使用以下参数：
```python
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,
    device_map="auto",
    load_in_8bit=True,  # 8位量化,可减少约60%内存使用
    low_cpu_mem_usage=True
)
```

---

> 注意：本文档假设项目根目录为F:\model\QSM，如果您的项目位于不同目录，请相应调整所有路径。 