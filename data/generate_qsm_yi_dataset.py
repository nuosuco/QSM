#!/usr/bin/env python3
"""
QSM 彝文数据集生成器 (2026-07-06)
合并所有训练 JSONL 为统一 QSM 彝文训练数据集，并生成统计报告。
"""
import json, os, sys, re, html
from collections import Counter, defaultdict

DATA_DIR = '/root/QSM/data'
OUTPUT_DIR = '/root/QSM/data/qsm_yi_dataset'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 工具函数 ──

def is_yi_char(c):
    """检测是否为彝文字符（U+F2000–U+F37FF）"""
    cp = ord(c)
    return 0xF2000 <= cp <= 0xF37FF

def count_yi_chars(text):
    """统计文本中彝文字符数量"""
    return sum(1 for c in str(text) if is_yi_char(c))

def safe_load_jsonl(path):
    """安全加载 JSONL，跳过无效行"""
    samples = []
    errors = 0
    with open(path, encoding='utf-8', errors='replace') as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            try:
                obj = json.loads(line)
                samples.append(obj)
            except json.JSONDecodeError:
                errors += 1
    return samples, errors

def normalize_to_messages(sample):
    """将所有格式统一为 {messages: [{role, content}]} 格式"""
    if isinstance(sample, dict):
        # 格式1: messages
        if 'messages' in sample and isinstance(sample['messages'], list):
            msgs = []
            for m in sample['messages']:
                if isinstance(m, dict):
                    role = m.get('role', 'user')
                    content = m.get('content', '')
                    if content:
                        msgs.append({'role': role, 'content': str(content)})
            if msgs:
                return {'messages': msgs}
        # 格式2: input/output
        if 'input' in sample and 'output' in sample:
            inp = str(sample['input']) if sample['input'] else ''
            out = str(sample['output']) if sample['output'] else ''
            if inp or out:
                return {'messages': [
                    {'role': 'user', 'content': inp},
                    {'role': 'assistant', 'content': out}
                ]}
        # 格式3: user/assistant
        if 'user' in sample and 'assistant' in sample:
            u = str(sample['user']) if sample['user'] else ''
            a = str(sample['assistant']) if sample['assistant'] else ''
            if u or a:
                return {'messages': [
                    {'role': 'user', 'content': u},
                    {'role': 'assistant', 'content': a}
                ]}
        # 格式4: query/response
        for k in ['query', 'question', 'text']:
            if k in sample and sample[k]:
                for r in ['response', 'answer', 'reply']:
                    if r in sample and sample[r]:
                        return {'messages': [
                            {'role': 'user', 'content': str(sample[k])},
                            {'role': 'assistant', 'content': str(sample[r])}
                        ]}
    return None

def detect_category(filename):
    """根据文件名检测数据类别"""
    f = filename.lower()
    cats = {
        'dictionary': ['对照表', '三语', 'trilingual', 'dict'],
        'character': ['char', '字符', 'character'],
        'conversation': ['conversation', 'chat', '对话'],
        'translation': ['translate', '翻译', 'translation'],
        'culture': ['culture', '文化', 'wisdom', 'proverb', 'idiam'],
        'grammar': ['grammar', '语法', 'sov'],
        'daily_life': ['daily', '日常', 'life'],
        'tech': ['tech', 'programming', 'internet', '量子', 'quantum', 'qentl'],
        'science': ['science', 'geo', 'health', 'math', 'science'],
        'language_learning': ['learning', 'teach', 'lesson'],
        'paragraph': ['paragraph', '段'],
        'sentence': ['sentence', '句'],
        'structured': ['structured', 'dense', 'detailed', 'expanded', 'diverse'],
        'merged': ['merged', 'gemma', 'all_in_one', 'all_training'],
        'general': [],
    }
    for cat, keywords in cats.items():
        for kw in keywords:
            if kw in f:
                return cat
    return 'general'

# ── 主流程 ──

print("=" * 70)
print("QSM 彝文数据集生成器")
print("=" * 70)

# 1. 扫描所有 JSONL
jsonl_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.jsonl')])
print(f"\n[1/5] 扫描数据目录: 找到 {len(jsonl_files)} 个 JSONL 文件")

# 2. 逐文件分析
file_stats = []
all_samples = []
all_messages = []
category_counts = Counter()
total_yi_chars_in_user = 0
total_yi_chars_in_assistant = 0
yi_vocab = Counter()
total_lines = 0
total_errors = 0

for fname in jsonl_files:
    fpath = os.path.join(DATA_DIR, fname)
    fsize = os.path.getsize(fpath)
    raw_lines = sum(1 for _ in open(fpath, errors='replace'))
    samples, errors = safe_load_jsonl(fpath)
    
    # 统一格式
    normalized = []
    yi_in_file = 0
    for s in samples:
        msg = normalize_to_messages(s)
        if msg:
            normalized.append(msg)
            for m in msg.get('messages', []):
                c = count_yi_chars(m['content'])
                yi_in_file += c
                # 收集彝文字汇
                for ch in str(m['content']):
                    if is_yi_char(ch):
                        yi_vocab[ch] += 1
    
    cat = detect_category(fname)
    category_counts[cat] += len(normalized)
    
    file_stats.append({
        'file': fname,
        'size': fsize,
        'raw_lines': raw_lines,
        'valid_samples': len(normalized),
        'yi_chars': yi_in_file,
        'category': cat,
        'errors': errors
    })
    
    all_samples.extend(normalized)
    total_lines += raw_lines
    total_errors += errors

