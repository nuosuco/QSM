# add_two_streams.awk: 两个单行逗号值文件逐字段相加
# 用法: awk -f add_two_streams.awk fileA fileB > sum
BEGIN{FS=","; OFS=","}
NR==FNR{ n=split($0,a,","); next }
{ m=split($0,b,","); s=""; for(i=1;i<=n;i++){ v=(i<=m? b[i]:0)+a[i]; s=(i==1? v : s","v) } print s }
