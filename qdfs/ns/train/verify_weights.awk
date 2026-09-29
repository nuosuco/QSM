#!/usr/bin/awk -f
# verify_weights.awk - 防欺骗权重结构验证器（纯awk，禁Python）
# 用途: 训练完成后独立验证权重块完整性，防"走通流程但权重错/维度错"的伪结果（qentl-runtime-pitfalls §11/§17）
#
# 权重规格（从 qscl_32x32_v7b.qentl 源码推导，非臆造）:
#   - 布局: W[c*1024 + p]，c=0..514类, p=0..1023像素（见 predict(): idx = g_c*1024）
#   - 总元素: 515类 x 1024像素 = 527360
#   - 物理存储: 9段定长数组 g_W0..g_W8[65535]，527360 < 9*65535=589815（源码注释 L13）
#   - 段路由: seg=idx/65535, off=idx%65535（get_w，源码 L26-38）
#
# 输入格式: 权重文件"数字+日志混合格式"（§12）
#   QVM printf 走 stderr，stdout 里混入 ep=xx ok=xx acc=xx / [save] 等文本行。
#   本工具只取"纯数字或纯逗号分隔数字"的行/字段，跳过所有日志行。
#   支持两种输入布局:
#     A. 分片文件（每类1024值的逗号行）—— 逐个文件喂入，用 -v mode=shard
#     B. 单块文件（连续527360个逗号分隔值，可能夹杂日志行）—— 用 -v mode=block
#
# 用法:
#   awk -v mode=block -f verify_weights.awk qscl_32x32_b0.w
#   awk -v mode=shard -f verify_weights.awk qscl_32x32_b0_m_c0.w qscl_32x32_b0_m_c1.w ...
#   # 分片模式批量:
#   awk -v mode=shard -f verify_weights.awk models/qscl_32x32_b0_m_c*.w
#
# 输出: 结构化文本报告（元素总数/期望值比对/非零数/min/max/结构标记）+ 退出码0=通过 1=失败
#
# 验证项:
#   ① 元素总数 == 527360 (515*1024)
#   ② 非零元素个数（全零权重 = 未训练/坍缩失败，必报）
#   ③ 权重值范围 min/max
#   ④ 结构性标记: 连续527360个纯数字值（日志数字不污染计数，见 §12 教训）

BEGIN {
    N_CLASS  = 515
    N_PIX    = 1024
    EXPECTED = N_CLASS * N_PIX       # 527360
    SEG      = 65535                 # 段路由分母（get_w: idx/65535）
    SEGS     = 9
    n        = 0                     # 已收纯数字元素数
    nonzero  = 0
    minv     = 0
    maxv     = 0
    first    = 1
    loglines = 0                     # 跳过的日志/非数字行数
    badline  = 0                     # 数字行数不足（结构警告）
    mode     = (mode == "" ? "block" : mode)
    FS       = ","
}

# 判定一行是否"纯数字（或逗号分隔纯数字）行"—— 只取数字，不取日志
# §12 铁律: 日志里 ep=70 这类数字会污染计数 → 必须按"整行是否全是数字"过滤
function is_numline(s,   t, i, ch) {
    t = s
    sub(/^[ \t\r]+/, "", t)
    sub(/[ \t\r]+$/, "", t)
    if (t == "") return 0
    # 容忍尾部逗号 (v10 save_weights 用 emit_ints 每值后打 ",")
    sub(/,$/, "", t)
    # 逐字符检查: 只允许数字/逗号/负号 (mawk 不支持复杂正则, 用简单判定)
    # mawk 的 /-/ 会匹配所有字符 (POSIX quirk), 用 char class [^...] 判定
    if (t ~ /[^0-9,-]/) return 0
    # 允许: 首字符数字或'-', 之后任意次"逗号+数字+可选负号"
    if (t !~ /^[0-9-]/) return 0
    return 1
}

{
    if (!is_numline($0)) {
        loglines++
        next
    }
    for (i = 1; i <= NF; i++) {
        if ($i == "") continue
        n++
        v = $i + 0
        if (v != 0) nonzero++
        if (first || v < minv) minv = v
        if (first || v > maxv) maxv = v
        first = 0
    }
}

END {
    print "======================================================"
    print "  QEntL 权重结构验证报告 (verify_weights.awk)"
    print "======================================================"
    print "权重规格 (源码推导, 非臆造):"
    print "  布局        : W[c*1024 + p]  c=0..514 类, p=0..1023 像素"
    print "  类数        : " N_CLASS "   像素数: " N_PIX
    print "  期望总元素  : " N_CLASS " x " N_PIX " = " EXPECTED
    print "  物理存储    : " SEGS "段定长数组 x " SEG " = " (SEGS*SEG) " (527360<" (SEGS*SEG) ")"
    print "------------------------------------------------------"
    print "输入统计:"
    print "  模式           : " mode
    print "  纯数字元素数   : " n
    print "  期望元素数     : " EXPECTED
    print "  差值           : " (n - EXPECTED)
    print "  跳过日志行数   : " loglines
    print "  非零元素个数   : " nonzero
    print "  零元素个数     : " (n - nonzero)
    print "  权重值范围     : min=" minv "  max=" maxv
    print "  值幅度         : " (maxv - minv)
    print "------------------------------------------------------"

    ok = 1
    if (n != EXPECTED) {
        print "[FAIL] 元素总数不符: " n " != " EXPECTED
        print "       结构性标记(连续527360个数字)不成立 ——"
        print "       权重块偏移/日志污染/分片缺失，按 §12/§17 属伪权重"
        ok = 0
    } else {
        print "[PASS] 元素总数 = " EXPECTED " (结构性标记成立)"
    }
    if (nonzero == 0) {
        print "[FAIL] 非零元素 = 0 —— 全零权重，未训练或坍缩合并失败(见§7 var遮蔽坑)"
        ok = 0
    } else {
        print "[PASS] 非零元素 = " nonzero " (" sprintf("%.4f", nonzero/n*100) "%)"
    }
    if (minv == maxv) {
        print "[FAIL] min==max —— 权重退化为常数组，无区分能力"
        ok = 0
    } else {
        print "[PASS] 值范围非退化: " minv ".." maxv
    }

    print "------------------------------------------------------"
    if (ok) print "结论: 权重结构校验 通过"
    else    print "结论: 权重结构校验 失败 —— 不可用于准确率验证(§17 伪准确率风险)"
    print "======================================================"
    exit (ok ? 0 : 1)
}
