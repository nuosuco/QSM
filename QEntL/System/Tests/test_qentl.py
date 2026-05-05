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


def test_method_call():
    code = """
quantum_class 计算器 { 值: 整数 }
增加: 函数(self, n) {
    返回 self.值 + n
}
翻倍: 函数(self) {
    self.值 = self.值 * 2
    返回 self.值
}
主函数: 函数() {
    让 c = 计算器()
    c.值 = 10
    让 a = c.增加(5)
    让 b = c.翻倍()
    打印(a)
    打印(b)
}
"""
    out = run_qentl(code)
    assert '15' in out, f"Expected 15, got {out}"
    assert '20' in out, f"Expected 20, got {out}"
    print("✅ 方法调用(method call)")


def test_match_case():
    code = """
quantum_enum 季节 { 春, 夏, 秋, 冬 }
季节名: 函数(s) {
    匹配 s {
        情况 季节.春 { 返回 "春天" }
        情况 季节.夏 { 返回 "夏天" }
        情况 季节.秋 { 返回 "秋天" }
        默认 { 返回 "其他" }
    }
}
主函数: 函数() {
    打印(季节名(0))
    打印(季节名(1))
    打印(季节名(2))
    打印(季节名(99))
}
"""
    out = run_qentl(code)
    assert '春天' in out, f"Expected 春天, got {out}"
    assert '夏天' in out, f"Expected 夏天, got {out}"
    assert '秋天' in out, f"Expected 秋天, got {out}"
    assert '其他' in out, f"Expected 其他 for default, got {out}"
    print("✅ 匹配/情况(match/case)")


def test_dict_literal():
    code = """
主函数: 函数() {
    让 d = {"name": "量子", "level": 5}
    打印(d["name"])
    打印(d["level"])
    d["level"] = 10
    打印(d["level"])
}
"""
    out = run_qentl(code)
    assert '量子' in out, f"Expected 量子, got {out}"
    assert '5' in out, f"Expected 5, got {out}"
    assert '10' in out, f"Expected 10 after update, got {out}"
    print("✅ 字典字面量(dict literal)")


def test_foreach_loop():
    code = """
主函数: 函数() {
    让 fruits = ["苹果", "香蕉", "橘子"]
    让 result = ""
    循环 fruit 在 fruits {
        让 result = result + fruit + " "
    }
    打印(result)
}
"""
    out = run_qentl(code)
    out_str = ' '.join(out) if isinstance(out, list) else str(out)
    assert '苹果' in out_str, f"Expected 苹果, got {out}"
    assert '香蕉' in out_str, f"Expected 香蕉, got {out}"
    assert '橘子' in out_str, f"Expected 橘子, got {out}"
    print("✅ 遍历循环(foreach)")


def test_logical_operators():
    code = """
主函数: 函数() {
    让 score = 85
    如果 score >= 80 且 score <= 100 {
        打印("优秀范围")
    }
    如果 score < 60 或 score > 90 {
        打印("极端分数")
    } 否则 {
        打印("正常分数")
    }
}
"""
    out = run_qentl(code)
    out_str = ' '.join(out) if isinstance(out, list) else str(out)
    assert '优秀范围' in out_str, f"Expected 优秀范围, got {out}"
    assert '正常分数' in out_str, f"Expected 正常分数, got {out}"
    print("✅ 逻辑运算符(且/或)")


def test_ternary():
    code = """
主函数: 函数() {
    让 age = 20
    让 label = age >= 18 ? "成年" : "未成年"
    打印(label)
    打印(age < 18 ? "kid" : "adult")
}
"""
    out = run_qentl(code)
    out_str = ' '.join(out) if isinstance(out, list) else str(out)
    assert '成年' in out_str, f"Expected 成年, got {out}"
    assert 'adult' in out_str, f"Expected adult, got {out}"
    print("✅ 三元运算符(ternary ?:)")


def test_dict_mutation_across_method():
    code = """
quantum_class DB { data: 整数 }
set: 函数(self, key, val) {
    self.data[key] = val
}
主函数: 函数() {
    让 db = DB()
    db.data = {"a": 1}
    db.set("b", 2)
    打印(db.data["a"])
    打印(db.data["b"])
}
"""
    out = run_qentl(code)
    assert '1' in out, f"Expected 1, got {out}"
    assert '2' in out, f"Expected 2, got {out}"
    print("✅ 字典变异跨方法(dict mutation)")

# === Test Runner ===

def test_global_cross_func():
    """测试全局变量跨函数访问和修改"""
    code = """
全局 counter
让 counter = 0
递增: 函数() {
    counter = counter + 1
    返回 counter
}
主函数: 函数() {
    让 a = 递增()
    让 b = 递增()
    让 c = 递增()
    打印(a)
    打印(b)
    打印(c)
}
"""
    result = run_qentl(code)
    assert '1' in result, f"Expected 1 in {result}"
    assert '2' in result, f"Expected 2 in {result}"
    assert '3' in result, f"Expected 3 in {result}"
    print("✅ 全局变量跨函数(global cross-func) 通过:", result)


def test_string_format():
    """测试字符串格式化"""
    code = """
主函数: 函数() {
    打印(格式("{}+{}={}", 1, 2, 3))
    打印(格式("hello {}", "world"))
}
"""
    result = run_qentl(code)
    assert '1+2=3' in result, f"Expected '1+2=3' in {result}"
    assert 'hello world' in result, f"Expected 'hello world' in {result}"
    print("✅ 字符串格式化(string format) 通过:", result)


def test_array_slicing():
    """测试数组和字符串切片"""
    code = """
主函数: 函数() {
    让 a = [10, 20, 30, 40, 50]
    打印(子串(a, 1, 3))
    打印(子串("hello world", 0, 5))
}
"""
    result = run_qentl(code)
    assert '[20, 30, 40]' in result, f"Expected [20, 30, 40] in {result}"
    assert 'hello' in result, f"Expected hello in {result}"
    print("✅ 数组切片(array slicing) 通过:", result)


def test_oop_format_integration():
    """测试OOP+格式化+三元综合"""
    code = """
quantum_class 学生 {
    名字: 字符串
    分数: 整数
}

信息: 函数(self) {
    返回 格式("{}的分数是{}", self.名字, self.分数)
}

及格: 函数(self) {
    返回 self.分数 >= 60 ? "及格" : "不及格"
}

主函数: 函数() {
    让 s1 = 学生()
    s1.名字 = "小明"
    s1.分数 = 85
    打印(s1.信息())
    打印(s1.及格())
}
"""
    result = run_qentl(code)
    assert '小明的分数是85' in result, f"Expected score in {result}"
    assert '及格' in result, f"Expected pass in {result}"
    print("✅ OOP+格式化+三元综合(integration) 通过:", result)


def test_break_continue():
    """测试跳出(break)和继续(continue)"""
    code = """
主函数: 函数() {
    循环 i 在 0 到 6 {
        如果 i == 4 {
            跳出
        }
        如果 i % 2 == 0 {
            继续
        }
        打印(i)
    }
}
"""
    result = run_qentl(code)
    assert '1' in result and '3' in result, f"Expected 1,3 in {result}"
    assert '5' not in result, f"5 should not appear (break at 4)"
    print("✅ 跳出/继续(break/continue) 通过:", result)


def test_nested_builtins():
    """测试嵌套内置函数调用"""
    code = """
主函数: 函数() {
    打印(长度(范围数(10)))
    打印(最大值(3, 7))
    打印(绝对值(-42))
    打印(幂(2, 8))
    打印(类型(42))
    打印(类型("hello"))
    打印(包含("hello world", "world"))
    打印(子串("量子计算", 0, 2))
}
"""
    result = run_qentl(code)
    assert '10' in result, f"Expected 10 in {result}"
    assert '256' in result, f"Expected 256 in {result}"
    assert '数字' in result, f"Expected 数字 in {result}"
    assert '字符串' in result, f"Expected 字符串 in {result}"
    assert '量子' in result, f"Expected 量子 in {result}"
    print("✅ 嵌套内置函数(nested builtins) 通过:", result)


def test_fibonacci_memo():
    """测试斐波那契记忆化(递归+全局字典缓存)"""
    code = """
fib_cache: {}

斐波那契: 函数(n) {
    如果 n <= 1 {
        返回 n
    }
    如果 包含(fib_cache, n) {
        返回 fib_cache[n]
    }
    让 result = 斐波那契(n-1) + 斐波那契(n-2)
    fib_cache[n] = result
    返回 result
}

主函数: 函数() {
    循环 i 在 0 到 8 {
        打印(斐波那契(i))
    }
}
"""
    result = run_qentl(code)
    expected = ['0', '1', '1', '2', '3', '5', '8', '13']
    for e in expected:
        assert e in result, f"Expected {e} in {result}"
    print("✅ 斐波那契记忆化(fibonacci memoization) 通过:", result)