print(f"[2/5] 解析完成: {len(jsonl_files)} 文件, {len(all_samples)} 有效样本, {total_errors} 解析错误")

# 3. 生成合并数据集（messages 格式）
merged_path = os.path.join(OUTPUT_DIR, 'qsm_yi_merged_messages.jsonl')
with open(merged_path, 'w', encoding='utf-8') as f:
    for s in all_samples:
        f.write(json.dumps(s, ensure_ascii=False) + '\n')
merged_size = os.path.getsize(merged_path)
print(f"[3/5] 合并数据集写入: {merged_path}")
print(f"     大小: {merged_size/1024/1024:.2f} MB, 样本数: {len(all_samples)}")

# 4. 生成输入输出格式（input/output）
io_samples = []
for s in all_samples:
    msgs = s.get('messages', [])
    if len(msgs) >= 2:
        u = msgs[0]['content']
        a = msgs[1]['content'] if len(msgs) > 1 else ''
        if u and a:
            io_samples.append({'input': u, 'output': a})
    elif len(msgs) == 1:
        io_samples.append({'input': msgs[0]['content'], 'output': ''})

io_path = os.path.join(OUTPUT_DIR, 'qsm_yi_merged_input_output.jsonl')
with open(io_path, 'w', encoding='utf-8') as f:
    for s in io_samples:
        f.write(json.dumps(s, ensure_ascii=False) + '\n')
io_size = os.path.getsize(io_path)
print(f"[4/5] 输入输出格式: {io_path} ({io_size/1024/1024:.2f} MB, {len(io_samples)} 样本)")

# 5. 生成报告
print(f"[5/5] 生成分析报告...")

# 统计
total_yi_vocab = len(yi_vocab)
top_yi_chars = yi_vocab.most_common(50)

# 按类别统计
cat_stats = sorted(category_counts.items(), key=lambda x: -x[1])

# 有彝文的样本数
yi_samples = sum(1 for s in all_samples if any(
    count_yi_chars(m['content']) > 0 for m in s.get('messages', [])
))

