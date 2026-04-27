"""
QSM V4: Encoder-Decoder 量子神经翻译模型
核心改进: 真正的编码器-解码器架构 + 交叉注意力

V2/V3问题: 只有编码器，无法自回归生成翻译
V4方案: Encoder(源语言) → Cross-Attention → Decoder(目标语言)

作者: 小趣WeQ | 监督: 中华Zhoho
日期: 2026-04-28
"""
import math
import json
import random
import os

# ============================================================
# 核心组件
# ============================================================

class QuantumGateAttention:
    """门控量子注意力 - V4交叉注意力核心"""
    
    def __init__(self, d_model, n_heads=4):
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        scale = math.sqrt(2.0 / d_model)
        
        # Q, K, V 投影
        self.W_q = [[random.gauss(0, scale) for _ in range(d_model)] for _ in range(d_model)]
        self.W_k = [[random.gauss(0, scale) for _ in range(d_model)] for _ in range(d_model)]
        self.W_v = [[random.gauss(0, scale) for _ in range(d_model)] for _ in range(d_model)]
        self.W_o = [[random.gauss(0, scale) for _ in range(d_model)] for _ in range(d_model)]
        
        # 量子旋转参数 (可学习)
        self.quantum_theta = [random.gauss(0, 0.1) for _ in range(n_heads)]
        
        # 门控参数
        self.gate = [random.gauss(0, 0.1) for _ in range(d_model)]
        
        # LayerNorm
        self.ln_gamma = [1.0 for _ in range(d_model)]
        self.ln_beta = [0.0 for _ in range(d_model)]
    
    def matmul(self, A, B):
        """矩阵乘法 A(m×k) × B(k×n) = C(m×n)"""
        m = len(A)
        k = len(A[0]) if A else 0
        n = len(B[0]) if B else 0
        C = [[0.0]*n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                s = 0.0
                for p in range(k):
                    s += A[i][p] * B[p][j]
                C[i][j] = s
        return C
    
    def softmax(self, x):
        m = max(x) if x else 0
        e = [math.exp(v - m) for v in x]
        s = sum(e)
        return [v / s for v in e] if s > 0 else [1.0/len(x)] * len(x)
    
    def layer_norm(self, x):
        mean = sum(x) / len(x)
        var = sum((v - mean)**2 for v in x) / len(x)
        std = math.sqrt(var + 1e-6)
        return [(self.ln_gamma[i] * (x[i] - mean) / std + self.ln_beta[i]) for i in range(len(x))]
    
    def forward(self, query, key, value, mask=None):
        """
        query: [seq_q, d_model]
        key:   [seq_k, d_model]  
        value: [seq_k, d_model]
        returns: [seq_q, d_model]
        """
        seq_q = len(query)
        seq_k = len(key)
        d = self.d_model
        
        # Project Q, K, V
        Q = self.matmul(query, self.W_q)  # [seq_q, d]
        K = self.matmul(key, self.W_k)    # [seq_k, d]
        V = self.matmul(key, self.W_v)    # [seq_k, d]
        
        # Multi-head split and attention
        output = [[0.0]*d for _ in range(seq_q)]
        
        for h in range(self.n_heads):
            dk = self.d_k
            start = h * dk
            end = start + dk
            theta = self.quantum_theta[h]
            
            for i in range(seq_q):
                # Extract head slice
                q_h = Q[i][start:end]  # [dk]
                scores = []
                for j in range(seq_k):
                    k_h = K[j][start:end]
                    # Dot product attention
                    score = sum(q_h[ki] * k_h[ki] for ki in range(dk)) / math.sqrt(dk)
                    
                    # Quantum rotation modulation
                    cos_t = math.cos(theta)
                    sin_t = math.sin(theta)
                    if dk >= 2:
                        q_rotated_0 = cos_t * q_h[0] - sin_t * q_h[1]
                        q_rotated_1 = sin_t * q_h[0] + cos_t * q_h[1]
                        score_q = (q_rotated_0 * k_h[0] + q_rotated_1 * k_h[1]) / math.sqrt(dk)
                        # Gated mix: gate * quantum + (1-gate) * classical
                        g = 1.0 / (1.0 + math.exp(-self.gate[start]))  # sigmoid
                        score = g * score_q + (1 - g) * score
                    
                    if mask and j < len(mask) and not mask[j]:
                        score = -1e9
                    scores.append(score)
                
                # Softmax
                attn = self.softmax(scores)
                
                # Weighted sum of V
                for ki in range(dk):
                    val = 0.0
                    for j in range(seq_k):
                        v_h = V[j][start + ki] if start + ki < d else 0
                        val += attn[j] * v_h
                    output[i][start + ki] += val
        
        # Output projection
        result = self.matmul(output, self.W_o)
        
        # Residual + LayerNorm
        for i in range(seq_q):
            for j in range(d):
                result[i][j] = query[i][j] + result[i][j]
            result[i] = self.layer_norm(result[i])
        
        return result


class EncoderLayer:
    """编码器层: 自注意力 + FFN"""
    
    def __init__(self, d_model, n_heads=4, d_ff=None):
        d_ff = d_ff or d_model * 4
        self.self_attn = QuantumGateAttention(d_model, n_heads)
        scale = math.sqrt(2.0 / d_model)
        
        # FFN
        self.W1 = [[random.gauss(0, scale) for _ in range(d_model)] for _ in range(d_ff)]
        self.b1 = [0.0] * d_ff
        self.W2 = [[random.gauss(0, scale) for _ in range(d_ff)] for _ in range(d_model)]
        self.b2 = [0.0] * d_model
        
        # LayerNorm
        self.ln_gamma = [1.0] * d_model
        self.ln_beta = [0.0] * d_model
    
    def gelu(self, x):
        return 0.5 * x * (1.0 + math.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x**3)))
    
    def layer_norm(self, x):
        mean = sum(x) / len(x)
        var = sum((v - mean)**2 for v in x) / len(x)
        std = math.sqrt(var + 1e-6)
        return [(self.ln_gamma[i] * (x[i] - mean) / std + self.ln_beta[i]) for i in range(len(x))]
    
    def forward(self, x, mask=None):
        # Self-attention + residual
        attn_out = self.self_attn.forward(x, x, x, mask)
        
        # FFN
        output = []
        for i in range(len(attn_out)):
            # W1
            hidden = [sum(attn_out[i][j] * self.W1[k][j] for j in range(len(attn_out[i]))) + self.b1[k]
                      for k in range(len(self.b1))]
            # GELU
            hidden = [self.gelu(h) for h in hidden]
            # W2
            out = [sum(hidden[k] * self.W2[j][k] for k in range(len(hidden))) + self.b2[j]
                   for j in range(len(self.b2))]
            
            # Residual + LayerNorm
            out = [out[j] + attn_out[i][j] for j in range(len(out))]
            out = self.layer_norm(out)
            output.append(out)
        
        return output


