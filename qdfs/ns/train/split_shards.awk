#!/usr/bin/awk -f
# ============================================================================
# split_shards.awk - v9 权重流分片切分器（纯 awk，禁 Python）
#
# 配套: qscl_32x32_v9.qentl 的 save_weights_stderr()
#       该函数用 printf 把 515 类权重打到 stderr（QVM printf 实际写 stderr，
#       见 qentl-runtime-pitfalls §12），shell 用 `2> stream` 收集成单流，
#       再由本脚本按标记行切成 515 个分片文件。
#
# 输入流格式（v9 save_weights_stderr 产出）:
#   === QSCL 32x32 v9 权重流 (stderr stream) ===        <- 日志行，跳过
#   META batch=0 state=0 seed=1 lr=500 nclass=515 pix=1024 nelem=527360
#   C0: 0,3,5,7,...(1024个逗号分隔整数)
#   C1: ...
#   ...
#   C514: ...
#   === 权重流结束 (515类 x 1024值 = 527360值, 标记行C0..C514) ===
#
# 三态输入布局（运行时 printf 的换行时机不可控，三种都必须正确）:
#   A. 标记与值同一行:      "C0: v0,v1,...v1023"          （理想情况）
#   B. 标记行无值+续行:     "C0:" / "v0,v1,..."
#   C. 标记行有值+再刷续行: "C0: v0..v299" / "v300..v799" / "v800..v1023"
#   B/C 的判定依据: 只有【整行全是 -?[0-9]+ 逗号分隔】的行才算续行；
#   含字母/中文/空格/冒号的训练日志行绝不可能是续行（防 §12 日志数字污染计数）。
#
# 输入日志混流:
#   v9 进程 stdout 为空（`>/dev/null`），stderr 同时含【训练日志】
#   （"态0 ep0: 正确115/~129 更新60"、"行偏移表: 4226行" 等）与权重块。
#   本脚本只认 ① 标记行 ^C[0-9]+:  ② 纯数字续行；其余全部跳过。
#
# 输出（每类一个文件，与 v7b save_state_weights 的分片命名/格式完全一致）:
#   ${dir}/qscl_32x32_b{batch}_s{state}_c{c}.w   c=0..514，各1024逗号分隔整数
#   ${dir}/qscl_32x32_b{batch}_s{state}_stream.w  515个逗号行顺序拼接（可选）
#
# 下游兼容性:
#   * merge_32x32.sh  -- 形态B: qscl_32x32_b{b}_s{s}_c{c}.w 各1024逗号值。
#       norm_one_state() 优先找单文件 b{s}.w，缺失时按形态B收集515分片 →
#       本脚本产出的分片正好命中形态B分支。分片内严禁任何标记/日志行，
#       否则 merge 的元素数校验（527360）会失败。
#   * verify_weights.awk -- is_numline() 要求每行匹配 ^-?([0-9]+,)*[0-9]+$，
#       本脚本每行都是纯数字逗号分隔（无标记前缀），直接兼容:
#         awk -v mode=shard -f verify_weights.awk models/qscl_32x32_b0_s0_c*.w
#       或单流: awk -v mode=block -f verify_weights.awk ..._s0_stream.w
#   * verify_accuracy.awk -- ARGV 按 c 升序喂515个分片 + stdin 数据，
#       本脚本按 c 升序写出，glob 排序即升序，直接兼容。
#       注意: verify_accuracy.awk 用 awk 数值转换解析标签，无法解析本数据
#       的 hex 大写标签（A..1081），只能评估纯数字标签行。这是该工具
#       自身的既有局限（awk 无 hex2dec），非本脚本问题。
#
# 用法:
#   awk -v dir=qdfs/ns/models -f split_shards.awk stream.w
#   # 从 stdin 读流:
#   ./bin/qvm_boot run/qscl_32x32_v9.qbc | awk -v dir=qdfs/ns/models -f split_shards.awk
#   # 命令行覆盖 batch/state（否则从 META 行解析，再否则默认 b0/s0）:
#   awk -v dir=... -v batch=3 -v state=2 -f split_shards.awk stream.w
#
# 输出: 结构化报告 + 退出码 0=515分片全部1024值 1=校验失败
# 注: 用 awk 写文件（重定向 > 字符串文件名），不依赖 ARGIND，POSIX awk/mawk 均可用。
#     awk 里 `>>` 重定向优先级低于算术运算，故所有写入先用临时变量承接。
# ============================================================================

