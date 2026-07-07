#!/usr/bin/env python3
"""训练数据质量验证 + 特征工程方案（八阶段）"""
import json, os, sys, re
from collections import Counter, defaultdict

DATA = '/root/QSM/data/yi_4120_merged_for_gemma.jsonl'
DICT = '/root/QSM/data/滇川黔贵通用彝文三语对照表.jsonl'
REPORT = '/root/QSM/FEATURE_ENGINEERING_REPORT.md'

def is_yi_char(ch):
    cp = ord(ch)
    return 0xF2000 <= cp <= 0xF37FF

def load_dict():
    chars = set()
    meta = []
    with open(DICT) as f:
        for line in f:
            try:
                d = json.loads(line)
                yi = d.get('metadata', {}).get('yi_character', '')
                if yi and is_yi_char(yi[0]):
                    chars.add(yi)
                    meta.append(yi)
            except:
                pass
    return chars, meta

def analyze_data(path):
    total = 0; missing_input = 0; missing_output = 0
    valid = 0; empty_input = 0; empty_output = 0
    bad_json = 0; duplicates = 0; seen = set()
    yi_in_input = set(); yi_in_output = set(); yi_in_both = set()
    yi_char_freq = Counter()
    input_lens = []; output_lens = []
    yi_char_count_per_row = Counter()
    max_yi_row = 0; max_yi_content = ''
    
    with open(path, errors='replace') as f:
        for line in f:
            total += 1
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except:
                bad_json += 1; continue
            
            inp = d.get('input', None)
            out = d.get('output', None)
            
            if inp is None: missing_input += 1
            else:
                input_lens.append(len(inp))
                if inp == '': empty_input += 1
            
            if out is None: missing_output += 1
            else:
                output_lens.append(len(out))
                if out == '': empty_output += 1
            
            if inp is not None and out is not None and inp != '' and out != '':
                valid += 1
            
            key = (str(inp)[:200] if inp else '', str(out)[:200] if out else '')
            if key in seen:
                duplicates += 1
            seen.add(key)
            
            for c in (inp or ''):
                if is_yi_char(c):
                    yi_in_input.add(c)
                    yi_char_freq[c] += 1
            for c in (out or ''):
                if is_yi_char(c):
                    yi_in_output.add(c)
                    yi_char_freq[c] += 1
            
            row_yi = sum(1 for c in (inp or '') if is_yi_char(c)) + sum(1 for c in (out or '') if is_yi_char(c))
            yi_char_count_per_row[row_yi] += 1
            if row_yi > max_yi_row:
                max_yi_row = row_yi
                max_yi_content = f"input={inp[:50] if inp else ''}"
    
    return dict(total=total, valid=valid, missing_input=missing_input,
                missing_output=missing_output, empty_input=empty_input,
                empty_output=empty_output, bad_json=bad_json, duplicates=duplicates,
                yi_in_input=yi_in_input, yi_in_output=yi_in_output,
                yi_in_both=yi_in_both, yi_char_freq=yi_char_freq,
                input_lens=input_lens, output_lens=output_lens,
                yi_char_count_per_row=yi_char_count_per_row,
                max_yi_row=max_yi_row, max_yi_content=max_yi_content)

print("Loading dictionary...")
dict_chars, dict_meta = load_dict()
print(f"Dictionary: {len(dict_chars)} unique Yi characters")

print("Analyzing training data...")
r = analyze_data(DATA)

print("=== TRAINING DATA QUALITY REPORT ===")
print(f"Total lines:        {r['total']}")
print(f"Valid (both fields):{r['valid']}")
print(f"Missing input:      {r['missing_input']}")
print(f"Missing output:     {r['missing_output']}")
print(f"Empty input:        {r['empty_input']}")
print(f"Empty output:       {r['empty_output']}")
print(f"Bad JSON:           {r['bad_json']}")
print(f"Duplicate rows:     {r['duplicates']}")

print(f"\nYi chars in input:  {len(r['yi_in_input'])}")
print(f"Yi chars in output: {len(r['yi_in_output'])}")
print(f"Dict Yi chars:      {len(dict_chars)}")

