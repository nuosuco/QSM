import os
import json
from flask import Flask, jsonify, request, send_from_directory
import sys

# Add project root to path to allow imports from other directories
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

# Import the new Yi Wen service
from Models.QSM.src.qsm_yi_wen_service import QsmYiWenChatbot

# --- Flask Web Server ---
app = Flask(__name__, template_folder='templates')

# --- Configuration ---
# Correctly locate the status file relative to the project root
RESULTS_DIR = os.path.join(PROJECT_ROOT, 'Models', 'training_data', 'results')
QSM_MODEL_DIR = os.path.join(PROJECT_ROOT, 'Models', 'QSM', 'bin')
MODELS = ["QSM", "Ref", "SOM", "WeQ", "QEntL"]

# --- Initialize Chatbot ---
# Global variable to hold the chatbot instance
qsm_chatbot = None
try:
    # Check if the Yi Wen model has been trained before trying to load it
    qsm_model_path = os.path.join(QSM_MODEL_DIR, 'qsm_yi_wen_generation_model_fixed.pth')
    if not os.path.exists(qsm_model_path):
        print("QSM Yi Wen model not found. Chat functionality will be disabled.")
    else:
        print("QSM Yi Wen model found. Chatbot will be loaded on the first chat request.")
except Exception as e:
    print(f"Error during initial QSM Yi Wen model check: {e}")
    qsm_chatbot = None


# --- Web Routes ---
@app.route('/')
def serve_index():
    return send_from_directory('templates', 'training_monitor.html')

@app.route('/font-test')
def serve_font_test():
    return send_from_directory('templates', 'font_test.html')

@app.route('/simple-font-test')
def serve_simple_font_test():
    return send_from_directory('templates', 'simple_font_test.html')

@app.route('/fallback-test')
def serve_fallback_test():
    return send_from_directory('templates', 'fallback_test.html')

@app.route('/image-test')
def serve_image_test():
    return send_from_directory('templates', 'image_test.html')

@app.route('/yi-chat')
def serve_yi_chat():
    return send_from_directory('templates', 'yi_wen_chat.html')

@app.route('/simple-test')
def serve_simple_test():
    return send_from_directory('templates', 'simple_yi_test.html')

@app.route('/debug-yi')
def serve_debug_yi():
    return send_from_directory('templates', 'debug_yi.html')

@app.route('/yi-font-fix')
def serve_yi_font_fix():
    return send_from_directory('templates', 'yi_font_fix.html')

@app.route('/yi-image-renderer')
def serve_yi_image_renderer():
    return send_from_directory('templates', 'yi_image_renderer.html')

@app.route('/yi-font-display')
def serve_yi_font_display():
    return send_from_directory('templates', 'yi_font_display.html')

@app.route('/yi-browser-fix')
def serve_yi_browser_fix():
    return send_from_directory('templates', 'yi_browser_fix.html')

@app.route('/font-debug')
def serve_font_debug():
    return send_from_directory('templates', 'font_debug.html')

@app.route('/yi-advanced-font')
def serve_yi_advanced_font():
    return send_from_directory('templates', 'yi_advanced_font.html')

@app.route('/yi-browser-fix-simple')
def serve_yi_browser_fix_simple():
    return send_from_directory('templates', 'yi_browser_fix_simple.html')

@app.route('/yi-real-chars')
def serve_yi_real_chars():
    return send_from_directory('templates', 'yi_real_chars.html')

@app.route('/yi-force-display')
def serve_yi_force_display():
    return send_from_directory('templates', 'yi_force_display.html')

@app.route('/yi-canvas-only')
def serve_yi_canvas_only():
    return send_from_directory('templates', 'yi_canvas_only.html')

@app.route('/simple-yi-test')
def serve_simple_yi_test():
    return send_from_directory('templates', 'simple_yi_test.html')

@app.route('/yi-font-web')
def serve_yi_font_web():
    return send_from_directory('templates', 'yi_font_web.html')

