#!/usr/bin/awk -f
# verify_state_acc.awk - 按态施加 transform + x100 缩放后验证准确率 (与训练管线同口径)
# 用法: awk -v state=0 -v batch=0 -f verify_state_acc.awk shard_c0.w shard_c1.w ... < data
#   state=0: identity, x100
#   state=1: row-mirror (每行像素左右翻转), x100   (transform_sample g_state==1)
#   state=2: random-inversion (不可复现, 仅报权重结构, 不计准确率)
#   state=3: vertical-flip (上下行翻转), x100       (transform_sample g_state==3)
#   state=merged: identity, x100
BEGIN {
    N_CLASS = 515; N_PIX = 1024; EXPECTED = N_CLASS * N_PIX
    state = (state == "" ? "merged" : state)
    batch = (batch == "" ? 0 : batch + 0); base = batch * N_CLASS
    for (fi = 1; fi < ARGC; fi++) {
        f = ARGV[fi]
        while ((getline line < f) > 0) {
            sub(/^[ \t\r]+/, "", line); sub(/[ \t\r]+$/, "", line)
            if (line == "") continue
            if (line !~ /^-?[0-9]+(,-?[0-9]+)*$/) continue
            m = split(line, arr, ",")
            for (i = 1; i <= m; i++) { W[n++] = arr[i] + 0 }
        }
        close(f); ARGV[fi] = ""
    }
}
function hex2dec(h, v, ch, i) {
    v = 0; h = tolower(h)
    for (i = 1; i <= length(h); i++) {
        ch = substr(h, i, 1); v = v * 16
        if (ch >= "0" && ch <= "9") v = v + (ch + 0)
        else if (ch == "a") v = v + 10; else if (ch == "b") v = v + 11
        else if (ch == "c") v = v + 12; else if (ch == "d") v = v + 13
        else if (ch == "e") v = v + 14; else if (ch == "f") v = v + 15
    }
    return v
}
function predict() {
    # 与训练器 predict() 同口径: g_max_val = -30000
    max_val = -30000; max_idx = 0
    c = 0
    while (c < N_CLASS) {
        s = 0; b = c * N_PIX
        for (i = 0; i < N_PIX; i++) if (x[i] != 0) s += W[b + i] * x[i]
        if (s > max_val) { max_val = s; max_idx = c }
        c++
    }
    return max_idx
}
{
    line = $0
    sub(/^[ \t\r]+/, "", line); sub(/[ \t\r]+$/, "", line)
    if (line == "") next
    colon = index(line, ":")
    if (colon == 0) { badlines++; next }
    label = hex2dec(substr(line, 1, colon - 1))
    llocal = label - base
    if (llocal < 0 || llocal >= N_CLASS) { oob++; next }
    pix = substr(line, colon + 1)
    m = split(pix, arr, ",")
    if (m != N_PIX) { badlines++; next }
    for (i = 0; i < N_PIX; i++) p[i] = (arr[i+1] + 0) * 100   # x100 缩放 (训练管线同口径)
    if (state == "1") {   # 行内左右镜像, 仅前16行 (源码 g_t1_i<512 -> row=i/32 0..15)
        for (r = 0; r < 16; r++) for (c2 = 0; c2 < 16; c2++) {
            t = p[r*32+c2]; p[r*32+c2] = p[r*32+31-c2]; p[r*32+31-c2] = t
        }
    } else if (state == "3") {   # 上下行翻转 (源码 row r <-> 31-r, r=0..15, 全32列)
        for (r = 0; r < 16; r++) for (c2 = 0; c2 < 32; c2++) {
            t = p[r*32+c2]; p[r*32+c2] = p[(31-r)*32+c2]; p[(31-r)*32+c2] = t
        }
    }
    for (i = 0; i < N_PIX; i++) x[i] = p[i]
    nz = 0; for (i = 0; i < N_PIX; i++) if (x[i] != 0) nz++
    if (nz == 0) { skipped_zero++; next }
    pred = predict()
    total++
    if (pred == llocal) correct++; else wrong[llocal]++
}
END {
    print "======================================================"
    print "  按态 transform + x100 独立准确率验证 (verify_state_acc.awk)"
    print "======================================================"
    print "state=" state "  batch=" batch "  base=" base
    print "权重: 元素数=" n " 期望=" EXPECTED (n==EXPECTED?"  OK":"  MISMATCH")
    if (n != EXPECTED) { print "[FAIL] 维度不匹配"; exit 1 }
    if (state == "2") {
        print "[SKIP] state2 = 随机反相扰动, 训练时 g_rnd 不可复现"
        print "       无确定 transform 可施加 -> 准确率不可独立验证 (仅报告权重结构)"
        nz2 = 0; mn = 0; mx = 0; first = 1
        for (i = 0; i < n; i++) {
            if (W[i] != 0) nz2++
            if (first || W[i] < mn) mn = W[i]
            if (first || W[i] > mx) mx = W[i]
            first = 0
        }
        print "权重: 非零=" nz2 " min=" mn " max=" mx
        print "======================================================"
        exit 0
    }
    print "有效样本=" total "  正确=" correct "  准确率=" (total>0?sprintf("%.4f%%", correct/total*100):"N/A") "  (" correct "/" total ")"
    print "越界=" oob "  坏行=" badlines "  全零跳过=" skipped_zero
    print "======================================================"
    exit 0
}
