# QEntL 安装故障排除

## 🔧 常见安装问题

### 1. 安装程序无法启动

**问题**: 双击setup.bat没有反应或报错

**解决方案**:
```powershell
# 检查PowerShell执行策略
Get-ExecutionPolicy

# 如果是Restricted，临时更改策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 以管理员身份运行
Right-click setup.bat -> "以管理员身份运行"
```

### 2. 磁盘空间不足

**问题**: "磁盘空间不足，无法继续安装"

**解决方案**:
```powershell
# 检查可用空间
Get-PSDrive -Name C | Select-Object Used,Free

# 清理临时文件
Remove-Item $env:TEMP\* -Recurse -Force -ErrorAction SilentlyContinue

# 磁盘清理
cleanmgr /sagerun:1
```

### 3. 权限访问被拒绝

**问题**: "访问被拒绝"或"权限不足"错误

**解决方案**:
```powershell
# 检查当前用户权限
whoami /priv

# 添加必要权限
# 右键"此电脑" -> 属性 -> 高级系统设置 -> 用户配置文件
```

### 4. 网络连接问题

**问题**: 无法下载组件或验证许可证

**解决方案**:
```powershell
# 测试网络连接
Test-NetConnection quantum.qentl.org -Port 443

# 检查代理设置
netsh winhttp show proxy

# 配置防火墙例外
New-NetFirewallRule -DisplayName "QEntL" -Direction Inbound -Port 8080 -Protocol TCP -Action Allow
```

### 5. 组件安装失败

**问题**: 特定组件安装失败

**解决方案**:
```powershell
# 单独安装失败的组件
.\qentl_installer.exe /COMPONENT=VM
.\qentl_installer.exe /COMPONENT=COMPILER

# 检查安装日志
Get-Content "$env:TEMP\QEntL_Install.log" -Tail 50
```

## 🚨 严重错误处理

### 系统崩溃或蓝屏

**可能原因**:
- 硬件兼容性问题
- 驱动程序冲突
- 内存不足

**解决方案**:
1. 重启到安全模式
2. 运行系统文件检查: `sfc /scannow`
3. 检查内存: `mdsched.exe`
4. 更新硬件驱动程序

### 安装后系统无法启动

**恢复步骤**:
```powershell
# 使用恢复工具
.\support\tools\recovery.bat

# 从引导镜像恢复
qentl-recovery restore --boot-image sources\boot.qim

# 最后手段：完全卸载
.\qentl_installer.exe /UNINSTALL /FORCE
```

## 📋 安装前检查清单

- [ ] 系统满足最低要求
- [ ] 有足够的磁盘空间 (至少15GB)
- [ ] 网络连接正常
- [ ] 以管理员身份运行
- [ ] 关闭杀毒软件临时排除
- [ ] 备份重要数据

## 📞 获取帮助

### 自助诊断
```powershell
# 运行诊断工具
.\support\tools\diagnostic.bat

# 生成系统报告
msinfo32 /report system_info.txt
```

### 联系支持
- **邮箱**: support@qentl.org
- **在线聊天**: https://support.qentl.org/chat
- **远程协助**: TeamViewer ID在安装日志中
- **电话支持**: +86-400-QENTL-1 (工作日 9:00-18:00)

### 提交问题时请包含:
1. 详细的错误信息
2. 安装日志文件
3. 系统配置信息 (msinfo32输出)
4. 重现步骤

---
**最后更新**: 2025年6月19日
**适用版本**: QEntL v1.0.0+
