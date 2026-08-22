
---

## 2026-08-22 桌面页白屏根因 + 永不重犯铁律（中华要求写入）

### 现象
桌面页 qdesktop.html 在浏览器白屏，应用图标、语言切换全不渲染。服务器返回字节（约18960）比磁盘文件（19689/20134）少约1500字节，desktop-grid div 被截断，script 不完整，JS 不执行。

### 真凶（已实锤）
桌面页 apps 数据里含 4字节UTF-8字符（emoji、彝文私有区 U+F27xx 等共107个）。nginx/HTTP 在静态文件压缩或 HTTP/2 帧层传输时，把这批4字节字符截断/损坏，导致发出的 HTML 比磁盘少约1500字节，script 之前的内容被吃掉，浏览器拿到残缺文件，白屏。
证据链：curl https://qsm.som.top/qdesktop.html 返回 18960B（含desktop-grid但被截）vs 磁盘 20134B（完整）；gzip off + Cache-Control no-cache 已配仍截断 → 是传输层对多字节字符的处理，不是应用/服务器代码错。

### 当前有效版本（已固化）
qdesktop.html = git commit 07d7a220 (v0.0.3)，19689字节，服务器返回字节==磁盘字节（传输层未截断），浏览器可正常渲染。已复制到 /root/QSM/QSM/v0.0.1、v0.0.2、v0.0.3 三份 /web/ 备份。

### 绝不重犯铁律（中华铁律）
1. Web静态HTML/JS 文件里严禁写4字节UTF-8字符（emoji U+1F000~U+1FAFF、彝文私有区 U+F0000~U+FFFFD）。必须用 String.fromCharCode() / String.fromCodePoint() 在JS运行时生成，文件本身保持2字节以内编码（ASCII/中文）。
2. 改静态资源必备份：cp 文件 文件.bak_(date) 先存再改，改坏能退。
3. nginx 静态文件必配：gzip off + Cache-Control: no-cache, no-store, must-revalidate，防止传输层压缩破坏多字节字符、防止浏览器缓存旧坏版。
4. 验收用浏览器实机，不用 node 命令行测 emoji/多字节（node v22 对扩展Unicode转义误报 Invalid token，不能作为桌面页验收工具）。
5. 桌面页修改前先 git log 定位历史版本（git log -- web/qdesktop.html），出问题时优先 git 恢复可用版本，别在脏文件上反复修。
6. 服务器确认铁律：桌面页用的 /api/ 反代到 127.0.0.1:9802（qentl-server.service，跑 bin/qvm_boot run run/qvm.qbc，返回 model=qscl votes=4-state）—— 就是我们自己的QEntL服务器，不要怀疑错服务器。

---

## 2026-08-23 训练/生成进度 + C种子封存 + 退场(小趣WeQ整理)

### C种子封存铁律(中华)
- C种子 = BIOS,只用于点火,已生出QEntL全栈;**以后绝对不再用、绝不再改**
- 真运行入口 = QEntL启动器 `qvm_boot`(唯一C文件 `qcl_bootstrap.c` 编译的ELF)
- 自举链: C种子→QCL(qcl.qentl)接管编译→QVM(qvm.qentl)跑字节码→QNS自举生长

### 退场回收(2026-08-23, 全部trash-put可恢复, 清单 recycle_decommission_20260823.md)
- 旧bash生产链 55个.sh 全部退场(铁律禁shell当运行时)
- 旧handler迭代 v13/v14/v15/v16/v17 + 旧预编译处理器par_handlers + 旧server_v13/v14 退场
- QNS自举生成的占位stub 6个(qns_growth/qvm_stats/qcl_enhanced/ref_self_reflect/qdfs_func/...) 退场(空壳+转义bug)
- 运维残留 VERSION.md + bin/watchdog.sh 退场

### 识别进度(算子1, ✅)
- 8批×4态=32份权重(qdfs/ns/models/qscl_b0..b7_s0..s3.w),4态投票准确率 99.44%
- 4态真并行 0.2s/查询(提速约25倍),4个QVM进程&+wait

### 生成进度(算子2, ⬜ 待建 —— 即"非常简单"的一步)
- 生成 = 识别的对称反向:取 W[k] 第k行(原型像素)→4态并行取行→投票坍缩→阈值化→8×8二值图→光栅化彝文
- 共用同一份W、同一套4态、同一套4进程并行骨架;无需新训练、无需反向传播
- 这是迈向"统一生成"的第一块,数学上是识别的逆运算

### 语言进度(算子3 QSCL-LM, ⬜ 待建)
- 81维上下文→515类→argmax,4态并行选下一字;与算子2串接=完整文字生成

### 下一步方向(中华定调:不同起点叠加态并行多模态统一推理与生成)
1. 先让项目对外可用:把 server_qentl.qentl 的 /ide /api/xiaoqu / 路由真挂到9802
2. 建反向QSCL(算子2),实现生成=识别逆运算
3. 补真QNS训练层,把训练完全搬进QVM能跑的QEntL代码
4. 四大组件(qsm/ref/som/weq)从printf空壳变真功能