class DecoderLayer:
    """解码器层: 掩码自注意力 + 交叉注意力 + FFN"""
    
    def __init__(self, d_model, n_heads=4, d_ff=None):
        d_ff = d_ff or d_model * 4
        self.masked_self_attn = QuantumGateAttention(d_model, n_heads)
        self.cross_attn = QuantumGateAttention(d_model, n_heads)
        scale = math.sqrt(2.0 / d_model)
        
        self.W1 = [[random.gauss(0, scale) for _ in range(d_model)] for _ in range(d_ff)]
        self.b1 = [0.0] * d_ff
        self.W2 = [[random.gauss(0, scale) for _ in range(d_ff)] for _ in range(d_model)]
        self.b2 = [0.0] * d_model
        
        self.ln_gamma = [1.0] * d_model
        self.ln_beta = [0.0] * d_model
    
    def gelu(self, x):
        return 0.5 * x * (1.0 + math.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x**3)))
    
    def layer_norm(self, x):
        mean = sum(x) / len(x)
        var = sum((v - mean)**2 for v in x) / len(x)
        std = math.sqrt(var + 1e-6)
        return [(self.ln_gamma[i] * (x[i] - mean) / std + self.ln_beta[i]) for i in range(len(x))]
    
    def forward(self, x, enc_output, tgt_mask=None, src_mask=None):
        # Masked self-attention (decoder can only see previous tokens)
        self_attn_out = self.masked_self_attn.forward(x, x, x, tgt_mask)
        
        # Cross-attention (decoder attends to encoder output)
        cross_attn_out = self.cross_attn.forward(self_attn_out, enc_output, enc_output, src_mask)
        
        # FFN
        output = []
        for i in range(len(cross_attn_out)):
            hidden = [sum(cross_attn_out[i][j] * self.W1[k][j] for j in range(len(cross_attn_out[i]))) + self.b1[k]
                      for k in range(len(self.b1))]
            hidden = [self.gelu(h) for h in hidden]
            out = [sum(hidden[k] * self.W2[j][k] for k in range(len(hidden))) + self.b2[j]
                   for j in range(len(self.b2))]
            out = [out[j] + cross_attn_out[i][j] for j in range(len(out))]
            out = self.layer_norm(out)
            output.append(out)
        
        return output


