import torch
import torch.nn as nn
import json
import os
import math
from typing import Optional

class PositionalEncoding(nn.Module):
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
        x = x + self.pe[:x.size(0)]
        return self.dropout(x)

class QuantumTransformerModel(nn.Module):
    def __init__(self, vocab_size: int, d_model: int, nhead: int, num_encoder_layers: int, dim_feedforward: int, dropout: float = 0.1, max_seq_length: int = 8192):
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
        src = self.embedding(src) * math.sqrt(self.d_model)
        src = src.transpose(0, 1)
        src = self.pos_encoder(src)
        src = src.transpose(0, 1)
        output = self.transformer_encoder(src, src_mask)
        output = self.decoder(output)
        return output

class SimpleTokenizer:
    def __init__(self, vocab_path):
        with open(vocab_path, 'r', encoding='utf-8') as f:
            vocab_data = json.load(f)
            self.char_to_id = vocab_data['char_to_id']
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}
        self.unk_token_id = self.char_to_id.get('‪', 0)

    def encode(self, text):
        return [self.char_to_id.get(char, self.unk_token_id) for char in text]

    def decode(self, token_ids):
        return "".join([self.id_to_char.get(token_id, '�') for token_id in token_ids])

    @property
    def vocab_size(self):
        return len(self.char_to_id)

class QsmChatbot:
    def __init__(self, model_dir):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"QSM Chatbot using device: {self.device}")

        # Load tokenizer
        vocab_path = os.path.join(model_dir, 'vocab.json')
        self.tokenizer = SimpleTokenizer(vocab_path)
        
        # Hardcoded model params based on training script and qentl configs
        # In a real system, these would be saved in a config file.
        model_params = {
            'vocab_size': self.tokenizer.vocab_size,
            'd_model': 256,
            'nhead': 8,
            'num_encoder_layers': 3,
            'dim_feedforward': 1024,
            'max_seq_length': 256
        }

        # Initialize model
        self.model = QuantumTransformerModel(**model_params).to(self.device)
        
        # Load model weights
        model_path = os.path.join(model_dir, 'qsm_model.pth')
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        print("QSM model loaded successfully.")

    def generate_response(self, prompt, max_len=80, temperature=0.75, top_k=50, repetition_penalty=1.3):
        # Frame the prompt to guide the model's response style.
        system_prompt = "这是一个聪明的AI助手正在与用户对话。\\n\\n用户：{user_prompt}\\n助手："
        full_prompt = system_prompt.format(user_prompt=prompt)

        try:
            input_ids = self.tokenizer.encode(full_prompt)
            input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)
            
            # The generated_ids should only contain the response, not the prompt.
            generated_ids = []
            with torch.no_grad():
                # We generate one token more than max_len because the input will be part of the output
                for _ in range(max_len):
                    outputs = self.model(input_tensor)
                    # Get the logits for the last token
                    next_token_logits = outputs[:, -1, :]

                    # Apply temperature
                    if temperature > 0:
                        next_token_logits = next_token_logits / temperature
                    
                    # Apply repetition penalty to the generated part
                    if len(generated_ids) > 0:
                        for token_id in set(generated_ids):
                            next_token_logits[0, token_id] /= repetition_penalty

                    # Apply top-k sampling
                    top_k_logits, top_k_indices = torch.topk(next_token_logits, top_k)
                    probabilities = torch.nn.functional.softmax(top_k_logits, dim=-1)
                    next_token_id_index = torch.multinomial(probabilities, 1).item()
                    next_token_id = top_k_indices[0, next_token_id_index].item()
                    
                    # Stop if we generate a stop token.
                    decoded_token = self.tokenizer.decode([next_token_id])
                    if '</s>' in decoded_token or '<|endoftext|>' in decoded_token:
                        break
                    
                    generated_ids.append(next_token_id)

                    # Append the predicted token to the input for the next iteration
                    input_tensor = torch.cat([input_tensor, torch.tensor([[next_token_id]], device=self.device)], dim=1)
            
            response_text = self.tokenizer.decode(generated_ids).strip()
            # Clean up potential instruction-following artifacts
            if response_text.startswith("助手："):
                response_text = response_text[len("助手："):].strip()
                
            return ''.join(c for c in response_text if c.isprintable() or c in ' \\n\\t')

        except Exception as e:
            print(f"Error during QSM response generation: {e}")
            return "抱歉，我在思考时遇到了一个错误。"

# Example usage if you run this file directly
if __name__ == '__main__':
    # Assuming the script is in Models/QSM/src/ and bin is a sibling dir
    qsm_bin_dir = os.path.join(os.path.dirname(__file__), '..', 'bin')
    chatbot = QsmChatbot(model_dir=qsm_bin_dir)
    
    print("\\n--- QSM Chatbot Ready ---")
    print("Enter 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        response = chatbot.generate_response(user_input)
        print(f"QSM: {response}") 