BEGIN {
    N_CLASS = 515
    N_PIX   = 1024
    EXPECTED= N_CLASS * N_PIX          # 527360

    dir     = (dir == "" ? "/root/QSM/QLife/qdfs/ns/models" : dir)
    batch   = (batch == "" ? -1 : batch + 0)
    state   = (state == "" ? -1 : state + 0)

    cur   = -1                        # 当前在收值的类号（-1=无）
    linebuf = ""                      # 该类累积的完整逗号串（内联+续行）
    have_any = 0                      # 该类是否已收到任何值
    n_class_done = 0
    n_elem       = 0
    nonzero      = 0
    minv = 0; maxv = 0; first = 1
    dupmark = 0; badmark = 0; oops = 0
    contline = 0
    loglines = 0
    init_paths = 0
    nstream = 0

    # 预生成515个分片名（命令行已给 batch/state 时可直接用；否则 META 后重建）
    for (c = 0; c < N_CLASS; c++) {
        fshard[c] = dir "/qscl_32x32_b" (batch >= 0 ? batch : "X") "_s" \
                    (state >= 0 ? state : "X") "_c" c ".w"
    }
    nstream_name = dir "/qscl_32x32_bX_sX_stream.w"
}

# 判定整行是否纯数字逗号串（含可选空白）；返回 "" = 非纯数字行
function is_numline(s,   t) {
    t = s
    sub(/^[ \t\r]+/, "", t); sub(/[ \t\r]+$/, "", t)
    if (t == "") return ""
    if (t ~ /^-?([0-9]+,)*[0-9]+$/) return t
    return ""
}

# 把一段逗号串并入 linebuf，同时统计元素/非零/min/max
function merge(vals,   n, i, v) {
    if (linebuf != "") linebuf = linebuf "," vals
    else              linebuf = vals
    n = split(vals, arr, ",")
    for (i = 1; i <= n; i++) {
        if (arr[i] == "") continue
        v = arr[i] + 0
        n_elem++
        if (v != 0) nonzero++
        if (first || v < minv) minv = v
        if (first || v > maxv) maxv = v
        first = 0
    }
    have_any = 1
}

# 类 cur 的值流结束 → 写单行分片 + 单流 + 关文件
function finalize_class(   f) {
    if (cur < 0) return
    f = fshard[cur]
    if (!have_any) {
        oops++                       # 标记行既无内联值也无续行
        cur = -1; linebuf = ""; have_any = 0
        n_class_done++
        return
    }
    printf "%s\n", linebuf >> f
    printf "%s\n", linebuf >> nstream_name
    nstream++
    close(f)
    cur = -1; linebuf = ""; have_any = 0
    n_class_done++
}

# 解析一行 "C<c>: <值>" 标记行；返回 "MARK" / "DUP" / ""
function try_marker(s,   p, cs, c, rest) {
    if (s !~ /^C[0-9]+:/) return ""
    p = index(s, ":")
    cs = substr(s, 2, p - 2)
    c = cs + 0
    if (c < 0 || c >= N_CLASS) return ""
    rest = substr(s, p + 1)
    sub(/^[ \t]+/, "", rest)
    sub(/[ \t\r]+$/, "", rest)
    if (c_seen[c]) { dupmark++; return "DUP" }
    c_seen[c] = 1
    cur = c
    linebuf = ""
    have_any = 0
    if (rest != "") merge(rest)      # 内联值也计入元素/非零/min/max 统计
    return "MARK"
}

{
    line = $0
    sub(/\r$/, "", line)

    # META 行: 解析 batch/state（命令行未指定时）
    if (line ~ /^META[ \t]/) {
        if (batch < 0) {
            k = index(line, "batch="); if (k > 0) {
                v = substr(line, k + 6); sub(/[^0-9].*$/, "", v); batch = v + 0
            }
        }
        if (state < 0) {
            k = index(line, "state="); if (k > 0) {
                v = substr(line, k + 6); sub(/[^0-9].*$/, "", v); state = v + 0
            }
        }
        init_paths = 1
        loglines++
        next
    }
    if (init_paths) {
        for (c = 0; c < N_CLASS; c++) {
            fshard[c] = dir "/qscl_32x32_b" batch "_s" state "_c" c ".w"
        }
        nstream_name = dir "/qscl_32x32_b" batch "_s" state "_stream.w"
        nstream = 0
        init_paths = 0
    }

    # ---- 已在收某类的值: 本行是否为它的续行 ----
    if (cur >= 0) {
        t = is_numline(line)
        if (t != "") { merge(t); contline++; next }
        finalize_class()             # 值流结束；本行可能是下一个标记行
    }

    m = try_marker(line)
    if (m == "MARK") next
    if (m == "DUP")  next

    # 其余一律跳过（banner / 训练日志 / 空行 / 行偏移表 / 提示行）
    loglines++
}