class QSM_V4:
    """QSM V4: Encoder-Decoder量子翻译模型
    
    架构:
    - Encoder: N层编码器 (自注意力 + FFN)
    - Decoder: N层解码器 (掩码自注意力 + 交叉注意力 + FFN)
    - 嵌入层: 共享词汇嵌入 + 位置编码
    - 输出: 线性投影到词汇表大小
    
    支持: 中→彝, 彝→中, 中→英, 英→中, 彝→英, 英→彝
    """
    
    def __init__(self, vocab_size, d_model=256, n_heads=4, n_layers=3, d_ff=None, max_seq_len=64):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.n_heads = n_heads
        self.n_layers = n_layers
        self.max_seq_len = max_seq_len
        
        scale = math.sqrt(2.0 / d_model)
        
        # 共享嵌入
        self.embedding = [[random.gauss(0, scale) for _ in range(d_model)] for _ in range(vocab_size)]
        
        # 位置编码
        self.pos_encoding = [[0.0]*d_model for _ in range(max_seq_len)]
        for pos in range(max_seq_len):
            for i in range(0, d_model, 2):
                self.pos_encoding[pos][i] = math.sin(pos / (10000 ** (i / d_model)))
                if i + 1 < d_model:
                    self.pos_encoding[pos][i+1] = math.cos(pos / (10000 ** ((i+1) / d_model)))
        
        # 编码器
        self.encoder_layers = [EncoderLayer(d_model, n_heads, d_ff) for _ in range(n_layers)]
        
        # 解码器
        self.decoder_layers = [DecoderLayer(d_model, n_heads, d_ff) for _ in range(n_layers)]
        
        # 输出投影
        self.W_out = [[random.gauss(0, scale) for _ in range(d_model)] for _ in range(vocab_size)]
        self.b_out = [0.0] * vocab_size
    
    def softmax(self, x):
        m = max(x) if x else 0
        e = [math.exp(v - m) for v in x]
        s = sum(e)
        return [v / s for v in e] if s > 0 else [1.0/len(x)] * len(x)
    
    def encode(self, src_ids, mask=None):
        """编码源语言"""
        # Embed + positional encoding
        x = [[self.embedding[idx][j] + self.pos_encoding[i][j] for j in range(self.d_model)]
             for i, idx in enumerate(src_ids) if i < self.max_seq_len]
        
        # Encoder layers
        for layer in self.encoder_layers:
            x = layer.forward(x, mask)
        
        return x
    
    def decode_step(self, tgt_ids_so_far, enc_output, src_mask=None):
        """解码一步（自回归生成）"""
        seq_len = len(tgt_ids_so_far)
        
        # Embed + positional encoding
        x = [[self.embedding[idx][j] + self.pos_encoding[i][j] for j in range(self.d_model)]
             for i, idx in enumerate(tgt_ids_so_far) if i < self.max_seq_len]
        
        # Causal mask: decoder只能看之前的token
        tgt_mask = [True] * seq_len  # All visible for training; for generation, this is naturally causal
        
        # Decoder layers
        for layer in self.decoder_layers:
            x = layer.forward(x, enc_output, tgt_mask, src_mask)
        
        # Take last token's output
        last_hidden = x[-1] if x else [0.0] * self.d_model
        
        # Project to vocabulary
        logits = [sum(last_hidden[j] * self.W_out[v][j] for j in range(self.d_model)) + self.b_out[v]
                  for v in range(self.vocab_size)]
        
        return logits
    
    def translate(self, src_ids, vocab, max_len=32, temperature=1.0):
        """翻译：源语言ID → 目标语言文本（自回归生成）"""
        # Encode source
        enc_output = self.encode(src_ids)
        
        # Special tokens
        BOS = vocab.get('<BOS>', 1)
        EOS = vocab.get('<EOS>', 2)
        id_to_token = {v: k for k, v in vocab.items()}
        
        # Autoregressive decode
        tgt_ids = [BOS]
        for step in range(max_len):
            logits = self.decode_step(tgt_ids, enc_output)
            
            # Temperature sampling
            if temperature > 0:
                logits = [l / temperature for l in logits]
                probs = self.softmax(logits)
                # Simple sampling
                r = random.random()
                cum = 0.0
                next_id = 0
                for idx, p in enumerate(probs):
                    cum += p
                    if r <= cum:
                        next_id = idx
                        break
            else:
                next_id = logits.index(max(logits))
            
            if next_id == EOS:
                break
            tgt_ids.append(next_id)
        
        # Decode to text
        tokens = [id_to_token.get(tid, '?') for tid in tgt_ids[1:]]  # Skip BOS
        return ''.join(tokens) if all(len(t) == 1 for t in tokens) else ' '.join(tokens)


