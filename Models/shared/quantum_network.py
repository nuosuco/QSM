import torch
import torch.nn as nn
import math
from typing import Optional

class PositionalEncoding(nn.Module):
    """
    Injects some information about the relative or absolute position of the tokens in the sequence.
    The positional encodings have the same dimension as the embeddings, so that the two can be summed.
    """
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor, shape [seq_len, batch_size, embedding_dim]
        """
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)

class QuantumTransformerModel(nn.Module):
    """
    A Transformer-based model for our Quantum OS.
    This architecture is inspired by the specifications found in the project's .qentl files.
    """
    def __init__(self, 
                 vocab_size: int, 
                 d_model: int = 4096, 
                 nhead: int = 32, 
                 num_encoder_layers: int = 24, 
                 dim_feedforward: int = 4096, 
                 dropout: float = 0.1,
                 max_seq_length: int = 8192):
        super().__init__()
        self.model_type = 'Transformer'
        self.d_model = d_model
        
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout, max_len=max_seq_length)
        
        encoder_layers = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layers, num_encoder_layers)
        
        self.decoder = nn.Linear(d_model, vocab_size)

        self.init_weights()

    def init_weights(self) -> None:
        initrange = 0.1
        self.embedding.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    def forward(self, src: torch.Tensor, src_mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Args:
            src: Tensor, shape [batch_size, seq_len]
            src_mask: Tensor, shape [seq_len, seq_len]

        Returns:
            output Tensor of shape [batch_size, seq_len, vocab_size]
        """
        # Embedding and positional encoding expect [seq_len, batch_size, d_model]
        # but TransformerEncoderLayer with batch_first=True expects [batch_size, seq_len, d_model]
        # We handle this by transposing
        
        src = self.embedding(src) * math.sqrt(self.d_model)
        
        # PyTorch Transformer layers expect [seq_len, batch, features] if batch_first=False (default)
        # or [batch, seq_len, features] if batch_first=True.
        # Our PositionalEncoding is [seq_len, batch, features]. Let's adapt.
        src = src.transpose(0, 1) # [seq_len, batch_size, d_model]
        src = self.pos_encoder(src)
        src = src.transpose(0, 1) # [batch_size, seq_len, d_model] for the encoder

        output = self.transformer_encoder(src, src_mask)
        output = self.decoder(output)
        return output

    def resize_embedding_layer(self, new_num_tokens: int):
        """
        Resizes the token embedding layer to accommodate a new vocabulary size.
        """
        old_embedding = self.embedding
        new_embedding = nn.Embedding(new_num_tokens, self.d_model)
        new_embedding.to(old_embedding.weight.device)

        # Copy weights from the old embedding to the new one
        num_tokens_to_copy = min(old_embedding.num_embeddings, new_num_tokens)
        new_embedding.weight.data[:num_tokens_to_copy, :] = old_embedding.weight.data[:num_tokens_to_copy, :]
        
        # Replace the old embedding layer
        self.embedding = new_embedding 