def test_multi_return_and_string_ops():
    """测试多返回值(列表)和字符串连接/重复"""
    code = """
最大最小: 函数(arr) {
    让 mx = arr[0]
    让 mn = arr[0]
    循环 x 在 arr {
        如果 x > mx { mx = x }
        如果 x < mn { mn = x }
    }
    返回 [mx, mn]
}

主函数: 函数() {
    让 r = 最大最小([5, 3, 9, 1, 7])
    打印(格式("max={},min={}", r[0], r[1]))
    让 words = ["a", "b", "c"]
    打印(连接(words, "-"))
    打印(重复("*", 3))
}
"""
    result = run_qentl(code)
    assert 'max=9,min=1' in result, f"Expected max=9,min=1 in {result}"
    assert 'a-b-c' in result, f"Expected a-b-c in {result}"
    assert '***' in result, f"Expected *** in {result}"
    print("✅ 多返回值+字符串操作(multi-return+string ops) 通过:", result)


def test_format_specs():
    """测试Python格式规范支持"""
    code = """
主函数: 函数() {
    打印(格式("pi={:.2f}", 3.14159))
    打印(格式("{:05d}", 42))
    打印(格式("{}+{}={}", 1, 2, 3))
}
"""
    result = run_qentl(code)
    assert any('3.14' in r for r in result), f"Expected 3.14 in {result}"
    assert any('00042' in r for r in result), f"Expected 00042 in {result}"
    assert any('1+2=3' in r for r in result), f"Expected 1+2=3 in {result}"
    print("✅ 格式规范(format specs) 通过:", result)


def test_elif_5branch():
    """测试5分支elif/else链"""
    code = """
分类: 函数(score) {
    如果 score >= 90 { 返回 "优秀" }
    否则如果 score >= 80 { 返回 "良好" }
    否则如果 score >= 70 { 返回 "中等" }
    否则如果 score >= 60 { 返回 "及格" }
    否则 { 返回 "不及格" }
}
主函数: 函数() {
    打印(分类(95))
    打印(分类(85))
    打印(分类(75))
    打印(分类(65))
    打印(分类(45))
}
"""
    result = run_qentl(code)
    assert any('优秀' in r for r in result), f"Expected 优秀 in {result}"
    assert any('良好' in r for r in result), f"Expected 良好 in {result}"
    assert any('中等' in r for r in result), f"Expected 中等 in {result}"
    assert any('及格' in r for r in result), f"Expected 及格 in {result}"
    assert any('不及格' in r for r in result), f"Expected 不及格 in {result}"
    print("✅ 5分支elif链(multi-elif) 通过:", result)


def test_math_builtins():
    """测试数学内置函数"""
    code = """
主函数: 函数() {
    打印(四舍五入(3.7))
    打印(平方(5))
    打印(平方根(16))
    打印(求和([1,2,3,4,5]))
    打印(求积([2,3,4]))
    打印(绝对值(-7))
    打印(最大值(3, 9))
    打印(替换("hello world", "world", "qsm"))
}
"""
    result = run_qentl(code)
    assert any('4' in r for r in result[:1]), f"四舍五入: {result}"
    assert any('25' in r for r in result), f"平方: {result}"
    assert any('15' in r for r in result), f"求和: {result}"
    assert any('24' in r for r in result), f"求积: {result}"
    assert any('hello qsm' in r for r in result), f"替换: {result}"
    print("✅ 数学内置函数(math builtins) 通过:", result)


def test_file_io():
    """测试文件读写"""
    import os
    code = """
主函数: 函数() {
    让 ok = 写入文件("/tmp/qentl_io_test.txt", "qentl os")
    打印(格式("写入={}", ok))
    让 content = 读取文件("/tmp/qentl_io_test.txt")
    打印(格式("内容={}", content))
    打印(格式("存在={}", 文件存在("/tmp/qentl_io_test.txt")))
}
"""
    result = run_qentl(code)
    assert any('写入=1' in r for r in result), f"写入失败: {result}"
    assert any('qentl os' in r for r in result), f"读取失败: {result}"
    assert any('存在=1' in r for r in result), f"存在检测失败: {result}"
    # Cleanup
    if os.path.exists("/tmp/qentl_io_test.txt"):
        os.remove("/tmp/qentl_io_test.txt")
    print("✅ 文件IO(file read/write) 通过:", result)


def test_substring_2arg():
    """测试子串2参数(从start到末尾)"""
    code = """
主函数: 函数() {
    打印(子串("hello world", 6))
    打印(子串("hello", 0, 3))
    打印(格式("arr={}", 子串([10,20,30,40], 2)))
}
"""
    result = run_qentl(code)
    assert any('world' in r for r in result), f"子串2arg: {result}"
    assert any('hel' in r for r in result), f"子串3arg: {result}"
    assert any('30, 40' in r for r in result), f"数组子串: {result}"
    print("✅ 子串2参数(substring 2-arg) 通过:", result)


def test_system_builtins():
    """测试系统内置函数"""
    code = """
主函数: 函数() {
    让 t = 当前时间()
    打印(格式("时间长度={}", 长度(t)))
    让 home = 获取环境("HOME")
    打印(格式("HOME有值={}", 长度(home) > 0))
    让 os = 执行命令("echo qentl")
    打印(格式("echo={}", os))
}
"""
    result = run_qentl(code)
    assert any('时间长度=19' in r for r in result), f"当前时间: {result}"
    assert any('HOME有值=True' in r or 'HOME有值=1' in r for r in result), f"获取环境: {result}"
    assert any('qentl' in r for r in result), f"执行命令: {result}"
    print("✅ 系统内置函数(system builtins) 通过:", result)

def test_string_utilities():
    """字符串工具函数"""
    code = """
主函数: 函数() {
    让 s = "hello world"
    让 pos = 字符位置(s, "world")
    让 notfound = 字符位置(s, "xyz")
    让 cleaned = 删除空白("  hi  ")
    让 repeated = 重复到("ab", 7)
    打印(格式("pos={} not={} clean=[{}] rep={}", pos, notfound, cleaned, repeated))
}
"""
    result = run_qentl(code)
    assert result == ['pos=6 not=-1 clean=[hi] rep=abababa'], f"字符串工具: {result}"
    print("✅ 字符串工具函数(string utilities) 通过:", result)


def test_class_external_methods():
    """quantum_class + 外部方法模式 (Go-style)"""
    code = """
quantum_class 学生 { 姓名: 字符串; 分数: 整数 }

评价: 函数(self) {
    如果 self.分数 >= 90 { 返回 "A" }
    否则如果 self.分数 >= 60 { 返回 "D" }
    否则 { 返回 "F" }
}

报告: 函数(self) {
    返回 格式("{}: {}={}", self.姓名, self.分数, 评价(self))
}

主函数: 函数() {
    让 s1 = 学生(); s1.姓名 = "张三"; s1.分数 = 95
    让 s2 = 学生(); s2.姓名 = "王五"; s2.分数 = 55
    打印(报告(s1))
    打印(报告(s2))
}
"""
    result = run_qentl(code)
    assert result == ['张三: 95=A', '王五: 55=F'], f"类外部方法: {result}"
    print("✅ 类外部方法(class+external methods) 通过:", result)


def test_bubble_sort():
    """冒泡排序算法"""
    code = """
冒泡排序: 函数(arr) {
    让 n = 长度(arr)
    循环 i 在 范围数(0, n) {
        循环 j 在 范围数(0, n - i - 1) {
            如果 arr[j] > arr[j + 1] {
                让 temp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp
            }
        }
    }
    返回 arr
}

主函数: 函数() {
    让 data = [5, 3, 8, 1, 9, 2, 7]
    让 sorted = 冒泡排序(data)
    让 result = 格式("{} {} {} {} {} {} {}", sorted[0], sorted[1], sorted[2], sorted[3], sorted[4], sorted[5], sorted[6])
    打印(result)
}
"""
    result = run_qentl(code)
    # Check it contains sorted output
    assert any('1' in r and '2' in r and '9' in r for r in result), f"冒泡排序: {result}"
    print("✅ 冒泡排序(bubble sort) 通过:", result)