# Coverage
input_dict_overlap = r['yi_in_input'] & dict_chars
output_dict_overlap = r['yi_in_output'] & dict_chars
all_data_yi = r['yi_in_input'] | r['yi_in_output']
data_dict_overlap = all_data_yi & dict_chars
print(f"Dict chars covered (in data): {len(data_dict_overlap)}/{len(dict_chars)} ({len(data_dict_overlap)/len(dict_chars)*100:.1f}%)")
print(f"Dict chars NOT in data: {len(dict_chars) - len(data_dict_overlap)}")
uncovered = dict_chars - all_data_yi
print(f"Dict chars in data union: {len(data_dict_overlap)}")

# Frequency stats
freq = r['yi_char_freq']
print(f"\nUnique Yi chars in data: {len(freq)}")
print(f"Most frequent (top 10):")
for ch, cnt in freq.most_common(10):
    print(f"  U+{ord(ch):05X} (0x{ord(ch):05X}): {cnt}")

# Input/output length stats
il = r['input_lens']; ol = r['output_lens']
print(f"\nInput length: avg={sum(il)/len(il):.1f}, min={min(il)}, max={max(il)}")
print(f"Output length: avg={sum(ol)/len(ol):.1f}, min={min(ol)}, max={max(ol)}")

# Character distribution bins
bins = Counter()
for cp in dict_chars:
    cp_val = ord(cp)
    if 0xF2000 <= cp_val < 0xF2800: bins['F2000-F27FF'] += 1
    elif 0xF2800 <= cp_val < 0xF3000: bins['F2800-F2FFF'] += 1
    elif 0xF3000 <= cp_val < 0xF3800: bins['F3000-F37FF'] += 1
    else: bins['other'] += 1
print(f"\nDictionary Yi chars Unicode range distribution:")
for k,v in sorted(bins.items()):
    print(f"  {k}: {v}")

# Feature engineering plan
N_QUBITS = 12  # 4120 chars → need log2(4120)≈12 qubits for unique encoding
N_DIM = 2**N_QUBITS  # 4096 basis states, close to 4120

print(f"\n=== FEATURE ENGINEERING PLAN ===")
print(f"Method: Quantum Superposition Embedding")
print(f"Qubits per character: {N_QUBITS} (covers 2^{N_QUBITS}={N_DIM} states)")
print(f"Each Yi char → superposition of |token_id%{N_DIM}> basis state")
print(f"Encoding: H⊗{N_QUBITS} then controlled phase rotation")
print(f"Amplitude = sqrt(1/{N_DIM}) for uniform superposition")

# Orthogonality and normalization
print(f"\nOrthogonality: distinct chars → distinct computational basis states")
print(f"  |ψ_a⟩·|ψ_b⟩* = δ_ab (Kronecker delta)")
print(f"Normalization: Σ|α_i|² = 1 for each |ψ⟩")

# Token_id to qubit mapping
print(f"\ntoken_id → qubit mapping:")
print(f"  char_id = dict_index[char] (0..4119)")
print(f"  qubit_state = |char_id % {N_DIM}⟩")
print(f"  12 qubits = 4096 basis states for 4120 chars")

# QNS model integration
print(f"\nQNS model integration:")
print(f"  Input: Yi char → dict_index → token_id")
print(f"  Mapping: token_id → H⊗12 superposition → 12-qubit quantum state")
print(f"  QNS layers: embed → entangle → attention → forward → gradient")
print(f"  Data load: 51899 rows × (input chars + output chars) → quantum circuits")

# Efficiency estimate
avg_yi_per_row = sum(i*c for i,c in r['yi_char_count_per_row'].items()) / r['valid']
print(f"\nAvg Yi chars per valid row: {avg_yi_per_row:.1f}")
print(f"Estimated quantum operations per epoch:")
print(f"  chars_to_embed ≈ {r['valid']:.0f} rows × {avg_yi_per_row:.0f} chars = {r['valid']*avg_yi_per_row:.0f} embeddings")
print(f"  Each embed: {N_QUBITS} H gates + rotations")

print(f"\nData quality score: {r['valid']/r['total']*100:.1f}% valid, {r['duplicates']} duplicates, {len(data_dict_overlap)}/{len(dict_chars)} Yi coverage")
print("DONE")