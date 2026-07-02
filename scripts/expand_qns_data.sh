#!/bin/bash
# QNS训练数据扩充脚本 - 纯bash实现（符合QEntL全栈要求，不使用第三方库）
# 将messages格式的JSONL转换为{input, output}格式

set -e
cd /root/QSM/data

echo "=== QNS 训练数据扩充脚本 ==="
echo "目标：将 messages 格式转换为 {input, output} 格式"
echo ""

# 函数：转换 messages 格式为 {input, output}
convert_messages_to_io() {
    local infile="$1"
    local outfile="$2"
    echo "  转换: $infile -> $outfile"
    
    # 使用 awk 提取 user content 和 assistant content
    awk '{
        line = $0
        # 提取 user content
        user_start = index(line, "\"role\": \"user\"")
        if (user_start == 0) next
        
        # 找到 user 的 content
        user_content_start = index(line, "\"content\": \"")
        if (user_content_start == 0) next
        user_content_start += 13  # 跳过 "content": "
        
        # 找到 user content 的结束（在 assistant 之前）
        rest = substr(line, user_content_start)
        # 寻找 "}, {" 作为分隔
        sep = index(rest, "\"}, {\"")
        if (sep == 0) sep = index(rest, "\"}, {")
        if (sep == 0) next
        
        user_val = substr(rest, 1, sep - 1)
        # 移除末尾可能的引号
        if (substr(user_val, length(user_val), 1) == "\"") user_val = substr(user_val, 1, length(user_val) - 1)
        
        # 提取 assistant content
        rest2 = substr(rest, sep)
        asst_start = index(rest2, "\"content\": \"")
        if (asst_start == 0) next
        asst_start += 13
        asst_val = substr(rest2, asst_start)
        # 移除末尾的 "]}"
        gsub("\"\\]}", "", asst_val)
        gsub("\"\\]", "", asst_val)
        gsub("\\]}", "", asst_val)
        gsub("\\]", "", asst_val)
        
        # 输出 {input, output} 格式
        printf "{\"input\": \"%s\", \"output\": \"%s\"}\n", user_val, asst_val
    }' "$infile" > "$outfile"
    
    local count=$(wc -l < "$outfile")
    echo "    转换完成: $count 条记录"
}

# 函数：统计文件记录数
count_records() {
    wc -l < "$1"
}

echo "=== 步骤1：分析现有数据格式 ==="
echo ""

# 检查 yi_4120_merged_for_gemma.jsonl（已经是正确格式）
io_count=$(count_records yi_4120_merged_for_gemma.jsonl)
echo "yi_4120_merged_for_gemma.jsonl: $io_count 条 (已为 {input,output} 格式)"

# 检查 messages 格式的大文件
msg_count=$(count_records yi_gemma_training_merged.jsonl)
echo "yi_gemma_training_merged.jsonl: $msg_count 条 (messages 格式)"

msg_count2=$(count_records yi_char_trilingual_v3.jsonl)
echo "yi_char_trilingual_v3.jsonl: $msg_count2 条 (messages 格式)"

msg_count3=$(count_records yi_structured_v3.jsonl)
echo "yi_structured_v3.jsonl: $msg_count3 条 (messages 格式)"

msg_count4=$(count_records yi_detailed_descriptions_v3.jsonl)
echo "yi_detailed_descriptions_v3.jsonl: $msg_count4 条 (messages 格式)"

msg_count5=$(count_records yi_dense_training_v3.jsonl)
echo "yi_dense_training_v3.jsonl: $msg_count5 条 (messages 格式)"

echo ""
echo "=== 步骤2：转换 messages 格式为 {input, output} 格式 ==="
echo ""

# 转换大文件
convert_messages_to_io yi_gemma_training_merged.jsonl yi_gemma_training_merged_io.jsonl
convert_messages_to_io yi_char_trilingual_v3.jsonl yi_char_trilingual_v3_io.jsonl
convert_messages_to_io yi_structured_v3.jsonl yi_structured_v3_io.jsonl
convert_messages_to_io yi_detailed_descriptions_v3.jsonl yi_detailed_descriptions_v3_io.jsonl
convert_messages_to_io yi_dense_training_v3.jsonl yi_dense_training_v3_io.jsonl

echo ""
echo "=== 步骤3：合并所有 {input, output} 格式数据 ==="
echo ""

# 合并所有转换后的文件 + 原始 yi_4120_merged
cat yi_4120_merged_for_gemma.jsonl \
    yi_gemma_training_merged_io.jsonl \
    yi_char_trilingual_v3_io.jsonl \
    yi_structured_v3_io.jsonl \
    yi_detailed_descriptions_v3_io.jsonl \
    yi_dense_training_v3_io.jsonl \
    > qns_expanded_all.jsonl

total=$(wc -l < qns_expanded_all.jsonl)
echo "合并完成: qns_expanded_all.jsonl ($total 条记录)"

echo ""
echo "=== 步骤4：数据质量检查 ==="
echo ""

# 检查空记录
empty_count=$(grep -c '"input": "", "output": ""' qns_expanded_all.jsonl 2>/dev/null || echo 0)
echo "空记录数: $empty_count"

# 检查有效记录
valid_count=$(grep -c '"input": "[^"]*"' qns_expanded_all.jsonl 2>/dev/null || echo 0)
echo "有效记录数: $valid_count"

# 检查前几条
echo ""
echo "前5条记录示例:"
head -5 qns_expanded_all.jsonl | while read line; do
    echo "  $line"
done

echo ""
echo "=== 步骤5：生成最终训练数据集 ==="
echo ""

# 去重（基于 input 字段）
echo "去重处理中..."
awk '!seen[$0]++' qns_expanded_all.jsonl > qns_expanded_dedup.jsonl
dedup_count=$(wc -l < qns_expanded_dedup.jsonl)
echo "去重后: $dedup_count 条记录 (去除了 $((total - dedup_count)) 条重复)"

# 创建最终数据集（与原始文件名相同，便于直接替换）
cp qns_expanded_dedup.jsonl yi_4120_merged_for_gemma.jsonl

echo ""
echo "=== 完成 ==="
echo "最终数据集: yi_4120_merged_for_gemma.jsonl ($dedup_count 条记录)"
echo ""

# 清理临时文件
echo "清理临时转换文件..."
rm -f *_io.jsonl qns_expanded_all.jsonl
echo "清理完成"

echo ""
echo "=== 数据扩充汇总 ==="
echo "原始数据: 355 条"
echo "扩充后: $dedup_count 条"
echo "扩充倍数: $(echo "scale=1; $dedup_count / 355" | bc) 倍"