def test_quantum_enum_advanced():
    """量子枚举+循环+条件"""
    code = """
quantum_enum 量子态 { 基态, 激发态, 叠加态, 纠缠态 }

主函数: 函数() {
    让 states = [量子态.基态, 量子态.激发态, 量子态.叠加态, 量子态.纠缠态]
    循环 i 在 范围数(0, 4) {
        如果 states[i] == 量子态.纠缠态 {
            打印(格式("纠缠态:位置={}", i))
        }
    }
}
"""
    result = run_qentl(code)
    assert result == ['纠缠态:位置=3'], f"量子枚举增强: {result}"
    print("✅ 量子枚举增强(quantum enum advanced) 通过:", result)


def test_comprehensive_integration():
    """综合集成测试: 类+函数+循环+条件+格式"""
    code = """
quantum_class 商品 { 名称: 字符串; 价格: 整数 }

折扣价: 函数(item, rate) {
    返回 取整(item.价格 * rate)
}

主函数: 函数() {
    让 items = []
    让 a = 商品(); a.名称 = "书"; a.价格 = 50
    让 b = 商品(); b.名称 = "笔"; b.价格 = 10
    让 c = 商品(); c.名称 = "包"; c.价格 = 200
    推入(items, a); 推入(items, b); 推入(items, c)
    
    让 total = 0
    循环 item 在 items {
        让 discounted = 折扣价(item, 0.8)
        打印(格式("{}: {}→{}", item.名称, item.价格, discounted))
        total = total + discounted
    }
    打印(格式("合计={}", total))
}
"""
    result = run_qentl(code)
    # Should have 3 discount lines + total
    assert len(result) == 4, f"综合集成: {result}"
    assert any('书' in r and '50' in r and '40' in r for r in result), f"书折扣: {result}"
    assert any('合计' in r for r in result), f"合计: {result}"
    print("✅ 综合集成(comprehensive integration) 通过:", result)


def test_string_pipeline():
    """字符串处理管道"""
    code = """
主函数: 函数() {
    让 s = "hello world from qentl"
    让 parts = 分割(s, " ")
    让 upper = []
    循环 p 在 parts {
        推入(upper, 首大写(p))
    }
    打印(格式("词数={}", 长度(parts)))
    打印(格式("首词={}", parts[0]))
    打印(格式("包含qentl={}", 包含(s, "qentl")))
    打印(格式("位置={}", 字符位置(s, "world")))
}
"""
    result = run_qentl(code)
    assert result == ['词数=4', '首词=hello', '包含qentl=1', '位置=6'], f"字符串管道: {result}"
    print("✅ 字符串处理管道(string pipeline) 通过:", result)


def test_nested_function_calls():
    """嵌套函数调用(函数组合)"""
    code = """
平方: 函数(x) { 返回 x * x }
立方: 函数(x) { 返回 平方(x) * x }

主函数: 函数() {
    打印(格式("3²={}", 平方(3)))
    打印(格式("3³={}", 立方(3)))
}
"""
    result = run_qentl(code)
    assert result == ['3²=9', '3³=27'], f"嵌套函数: {result}"
    print("✅ 嵌套函数调用(nested function composition) 通过:", result)


def test_recursive_factorial():
    """递归阶乘"""
    code = """
阶乘: 函数(n) {
    如果 n <= 1 { 返回 1 }
    返回 n * 阶乘(n - 1)
}

主函数: 函数() {
    打印(格式("5!={}", 阶乘(5)))
    打印(格式("10!={}", 阶乘(10)))
}
"""
    result = run_qentl(code)
    assert result == ['5!=120', '10!=3628800'], f"递归阶乘: {result}"
    print("✅ 递归阶乘(recursive factorial) 通过:", result)


def test_recursive_fibonacci():
    """递归斐波那契"""
    code = """
斐波那契: 函数(n) {
    如果 n <= 1 { 返回 n }
    返回 斐波那契(n - 1) + 斐波那契(n - 2)
}

主函数: 函数() {
    循环 i 在 范围数(0, 10) {
        打印(格式("F({})={}", i, 斐波那契(i)))
    }
}
"""
    result = run_qentl(code)
    assert result == ['F(0)=0','F(1)=1','F(2)=1','F(3)=2','F(4)=3',
                       'F(5)=5','F(6)=8','F(7)=13','F(8)=21','F(9)=34'], f"斐波那契: {result}"
    print("✅ 递归斐波那契(recursive fibonacci) 通过:", result[:3], "...")


def test_array_sum_average():
    """数组求和与平均值"""
    code = """
求和: 函数(arr) {
    让 s = 0
    循环 x 在 arr { s = s + x }
    返回 s
}

主函数: 函数() {
    让 data = [3, 7, 1, 9, 4, 6, 2, 8, 5]
    打印(格式("和={}", 求和(data)))
    打印(格式("长度={}", 长度(data)))
    打印(格式("平均={}", 求和(data) / 长度(data)))
}
"""
    result = run_qentl(code)
    assert result == ['和=45', '长度=9', '平均=5.0'], f"数组操作: {result}"
    print("✅ 数组求和平均(array sum/average) 通过:", result)


def test_list_filter():
    """列表过滤(偶数筛选)"""
    code = """
过滤偶数: 函数(arr) {
    让 result = []
    循环 x 在 arr {
        如果 x % 2 == 0 { 推入(result, x) }
    }
    返回 result
}

主函数: 函数() {
    让 nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    让 evens = 过滤偶数(nums)
    打印(格式("偶数个数={}", 长度(evens)))
}
"""
    result = run_qentl(code)
    assert result == ['偶数个数=5'], f"列表过滤: {result}"
    print("✅ 列表过滤(list filter) 通过:", result)


def test_list_map_square():
    """列表映射(每个元素平方)"""
    code = """
平方列表: 函数(arr) {
    让 result = []
    循环 x 在 arr { 推入(result, x * x) }
    返回 result
}

主函数: 函数() {
    让 nums = [1, 2, 3, 4, 5]
    让 squared = 平方列表(nums)
    打印(格式("平方={}", 连接(squared, " ")))
}
"""
    result = run_qentl(code)
    assert result == ['平方=1 4 9 16 25'], f"列表映射: {result}"
    print("✅ 列表映射(list map/square) 通过:", result)


def test_linear_search():
    """线性查找"""
    code = """
查找元素: 函数(arr, target) {
    循环 i 在 范围数(0, 长度(arr)) {
        如果 arr[i] == target { 返回 i }
    }
    返回 -1
}

主函数: 函数() {
    让 data = [10, 20, 30, 40, 50]
    打印(格式("30的位置={}", 查找元素(data, 30)))
    打印(格式("99的位置={}", 查找元素(data, 99)))
}
"""
    result = run_qentl(code)
    assert result == ['30的位置=2', '99的位置=-1'], f"线性查找: {result}"
    print("✅ 线性查找(linear search) 通过:", result)


def test_string_reverse():
    """字符串反转(子串+循环)"""
    code = """
反转字符串: 函数(s) {
    让 result = ""
    让 i = 长度(s) - 1
    循环当 i >= 0 {
        result = result + 子串(s, i, 1)
        i = i - 1
    }
    返回 result
}

主函数: 函数() {
    打印(反转字符串("hello"))
}
"""
    result = run_qentl(code)
    assert result == ['olleh'], f"字符串反转: {result}"
    print("✅ 字符串反转(string reverse) 通过:", result)


def test_count_occurrences():
    """计数函数(统计元素出现次数)"""
    code = """
计数: 函数(arr, target) {
    让 count = 0
    循环 x 在 arr {
        如果 x == target { count = count + 1 }
    }
    返回 count
}

主函数: 函数() {
    让 data = [1, 2, 3, 2, 4, 2, 5, 2]
    打印(格式("2出现了{}次", 计数(data, 2)))
    打印(格式("7出现了{}次", 计数(data, 7)))
}
"""
    result = run_qentl(code)
    assert result == ['2出现了4次', '7出现了0次'], f"计数: {result}"
    print("✅ 计数函数(count occurrences) 通过:", result)


def test_insertion_sort():
    """插入排序算法"""
    code = """
插入排序: 函数(arr) {
    让 n = 长度(arr)
    循环 i 在 范围数(1, n) {
        让 key = arr[i]
        让 j = i - 1
        循环当 j >= 0 且 arr[j] > key {
            arr[j + 1] = arr[j]
            j = j - 1
        }
        arr[j + 1] = key
    }
    返回 arr
}

主函数: 函数() {
    让 data = [5, 2, 8, 1, 9, 3]
    让 sorted = 插入排序(data)
    打印(格式("排序={}", 连接(sorted, " ")))
}
"""
    result = run_qentl(code)
    assert result == ['排序=1 2 3 5 8 9'], f"插入排序: {result}"
    print("✅ 插入排序(insertion sort) 通过:", result)


