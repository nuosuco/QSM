#!/usr/bin/awk -f
# verify_accuracy.awk - 防欺骗准确率独立验证器（纯awk，禁Python）
# 用途: 训练完成后独立复算准确率，防"训练器自己报的准确率是伪准确率"（qentl-runtime-pitfalls §11/§17）
#
# ===== 权重维度声明（从 qscl_32x32_v7b.qentl 源码逐行推导，非臆造 —— §17 铁律） =====
# ① 布局: W[c*1024 + p]   c=0..514(类)  p=0..1023(像素)
#    依据: v7b L232-238 predict() 里 "var idx = g_c * 1024" + "get_w(idx + g_i)"
#          以及 train_one() L259/L264/L280/L286 "var idx1 = g_label * 1024"
#          像素索引 g_i 是低位，类索引 g_c 是高位 → 行优先，每类占 1024 个连续元素
# ② 段路由: seg=idx/65535, off=idx%65535（v7b L26-38 get_w 源码）
#          用于校验点积索引不越界：c<515 且 p<1024 → idx<527360<589815=9*65535
# ③ 每批权重 = 单块 527360 元素（不是 9 段拼接文件！v7b 分 9 段是 QVM 内部数组组织，
#    落盘时是 save_weights() L403-427 分片写出 + merge 后仍是同一 527360 元素逻辑块）
# ④ 保存格式（v7b L403-427 save_weights / L431-456 save_state_weights）:
#    每类一个文件 qscl_32x32_b{B}_{m|s{S}}_c{C}.w，内容 = 1024 个逗号分隔整数（单行无日志）
#    因此一个"批"的权重 = 515 个此类文件的拼接，不是单个大文件
# ⑤ 标签: 数据行 "标签:像素0,像素1,..."，标签是【全局类号 0..4225】
#    训练器 parse_sample() L159: g_label = str_to_int(...) - g_base,  g_base = batch*515
#    → 本批验证时须同样减 batch*515 得本批内类号（§11 越界即伪结果的根因）
# ⑥ 点积: score_c = Σ_{p: x[p]>0} W[c*1024+p] * x[p]  （v7b L234-238，x 为 0/1，跳零加速）
#    argmax_c(score_c) = 预测类；与 (label - batch*515) 比对
# ============================================================
#
# 输入:
#   ARGV[1..N]  = 515 个权重分片文件（按 c 升序，每片 1024 逗号分隔整数）
#   stdin       = 数据文件（标签:像素0,像素1,...）
#   -v batch=B : 本批号，决定标签基址 B*515（默认 0）
#   -v tag=STR : 报告中标识（默认 batch<B>）
#
# 用法:
#   # 验证坍缩合并后的权重（batch0）
#   awk -v mode=merged -v batch=0 -f verify_accuracy.awk \
#       models/qscl_32x32_b0_m_c*.w < data/yi_glyph_4226_32x32.data
#   # 验证某一态的独立权重
#   awk -v mode=shard -v batch=2 -f verify_accuracy.awk \
#       models/qscl_32x32_b2_s1_c*.w < data/yi_glyph_4226_32x32.data
#
# 输出: 结构化文本报告 + 退出码 0=权重维度匹配且评估完成 1=权重不合法 2=缺参数

BEGIN {
    N_CLASS  = 515
    N_PIX    = 1024
    EXPECTED = N_CLASS * N_PIX       # 527360
    SEG      = 65535
    SEGS     = 9
    batch    = (batch == "" ? 0 : batch + 0)
    base     = batch * N_CLASS       # 本批标签基址（parse_sample L159 同款）
    mode     = (mode  == "" ? "merged" : mode)
    tag      = (tag   == "" ? "batch" batch : tag)
    n        = 0                     # 已读权重元素数
    nonzero  = 0
    minv     = 0; maxv = 0; first = 1
    FS       = ","

    # ---- 预读所有权重分片（在 stdin 数据之前）----
    if (ARGC < 2) {
        print "[FATAL] 无权重分片文件传入 (ARGV[1..])"
        exit 2
    }
    for (fi = 1; fi < ARGC; fi++) {
        f = ARGV[fi]
        # mawk/gawk 兼容的逐行读取: while ((getline line < f) > 0)
        while ((getline line < f) > 0) {
            t = line
            sub(/^[ \t\r]+/, "", t); sub(/[ \t\r]+$/, "", t)
            if (t == "") continue
            # §11/§17: 每个字段都可能是负数 (训练后权重含 -7/-600 等)
            # 旧正则 -?([0-9]+,)*[0-9]+ 只允许 1 个前导负号 -> 含内部负数的分片被整体跳过
            # -> 维度对不上、漏算, 属伪结果。改成每字段独立判负号。
            if (t !~ /^-?[0-9]+(,-?[0-9]+)*$/) continue
            m = split(t, arr, ",")
            for (i = 1; i <= m; i++) {
                v = arr[i] + 0
                W[n++] = v
                if (v != 0) nonzero++
                if (first || v < minv) minv = v
                if (first || v > maxv) maxv = v
                first = 0
            }
        }
        close(f)
        ARGV[fi] = ""      # 标记为已消费，阻止主循环把权重文件当数据再读一遍
    }
}

