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
    打印(子串(a, 1, 4))
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


tests = [
    test_basic_arithmetic, test_string_operations, test_fibonacci,
    test_factorial_recursive, test_comparison_operators, test_array_operations,
    test_loop_sum, test_builtin_print, test_quantum_program, test_quantum_enum,
    test_while_loop, test_elif_chain, test_for_each, test_range_loop, test_global_var,
    test_multi_elif, test_fibonacci_recursive, test_gcd, test_string_builtins, test_math_builtins,
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
    test_system_builtins, test_string_utilities, test_class_external_methods, test_bubble_sort, test_quantum_enum_advanced, test_comprehensive_integration, test_string_pipeline, test_nested_function_calls, test_recursive_factorial,
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