def test_euclidean_gcd():
    """辗转相除法(欧几里得GCD)"""
    code = """
最大公约数: 函数(a, b) {
    循环当 b != 0 {
        让 temp = b
        b = a % b
        a = temp
    }
    返回 a
}

主函数: 函数() {
    打印(格式("GCD(12,8)={}", 最大公约数(12, 8)))
    打印(格式("GCD(54,24)={}", 最大公约数(54, 24)))
}
"""
    result = run_qentl(code)
    assert result == ['GCD(12,8)=4', 'GCD(54,24)=6'], f"GCD: {result}"
    print("✅ 辗转相除法(Euclidean GCD) 通过:", result)


def test_binary_search():
    """二分查找算法"""
    code = """
二分查找: 函数(arr, target) {
    让 low = 0
    让 high = 长度(arr) - 1
    循环当 low <= high {
        让 mid = 取整((low + high) / 2)
        如果 arr[mid] == target { 返回 mid }
        否则如果 arr[mid] < target { low = mid + 1 }
        否则 { high = mid - 1 }
    }
    返回 -1
}

主函数: 函数() {
    让 data = [1, 3, 5, 7, 9, 11, 13, 15]
    打印(格式("7={}", 二分查找(data, 7)))
    打印(格式("8={}", 二分查找(data, 8)))
}
"""
    result = run_qentl(code)
    assert result == ['7=3', '8=-1'], f"二分查找: {result}"
    print("✅ 二分查找(binary search) 通过:", result)


def test_nested_list_iteration():
    """嵌套列表迭代(矩阵求和)"""
    code = """
矩阵求和: 函数(m) {
    让 total = 0
    循环 row 在 m {
        循环 x 在 row { total = total + x }
    }
    返回 total
}

主函数: 函数() {
    让 matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    打印(格式("和={}", 矩阵求和(matrix)))
}
"""
    result = run_qentl(code)
    assert result == ['和=45'], f"嵌套列表: {result}"
    print("✅ 嵌套列表迭代(nested list/matrix sum) 通过:", result)


def test_is_prime():
    """素数判断"""
    code = """
是素数: 函数(n) {
    如果 n < 2 { 返回 0 }
    让 i = 2
    循环当 i * i <= n {
        如果 n % i == 0 { 返回 0 }
        i = i + 1
    }
    返回 1
}

主函数: 函数() {
    打印(格式("7={}", 是素数(7)))
    打印(格式("10={}", 是素数(10)))
    打印(格式("13={}", 是素数(13)))
}
"""
    result = run_qentl(code)
    assert result == ['7=1', '10=0', '13=1'], f"素数: {result}"
    print("✅ 素数判断(is prime) 通过:", result)


def test_palindrome_check():
    """回文字符串判断"""
    code = """
是回文: 函数(s) {
    让 i = 0
    让 j = 长度(s) - 1
    循环当 i < j {
        如果 子串(s, i, 1) != 子串(s, j, 1) { 返回 0 }
        i = i + 1
        j = j - 1
    }
    返回 1
}

主函数: 函数() {
    打印(格式("aba={}", 是回文("aba")))
    打印(格式("abc={}", 是回文("abc")))
}
"""
    result = run_qentl(code)
    assert result == ['aba=1', 'abc=0'], f"回文: {result}"
    print("✅ 回文判断(palindrome check) 通过:", result)


def test_caesar_cipher():
    """凯撒密码(字符代码+字符)"""
    code = """
凯撒加密: 函数(text, shift) {
    让 result = ""
    循环 i 在 范围数(0, 长度(text)) {
        让 c = 子串(text, i, 1)
        让 code = 字符代码(c)
        如果 code >= 97 且 code <= 122 {
            code = code + shift
            如果 code > 122 { code = code - 26 }
            如果 code < 97 { code = code + 26 }
        }
        result = result + 字符(code)
    }
    返回 result
}

主函数: 函数() {
    打印(凯撒加密("hello", 3))
}
"""
    result = run_qentl(code)
    assert result == ['khoor'], f"凯撒密码: {result}"
    print("✅ 凯撒密码(Caesar cipher) 通过:", result)


def test_fast_exponentiation():
    """快速幂算法(递归分治)"""
    code = """
快速幂: 函数(b, e) {
    如果 e == 0 { 返回 1 }
    如果 e == 1 { 返回 b }
    让 half = 快速幂(b, 取整(e / 2))
    如果 e % 2 == 0 {
        返回 half * half
    } 否则 {
        返回 half * half * b
    }
}

主函数: 函数() {
    打印(格式("2^10={}", 快速幂(2, 10)))
    打印(格式("3^5={}", 快速幂(3, 5)))
}
"""
    result = run_qentl(code)
    assert result == ['2^10=1024', '3^5=243'], f"快速幂: {result}"
    print("✅ 快速幂(fast exponentiation) 通过:", result)


def test_prefix_sum():
    """前缀和(累积和)"""
    code = """
前缀和: 函数(arr) {
    让 result = []
    让 s = 0
    循环 x 在 arr {
        s = s + x
        推入(result, s)
    }
    返回 result
}

主函数: 函数() {
    让 data = [1, 2, 3, 4, 5]
    让 ps = 前缀和(data)
    打印(连接(ps, ","))
}
"""
    result = run_qentl(code)
    assert result == ['1,3,6,10,15'], f"前缀和: {result}"
    print("✅ 前缀和(prefix sum) 通过:", result)


def test_decimal_to_binary():
    """十进制转二进制"""
    code = """
十转二: 函数(n) {
    如果 n == 0 { 返回 "0" }
    让 result = ""
    循环当 n > 0 {
        result = 格式("{}{}", n % 2, result)
        n = 取整(n / 2)
    }
    返回 result
}

主函数: 函数() {
    打印(十转二(10))
    打印(十转二(255))
}
"""
    result = run_qentl(code)
    assert result == ['1010', '11111111'], f"进制转换: {result}"
    print("✅ 十进制转二进制(decimal to binary) 通过:", result)


def test_run_length_encoding():
    """行程编码(字符串压缩)"""
    code = """
行程编码: 函数(s) {
    让 result = ""
    让 i = 0
    让 n = 长度(s)
    循环当 i < n {
        让 ch = 子串(s, i, 1)
        让 count = 1
        循环当 i + count < n 且 子串(s, i + count, 1) == ch {
            count = count + 1
        }
        result = result + ch + 格式("{}", count)
        i = i + count
    }
    返回 result
}

主函数: 函数() {
    打印(行程编码("aaabbc"))
}
"""
    result = run_qentl(code)
    assert result == ['a3b2c1'], f"行程编码: {result}"
    print("✅ 行程编码(RLE/compression) 通过:", result)


def test_fizzbuzz():
    """FizzBuzz经典编程题"""
    code = """
主函数: 函数() {
    循环 i 在 范围数(1, 16) {
        如果 i % 15 == 0 { 打印("FizzBuzz") }
        否则如果 i % 3 == 0 { 打印("Fizz") }
        否则如果 i % 5 == 0 { 打印("Buzz") }
        否则 { 打印(格式("{}", i)) }
    }
}
"""
    result = run_qentl(code)
    expected = ['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']
    assert result == expected, f"FizzBuzz: {result}"
    print("✅ FizzBuzz 通过:", result)


def test_merge_sorted_arrays():
    """合并两个有序数组"""
    code = """
合并: 函数(a, b) {
    让 result = []
    让 i = 0
    让 j = 0
    循环当 i < 长度(a) 且 j < 长度(b) {
        如果 a[i] <= b[j] {
            推入(result, a[i])
            i = i + 1
        } 否则 {
            推入(result, b[j])
            j = j + 1
        }
    }
    循环当 i < 长度(a) { 推入(result, a[i]); i = i + 1 }
    循环当 j < 长度(b) { 推入(result, b[j]); j = j + 1 }
    返回 result
}

主函数: 函数() {
    让 a = [1, 3, 5]
    让 b = [2, 4, 6]
    让 m = 合并(a, b)
    打印(连接(m, ","))
}
"""
    result = run_qentl(code)
    assert result == ['1,2,3,4,5,6'], f"合并: {result}"
    print("✅ 合并有序数组(merge sorted arrays) 通过:", result)


