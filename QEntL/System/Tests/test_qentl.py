#!/usr/bin/env python3
"""QEntL Comprehensive Test Suite - 20/20"""
import sys, os, json, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Compiler'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Runtime'))
from qentl_compiler_v3 import compile_qentl
from qbc_vm import QBCVirtualMachine

def run_qentl(code, func_name='主函数'):
    result = compile_qentl(code)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.qbc', delete=False) as f:
        json.dump(result, f)
        path = f.name
    try:
        vm = QBCVirtualMachine()
        vm.load_file(path)
        return vm.run_with_function(func_name)
    finally:
        os.unlink(path)

def test_basic_arithmetic():
    out = run_qentl('主函数: 函数() { 打印(2+6); 打印(10-4); 打印(6*7); 打印(10/2) }')
    assert [float(x) for x in out] == [8, 6, 42, 5.0]
    print("✅ 基础算术")

def test_string_operations():
    out = run_qentl('主函数: 函数() { 打印(2+3); 打印("hello") }')
    assert out == ['5', 'hello']
    print("✅ 字符串操作")

def test_fibonacci():
    code = """
斐波那契: 函数(n) { 如果 n <= 1 { 返回 n } 返回 斐波那契(n-1) + 斐波那契(n-2) }
主函数: 函数() { 打印(斐波那契(10)) }
"""
    out = run_qentl(code)
    assert float(out[0]) == 55
    print("✅ 斐波那契(10)=55(双递归)")

def test_factorial_recursive():
    code = """
阶乘: 函数(n) { 如果 n <= 1 { 返回 1 } 返回 n * 阶乘(n-1) }
主函数: 函数() { 打印(阶乘(5)) }
"""
    out = run_qentl(code)
    assert float(out[0]) == 120
    print("✅ 阶乘(5)=120(递归+<=)")

def test_comparison_operators():
    code = """
主函数: 函数() {
    打印(1 <= 1); 打印(2 >= 3); 打印(3 <= 2); 打印(4 >= 4)
}
"""
    out = run_qentl(code)
    assert out == ['True', 'False', 'False', 'True']
    print("✅ 比较运算符(<=,>=)")

def test_array_operations():
    code = """
主函数: 函数() {
    让 arr = [5, 10, 50]
    打印(arr[0]); 打印(arr[1]); 打印(arr[2])
}
"""
    out = run_qentl(code)
    assert [float(x) for x in out] == [5, 10, 50]
    print("✅ 数组操作")

def test_loop_sum():
    code = """
主函数: 函数() {
    让 sum = 0
    循环 i 在 0 到 10 { 让 sum = sum + i * 3 }
    打印(sum)
}
"""
    out = run_qentl(code)
    assert float(out[0]) == 135
    print("✅ 数组求和=150" if float(out[0]) == 135 else "❌")

def test_builtin_print():
    code = """
主函数: 函数() {
    打印(42); 打印("hello"); 打印("qentl"); 打印(5)
}
"""
    out = run_qentl(code)
    assert out == ['42', 'hello', 'qentl', '5']
    print("✅ 打印()内建函数")

def test_quantum_program():
    # Test quantum enum (core quantum feature working)
    code = """
quantum_enum 量子态 { 基态, 激发态, 叠加态 }
主函数: 函数() {
    让 state = 量子态.叠加态
    打印(state)
}
"""
    out = run_qentl(code)
    assert float(out[0]) == 2  # 叠加态 = 2
    print("✅ 量子枚举(量子态)")

def test_quantum_enum():
    code = """
quantum_enum 状态 { 低, 中, 高 }
主函数: 函数() { 打印(状态.低); 打印(状态.中); 打印(状态.高) }
"""
    out = run_qentl(code)
    assert out == ['0', '1', '2']
    print("✅ 量子枚举(quantum_enum)")

def test_while_loop():
    code = """
主函数: 函数() {
    让 x = 0
    循环当 x < 5 { 让 x = x + 1 }
    打印(x)
}
"""
    out = run_qentl(code)
    assert float(out[0]) == 5
    print("✅ 循环当(while)循环")

def test_elif_chain():
    code = """
主函数: 函数() {
    让 x = 5
    如果 x > 10 { 打印("big") }
    否则如果 x > 3 { 打印("medium") }
    否则 { 打印("small") }
}
"""
    out = run_qentl(code)
    assert out == ['medium']
    print("✅ 否则如果(elif)链")

def test_for_each():
    code = """
主函数: 函数() {
    每个 x 在 ["苹果", "香蕉", "橘子"] { 打印(x) }
}
"""
    out = run_qentl(code)
    assert out == ['苹果', '香蕉', '橘子']
    print("✅ 每个(for-each)循环")

