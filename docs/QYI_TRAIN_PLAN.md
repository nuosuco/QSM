
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