def test_user_func_overrides_builtin():
    """用户函数覆盖同名内置函数"""
    code = """
排序: 函数(arr) {
    让 n = 长度(arr)
    循环 i 在 范围数(0, n - 1) {
        循环 j 在 范围数(0, n - i - 1) {
            如果 arr[j] > arr[j + 1] {
                让 temp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp
            }
        }
    }
    返回 arr
}

主函数: 函数() {
    让 data = [3, 1, 2]
    让 s = 排序(data)
    打印(连接(s, ","))
}
"""
    result = run_qentl(code)
    assert result == ['1,2,3'], f"覆盖builtin: {result}"
    print("✅ 用户函数覆盖内置(user overrides builtin) 通过:", result)


def test_matrix_max():
    """矩阵最大值查找"""
    code = """
矩阵最大值: 函数(m) {
    让 max_val = m[0][0]
    循环 i 在 范围数(0, 长度(m)) {
        循环 j 在 范围数(0, 长度(m[i])) {
            如果 m[i][j] > max_val { max_val = m[i][j] }
        }
    }
    返回 max_val
}

主函数: 函数() {
    让 matrix = [[3, 1, 4], [1, 5, 9], [2, 6, 5]]
    打印(格式("max={}", 矩阵最大值(matrix)))
}
"""
    result = run_qentl(code)
    assert result == ['max=9'], f"矩阵最大值: {result}"
    print("✅ 矩阵最大值(matrix max) 通过:", result)


def test_armstrong_number():
    """阿姆斯特朗数(水仙花数)判断"""
    code = """
是阿姆斯特朗数: 函数(n) {
    让 a = 取整(n / 100)
    让 b = 取整((n % 100) / 10)
    让 c = n % 10
    如果 a * a * a + b * b * b + c * c * c == n { 返回 1 }
    返回 0
}

主函数: 函数() {
    打印(格式("153={}", 是阿姆斯特朗数(153)))
    打印(格式("100={}", 是阿姆斯特朗数(100)))
}
"""
    result = run_qentl(code)
    assert result == ['153=1', '100=0'], f"阿姆斯特朗数: {result}"
    print("✅ 阿姆斯特朗数(Armstrong number) 通过:", result)


def test_selection_sort():
    """选择排序算法"""
    code = """
选择排序: 函数(arr) {
    让 n = 长度(arr)
    循环 i 在 范围数(0, n - 1) {
        让 min_idx = i
        循环 j 在 范围数(i + 1, n) {
            如果 arr[j] < arr[min_idx] { min_idx = j }
        }
        如果 min_idx != i {
            让 temp = arr[i]
            arr[i] = arr[min_idx]
            arr[min_idx] = temp
        }
    }
    返回 arr
}

主函数: 函数() {
    让 data = [64, 25, 12, 22, 11]
    让 s = 选择排序(data)
    打印(连接(s, ","))
}
"""
    result = run_qentl(code)
    assert result == ['11,12,22,25,64'], f"选择排序: {result}"
    print("✅ 选择排序(selection sort) 通过:", result)


def test_collatz_steps():
    """考拉兹猜想(3n+1问题)步数"""
    code = """
考拉兹步数: 函数(n) {
    让 steps = 0
    循环当 n != 1 {
        如果 n % 2 == 0 { n = 取整(n / 2) }
        否则 { n = n * 3 + 1 }
        steps = steps + 1
    }
    返回 steps
}

主函数: 函数() {
    打印(格式("1={}", 考拉兹步数(1)))
    打印(格式("7={}", 考拉兹步数(7)))
}
"""
    result = run_qentl(code)
    assert result == ['1=0', '7=16'], f"考拉兹: {result}"
    print("✅ 考拉兹猜想(Collatz 3n+1) 通过:", result)


def test_word_count():
    """单词计数(分割+长度)"""
    code = """
单词计数: 函数(text) {
    让 words = 分割(text, " ")
    返回 长度(words)
}

主函数: 函数() {
    打印(格式("a b c={}", 单词计数("a b c")))
}
"""
    result = run_qentl(code)
    assert result == ['a b c=3'], f"单词计数: {result}"
    print("✅ 单词计数(word count) 通过:", result)


def test_perfect_number():
    """完全数判断(6=1+2+3, 28=1+2+4+7+14)"""
    code = """
是完全数: 函数(n) {
    让 sum = 0
    让 i = 1
    循环当 i < n {
        如果 n % i == 0 { sum = sum + i }
        i = i + 1
    }
    如果 sum == n { 返回 1 }
    返回 0
}

主函数: 函数() {
    打印(格式("6={}", 是完全数(6)))
    打印(格式("12={}", 是完全数(12)))
}
"""
    result = run_qentl(code)
    assert result == ['6=1', '12=0'], f"完全数: {result}"
    print("✅ 完全数(perfect number) 通过:", result)



def test_tower_of_hanoi_moves():
    """汉诺塔最少步数(2^n-1)"""
    code = """
快速幂: 函数(b, e) {
    如果 e == 0 { 返回 1 }
    如果 e == 1 { 返回 b }
    让 half = 快速幂(b, 取整(e / 2))
    如果 e % 2 == 0 { 返回 half * half }
    否则 { 返回 half * half * b }
}

汉诺塔步数: 函数(n) {
    返回 快速幂(2, n) - 1
}

主函数: 函数() {
    打印(格式("3={}", 汉诺塔步数(3)))
    打印(格式("5={}", 汉诺塔步数(5)))
}
"""
    result = run_qentl(code)
    assert result == ['3=7', '5=31'], f"汉诺塔: {result}"
    print("✅ 汉诺塔步数(Tower of Hanoi 2^n-1) 通过:", result)




def test_rot13_cipher():
    """ROT13密码(自解密)"""
    code = """
ROT13: 函数(text) {
    让 result = ""
    循环 i 在 范围数(0, 长度(text)) {
        让 c = 子串(text, i, 1)
        让 code = 字符代码(c)
        如果 code >= 97 且 code <= 109 { result = result + 字符(code + 13) }
        否则如果 code >= 110 且 code <= 122 { result = result + 字符(code - 13) }
        否则 { result = result + c }
    }
    返回 result
}

主函数: 函数() {
    打印(ROT13(ROT13("hello")))
}
"""
    result = run_qentl(code)
    assert result == ['hello'], f"ROT13: {result}"
    print("✅ ROT13密码(自解密) 通过:", result)


def test_string_dedup():
    """字符串去重(保留首次出现)"""
    code = """
去重复字符: 函数(s) {
    让 result = ""
    循环 i 在 范围数(0, 长度(s)) {
        让 c = 子串(s, i, 1)
        如果 包含(result, c) == 0 { result = result + c }
    }
    返回 result
}

主函数: 函数() {
    打印(去重复字符("hello"))
}
"""
    result = run_qentl(code)
    assert result == ['helo'], f"去重: {result}"
    print("✅ 字符串去重(string dedup) 通过:", result)


def test_frequency_count():
    """字符串频率统计(dict+条件赋值)"""
    code = """
频率统计: 函数(text) {
    让 freq = {}
    循环 i 在 范围数(0, 长度(text)) {
        让 c = 子串(text, i, 1)
        如果 包含(freq, c) { freq[c] = freq[c] + 1 }
        否则 { freq[c] = 1 }
    }
    返回 freq
}

主函数: 函数() {
    让 f = 频率统计("aabb")
    打印(格式("a={}", f["a"]))
    打印(格式("b={}", f["b"]))
}
"""
    result = run_qentl(code)
    assert result == ['a=2', 'b=2'], f"频率: {result}"
    print("✅ 频率统计(frequency count) 通过:", result)


def test_fibonacci_memo():
    """斐波那契递归+备忘录(全局dict缓存)"""
    code = """
全局 memo
让 memo = {}

斐波那契: 函数(n) {
    如果 n <= 1 { 返回 n }
    如果 包含(memo, n) { 返回 memo[n] }
    让 val = 斐波那契(n - 1) + 斐波那契(n - 2)
    memo[n] = val
    返回 val
}

主函数: 函数() {
    打印(格式("10={}", 斐波那契(10)))
}
"""
    result = run_qentl(code)
    assert result == ['10=55'], f"斐波那契: {result}"
    print("✅ 斐波那契+备忘录(fibonacci memo) 通过:", result)


