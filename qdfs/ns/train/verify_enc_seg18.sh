#!/bin/bash
# 类号→码点 推理验证 (纯权重, 不查码点表)
# 推理: 类号 → 13位二进制 → 段选择wh内积(权重) → 选段s → 码点=类+段偏移(off池)
# 偏移在训练时由模型学习并存入off池, 推理只读off池(权重), 不读码点表
set -u
cd /root/QSM/QLife
CC=qdfs/ns/data/yi_5316_classcode.txt
W=qdfs/ns/models/enc_seg18_stream.w
WH=$(sed -n '1p' "$W" | sed 's/,$//')
OFF=$(sed -n '3p' "$W" | sed 's/,$//')
awk -v wh="$WH" -v off="$OFF" '
BEGIN{
  nW=split(wh,W,",")
  nO=split(off,O,",")
  p=1
  for(j=0;j<13;j++){POW2[j]=p; p=p*2}
}
{
  cls=$1; cptrue=$2; tot++
  # 段选择: 每段s, active_s=Σ_j WH[j*18+s]*bit_j(cls), 取最大active
  bs=0; ba=-999999
  for(s=0;s<18;s++){
    act=0
    for(j=0;j<13;j++){
      b=(cls/POW2[j])%2
      act=act+W[j*18+s+1]*b
    }
    if(act>ba){ba=act;bs=s}
  }
  cpp=cls+O[bs+1]
  if(cpp==cptrue){ ok++; if(cls<5000){yo++;yt++} else {po++;pt++} }
  else if(tot<=8){ print "  类"cls": 真"cptrue" 推"cpp" (选段"bs" 偏移"O[bs+1]") ❌" }
}
END{
  print ""
  print "=== 类号→码点 推理验证 (纯权重内积, 不查码点表) ==="
  print "总类: "tot"  正确: "ok"  正确率: "int(ok*100/tot)"%"
  print "--- 分层 ---"
  print "彝文段(类0~4999): "yo"/"yt" = "int(yo*100/yt)"%"
  print "标点段(类5000~5315): "po"/"pt" = "int(po*100/pt)"%"
}' "$CC"
