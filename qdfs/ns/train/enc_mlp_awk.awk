#!/usr/bin/awk -f
# 标点段 17窄段 MLP 训练器 (纯awk, 无池上限)
# 9位类号局部输入 → 12隐藏 → 17段输出, 学17窄段界
BEGIN {
    # 17段界 (类号局部 0~315)
    seg_bounds[0]=0; seg_bounds[1]=95; seg_bounds[2]=102; seg_bounds[3]=112
    seg_bounds[4]=116; seg_bounds[5]=117; seg_bounds[6]=118; seg_bounds[7]=120
    seg_bounds[8]=121; seg_bounds[9]=122; seg_bounds[10]=123; seg_bounds[11]=212
    seg_bounds[12]=217; seg_bounds[13]=219; seg_bounds[14]=220; seg_bounds[15]=221
    seg_bounds[16]=222; seg_bounds[17]=316

    # 初始化权重 (w1: 9x12, w2: 12x17)
    for (i=0;i<108;i++) w1[i] = (i*7)%9 - 4
    for (i=0;i<12;i++) b1[i] = 0
    for (i=0;i<204;i++) w2[i] = (i*5)%9 - 4
    for (i=0;i<17;i++) b2[i] = 0

    lr = 10
    for (ep=0; ep<200; ep++) {
        tc=0; tw=0
        for (lcl=0; lcl<316; lcl++) {
            # 目标段
            tseg=0
            for (s=1;s<17;s++) if (lcl >= seg_bounds[s]) tseg=s
            # 输入 9位
            for (i=0;i<9;i++) x[i] = int(lcl / 2^i) % 2
            # 前向 h = relu(w1*x+b1)
            for (i=0;i<12;i++) {
                acc = b1[i]
                for (j=0;j<9;j++) acc += w1[j*12+i]*x[j]
                if (acc<0) acc=0
                if (acc>400) acc=400
                h[i]=acc
            }
            # 前向 o = w2*h+b2
            for (i=0;i<17;i++) {
                acc2 = b2[i]
                for (j=0;j<12;j++) acc2 += w2[j*17+i]*h[j]
                o[i]=acc2
            }
            # argmax
            best=0; bv=-30000
            for (i=0;i<17;i++) if (o[i]>bv) {bv=o[i]; best=i}
            if (best==tseg) tc++
            else {
                tw++
                # w2更新
                for (j=0;j<12;j++) {
                    hv=h[j]
                    for (i=0;i<17;i++) {
                        gv=0
                        if (i==tseg) gv=1
                        if (i==best) gv--
                        w2[j*17+i] += lr*gv*hv/100
                    }
                }
                # b2更新
                for (i=0;i<17;i++) {
                    gv2=0
                    if (i==tseg) gv2=1
                    if (i==best) gv2--
                    b2[i] += lr*gv2/100
                }
                # w1更新
                for (j=0;j<9;j++) {
                    xv=x[j]
                    for (i=0;i<12;i++) {
                        hk=h[i]; hd=(hk>0)?1:0
                        sumi=0
                        for (k=0;k<17;k++) {
                            gvk=0
                            if (k==tseg) gvk=1
                            if (k==best) gvk--
                            sumi += w2[i*17+k]*gvk
                        }
                        w1[j*12+i] += lr*sumi*hd*xv/1000
                    }
                }
            }
        }
        cr = tc*100/(tc+tw)
        printf("ep%d: 17段MLP(316类) 对%d 错%d = %d%%\n", ep, tc, tw, cr)
        if (tw==0) break
    }

    # 验证
    vok=0
    for (lcl=0; lcl<316; lcl++) {
        tseg=0
        for (s=1;s<17;s++) if (lcl >= seg_bounds[s]) tseg=s
        for (i=0;i<9;i++) x[i] = int(lcl / 2^i) % 2
        for (i=0;i<12;i++) {
            acc=b1[i]
            for (j=0;j<9;j++) acc += w1[j*12+i]*x[j]
            if (acc<0) acc=0
            if (acc>400) acc=400
            h[i]=acc
        }
        for (i=0;i<17;i++) {
            acc2=b2[i]
            for (j=0;j<12;j++) acc2 += w2[j*17+i]*h[j]
            o[i]=acc2
        }
        best=0; bv=-30000
        for (i=0;i<17;i++) if (o[i]>bv) {bv=o[i]; best=i}
        if (best==tseg) vok++
    }
    printf("验证: 17段MLP(316类) 对%d/316 = %d%%\n", vok, vok*100/316)

    # 保存权重
    printf("w1")
    for (i=0;i<108;i++) printf(" %d", w1[i])
    printf("\nb1")
    for (i=0;i<12;i++) printf(" %d", b1[i])
    printf("\nw2")
    for (i=0;i<204;i++) printf(" %d", w2[i])
    printf("\nb2")
    for (i=0;i<17;i++) printf(" %d", b2[i])
    printf("\n")
}