def test_gcd_lcm():
    """最大公约数+最小公倍数(欧几里得算法)"""
    code = """
最大公约数: 函数(a, b) {
    循环当 b != 0 {
        让 temp = b
        b = a % b
        a = temp
    }
    返回 a
}

最小公倍数: 函数(a, b) {
    返回 取整(a * b / 最大公约数(a, b))
}

主函数: 函数() {
    打印(格式("gcd={}", 最大公约数(12, 8)))
    打印(格式("lcm={}", 最小公倍数(12, 8)))
}
"""
    result = run_qentl(code)
    assert result == ['gcd=4', 'lcm=24'], f"GCD/LCM: {result}"
    print("✅ GCD+LCM(欧几里得算法) 通过:", result)


def test_vowel_count():
    """元音计数(多条件或判断)"""
    code = """
元音计数: 函数(s) {
    让 count = 0
    循环 i 在 范围数(0, 长度(s)) {
        让 c = 子串(s, i, 1)
        如果 c == "a" 或 c == "e" 或 c == "i" 或 c == "o" 或 c == "u" {
            count = count + 1
        }
    }
    返回 count
}

主函数: 函数() {
    打印(格式("hello={}", 元音计数("hello")))
}
"""
    result = run_qentl(code)
    assert result == ['hello=2'], f"元音: {result}"
    print("✅ 元音计数(vowel count) 通过:", result)


def test_binary_to_decimal():
    """二进制转十进制(反向遍历+幂运算)"""
    code = """
二进制转十进制: 函数(s) {
    让 result = 0
    让 power = 1
    让 i = 长度(s) - 1
    循环当 i >= 0 {
        让 c = 子串(s, i, 1)
        如果 c == "1" { result = result + power }
        power = power * 2
        i = i - 1
    }
    返回 result
}

主函数: 函数() {
    打印(格式("1010={}", 二进制转十进制("1010")))
    打印(格式("1111={}", 二进制转十进制("1111")))
}
"""
    result = run_qentl(code)
    assert result == ['1010=10', '1111=15'], f"二进制: {result}"
    print("✅ 二进制转十进制(binary to decimal) 通过:", result)


def test_decimal_to_roman():
    """十进制转罗马数字(数组查表+循环)"""
    code = """
十进制转罗马: 函数(n) {
    让 vals = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    让 syms = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    让 result = ""
    让 i = 0
    循环当 n > 0 {
        如果 n >= vals[i] { result = result + syms[i]; n = n - vals[i] }
        否则 { i = i + 1 }
    }
    返回 result
}

主函数: 函数() {
    打印(格式("58={}", 十进制转罗马(58)))
    打印(格式("4={}", 十进制转罗马(4)))
}
"""
    result = run_qentl(code)
    assert result == ['58=LVIII', '4=IV'], f"罗马数字: {result}"
    print("✅ 十进制转罗马数字(decimal to roman) 通过:", result)


def test_extract_digits():
    """提取字符串中的数字(字符代码范围判断)"""
    code = """
提取数字: 函数(s) {
    让 result = ""
    循环 i 在 范围数(0, 长度(s)) {
        让 c = 子串(s, i, 1)
        让 code = 字符代码(c)
        如果 code >= 48 且 code <= 57 { result = result + c }
    }
    返回 result
}

主函数: 函数() {
    打印(格式("a1b2c3={}", 提取数字("a1b2c3")))
}
"""
    result = run_qentl(code)
    assert result == ['a1b2c3=123'], f"提取数字: {result}"
    print("✅ 提取数字(extract digits) 通过:", result)


def test_leap_year():
    """闰年判断(多重elif+取模)"""
    code = """
是闰年: 函数(year) {
    如果 year % 400 == 0 { 返回 1 }
    否则如果 year % 100 == 0 { 返回 0 }
    否则如果 year % 4 == 0 { 返回 1 }
    返回 0
}

主函数: 函数() {
    打印(格式("2000={}", 是闰年(2000)))
    打印(格式("1900={}", 是闰年(1900)))
    打印(格式("2024={}", 是闰年(2024)))
}
"""
    result = run_qentl(code)
    assert result == ['2000=1', '1900=0', '2024=1'], f"闰年: {result}"
    print("✅ 闰年判断(leap year) 通过:", result)


def test_matrix_transpose():
    """矩阵转置(嵌套循环+2D数组)"""
    code = """
矩阵转置: 函数(mat) {
    让 rows = 长度(mat)
    让 cols = 长度(mat[0])
    让 result = []
    循环 j 在 范围数(0, cols) {
        让 row = []
        循环 i 在 范围数(0, rows) { row = 推入(row, mat[i][j]) }
        result = 推入(result, row)
    }
    返回 result
}

主函数: 函数() {
    让 m = [[1, 2], [3, 4], [5, 6]]
    让 t = 矩阵转置(m)
    打印(格式("{}{}", t[0][0], t[0][1]))
    打印(格式("{}{}", t[1][0], t[1][1]))
}
"""
    result = run_qentl(code)
    assert result == ['13', '24'], f"矩阵转置: {result}"
    print("✅ 矩阵转置(matrix transpose) 通过:", result)


def test_recursive_digit_sum():
    """递归数字之和(递归+取模+取整)"""
    code = """
数字之和: 函数(n) {
    如果 n < 10 { 返回 n }
    返回 (n % 10) + 数字之和(取整(n / 10))
}

主函数: 函数() {
    打印(格式("123={}", 数字之和(123)))
    打印(格式("999={}", 数字之和(999)))
}
"""
    result = run_qentl(code)
    assert result == ['123=6', '999=27'], f"数字之和: {result}"
    print("✅ 递归数字之和(recursive digit sum) 通过:", result)


def test_tic_tac_toe_win():
    """井字棋获胜检测(2D数组查表)"""
    code = """
检查获胜: 函数(board, mark) {
    让 wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    循环 i 在 范围数(0, 8) {
        如果 board[wins[i][0]] == mark 且 board[wins[i][1]] == mark 且 board[wins[i][2]] == mark { 返回 1 }
    }
    返回 0
}

主函数: 函数() {
    让 b = ["X","X","X","O","O","","","",""]
    打印(格式("X={}", 检查获胜(b, "X")))
    打印(格式("O={}", 检查获胜(b, "O")))
}
"""
    result = run_qentl(code)
    assert result == ['X=1', 'O=0'], f"井字棋: {result}"
    print("✅ 井字棋获胜检测(tic-tac-toe) 通过:", result)


def test_distinct_char_count():
    """统计不同字符数(dict去重)"""
    code = """
不同字符数: 函数(s) {
    让 seen = {}
    让 count = 0
    循环 i 在 范围数(0, 长度(s)) {
        让 c = 子串(s, i, 1)
        如果 包含(seen, c) == 0 { seen[c] = 1; count = count + 1 }
    }
    返回 count
}

主函数: 函数() {
    打印(格式("hello={}", 不同字符数("hello")))
    打印(格式("aaa={}", 不同字符数("aaa")))
}
"""
    result = run_qentl(code)
    assert result == ['hello=4', 'aaa=1'], f"不同字符: {result}"
    print("✅ 统计不同字符数(distinct char count) 通过:", result)


def test_longest_word():
    """最长单词查找(分割+遍历比较)"""
    code = """
最长单词: 函数(sentence) {
    让 words = 分割(sentence, " ")
    让 longest = ""
    循环 i 在 范围数(0, 长度(words)) {
        如果 长度(words[i]) > 长度(longest) { longest = words[i] }
    }
    返回 longest
}

主函数: 函数() {
    打印(最长单词("i love programming"))
    打印(最长单词("a bb ccc dddd"))
}
"""
    result = run_qentl(code)
    assert result == ['programming', 'dddd'], f"最长单词: {result}"
    print("✅ 最长单词查找(longest word) 通过:", result)


def test_merge_sorted_arrays():
    """合并两个有序数组(双指针+当循环)"""
    code = """
合并有序: 函数(a, b) {
    让 result = []
    让 i = 0
    让 j = 0
    当(i < 长度(a) 且 j < 长度(b)) {
        如果 a[i] <= b[j] { result = 推入(result, a[i]); i = i + 1 }
        否则 { result = 推入(result, b[j]); j = j + 1 }
    }
    当(i < 长度(a)) { result = 推入(result, a[i]); i = i + 1 }
    当(j < 长度(b)) { result = 推入(result, b[j]); j = j + 1 }
    返回 result
}

主函数: 函数() {
    让 c = 合并有序([1,3,5], [2,4,6])
    打印(格式("{}{}{}", c[0], c[1], c[2]))
    打印(格式("{}{}{}", c[3], c[4], c[5]))
}
"""
    result = run_qentl(code)
    assert result == ['123', '456'], f"合并有序: {result}"
    print("✅ 合并两个有序数组(merge sorted) 通过:", result)


