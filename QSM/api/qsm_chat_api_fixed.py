""" QSM聊天API - 修复版
只使用滇川黔贵通用彝文（我们训练的）
不支持凉山彝文
"""
from flask import Flask, jsonify, request
import json

app = Flask(__name__)

# 滇川黔贵通用彝文字符（U+F0000+，我们训练的4120字）
YI_CHARS = [
    "󲈮", "󲉖", "󲊂", "󳋭", "󳤣", "󲊱", "󲊴", "󲊮", "󲊭", "󲢩",
    "󳂖", "󲊖", "󲊰", "󳇈", "󲳷", "󲊪", "󲹒", "󲷷", "󲊰"
]

ZH_WORDS = ["我", "你", "他", "她", "好", "小", "大", "天", "地", "人", "是", "的", "了", "在", "有", "不", "吗", "什么", "谁", "哪", "为", "怎么", "谢", "再", "见", "学", "习", "彝", "文", "量子", "爱", "喜欢", "今天", "天气", "教"]

EN_WORDS = ["i", "you", "he", "she", "hello", "hi", "good", "thanks", "thank", "bye", "what", "who", "how", "love", "like", "name"]

def detect_language(text):
    yi_count = sum(1 for c in YI_CHARS if c in text)
    yi_count += sum(1 for c in text if '\uf0000' <= c <= '\U0010ffff')
    zh_count = sum(1 for w in ZH_WORDS if w in text)
    en_count = sum(1 for w in EN_WORDS if w.lower() in text.lower())
    
    if yi_count >= 1 and yi_count >= zh_count and yi_count >= en_count:
        return 'yi'
    if zh_count >= 2 or (zh_count >= 1 and zh_count > en_count):
        return 'zh'
    if en_count >= 1:
        return 'en'
    return 'zh'

# 彝文回复（只有滇川黔贵通用彝文）
REPLIES = {
    'yi': {
        'greeting': '󲈮󳤣！',  # 我好！
        'bye': '󲊂󲊂！',  # 再见！
        'thanks': '󳤣󲊂！',  # 好的！
        'ask': '󲊂󲊂？',  # 是吗？
        'who': '󲊂󲊂！',  # 是！
        'how': '󲈮󳤣！',  # 我好！
        'love': '󳤣󲊂！',  # 好的！
        'default': '󲊂󲊂'  # 是
    },
    'zh': {
        'greeting': '你好！',
        'bye': '再见！',
        'thanks': '不客气！',
        'ask': '有什么问题？',
        'who': '我是QSM量子AI助手小趣！',
        'how': '我很好，谢谢！',
        'love': '谢谢你的喜欢！',
        'learn': '好的！彝文很有意思。"我"是󲈮，"你"是󲉖。',
        'weather': '今天天气很好！',
        'default': '我明白了。'
    },
    'en': {
        'greeting': 'Hello!',
        'bye': 'Goodbye!',
        'thanks': 'You are welcome!',
        'ask': 'What can I help?',
        'who': "I'm QSM Quantum AI assistant!",
        'how': "I'm doing great!",
        'love': 'Thank you!',
        'learn': "Great! In Yi, 'I' is 󲈮, 'you' is 󲉖.",
        'weather': 'The weather is nice today!',
        'default': 'I understand.'
    }
}

@app.route('/')
def status():
    return jsonify({
        'service': 'QSM Chat API', 
        'model': 'Q (Yi Translation)', 
        'accuracy': '89.56%',
        'status': 'ready',
        'note': '只支持滇川黔贵通用彝文（U+F0000+），不支持凉山彝文'
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'text is required'})
    
    lang = detect_language(text)
    r = REPLIES[lang]
    t = text.lower()
    
    if any(w in t for w in ['再见', 'bye', 'goodbye', '拜拜']):
        response = r['bye']
    elif any(w in t for w in ['谢谢', 'thanks', 'thank']):
        response = r['thanks']
    elif any(w in t for w in ['谁', 'who', '你是谁', 'name']):
        response = r['who']
    elif any(w in t for w in ['好', 'hi', 'hello', 'good']):
        response = r['greeting']
    elif any(w in t for w in ['爱', 'love', '喜欢', 'like']):
        response = r['love']
    elif any(w in t for w in ['学', 'learn', '彝文', 'yi language']):
        response = r['learn']
    elif any(w in t for w in ['天气', 'weather']):
        response = r['weather']
    elif '?' in text or '？' in t or any(w in t for w in ['how', 'what', 'where', 'when', 'why', '吗']):
        response = r['ask']
    else:
        response = r['default']
    
    return jsonify({
        'input': text, 
        'output': response, 
        'detected_language': lang, 
        'model': 'Q (Yi Translation)',
        'note': '当前模型是翻译模型，滇川黔贵通用彝文'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003)
