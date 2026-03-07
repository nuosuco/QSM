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
        return "".join([self.id_to_char.get(token_id, '') for token_id in token_ids])

    @property
    def vocab_size(self):
        return len(self.char_to_id)

class QsmYiWenChatbot:
    def __init__(self, model_dir):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"QSM Yi Wen Chatbot using device: {self.device}")

        # Load tokenizer
        vocab_path = os.path.join(model_dir, 'qsm_yi_wen_vocab.json')
        self.tokenizer = SimpleTokenizer(vocab_path)
        
        # Model parameters
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
        
        # Load fixed model weights
        model_path = os.path.join(model_dir, 'qsm_yi_wen_generation_model_fixed.pth')
        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            print("✓ 成功加载彝文生成模型")
        except Exception as e:
            print(f"✗ 加载模型失败: {e}")
            print("使用随机初始化")
        
        self.model.eval()
        print(f"词汇表大小: {self.tokenizer.vocab_size}")

    def generate_response(self, prompt, max_len=50, temperature=0.7, top_k=50):
        """生成彝文回复"""
        try:
            # 检测是否包含彝文字符
            yi_chars_in_input = []
            for char in prompt:
                try:
                    if len(char) == 1 and (0xF0000 <= ord(char) <= 0xFFFFF):
                        yi_chars_in_input.append(char)
                except (TypeError, ValueError):
                    continue
            
            # 检测是否请求彝文回复
            yi_wen_keywords = ['彝文', '彝语', 'yi', 'yiwen', '翻译成彝文', '用彝文']
            is_yi_wen_request = any(keyword in prompt.lower() for keyword in yi_wen_keywords)
            
            # 如果输入包含彝文字符，强制使用彝文回复模式
            if yi_chars_in_input:
                print(f"检测到彝文输入: {yi_chars_in_input}")
                is_yi_wen_request = True
            
            if is_yi_wen_request:
                # 彝文生成模式
                input_ids = self.tokenizer.encode(prompt)
                input_tensor = torch.tensor([input_ids], dtype=torch.long).to(self.device)
                
                generated_ids = []
                with torch.no_grad():
                    for _ in range(max_len):
                        outputs = self.model(input_tensor)
                        next_token_logits = outputs[:, -1, :]

                        # Apply temperature
                        if temperature > 0:
                            next_token_logits = next_token_logits / temperature
                        
                        # Apply top-k sampling
                        top_k_logits, top_k_indices = torch.topk(next_token_logits, top_k)
                        probabilities = torch.nn.functional.softmax(top_k_logits, dim=-1)
                        next_token_id_index = torch.multinomial(probabilities, 1).item()
                        next_token_id = top_k_indices[0, next_token_id_index].item()
                        
                        # Stop if we generate a stop token or newline
                        decoded_token = self.tokenizer.decode([next_token_id])
                        if '\n' in decoded_token or len(generated_ids) >= max_len:
                            break
                        
                        generated_ids.append(next_token_id)
                        input_tensor = torch.cat([input_tensor, torch.tensor([[next_token_id]], device=self.device)], dim=1)
                
                response_text = self.tokenizer.decode(generated_ids).strip()
                
                # 检查是否生成了彝文字符
                yi_chars = []
                for char in response_text:
                    try:
                        if len(char) == 1 and (0xF0000 <= ord(char) <= 0xFFFFF):
                            yi_chars.append(char)
                    except (TypeError, ValueError):
                        continue
                
                if yi_chars:
                    if yi_chars_in_input:
                        return f"彝语回复: {response_text}"
                    else:
                        return f"彝文回复: {response_text}"
                else:
                    return f"生成回复: {response_text} (未检测到彝文字符)"
            else:
                # 普通中文回复模式
                return "请使用彝文字符或包含'彝文'、'彝语'、'翻译成彝文'等关键词来请求彝文回复。"
                
        except Exception as e:
            print(f"Error during Yi Wen generation: {e}")
            return "抱歉，彝文生成时遇到了错误。"

# Example usage if you run this file directly
if __name__ == '__main__':
    # Assuming the script is in Models/QSM/src/ and bin is a sibling dir
    qsm_bin_dir = os.path.join(os.path.dirname(__file__), '..', 'bin')
    chatbot = QsmYiWenChatbot(model_dir=qsm_bin_dir)
    
    print("\n--- QSM Yi Wen Chatbot Ready ---")
    print("Enter 'quit' to exit.")
    print("Use keywords like '彝文', '彝语', '翻译成彝文' to get Yi Wen responses.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        response = chatbot.generate_response(user_input)
        print(f"QSM Yi Wen: {response}") 