END {
    # 冲刷末尾悬挂的值流（文件结尾时还没有非数字行来触发 finalize）
    if (cur >= 0) finalize_class()

    print "======================================================"
    print "  QEntL v9 权重流分片切分报告 (split_shards.awk)"
    print "======================================================"
    print "规格 (从 qscl_32x32_v9.qentl 源码推导, 非臆造):"
    print "  布局        : W[c*1024 + p]  c=0..514 类, p=0..1023 像素"
    print "  来源        : save_weights_stderr() 每类 printf 'C<c>: ' + 1024值"
    print "  期望总元素  : " N_CLASS " x " N_PIX " = " EXPECTED
    print "  分片数      : " N_CLASS " 个 (qscl_32x32_b" batch "_s" state "_c0..514.w)"
    print "------------------------------------------------------"
    print "输入统计:"
    print "  已切分片类数 : " n_class_done "  期望 " N_CLASS
    print "  纯数字元素数 : " n_elem "  期望 " EXPECTED
    print "  单流行数     : " nstream "  (期望 " N_CLASS " 行, 每行1024值)"
    print "  非权重行数   : " loglines "  (banner/META/训练日志, 已跳过)"
    print "  续行修补     : " contline "  (printf 把1024值刷到多行)"
    print "  重复标记     : " dupmark "  断裂/空值: " oops
    print "------------------------------------------------------"
    print "权重值统计:"
    print "  非零元素     : " nonzero "  (" sprintf("%.4f", (n_elem > 0 ? nonzero / n_elem : 0) * 100) "%)"
    print "  值范围       : min=" minv "  max=" maxv "  幅度=" (maxv - minv)
    print "------------------------------------------------------"

    ok = 1
    if (n_class_done != N_CLASS) {
        print "[FAIL] 分片类数 " n_class_done " != " N_CLASS
        print "       标记行缺失/断裂 —— merge_32x32.sh 形态B收集会报 ERROR 缺分片"
        ok = 0
    } else {
        print "[PASS] 515个分片全部切出"
    }
    if (n_elem != EXPECTED) {
        print "[FAIL] 元素数 " n_elem " != " EXPECTED
        print "       按 §12/§17 属伪权重（偏移/断裂/日志污染）"
        ok = 0
    } else {
        print "[PASS] 元素数 = " EXPECTED " (结构性标记成立)"
    }
    if (nonzero == 0) {
        print "[FAIL] 非零元素 = 0 —— 全零权重，未训练（检查 axpy_arr_at 是否生效）"
        ok = 0
    } else {
        print "[PASS] 非零元素 = " nonzero " (权重非退化)"
    }
    if (minv == maxv && n_elem > 0) {
        print "[FAIL] min==max —— 权重退化为常数组"
        ok = 0
    }
    if (nstream != N_CLASS) {
        print "[WARN] 单流线数 " nstream " != " N_CLASS "（不影响分片，仅影响 stream.w 校验）"
    }
    if (dupmark > 0 || oops > 0) {
        print "[WARN] 流中有异常行 (重复=" dupmark " 断裂/空值=" oops ")，请查 v9 输出"
    }

    print "------------------------------------------------------"
    print "下游兼容性:"
    print "  merge_32x32.sh 形态B: 分片名 qscl_32x32_b" batch "_s" state "_c{0..514}.w"
    print "  verify_weights:  awk -v mode=shard -f verify_weights.awk <dir>/qscl_32x32_b" batch "_s" state "_c*.w"
    print "  verify_weights:  awk -v mode=block -f verify_weights.awk " nstream_name
    print "------------------------------------------------------"
    if (ok) print "结论: 分片切分 通过（可直接喂 merge_32x32.sh）"
    else    print "结论: 分片切分 失败 —— 不可用于合并/准确率验证"
    print "======================================================"
    exit (ok ? 0 : 1)
}