@app.route('/yi-simple-fix')
def serve_yi_simple_fix():
    return send_from_directory('templates', 'yi_simple_fix.html')

@app.route('/yi-diagnostic-solution')
def serve_yi_diagnostic_solution():
    return send_from_directory('templates', 'yi_diagnostic_solution.html')

@app.route('/yi-training-chars')
def serve_yi_training_chars():
    return send_from_directory('templates', 'yi_training_chars.html')

@app.route('/yi-ultimate-solution')
def serve_yi_ultimate_solution():
    return send_from_directory('templates', 'yi_ultimate_solution.html')

@app.route('/yi-private-only')
def serve_yi_private_only():
    return send_from_directory('templates', 'yi_private_only.html')

@app.route('/yi-font-test')
def serve_yi_font_test():
    return send_from_directory('templates', 'yi_font_test.html')

@app.route('/yi-inline-font')
def serve_yi_inline_font():
    return send_from_directory('templates', 'yi_inline_font.html')

@app.route('/yi-dialog-test')
def serve_yi_dialog_test():
    return send_from_directory('templates', 'yi_dialog_test.html')

@app.route('/yi-deep-diagnostic')
def serve_yi_deep_diagnostic():
    return send_from_directory('templates', 'yi_deep_diagnostic.html')

@app.route('/yi-canvas-solution')
def serve_yi_canvas_solution():
    return send_from_directory('templates', 'yi_canvas_solution.html')

@app.route('/yi-image-display')
def serve_yi_image_display():
    return send_from_directory('templates', 'yi_image_display.html')

@app.route('/yi_pua_png/<path:filename>')
def serve_yi_png(filename):
    return send_from_directory('yi_pua_png', filename)

@app.route('/fonts/<path:filename>')
def serve_font(filename):
    return send_from_directory('fonts', filename)

@app.route('/status')
def get_status():
    all_statuses = {}
    for model_name in MODELS:
        status_file = os.path.join(RESULTS_DIR, f"{model_name.lower()}_training_status.json")
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = json.load(f)
                    # The frontend JS expects a 'status' field with 'Completed' to show the chat.
                    # The training script writes "训练完成". We'll normalize it here.
                    if status_data.get("status") in ["训练完成", "Completed"]:
                        status_data["status"] = "Completed"
                    all_statuses[model_name] = status_data
            except Exception as e:
                print(f"Error reading status file for {model_name}: {e}")
                all_statuses[model_name] = {"status": "Error", "progress": 0}
        else:
            all_statuses[model_name] = {"status": "Pending", "progress": 0}
    return jsonify(all_statuses)

def get_chatbot():
    """Initializes and returns the chatbot instance, loading it on first call."""
    global qsm_chatbot
    if qsm_chatbot is None:
        try:
            print("First chat request received. Initializing QSM Yi Wen Chatbot...")
            qsm_chatbot = QsmYiWenChatbot(model_dir=QSM_MODEL_DIR)
            print("QSM Yi Wen Chatbot initialized.")
        except Exception as e:
            print(f"Error initializing QSM Yi Wen chatbot: {e}")
            # Return a temporary error-state object to avoid retrying on every request
            return {"error": str(e)}
    return qsm_chatbot

@app.route('/chat/qsm', methods=['POST'])
def chat_with_qsm():
    bot = get_chatbot()
    if isinstance(bot, dict) and "error" in bot:
         return jsonify({"reply": f"QSM Yi Wen model could not be loaded: {bot['error']}"}), 503
    
    if bot is None:
        return jsonify({"reply": "QSM Yi Wen model is not available or failed to load."}), 503

    data = request.json
    if not data:
        return jsonify({"reply": "Invalid request. JSON body required."}), 400
    
    message = data.get('message')

    if not message:
        return jsonify({"reply": "No message provided."}), 400

    try:
        response = bot.generate_response(message)
        return jsonify({"reply": response})
    except Exception as e:
        print(f"Error during chat processing: {e}")
        return jsonify({"reply": "An error occurred while generating a response."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