# HTML 报告
report = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>QSM 彝文数据集报告 2026-07-06</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #0a0e17; color: #c8d6e5; line-height: 1.7; padding: 40px; }}
h1 {{ font-size: 28px; background: linear-gradient(135deg, #00d2ff, #7b2ff7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }}
h2 {{ color: #00d2ff; font-size: 20px; margin: 30px 0 15px; border-bottom: 1px solid #1a2332; padding-bottom: 8px; }}
h3 {{ color: #7b2ff7; font-size: 16px; margin: 20px 0 10px; }}
.meta {{ color: #576574; font-size: 13px; margin-bottom: 30px; }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 20px 0; }}
.kpi {{ background: #0f1520; border: 1px solid #1a2332; border-radius: 8px; padding: 20px; text-align: center; }}
.kpi .num {{ font-size: 32px; font-weight: bold; color: #00d2ff; }}
.kpi .label {{ font-size: 13px; color: #7f8fa6; margin-top: 5px; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }}
th {{ background: #0f1520; color: #00d2ff; padding: 10px; text-align: left; border-bottom: 2px solid #1a2332; }}
td {{ padding: 8px 10px; border-bottom: 1px solid #0d1520; }}
tr:hover {{ background: #0f1520; }}
.tag {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }}
.ok {{ background: rgba(0,210,255,0.1); color: #00d2ff; }}
.warn {{ background: rgba(255,200,0,0.1); color: #ffc800; }}
.bar {{ height: 8px; background: #1a2332; border-radius: 4px; overflow: hidden; }}
.bar-fill {{ height: 100%; background: linear-gradient(90deg, #00d2ff, #7b2ff7); }}
.vocab {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 15px 0; }}
.vocab-char {{ background: #0f1520; border: 1px solid #1a2332; padding: 8px 12px; border-radius: 6px; font-size: 24px; }}
.vocab-char .count {{ font-size: 11px; color: #7f8fa6; }}
</style>
</head>
<body>
<h1>QSM 彝文数据集生成报告</h1>
<p class="meta">生成时间: 2026-07-06 | QEntL 项目 | 阶段4-8 推进</p>

<h2>📊 核心指标</h2>
<div class="kpis">
  <div class="kpi"><div class="num">{len(jsonl_files)}</div><div class="label">JSONL 源文件</div></div>
  <div class="kpi"><div class="num">{total_lines:,}</div><div class="label">总行数</div></div>
  <div class="kpi"><div class="num">{len(all_samples):,}</div><div class="label">有效训练样本</div></div>
  <div class="kpi"><div class="num">{merged_size/1024/1024:.1f}M</div><div class="label">合并数据集大小</div></div>
  <div class="kpi"><div class="num">{yi_samples:,}</div><div class="label">含彝文样本数</div></div>
  <div class="kpi"><div class="num">{total_yi_vocab}</div><div class="label">彝文字汇量</div></div>
</div>

<h2>📂 数据类别分布</h2>
<table>
<tr><th>类别</th><th>样本数</th><th>占比</th><th>分布</th></tr>"""

for cat, cnt in cat_stats:
    pct = cnt / len(all_samples) * 100 if all_samples else 0
    report += f'<tr><td><span class="tag ok">{cat}</span></td><td>{cnt:,}</td><td>{pct:.1f}%</td><td><div class="bar"><div class="bar-fill" style="width:{pct}%"></div></div></td></tr>'

report += f"""</table>

<h2>📁 源文件统计 (前20)</h2>
<table>
<tr><th>文件名</th><th>大小</th><th>行数</th><th>有效样本</th><th>彝文字符</th><th>类别</th></tr>"""

for fs in sorted(file_stats, key=lambda x: -x['valid_samples'])[:20]:
    report += f'<tr><td>{fs["file"]}</td><td>{fs["size"]/1024:.1f}K</td><td>{fs["raw_lines"]}</td><td>{fs["valid_samples"]}</td><td>{fs["yi_chars"]}</td><td><span class="tag ok">{fs["category"]}</span></td></tr>'

report += f"""</table>

<h2>🔤 彝文字汇 Top 30</h2>
<div class="vocab">"""
for ch, cnt in top_yi_chars[:30]:
    report += f'<div class="vocab-char">{html.escape(ch)}<div class="count">{cnt}次</div></div>'

report += f"""</div>

<h2>💾 输出文件</h2>
<table>
<tr><th>文件名</th><th>格式</th><th>大小</th><th>用途</th></tr>
<tr><td>qsm_yi_merged_messages.jsonl</td><td>messages</td><td>{merged_size/1024/1024:.1f} MB</td><td>统一训练集 (ChatML)</td></tr>
<tr><td>qsm_yi_merged_input_output.jsonl</td><td>input/output</td><td>{io_size/1024/1024:.1f} MB</td><td>QNN训练集</td></tr>
</table>

<h2>📋 解析统计</h2>
<table>
<tr><th>指标</th><th>值</th></tr>
<tr><td>总行数</td><td>{total_lines:,}</td></tr>
<tr><td>有效样本</td><td>{len(all_samples):,}</td></tr>
<tr><td>解析错误行</td><td>{total_errors}</td></tr>
<tr><td>含彝文样本</td><td>{yi_samples:,} ({yi_samples/len(all_samples)*100:.1f}%)</td></tr>
<tr><td>彝文字汇量</td><td>{total_yi_vocab}</td></tr>
</table>

<p class="meta">报告生成: QSM 彝文数据集生成器 v1.0 | 2026-07-06</p>
</body>
</html>"""

report_path = os.path.join(OUTPUT_DIR, 'QSM彝文数据集报告.html')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

# JSON 统计
stats_json = {
    'generated_at': '2026-07-06',
    'source_files': len(jsonl_files),
    'total_lines': total_lines,
    'valid_samples': len(all_samples),
    'parsed_errors': total_errors,
    'yi_samples': yi_samples,
    'yi_vocab_size': total_yi_vocab,
    'yi_samples_pct': round(yi_samples/len(all_samples)*100, 1) if all_samples else 0,
    'category_distribution': dict(cat_stats),
    'top_yi_chars': [{'char': ch, 'count': cnt} for ch, cnt in top_yi_chars[:50]],
    'output_files': [
        {'file': 'qsm_yi_merged_messages.jsonl', 'size': f'{merged_size/1024/1024:.1f}MB', 'format': 'messages'},
        {'file': 'qsm_yi_merged_input_output.jsonl', 'size': f'{io_size/1024/1024:.1f}MB', 'format': 'input/output'},
        {'file': 'QSM彝文数据集报告.html', 'size': 'N/A', 'format': 'report'},
    ],
    'top_files': [{'file': fs['file'], 'samples': fs['valid_samples'], 'yi_chars': fs['yi_chars'], 'category': fs['category']} for fs in sorted(file_stats, key=lambda x: -x['valid_samples'])[:15]],
}
stats_path = os.path.join(OUTPUT_DIR, 'qsm_yi_dataset_stats.json')
with open(stats_path, 'w', encoding='utf-8') as f:
    json.dump(stats_json, f, ensure_ascii=False, indent=2)

print()
print("=" * 70)
print("✅ 生成完成!")
print("=" * 70)
print(f"合并数据集 (messages):  {merged_path} ({merged_size/1024/1024:.1f} MB)")
print(f"合并数据集 (input/out): {io_path} ({io_size/1024/1024:.1f} MB)")
print(f"统计报告 (HTML):         {report_path}")
print(f"统计数据 (JSON):         {stats_path}")
print(f"有效样本: {len(all_samples):,}")
print(f"含彝文样本: {yi_samples:,} ({yi_samples/len(all_samples)*100:.1f}%)")
print(f"彝文字汇量: {total_yi_vocab}")
print(f"源文件: {len(jsonl_files)} 个")
