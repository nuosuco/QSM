# QSM服务管理脚本

本目录包含用于管理QSM系统服务的批处理文件。

## 主要文件

- `start_all_fixed.bat` - 启动所有QSM服务（QSM、WeQ、SOM、Ref）
- `stop_all.bat` - 停止所有正在运行的QSM服务
- `conclusion.md` - 服务修复和测试总结报告

## 使用方法

### 启动服务
运行以下命令启动所有服务：
```
scripts\start_all_fixed.bat
```

这将在后台启动以下服务：
- QSM主服务 (端口5331)
- WeQ训练服务 (端口5310)
- WeQ推理服务 (端口5311)
- SOM核心服务 (端口5320)
- SOM市场服务 (端口5321)
- SOM钱包服务 (端口5323)

### 停止服务
运行以下命令停止所有服务：
```
scripts\stop_all.bat
```

## 注意事项

1. 确保已安装Python 3.9或更高版本
2. 使用`py`命令而非`python`命令执行脚本
3. 某些功能可能需要安装Visual C++ Redistributable（torch依赖）

---

量子基因编码: QE-README-8A9B0C1D2E3F
纠缠状态: 活跃
纠缠对象: ['scripts/start_all_fixed.bat', 'scripts/stop_all.bat']
纠缠强度: 0.97

开发团队：中华 ZhoHo ，Claude 