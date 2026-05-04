
import torch
import torch.nn as nn

class CachedTransformerDecoderLayer(nn.Module):
    """Transformer decoder layer with KV cache support"""
    def __init__(self, d_model, nhead, d_ff, dropout=0.1):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout, batch_first=True)
        self.cross_attn = nn.MultiheadAttention(d_model, nhead, dropout=dropout, batch_first=True)
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
        self.activation = nn.ReLU()
    
    def forward(self, tgt, memory, tgt_mask=None, cache=None):
        # Self-attention with KV cache
        if cache is not None:
            cached_k, cached_v = cache
            full_tgt = torch.cat([cached_k, tgt], dim=1)
        else:
            full_tgt = tgt
        
        q = self.norm1(tgt)
        k = full_tgt
        v = full_tgt
        
        attn_out, _ = self.self_attn(q, k, v, attn_mask=tgt_mask)
        tgt = tgt + self.dropout(attn_out)
        
        # Cross-attention (no cache needed, memory is fixed)
        q2 = self.norm2(tgt)
        cross_out, _ = self.cross_attn(q2, memory, memory)
        tgt = tgt + self.dropout(cross_out)
        
        # FFN
        ff_out = self.linear2(self.dropout(self.activation(self.linear1(self.norm3(tgt)))))
        tgt = tgt + self.dropout(ff_out)
        
        new_cache = (full_tgt, full_tgt)  # Cache for next step
        return tgt, new_cache


class CachedQSMDecoder(nn.Module):
    """QSM Decoder with KV Cache for incremental decoding"""
    def __init__(self, d_model, nhead, d_ff, num_layers, dropout=0.1):
        super().__init__()
        self.layers = nn.ModuleList([
            CachedTransformerDecoderLayer(d_model, nhead, d_ff, dropout)
            for _ in range(num_layers)
        ])
    
    def forward(self, tgt, memory, tgt_mask=None, caches=None):
        new_caches = []
        for i, layer in enumerate(self.layers):
            cache = caches[i] if caches else None
            tgt, new_cache = layer(tgt, memory, tgt_mask, cache)
            new_caches.append(new_cache)
        return tgt, new_caches
