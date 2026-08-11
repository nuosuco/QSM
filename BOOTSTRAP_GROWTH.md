# QEntL 自举生长框架

## 核心理念
- **自举**: 用自己编译自己（QCL编译QCL，QVM运行QVM）
- **生长**: 每一代都进化，无限迭代，越变越强
- **个性化**: 每个用户的升级路径不同，像独立生命体

## 目录结构
```
run/              ← 当前运行版本 (qcl.qbc, qvm.qbc)
versions/         ← 所有历史版本快照
  v1/             ← 第1代 (qcl.qentl, qvm.qentl, qcl.qbc, qvm.qbc)
  v2/             ← 第2代
  v3/             ← ...
  ...
archive/a/        ← 历史归档组A
archive/b/        ← 历史归档组B
lib/              ← 库源码 (qdfs.qentl, qns.qentl, core.qentl, ...)
examples/         ← 示例代码
src/              ← C种子源码 (q_bootstrap.c) - 手动编辑
bin/              ← C种子可执行 (q_bootstrap)
```

## 版本管理规则
### 归档规则
- v1-v10: 存到 archive/a/
- v11-v20: 存到 archive/b/, 同时删除 archive/a/ 的前2代(v1,v2)
- v21-v30: 存到 archive/a/, 同时删除 archive/b/ 的前2代
- 以此类推，ab两目录循环使用
- 每100代: 清理全部归档，从1重新开始

### C种子升级
- 每10代手动编辑 src/q_bootstrap.c 升级能力
- 升级后用新C种子重新编译:
  ```
  bin/q_bootstrap compile qcl.qentl run/qcl.qbc
  bin/q_bootstrap compile qvm.qentl run/qvm.qbc
  ```

## 使用命令
```bash
# 查看版本状态
./version.sh status

# 创建版本快照
./version.sh snapshot

# 升级组件
./upgrade.sh qcl.qentl   # 升级QCL编译器
./upgrade.sh qvm.qentl   # 升级QVM运行时
./upgrade.sh lib/qdfs.qentl  # 升级QDFS库
./upgrade.sh lib/qns.qentl   # 升级QNS框架

# 版本管理
./version.sh switch      # 切换归档目录
./version.sh clean       # 清理最老版本
./version.sh fullclean   # 全清理（每100代）
```

## 生长循环
```
1. 修改源码 (qcl.qentl / qvm.qentl / lib/*.qentl / examples/*.qentl)
2. 运行升级 (./upgrade.sh <源文件>)
3. 自动快照 (versions/vN/ 保存源码+产物)
4. 归档历史 (archive/a/ 或 archive/b/)
5. 验证测试 (bin/q_bootstrap run run/qvm.qbc)
6. 循环迭代 → 无限生长
```

## 个性化生长
- 每个用户的QEntL升级路径不同
- 用户可以只升级某个组件（如只升级QDFS）
- 用户可以回滚到任意历史版本
- 用户可以自定义升级顺序
- 每个用户的QEntL都是独特的生命体

## 关键原则
1. **版本即快照**: 每一代保存完整的源码+产物
2. **归档循环**: 用ab两目录管理无限历史
3. **C种子定期升级**: 每10代增强一次
4. **自举验证**: 每次升级后验证自举链是否完整
5. **个性化**: 允许用户自由决定升级什么、什么时候升级