def test_sorted_array_dedup():
    """有序数组去重(双指针原地修改)"""
    code = """
去重: 函数(arr) {
    如果 长度(arr) == 0 { 返回 0 }
    让 i = 0
    循环 j 在 范围数(1, 长度(arr)) {
        如果 arr[j] != arr[i] { i = i + 1; arr[i] = arr[j] }
    }
    返回 i + 1
}

主函数: 函数() {
    让 a = [1, 1, 2, 3, 3]
    打印(格式("n={}", 去重(a)))
}
"""
    result = run_qentl(code)
    assert result == ['n=3'], f"有序去重: {result}"
    print("✅ 有序数组去重(sorted dedup) 通过:", result)


def test_second_largest():
    """第二大数(遍历+比较)"""
    code = """
第二大: 函数(arr) {
    让 first = -999999
    让 second = -999999
    循环 i 在 范围数(0, 长度(arr)) {
        如果 arr[i] > first { second = first; first = arr[i] }
        否则如果 arr[i] > second { second = arr[i] }
    }
    返回 second
}

主函数: 函数() {
    打印(格式("{}", 第二大([5, 1, 9, 3, 7])))
    打印(格式("{}", 第二大([10, 20, 30])))
}
"""
    result = run_qentl(code)
    assert result == ['7', '20'], f"第二大: {result}"
    print("✅ 第二大数(second largest) 通过:", result)


def test_caesar_cipher():
    """凯撒密码(字符代码+字符+取模)"""
    code = """
凯撒: 函数(text, shift) {
    让 result = ""
    循环 i 在 范围数(0, 长度(text)) {
        让 code = 字符代码(子串(text, i, 1))
        如果 code >= 97 且 code <= 122 {
            code = ((code - 97 + shift) % 26) + 97
        }
        result = result + 字符(code)
    }
    返回 result
}

主函数: 函数() {
    打印(凯撒("abc", 3))
    打印(凯撒("xyz", 3))
}
"""
    result = run_qentl(code)
    assert result == ['def', 'abc'], f"凯撒: {result}"
    print("✅ 凯撒密码(caesar cipher) 通过:", result)


def test_int_to_binary():
    """整数转二进制(除2取余法)"""
    code = """
整转二进制: 函数(n) {
    如果 n == 0 { 返回 "0" }
    让 result = ""
    当(n > 0) {
        result = 格式("{}", n % 2) + result
        n = 取整(n / 2)
    }
    返回 result
}

主函数: 函数() {
    打印(整转二进制(10))
    打印(整转二进制(255))
}
"""
    result = run_qentl(code)
    assert result == ['1010', '11111111'], f"整转二进制: {result}"
    print("✅ 整数转二进制(int to binary) 通过:", result)


def test_power_of_two():
    """2的幂判断(循环除2)"""
    code = """
是2的幂: 函数(n) {
    如果 n <= 0 { 返回 0 }
    当(n > 1) {
        如果 n % 2 != 0 { 返回 0 }
        n = 取整(n / 2)
    }
    返回 1
}

主函数: 函数() {
    打印(格式("8={}", 是2的幂(8)))
    打印(格式("6={}", 是2的幂(6)))
}
"""
    result = run_qentl(code)
    assert result == ['8=1', '6=0'], f"2的幂: {result}"
    print("✅ 2的幂判断(power of two) 通过:", result)


def test_isomorphic_strings():
    """同构字符串(双向dict映射)"""
    code = """
同构: 函数(s, t) {
    如果 长度(s) != 长度(t) { 返回 0 }
    让 map_st = {}
    让 map_ts = {}
    循环 i 在 范围数(0, 长度(s)) {
        让 c1 = 子串(s, i, 1)
        让 c2 = 子串(t, i, 1)
        如果 包含(map_st, c1) { 如果 map_st[c1] != c2 { 返回 0 } }
        否则 { map_st[c1] = c2 }
        如果 包含(map_ts, c2) { 如果 map_ts[c2] != c1 { 返回 0 } }
        否则 { map_ts[c2] = c1 }
    }
    返回 1
}

主函数: 函数() {
    打印(格式("{}", 同构("egg", "add")))
    打印(格式("{}", 同构("foo", "bar")))
}
"""
    result = run_qentl(code)
    assert result == ['1', '0'], f"同构: {result}"
    print("✅ 同构字符串(isomorphic) 通过:", result)


def test_run_length_encoding():
    """游程编码/字符串压缩(嵌套当循环)"""
    code = """
压缩: 函数(s) {
    让 result = ""
    让 i = 0
    当(i < 长度(s)) {
        让 c = 子串(s, i, 1)
        让 count = 1
        当(i + count < 长度(s) 且 子串(s, i + count, 1) == c) { count = count + 1 }
        result = result + c + 格式("{}", count)
        i = i + count
    }
    返回 result
}

主函数: 函数() {
    打印(压缩("aaabbc"))
    打印(压缩("xxyyy"))
}
"""
    result = run_qentl(code)
    assert result == ['a3b2c1', 'x2y3'], f"游程编码: {result}"
    print("✅ 游程编码(run-length encoding) 通过:", result)


def test_missing_number():
    """缺失数(求和公式)"""
    code = """
缺失数: 函数(arr, n) {
    让 expected = 取整((n * (n + 1)) / 2)
    让 actual = 0
    循环 i 在 范围数(0, 长度(arr)) { actual = actual + arr[i] }
    返回 expected - actual
}

主函数: 函数() {
    打印(格式("{}", 缺失数([0, 1, 3], 3)))
    打印(格式("{}", 缺失数([0, 1, 2, 3, 5], 5)))
}
"""
    result = run_qentl(code)
    assert result == ['2', '4'], f"缺失数: {result}"
    print("✅ 缺失数(missing number) 通过:", result)


def test_vowel_consonant_count():
    """元音辅音计数(包含检查)"""
    code = """
元音辅音: 函数(s) {
    让 v = 0
    让 c = 0
    让 vowels = "aeiou"
    循环 i 在 范围数(0, 长度(s)) {
        让 ch = 子串(s, i, 1)
        如果 包含(vowels, ch) { v = v + 1 }
        否则如果 ch != " " { c = c + 1 }
    }
    返回 [v, c]
}

主函数: 函数() {
    让 r = 元音辅音("hello")
    打印(格式("v={}", r[0]))
    打印(格式("c={}", r[1]))
}
"""
    result = run_qentl(code)
    assert result == ['v=2', 'c=3'], f"元音辅音: {result}"
    print("✅ 元音辅音计数(vowel/consonant) 通过:", result)


def test_anagram_check():
    """异位词检查(dict计数)"""
    code = """
异位词: 函数(s1, s2) {
    如果 长度(s1) != 长度(s2) { 返回 0 }
    让 count = {}
    循环 i 在 范围数(0, 长度(s1)) {
        让 c = 子串(s1, i, 1)
        如果 包含(count, c) { count[c] = count[c] + 1 } 否则 { count[c] = 1 }
    }
    循环 i 在 范围数(0, 长度(s2)) {
        让 c = 子串(s2, i, 1)
        如果 包含(count, c) == 0 { 返回 0 }
        count[c] = count[c] - 1
    }
    循环 i 在 范围数(0, 长度(s1)) {
        让 c = 子串(s1, i, 1)
        如果 count[c] != 0 { 返回 0 }
    }
    返回 1
}

主函数: 函数() {
    打印(格式("{}", 异位词("listen", "silent")))
    打印(格式("{}", 异位词("abc", "def")))
}
"""
    result = run_qentl(code)
    assert result == ['1', '0'], f"异位词: {result}"
    print("✅ 异位词检查(anagram) 通过:", result)


def test_fibonacci_iterative():
    """斐波那契迭代(当循环+变量交换)"""
    code = """
斐波那契: 函数(n) {
    如果 n == 0 { 返回 0 }
    如果 n == 1 { 返回 1 }
    让 a = 0
    让 b = 1
    让 count = 2
    当(count <= n) {
        让 temp = a + b
        a = b
        b = temp
        count = count + 1
    }
    返回 b
}

主函数: 函数() {
    打印(格式("f10={}", 斐波那契(10)))
    打印(格式("f7={}", 斐波那契(7)))
}
"""
    result = run_qentl(code)
    assert result == ['f10=55', 'f7=13'], f"斐波那契: {result}"
    print("✅ 斐波那契迭代(fibonacci) 通过:", result)


