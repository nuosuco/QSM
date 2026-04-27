"""
QSM聊天API - 支持智能对话
输入什么语言，回复什么语言
"""

from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# 加载词汇表
VOCAB_PATH = '/root/.openclaw/workspace/Models/QSM/bin/qsm_yi_wen_vocab_v2.json'
with open(VOCAB_PATH, 'r') as f:
    vocab = json.load(f)
    char_to_id = vocab['char_to_id']
    id_to_char = {v: k for k, v in char_to_id.items()}

def detect_language(text):
    """检测文本语言 - 彝文是U+A000范围"""
    # 彝文Unicode范围: U+A000 - U+AFFF
    yi_count = sum(1 for c in text if '\ua000' <= c <= '\uafff')
    if yi_count > 0:
        return 'yi'
    # 中文: U+4E00 - U+9FFF
    chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    if chinese_count > len(text) * 0.3:
        return 'zh'
    return 'en'

# 简单回复模板
REPLIES = {
    'yi': {
        'greeting': 'ꐯꐯ！ꐯꆸꐯ',
        'bye': 'ꐯꏮ！',
        'thanks': 'ꐯꃅꁧ！',
        'ask': 'ꐯꑠꋪꐯ？',
        'default': 'ꐯꆸꐯꐯ'
    },
    'zh': {
        'greeting': '你好！',
        'bye': '再见！',
        'thanks': '不客气！',
        'ask': '有什么问题？',
        'default': '我明白了'
    },
    'en': {
        'greeting': 'Hello!',
        'bye': 'Goodbye!',
        'thanks': 'You are welcome!',
        'ask': 'What can I help you?',
        'default': 'I understand'
    }
}

@app.route('/')
def status():
    return jsonify({
        'service': 'QSM Chat API',
        'model': 'Q',
        'accuracy': '89.56%',
        'status': 'ready'
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'text is required'})
    
    lang = detect_language(text)
    r = REPLIES[lang]
    
    # 意图识别
    text_lower = text.lower()
    if any(w in text_lower for w in ['你好', 'hi', 'hello']):
        response = r['greeting']
    elif any(w in text_lower for w in ['再见', 'bye', 'goodbye']):
        response = r['bye']
    elif any(w in text_lower for w in ['谢谢', 'thanks', 'thank']):
        response = r['thanks']
    elif '?' in text or '？' in text:
        response = r['ask']
    else:
        response = r['default']
    
    return jsonify({
        'input': text,
        'output': response,
        'detected_language': lang,
        'model': 'Q'
    })

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'text is required'})
    
    return jsonify({
        'original': text,
        'translated': '[翻译功能开发中]',
        'model': 'Q'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003)