# hex2dec: 逐字符 hex->int (与训练器 qscl_32x32_v10.qentl 的 hex2dec() 同口径)
# §18 铁律: awk 的 $0+0 只识别纯数字, hex 字母会被截断 ("100A"->1000, "202"->20)
function hex2dec(h,   v, ch, i) {
    v = 0
    h = tolower(h)
    for (i = 1; i <= length(h); i++) {
        ch = substr(h, i, 1)
        v = v * 16
        if (ch >= "0" && ch <= "9") v = v + (ch + 0)
        else if (ch == "a") v = v + 10
        else if (ch == "b") v = v + 11
        else if (ch == "c") v = v + 12
        else if (ch == "d") v = v + 13
        else if (ch == "e") v = v + 14
        else if (ch == "f") v = v + 15
    }
    return v
}

# 计算单样本 argmax（跳零加速，对应 v7b L234-238 的 if (get_x(g_i) > 0) 分支）
# 参数: nz = 非零像素数；nzarr[0..nz-1] = 非零像素下标
function predict(nz) {
    # 对齐训练器 qscl_32x32_v10.qentl L231: g_max_val = 0 - 30000
    # (所有分数 < -30000 时 max_idx 保持 0 -> 类0 成默认值, 与训练器同口径)
    max_val  = -30000
    max_idx  = 0
    c = 0
    while (c < N_CLASS) {
        s = 0
        b = c * N_PIX
        for (j = 0; j < nz; j++) {
            s += W[b + nzarr[j]] * x[nzarr[j]]
        }
        if (s > max_val) { max_val = s; max_idx = c }
        c++
    }
    return max_idx
}

# 主输入流 = 数据（stdin）
{
    line = $0
    sub(/^[ \t\r]+/, "", line); sub(/[ \t\r]+$/, "", line)
    if (line == "") next
    # 数据行格式: 标签:像素0,像素1,...
    # parse_sample L158: g_c1 = str_index_of(g_line, ":")
    colon = index(line, ":")
    if (colon == 0) { badlines++; next }
    label_str = substr(line, 1, colon - 1)
    pix_str   = substr(line, colon + 1)

    # 标签是 hex 码点 (§18: awk/$0+0 会把 "100A" 截断成 1000, "202" 截断成 20)
    # -> 必须逐字符 hex2dec, 与训练器 qscl_32x32_v10.qentl 的 hex2dec() 同口径
    label = hex2dec(label_str)
    llocal = label - base
    # §11 越界即伪结果：越界直接记为不可判定，不算分
    if (llocal < 0 || llocal >= N_CLASS) { oob++; next }

    # 解析 1024 像素
    m = split(pix_str, arr, ",")
    if (m != N_PIX) { badlines++; next }
    nz = 0
    for (i = 0; i < N_PIX; i++) {
        x[i] = arr[i + 1] + 0
        if (x[i] != 0) { nzarr[nz++] = i }
    }
    if (nz == 0) { skipped_zero++; next }   # 全零像素无信息，不计入有效样本
    pred = predict(nz)
    total++
    if (pred == llocal) {
        correct++
    } else {
        wrong[llocal]++
    }
}

END {
    print "======================================================"
    print "  QEntL 准确率独立验证报告 (verify_accuracy.awk)"
    print "======================================================"
    print "权重维度声明 (源码推导, 非臆造):"
    print "  布局     : W[c*1024 + p]  c=0..514  p=0..1023"
    print "  来源     : qscl_32x32_v7b.qentl L232-238 predict() + L26-38 get_w"
    print "  总元素   : " N_CLASS " x " N_PIX " = " EXPECTED
    print "  段路由   : seg=idx/" SEG " off=idx%" SEG " (v7b L27-28)"
    print "  标签基址 : batch=" batch "  base=" base "  (v7b L159 g_label = str_to_int - g_base)"
    print "------------------------------------------------------"
    print "权重加载统计:"
    print "  模式           : " mode "  tag=" tag
    print "  元素总数       : " n
    print "  期望元素数     : " EXPECTED
    print "  非零元素       : " nonzero "  (" sprintf("%.4f", (n>0?nonzero/n:0)*100) "%)"
    print "  权重范围       : min=" minv "  max=" maxv
    print "  分片文件数     : " (ARGC - 1)
    print "------------------------------------------------------"

    # 硬门: 权重维度必须匹配，否则一切准确率都是伪结果
    if (n != EXPECTED) {
        print "[FAIL] 权重元素数 " n " != " EXPECTED " —— 维度不匹配"
        print "       按 §17 铁律，此权重不可用于准确率验证，跳过评估"
        print "       请核对 v7b 分片保存格式（每类一个 1024 值文件）"
        print "======================================================"
        exit 1
    }
    if (nonzero == 0) {
        print "[FAIL] 权重全零 —— 未训练/坍缩失败，准确率必为 0（非真结果）"
        print "======================================================"
        exit 1
    }
    print "[PASS] 权重维度匹配，进入准确率评估"
    print "------------------------------------------------------"
    print "数据/评估统计:"
    print "  有效样本数     : " total "  (参与 argmax 评估的样本)"
    print "  正确数         : " correct
    if (total > 0) {
        acc = correct / total * 100
        print "  准确率         : " sprintf("%.4f%%", acc) "  (" correct "/" total ")"
    } else {
        print "  [无有效样本可评估]"
    }
    print "  全零像素跳过   : " skipped_zero "  (无信息, 不计入准确率分母)"
    print "  越界跳过       : " oob "  (§11 越界即伪结果, 不计入准确率)"
    print "  坏行跳过       : " badlines "  (格式不合法: 无冒号/像素数!=1024)"
    print "------------------------------------------------------"
    print "结论: " (total > 0 ? "可评估，准确率见上" : "无样本，未评估")
    print "======================================================"
    exit 0
}