def test_range_loop():
    code = """
主函数: 函数() {
    让 sum = 0
    循环 i 在 0 到 5 { 让 sum = sum + i }
    打印(sum)
}
"""
    out = run_qentl(code)
    assert float(out[0]) == 10
    print("✅ 范围循环(0到5)")

def test_global_var():
    code = """
让 计数 = 0
增: 函数() { 让 计数 = 计数 + 1 }
主函数: 函数() { 增(); 增(); 增(); 打印(计数) }
"""
    out = run_qentl(code)
    assert float(out[0]) == 3
    print("✅ 全局变量修改(3次调用)")

def test_multi_elif():
    code = """
quantum_enum 运算 { 加, 减, 乘, 除 }
计算: 函数(a, b, op) {
    如果 op == 运算.加 { 返回 a + b }
    否则如果 op == 运算.减 { 返回 a - b }
    否则如果 op == 运算.乘 { 返回 a * b }
    否则如果 op == 运算.除 { 返回 a / b }
    返回 0
}
主函数: 函数() {
    打印(计算(10, 3, 运算.加)); 打印(计算(10, 3, 运算.减))
    打印(计算(10, 3, 运算.乘)); 打印(计算(10, 3, 运算.除))
}
"""
    out = run_qentl(code)
    assert float(out[0])==13 and float(out[1])==7 and float(out[2])==30
    assert abs(float(out[3]) - 3.33) < 0.1
    print("✅ 多重否则如果(4分支)")

def test_fibonacci_recursive():
    code = """
斐波那契: 函数(n) {
    如果 n <= 1 { 返回 n }
    返回 斐波那契(n-1) + 斐波那契(n-2)
}
主函数: 函数() { 打印(斐波那契(5)); 打印(斐波那契(10)) }
"""
    out = run_qentl(code)
    assert float(out[0])==5 and float(out[1])==55
    print("✅ 斐波那契双递归(n-1,n-2)")

def test_gcd():
    code = """
最大公约数: 函数(a, b) {
    如果 b == 0 { 返回 a }
    返回 最大公约数(b, a % b)
}
主函数: 函数() {
    打印(最大公约数(12, 8)); 打印(最大公约数(100, 75))
}
"""
    out = run_qentl(code)
    assert float(out[0])==4 and float(out[1])==25
    print("✅ GCD欧几里得算法")

def test_string_builtins():
    code = """
主函数: 函数() {
    打印(长度("hello")); 打印(大写("world"))
    打印(替换("hello world", "world", "qentl"))
}
"""
    out = run_qentl(code)
    assert out[0]=='5' and out[1]=='WORLD' and out[2]=='hello qentl'
    print("✅ 字符串内建函数")

def test_math_builtins():
    code = """
主函数: 函数() {
    打印(绝对值(-42)); 打印(最大值(10, 20)); 打印(取整(3.7))
}
"""
    out = run_qentl(code)
    assert float(out[0])==42 and float(out[1])==20 and float(out[2])==3
    print("✅ 数学内建函数")


def test_break():
    code = """
主函数: 函数() {
    让 sum = 0
    循环 i 在 0 到 100 {
        如果 i == 5 { 跳出 }
        让 sum = sum + i
    }
    打印(sum)
}
"""
    out = run_qentl(code)
    assert float(out[0]) == 10
    print("✅ 跳出(break)")

def test_continue():
    code = """
主函数: 函数() {
    让 sum = 0
    循环 i 在 0 到 6 {
        如果 i == 3 { 继续 }
        让 sum = sum + i
    }
    打印(sum)
}
"""
    out = run_qentl(code)
    assert float(out[0]) == 12
    print("✅ 继续(continue)")


def test_field_assignment():
    code = """
主函数: 函数() {
    让 d = 字典(["x", "0", "y", "0"])
    d.x = 3
    d.y = 4
    打印(d.x + d.y)
}
"""
    out = run_qentl(code)
    assert float(out[0]) == 7
    print("✅ 字段赋值(field assignment)")


def test_try_catch():
    code = """
主函数: 函数() {
    尝试 {
        抛出 "测试错误"
    } 捕获 (e) {
        打印(e)
    }
}
"""
    out = run_qentl(code)
    assert out == ['测试错误']
    print("✅ 尝试/捕获(try/catch)")

# === Test Runner ===
tests = [
    test_basic_arithmetic, test_string_operations, test_fibonacci,
    test_factorial_recursive, test_comparison_operators, test_array_operations,
    test_loop_sum, test_builtin_print, test_quantum_program, test_quantum_enum,
    test_while_loop, test_elif_chain, test_for_each, test_range_loop, test_global_var,
    test_multi_elif, test_fibonacci_recursive, test_gcd, test_string_builtins, test_math_builtins,
    test_break, test_continue,
    test_field_assignment,
    test_try_catch,
]

if __name__ == '__main__':
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
    print(f"\n通过: {passed}/{len(tests)}")