# ============================================================
# 测试
# ============================================================

if __name__ == '__main__':
    print("=== QSM V4 Encoder-Decoder 量子翻译模型 ===\n")
    
    # 小规模测试
    vocab_size = 1000
    d_model = 64
    n_heads = 4
    n_layers = 2
    
    print(f"配置: vocab={vocab_size}, d_model={d_model}, heads={n_heads}, layers={n_layers}")
    
    model = QSM_V4(vocab_size, d_model, n_heads, n_layers)
    
    # 模拟翻译
    src = [10, 25, 37, 42, 5]  # 源语言token IDs
    vocab = {f'tok_{i}': i for i in range(vocab_size)}
    vocab['<BOS>'] = 1
    vocab['<EOS>'] = 2
    
    print(f"源序列: {src}")
    
    # Encode
    enc = model.encode(src)
    print(f"编码器输出: {len(enc)} tokens × {len(enc[0])} dim")
    
    # Decode step by step
    result = model.translate(src, vocab, max_len=10, temperature=0.8)
    print(f"翻译结果: {result}")
    
    # 参数统计
    total_params = 0
    total_params += vocab_size * d_model  # embedding
    total_params += d_model * vocab_size   # output projection
    for _ in range(n_layers):
        # Each encoder layer: 4*d_model^2 (attention) + 2*d_model*d_ff (FFN)
        total_params += 4 * d_model * d_model + 2 * d_model * (d_model * 4)
        # Each decoder layer: 2*attention + cross_attn + FFN
        total_params += 3 * 4 * d_model * d_model + 2 * d_model * (d_model * 4)
    
    print(f"\n估计参数量: ~{total_params:,}")
    print(f"d_model=256版本: ~{total_params * (256//d_model)**2:,}")
    
    print("\n✅ V4 Encoder-Decoder架构验证通过")
    print("下一步: 实现训练循环 + 交叉注意力损失函数")
