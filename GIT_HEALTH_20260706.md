# Git 仓库健康报告 — QSM

> 仓库路径：`/root/QSM`  
> 报告生成时间：2026-07-06  
> 检查方式：只读 Git 命令，未修改任何源码文件

---

## 1. .git/index 完整性

| 指标 | 值 |
|---|---|
| 文件大小 | 339,468 字节 (≈331 KB) |
| 状态 | ✅ 完整（>0 字节） |

---

## 2. 当前分支状态

| 指标 | 值 |
|---|---|
| 当前分支 | `main` |
| HEAD 提交 | `80e1a73` |
| 工作树状态 | ✅ 干净（nothing to commit, working tree clean） |
| 未跟踪文件数量 | **0** |

---

## 3. 分支状态表

| 分支 | 最新提交 | 提交哈希 | 与 main 差异 | 状态 |
|---|---|---|---|---|
| `main` | `80e1a73` fix: qcl_phase2 支持'导入...作为'和'量子模块'语法，修复QNS编译空壳 | `80e1a73` | — (基准) | ✅ 当前 HEAD |
| `master` | `b044e8b` feat: generate QSM training dataset (52986 samples, 7.77MB) | `b044e8b` | main 领先 master **1 个提交** | ⚠️ 落后 main |
| `dev` | `b044e8b` feat: generate QSM training dataset (52986 samples, 7.77MB) | `b044e8b` | dev 与 master 一致，落后 main **1 个提交** | ⚠️ 落后 main |

远程分支：`origin/dev`、`origin/main`、`origin/master` 均已追踪。

---

## 4. Git 对象健康状态 (`git fsck`)

| 检查项 | 结果 |
|---|---|
| 损坏对象 (corrupt) | ✅ 无 |
| 丢失对象 (missing) | ✅ 无 |
| 悬挂对象 (dangling) | ⚠️ 10 个（见下） |

**悬挂对象清单：**

| 类型 | 哈希 |
|---|---|
| dangling commit | `fbc91613e03d74cdc7d31c1b3a7d099cd06cd3af` |
| dangling commit | `2e102a116cf818bc4b8d7fec96ddf23c41c8729f` |
| dangling commit | `0d52b57d860b6ccf043229c58571621b54dceebe` |
| dangling commit | `041381ca1abcee0c05c2ca3bcb4ea69257e09223` |
| dangling commit | `ecf43d23db9c3c9ed2ba9e3aa01f120919a806d4` |
| dangling tree | `83441ddb15980ec3b9697bc7970a46f62e16c016` |
| dangling tree | `52cc4417c7a489b3b6aabb604a65a4a89e4d51db` |
| dangling blob | `489646e15aed99b4b1877d30d01b24fb961d5ec4` |
| dangling blob | `f5db084ed66a528cf38168b7c829d6338cc55540` |
| dangling blob | `73e67aae166d34eec50b5ef8b2f4d27d4bae4276` |

**对象统计：**

| 指标 | 值 |
|---|---|
| 总对象数 | 5,903 |
| 总大小 | 149.89 MiB |
| 打包数 (packs) | 0（未打包） |
| 垃圾文件 (garbage) | 0 |

---

## 5. 最近 3 个提交列表

| # | 哈希 | 作者 | 日期 | 提交信息 |
|---|---|---|---|---|
| 1 | `80e1a73` | zhonghua-ai | 2026-07-06 | fix: qcl_phase2 支持'导入...作为'和'量子模块'语法，修复QNS编译空壳 |
| 2 | `b044e8b` | zhonghua-ai | 2026-07-05 | feat: generate QSM training dataset (52986 samples, 7.77MB) |
| 3 | `b5d7a3d` | zhonghua-ai | 2026-07-05 | sync: 经典5平台+量子3部署编译更新，qvm_bootstrap更新，新增训练报告 |

---

## 6. 建议操作

### 🔴 建议（非阻断性）

1. **分支收敛**：`main` 比 `master`/`dev` 领先 1 个提交（`80e1a73`）。
   - 如 `main` 为活跃开发分支，建议执行 `git checkout dev && git merge main`（及 master）同步。
   - 如 `master` 应为唯一发布分支，建议反向操作。

2. **悬挂对象清理**：存在 10 个 dangling 对象，多为 GC 后可回收的孤立提交/blob。
   - 运行 `git gc --prune=now` 可安全清理，释放约少量磁盘空间。

3. **对象打包**：当前 5,903 个对象均未打包（packs=0），磁盘占用 149.89 MiB。
   - 运行 `git repack -a -d` 可将对象打包，显著减小仓库体积。

### 🟢 健康项

- ✅ .git/index 完整，工作树干净
- ✅ 无损坏/丢失对象（无 corrupt / missing）
- ✅ 无未跟踪文件（0）
- ✅ 三个本地分支 + 三个远程追踪分支均存在

---

*报告结束。仓库整体健康，存在轻微维护建议但不影响正常使用。*
