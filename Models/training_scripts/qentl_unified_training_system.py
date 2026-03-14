import os
import sys
import json
import time
import glob
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import struct
import re
from tqdm import tqdm
import argparse

# Add the project root to the Python path to allow for imports from 'Models/shared'
# This assumes the script is in Models/training_scripts/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

from Models.shared.quantum_network import QuantumTransformerModel

# Define paths relative to the project root
MODELS_DIR = os.path.join(PROJECT_ROOT, "Models")
QENTL_DIR = os.path.join(PROJECT_ROOT, "QEntL")
STATUS_FILE_PATH = os.path.join(MODELS_DIR, 'training_status.json')

# --- Model Definitions ---
MODEL_DEFS = {
    "QSM": {"desc": "Quantum Superposition Model", "config": os.path.join(MODELS_DIR, "QSM", "src", "qsm_neural_network.qentl")},
    "SOM": {"desc": "Social Organization Model", "config": os.path.join(MODELS_DIR, "SOM", "src", "som_neural_network.qentl")},
    "WeQ": {"desc": "World Emotion Model", "config": os.path.join(MODELS_DIR, "WeQ", "src", "weq_neural_network.qentl")},
    "Ref": {"desc": "Reflection Model", "config": os.path.join(MODELS_DIR, "Ref", "src", "ref_neural_network.qentl")},
    "QEntL": {"desc": "Quantum Entanglement Language Model", "config": os.path.join(MODELS_DIR, "QEntL", "src", "qentl_neural_network.qentl")},
}

# --- Status Update Function ---
def update_status(model_name, status, progress=0, details=""):
    """Updates a centralized JSON file with the training status of all models."""
    try:
        all_statuses = {}
        if os.path.exists(STATUS_FILE_PATH):
            with open(STATUS_FILE_PATH, 'r', encoding='utf-8') as f:
                all_statuses = json.load(f)

        if model_name not in all_statuses:
            all_statuses[model_name] = {}

        all_statuses[model_name]['status'] = status
        all_statuses[model_name]['progress'] = progress
        all_statuses[model_name]['details'] = details
        all_statuses[model_name]['timestamp'] = time.strftime("%Y-%m-%d %H:%M:%S")

        with open(STATUS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_statuses, f, ensure_ascii=False, indent=4)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error updating status file: {e}")


