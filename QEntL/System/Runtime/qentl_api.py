#!/usr/bin/env python3
"""QEntL量子操作系统API服务 (端口8003)
编译和运行QEntL量子程序
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys, os, json, tempfile, traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Compiler'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from qentl_compiler_v3 import compile_qentl
from qbc_vm import QBCVirtualMachine

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "QEntL Quantum OS", "version": "3.0"})

@app.route('/run', methods=['POST'])
def run_code():
    """Compile and run QEntL code"""
    try:
        data = request.get_json(force=True)
        code = data.get('code', '')
        func_name = data.get('func', '主函数')
        max_steps = data.get('max_steps', 5000)
        
        if not code.strip():
            return jsonify({"error": "Empty code"}), 400
        
        # Compile
        result = compile_qentl(code)
        instructions = result.get('instructions', [])
        functions = result.get('functions', {})
        
        # Save to temp file and run
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qbc', delete=False) as f:
            json.dump(result, f)
            path = f.name
        
        try:
            vm = QBCVirtualMachine()
            vm.load_file(path)
            
            if func_name not in functions:
                return jsonify({
                    "error": f"Function '{func_name}' not found",
                    "available_functions": list(functions.keys())
                }), 400
            
            output = vm.run_with_function(func_name, max_steps=max_steps)
            
            return jsonify({
                "output": output,
                "functions": functions,
                "instruction_count": len(instructions),
                "variables": {k: v for k, v in vm.variables.items() if v is not None and not k.startswith('_')},
                "success": True
            })
        finally:
            os.unlink(path)
            
    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "success": False
        }), 500

@app.route('/compile', methods=['POST'])
def compile_code():
    """Compile QEntL code to QBC (without running)"""
    try:
        data = request.get_json(force=True)
        code = data.get('code', '')
        
        if not code.strip():
            return jsonify({"error": "Empty code"}), 400
        
        result = compile_qentl(code)
        
        return jsonify({
            "functions": result.get('functions', {}),
            "function_params": result.get('function_params', {}),
            "instruction_count": len(result.get('instructions', [])),
            "constants": result.get('constants', []),
            "success": True
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc(),
            "success": False
        }), 500

@app.route('/examples', methods=['GET'])
def examples():
    """Return example QEntL programs"""
    return jsonify({
        "hello": '主函数: 函数() { 打印("你好量子世界!") }',
        "fibonacci": '''斐波那契: 函数(n) {
    如果 n <= 1 { 返回 n }
    返回 斐波那契(n-1) + 斐波那契(n-2)
}
主函数: 函数() { 打印(斐波那契(10)) }''',
        "calculator": '''quantum_enum 运算 { 加, 减, 乘, 除 }
计算: 函数(a, b, op) {
    如果 op == 运算.加 { 返回 a + b }
    否则如果 op == 运算.减 { 返回 a - b }
    否则如果 op == 运算.乘 { 返回 a * b }
    否则如果 op == 运算.除 { 返回 a / b }
    返回 0
}
主函数: 函数() { 打印(计算(10, 3, 运算.乘)) }''',
        "sort": '''主函数: 函数() {
    让 arr = [5, 3, 8, 1, 9, 2, 7]
    打印(排序(arr))
}''',
        "grades": '''quantum_class 成绩单 {
    名称: 字符串; 分数: 整数
    等级: 函数(self) {
        返回 self.分数 >= 90 ? "A" : self.分数 >= 60 ? "B" : "F"
    }
    信息: 函数(self) {
        返回 格式("{}: {}分({})", self.名称, self.分数, self.等级())
    }
}
主函数: 函数() {
    让 s1 = 成绩单(); s1.名称 = "张三"; s1.分数 = 95
    让 s2 = 成绩单(); s2.名称 = "李四"; s2.分数 = 58
    打印(s1.信息()); 打印(s2.信息())
}''',
        "fileio": '''主函数: 函数() {
    写入文件("/tmp/qentl.txt", "Hello QEntL OS!")
    让 content = 读取文件("/tmp/qentl.txt")
    打印(格式("读取: {}", content))
    打印(格式("存在: {}", 文件存在("/tmp/qentl.txt")))
}''',
        "math": '''主函数: 函数() {
    打印(格式("圆面积 = {:.2f", 平方(5) * 3.14159))
    打印(格式("sqrt(144) = {}", 平方根(144)))
    打印(格式("sum = {}", 求和([1,2,3,4,5])))
    打印(格式("product = {}", 求积([2,3,4])))
}''',
        "elif5": '''分类: 函数(score) {
    如果 score >= 90 { 返回 "优秀" }
    否则如果 score >= 80 { 返回 "良好" }
    否则如果 score >= 70 { 返回 "中等" }
    否则如果 score >= 60 { 返回 "及格" }
    否则 { 返回 "不及格" }
}
主函数: 函数() {
    打印(分类(95)); 打印(分类(45))
}''',
    })



@app.route('/stats', methods=['GET'])
def stats():
    """QEntL system statistics"""
    import sys
    return jsonify({
        'status': 'healthy',
        'version': '3.0',
        'builtin_functions': 62,
        'opcodes': 56,
        'test_coverage': '85/85',
        'features': [
            'quantum_class', 'functions', 'recursion',
            'for/while/foreach', 'if/elif/else', 
            'try/catch/throw', 'match/case',
            'file_io', 'system_calls', 'math_builtins',
            'string_utilities', 'format_specs',
            'beam_search', 'ngram_blocking',
            'stdlib', 'run_qbc'
        ],
        'python_version': sys.version.split()[0],
    })

if __name__ == '__main__':
    print("QEntL量子操作系统API启动 → 端口8003")
    app.run(host='0.0.0.0', port=8003, debug=False)