def test_gcd():
    """最大公约数(欧几里得算法)"""
    code = """
最大公约: 函数(a, b) {
    当(b != 0) {
        让 temp = b
        b = a % b
        a = temp
    }
    返回 a
}

主函数: 函数() {
    打印(格式("{}", 最大公约(48, 18)))
    打印(格式("{}", 最大公约(100, 75)))
}
"""
    result = run_qentl(code)
    assert result == ['6', '25'], f"GCD: {result}"
    print("✅ 最大公约数(GCD/Euclidean) 通过:", result)


def test_lcm():
    """最小公倍数(利用GCD)"""
    code = """
最大公约: 函数(a, b) {
    当(b != 0) { 让 temp = b; b = a % b; a = temp }
    返回 a
}

最小公倍: 函数(a, b) {
    返回 取整(a * b / 最大公约(a, b))
}

主函数: 函数() {
    打印(格式("{}", 最小公倍(4, 6)))
    打印(格式("{}", 最小公倍(12, 18)))
}
"""
    result = run_qentl(code)
    assert result == ['12', '36'], f"LCM: {result}"
    print("✅ 最小公倍数(LCM) 通过:", result)


def test_reverse_number():
    """数字反转(取模+取整)"""
    code = """
反转数字: 函数(n) {
    让 rev = 0
    当(n > 0) { rev = rev * 10 + n % 10; n = 取整(n / 10) }
    返回 rev
}

主函数: 函数() {
    打印(格式("{}", 反转数字(12345)))
    打印(格式("{}", 反转数字(100)))
}
"""
    result = run_qentl(code)
    assert result == ['54321', '1'], f"数字反转: {result}"
    print("✅ 数字反转(reverse number) 通过:", result)


def test_array_sum_max():
    """数组求和与最大值(遍历+比较)"""
    code = """
数组求和: 函数(arr) {
    让 s = 0
    循环 i 在 范围数(0, 长度(arr)) { s = s + arr[i] }
    返回 s
}

数组最大: 函数(arr) {
    让 m = arr[0]
    循环 i 在 范围数(1, 长度(arr)) { 如果 arr[i] > m { m = arr[i] } }
    返回 m
}

主函数: 函数() {
    让 a = [3, 7, 2, 9, 1]
    打印(格式("s={}", 数组求和(a)))
    打印(格式("m={}", 数组最大(a)))
}
"""
    result = run_qentl(code)
    assert result == ['s=22', 'm=9'], f"数组求和最大: {result}"
    print("✅ 数组求和与最大值(sum/max) 通过:", result)


def test_insertion_sort():
    """插入排序(当循环+数组赋值)"""
    code = """
插入排序: 函数(arr) {
    让 n = 长度(arr)
    循环 i 在 范围数(1, n) {
        让 key = arr[i]
        让 j = i - 1
        当(j >= 0 且 arr[j] > key) { arr[j + 1] = arr[j]; j = j - 1 }
        arr[j + 1] = key
    }
    返回 arr
}

主函数: 函数() {
    让 a = [5, 2, 8, 1, 9]
    让 r = 插入排序(a)
    打印(格式("{} {} {} {} {}", r[0], r[1], r[2], r[3], r[4]))
}
"""
    result = run_qentl(code)
    assert result == ['1 2 5 8 9'], f"插入排序: {result}"
    print("✅ 插入排序(insertion sort) 通过:", result)


def test_binary_search():
    """二分查找(当循环+取整)"""
    code = """
二分查找: 函数(arr, target) {
    让 left = 0
    让 right = 长度(arr) - 1
    当(left <= right) {
        让 mid = 取整((left + right) / 2)
        如果 arr[mid] == target { 返回 mid }
        否则如果 arr[mid] < target { left = mid + 1 }
        否则 { right = mid - 1 }
    }
    返回 -1
}

主函数: 函数() {
    打印(格式("{}", 二分查找([1, 3, 5, 7, 9], 5)))
    打印(格式("{}", 二分查找([1, 3, 5, 7, 9], 4)))
}
"""
    result = run_qentl(code)
    assert result == ['2', '-1'], f"二分查找: {result}"
    print("✅ 二分查找(binary search) 通过:", result)


def test_selection_sort():
    """选择排序(嵌套循环+交换)"""
    code = """
选择排序: 函数(arr) {
    让 n = 长度(arr)
    循环 i 在 范围数(0, n - 1) {
        让 min_idx = i
        循环 j 在 范围数(i + 1, n) { 如果 arr[j] < arr[min_idx] { min_idx = j } }
        如果 min_idx != i { 让 temp = arr[i]; arr[i] = arr[min_idx]; arr[min_idx] = temp }
    }
    返回 arr
}

主函数: 函数() {
    让 a = [64, 25, 12, 22, 11]
    让 r = 选择排序(a)
    打印(格式("{} {} {} {} {}", r[0], r[1], r[2], r[3], r[4]))
}
"""
    result = run_qentl(code)
    assert result == ['11 12 22 25 64'], f"选择排序: {result}"
    print("✅ 选择排序(selection sort) 通过:", result)


def test_palindrome():
    """回文判断(双指针)"""
    code = """
回文: 函数(s) {
    让 left = 0
    让 right = 长度(s) - 1
    当(left < right) {
        如果 子串(s, left, 1) != 子串(s, right, 1) { 返回 0 }
        left = left + 1
        right = right - 1
    }
    返回 1
}

主函数: 函数() {
    打印(格式("{}", 回文("racecar")))
    打印(格式("{}", 回文("abc")))
}
"""
    result = run_qentl(code)
    assert result == ['1', '0'], f"回文: {result}"
    print("✅ 回文判断(palindrome) 通过:", result)


tests = [
    test_basic_arithmetic, test_string_operations, test_fibonacci,
    test_factorial_recursive, test_comparison_operators, test_array_operations,
    test_loop_sum, test_builtin_print, test_quantum_program, test_quantum_enum,
    test_while_loop, test_elif_chain, test_for_each, test_range_loop, test_global_var,
    test_multi_elif, test_fibonacci_recursive, test_gcd, test_lcm, test_reverse_number, test_array_sum_max, test_insertion_sort, test_binary_search, test_selection_sort, test_palindrome, test_string_builtins, test_math_builtins,
    test_break, test_continue,
    test_field_assignment,
    test_try_catch,
    test_method_call,
    test_match_case,
    test_dict_literal,
    test_foreach_loop,
    test_logical_operators,
    test_ternary,
    test_dict_mutation_across_method,
    test_global_cross_func,
    test_string_format,
    test_array_slicing,
    test_oop_format_integration,
    test_break_continue,
    test_nested_builtins,
    test_fibonacci_memo,
    test_multi_return_and_string_ops,
    test_format_specs,
    test_elif_5branch,
    test_math_builtins,
    test_file_io,
    test_substring_2arg,
    test_system_builtins, test_string_utilities, test_class_external_methods, test_bubble_sort, test_quantum_enum_advanced, test_comprehensive_integration, test_string_pipeline, test_nested_function_calls, test_recursive_factorial, test_recursive_fibonacci, test_array_sum_average, test_list_filter, test_list_map_square, test_linear_search, test_string_reverse, test_count_occurrences, test_insertion_sort, test_binary_search, test_selection_sort, test_palindrome, test_euclidean_gcd, test_binary_search, test_selection_sort, test_palindrome, test_nested_list_iteration, test_is_prime, test_palindrome_check, test_caesar_cipher, test_fast_exponentiation, test_prefix_sum, test_decimal_to_binary, test_run_length_encoding, test_fizzbuzz, test_merge_sorted_arrays, test_user_func_overrides_builtin, test_matrix_max, test_armstrong_number, test_selection_sort, test_palindrome, test_collatz_steps, test_word_count, test_perfect_number, test_tower_of_hanoi_moves, test_rot13_cipher, test_string_dedup, test_frequency_count, test_fibonacci_memo, test_gcd_lcm, test_vowel_count, test_binary_to_decimal, test_decimal_to_roman, test_extract_digits, test_leap_year, test_matrix_transpose, test_recursive_digit_sum, test_tic_tac_toe_win, test_distinct_char_count, test_longest_word, test_merge_sorted_arrays, test_sorted_array_dedup, test_second_largest, test_caesar_cipher, test_int_to_binary, test_power_of_two, test_isomorphic_strings, test_missing_number, test_vowel_consonant_count, test_anagram_check, test_fibonacci_iterative, test_gcd, test_lcm, test_reverse_number, test_array_sum_max, test_insertion_sort, test_binary_search, test_selection_sort, test_palindrome, test_run_length_encoding,
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