# --- Tokenizer and Dataset ---
class SimpleTokenizer:
    """A simple character-level tokenizer that can be extended."""
    def __init__(self, texts=None, vocab_path=None):
        self.pad_token = '<pad>'
        self.unk_token = '‪'
        
        if vocab_path and os.path.exists(vocab_path):
            print(f"Loading existing vocabulary from {vocab_path}")
            with open(vocab_path, 'r', encoding='utf-8') as f:
                self.char_to_id = json.load(f).get('char_to_id', {})
        else:
            self.char_to_id = {self.pad_token: 0, self.unk_token: 1}

        if texts:
            self.add_texts(texts)
            
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}
        self.pad_token_id = self.char_to_id[self.pad_token]

    def add_texts(self, texts):
        """Adds new characters from texts to the vocabulary."""
        new_chars = sorted(list(set("".join(texts))))
        for char in new_chars:
            if char not in self.char_to_id:
                self.char_to_id[char] = len(self.char_to_id)
        # Rebuild id_to_char map after additions
        self.id_to_char = {i: ch for ch, i in self.char_to_id.items()}

    @property
    def vocab_size(self):
        return len(self.char_to_id)

    def encode(self, text):
        return [self.char_to_id.get(char, self.char_to_id[self.unk_token]) for char in text]

    def save_vocab(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({'char_to_id': self.char_to_id}, f, ensure_ascii=False, indent=2)


class QentlDataset(Dataset):
    def __init__(self, tokens, seq_length):
        self.seq_length = seq_length
        # Create sequences of tokens for input and target
        self.examples = []
        for i in range(0, len(tokens) - seq_length -1):
             self.examples.append(tokens[i:i + seq_length + 1])

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        chunk = self.examples[idx]
        # Input is the sequence, target is the sequence shifted by one
        return torch.tensor(chunk[:-1], dtype=torch.long), torch.tensor(chunk[1:], dtype=torch.long)


# --- Helper Functions ---
def get_all_qentl_content(base_dir):
    """Gathers all content from .qentl files."""
    print(f"Searching for .qentl files in: {base_dir}")
    content = ""
    qentl_files = glob.glob(os.path.join(base_dir, '**', '*.qentl'), recursive=True)
    print(f"Found {len(qentl_files)} .qentl files.")
    for file_path in qentl_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content += f.read() + "\n"
        except Exception as e:
            print(f"Could not read {file_path}: {e}")
    return content

def get_all_yi_wen_content(base_dir):
    """Gathers all content from Yi Wen .jsonl files, parsing the specific message format."""
    print(f"Searching for .jsonl files in: {base_dir}")
    content = ""
    jsonl_files = glob.glob(os.path.join(base_dir, '**', '*.jsonl'), recursive=True)
    print(f"Found {len(jsonl_files)} .jsonl files.")

    for file_path in jsonl_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                        if "messages" in data and isinstance(data["messages"], list):
                            line_content = []
                            for msg in data["messages"]:
                                if "content" in msg and isinstance(msg["content"], str):
                                    line_content.append(msg["content"])
                            if line_content:
                                content += " ".join(line_content) + "\\n"
                                
                    except json.JSONDecodeError:
                        print(f"Warning: Skipping malformed JSON on line {line_num} in {file_path}")
        except Exception as e:
            print(f"Could not read {file_path}: {e}")
    print(f"Extracted {len(content.splitlines())} lines of Yi Wen content.")
    return content

def get_specific_yi_wen_file_content(file_path):
    """Gathers content only from a specific Yi Wen .jsonl file."""
    if not os.path.exists(file_path):
        print(f"Error: Specified data file does not exist: {file_path}")
        return ""
        
    print(f"Loading specific data file: {file_path}")
    content = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    if "messages" in data and isinstance(data["messages"], list):
                        line_content = [msg.get("content", "") for msg in data["messages"] if isinstance(msg.get("content"), str)]
                        if line_content:
                            content += " ".join(line_content) + "\\n"
                except json.JSONDecodeError:
                    print(f"Warning: Skipping malformed JSON on line {line_num} in {file_path}")
    except Exception as e:
        print(f"Could not read {file_path}: {e}")
    print(f"Extracted {len(content.splitlines())} lines from the specific file.")
    return content

def get_model_config_from_qentl(qentl_file_path):
    """Parses a .qentl file to extract neural network configuration."""
    config = {'d_model': 256, 'nhead': 4, 'num_encoder_layers': 3, 'dim_feedforward': 1024, 'max_seq_length': 256}
    try:
        with open(qentl_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            for key in config:
                match = re.search(fr'{key}:\s*(\d+)', content)
                if match:
                    config[key] = int(match.group(1))
    except FileNotFoundError:
        print(f"Warning: Config file not found: {qentl_file_path}. Using defaults.")
    except Exception as e:
        print(f"Warning: Error parsing {qentl_file_path}: {e}. Using defaults.")
    return config

def generate_qbc_file(model_name, vocab, file_path):
    """Generates a Quantum Binary Code (.qbc) file from the vocabulary."""
    magic, version, num_instructions = b'QBC', 1, len(vocab.char_to_id)
    header = struct.pack('>3sBI', magic, version, num_instructions)
    with open(file_path, 'wb') as f:
        f.write(header)
        for char_id in vocab.char_to_id.values():
            opcode, target_id = 0x01, list(MODEL_DEFS.keys()).index(model_name)
            quantum_state = float(char_id / num_instructions)
            instruction = struct.pack('>BBfI', opcode, target_id, quantum_state, char_id)
            f.write(instruction)

# --- Main Training Function ---
def train_and_save_model(model_name, texts, tokenizer):
    """Trains a single model instance, loading existing weights for fine-tuning."""
    update_status(model_name, "Starting", 0, "Initializing training...")
    
    output_model_dir = os.path.join(MODELS_DIR, model_name, "bin")
    os.makedirs(output_model_dir, exist_ok=True)
    
    existing_model_path = os.path.join(output_model_dir, f"{model_name.lower()}_model.pth")

    # 1. Get model configuration
    model_config_path = MODEL_DEFS[model_name]['config']
    model_config = get_model_config_from_qentl(model_config_path)
    update_status(model_name, "Config Parsed", 5, f"d_model: {model_config['d_model']}, nhead: {model_config['nhead']}")

    # 2. Setup Device, Model, Optimizer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n--- Training {model_name} on {device} ---")
    
    model = QuantumTransformerModel(
        vocab_size=tokenizer.vocab_size,
        d_model=model_config['d_model'],
        nhead=model_config['nhead'],
        num_encoder_layers=model_config['num_encoder_layers'],
        dim_feedforward=model_config['dim_feedforward'],
        max_seq_length=model_config['max_seq_length']
    ).to(device)

    if os.path.exists(existing_model_path):
        print(f"Found existing model at {existing_model_path}. Loading weights for fine-tuning.")
        # Resize embedding layer if vocab size has changed
        original_vocab_size = model.embedding.num_embeddings
        if original_vocab_size != tokenizer.vocab_size:
            print(f"Vocabulary size changed from {original_vocab_size} to {tokenizer.vocab_size}. Resizing embedding layer.")
            model.resize_embedding_layer(tokenizer.vocab_size)

        model.load_state_dict(torch.load(existing_model_path, map_location=device), strict=False)
        print("Model weights loaded successfully.")
    else:
        print("No existing model found. Training from scratch.")

    # Use a smaller learning rate for fine-tuning
    lr = 1e-5 if os.path.exists(existing_model_path) else 1e-3
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
    update_status(model_name, "Model Created", 10)

    # 3. Create Dataset
    encoded_text = tokenizer.encode("".join(texts))
    dataset = QentlDataset(encoded_text, model_config['max_seq_length'])
    if len(dataset) == 0:
        print(f"ERROR: Not enough data to train {model_name}. Need at least {model_config['max_seq_length']+1} characters. Skipping.")
        update_status(model_name, "Error", 10, "Not enough text data to form a single batch.")
        return
        
    dataloader = DataLoader(dataset, batch_size=8, shuffle=True)
    
    # 4. Training Loop
    model.train()
    epochs = 3
    for epoch in range(epochs):
        progress_base = 10 + (epoch / epochs) * 80
        pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs} for {model_name}")
        for i, (inputs, targets) in enumerate(pbar):
            inputs, targets = inputs.to(device), targets.to(device)
            
            optimizer.zero_grad()
            output = model(inputs)
            loss = criterion(output.view(-1, tokenizer.vocab_size), targets.view(-1))
            loss.backward()
            optimizer.step()

            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
            if i % 5 == 0: # Update status less frequently
                progress = progress_base + ((i+1) / len(dataloader)) * (80 / epochs)
                update_status(model_name, "Training", int(progress), f"Epoch {epoch+1}, Loss: {loss.item():.4f}")

    update_status(model_name, "Training Complete", 95, "Saving artifacts...")

    # 5. Save Artifacts
    tokenizer.save_vocab(os.path.join(output_model_dir, "vocab.json"))
    generate_qbc_file(model_name, tokenizer, os.path.join(output_model_dir, f"{model_name.lower()}_instructions.qbc"))
    torch.save(model.state_dict(), os.path.join(output_model_dir, f"{model_name.lower()}_model.pth"))
    torch.save(model, os.path.join(output_model_dir, f"{model_name.lower()}_model.ckpt"))
    
    print(f"Artifacts for {model_name} saved successfully.")
    update_status(model_name, "Completed", 100, "Artifacts saved.")


# --- Main Orchestration ---
def main():
    """Main function to run the unified training pipeline."""
    parser = argparse.ArgumentParser(description="QEntL Unified Training System")
    parser.add_argument("--model", type=str, required=True, help="Train a specific model (e.g., QSM).")
    parser.add_argument("--data_file", type=str, help="Path to a specific data file to use for training.")
    parser.add_argument("--data_type", type=str, choices=['qentl', 'yi_wen', 'all'], help="Specify a general data type to use for training.")
    args = parser.parse_args()

    if not args.data_file and not args.data_type:
        print("Error: You must specify either --data_file or --data_type.")
        return

    models_to_train = [args.model]

    # Initialize status file
    with open(STATUS_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump({name: {"status": "Pending", "progress": 0, "details": "Waiting to start..."} for name in models_to_train}, f)
        
    training_texts = ""
    if args.data_file:
        # Prioritize specific file if provided
        training_texts = get_specific_yi_wen_file_content(args.data_file)
    elif args.data_type == 'qentl':
        print("Loading only .qentl training data...")
        training_texts = get_all_qentl_content(QENTL_DIR)
    elif args.data_type == 'yi_wen':
        print("Loading all Yi Wen training data...")
        training_texts = get_all_yi_wen_content(os.path.join(MODELS_DIR, "training_data", "datasets", "yi_wen"))
    else: # 'all'
        print("Loading all .qentl training data...")
        all_qentl_texts = get_all_qentl_content(QENTL_DIR)
        print("Loading all Yi Wen training data...")
        yi_wen_texts = get_all_yi_wen_content(os.path.join(MODELS_DIR, "training_data", "datasets", "yi_wen"))
        training_texts = all_qentl_texts + "\n" + yi_wen_texts

    if not training_texts.strip():
        print("No training data found for the specified source. Exiting.")
        return

    # Load existing tokenizer or create a new one, then add new texts
    vocab_path = os.path.join(MODELS_DIR, args.model, "bin", "vocab.json")
    tokenizer = SimpleTokenizer(texts=training_texts.splitlines(), vocab_path=vocab_path)
    
    for model_name in models_to_train:
        if model_name not in MODEL_DEFS:
            print(f"Error: Model '{model_name}' is not defined. Skipping.")
            continue
        # We pass the same data and tokenizer to each model being trained
        train_and_save_model(model_name, training_texts.splitlines(), tokenizer)

    print("\n\nUnified training process finished for all models.")


if __name__ == '__main__':
    main()
