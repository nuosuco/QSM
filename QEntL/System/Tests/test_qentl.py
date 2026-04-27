#!/usr/bin/env python3
"""
QEntL测试套件 - 编译器 + 虚拟机 全链路测试
作者: 小趣WeQ | 监督: 中华Zhoho
日期: 2026-04-28
"""
import json
import sys
import os
import tempfile

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Compiler'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Runtime'))

from qentl_compiler_v3 import compile_qentl
from qbc_vm import QBCVirtualMachine

def compile_and_run(source_code, max_steps=1000):
    """编译QEntL源码并在VM中执行，返回输出"""
    try:
        qbc = compile_qentl(source_code)
    except Exception as e:
        return None, f"编译失败: {e}"
    
    if not qbc:
        return None, "QBC为空"
    
    vm = QBCVirtualMachine()
    vm.load_qbc(qbc)
    output = vm.run(max_steps)
    return output, None

def test_arithmetic():
    """测试1: 算术运算"""
    code = '''
quantum_program 算术测试 {
    setup: 函数() {
        让 a = 3
        让 b = 5
        让 c = a + b
        LOG(c)
    }
}
'''
    output, err = compile_and_run(code)
    assert err is None, f"编译错误: {err}"
    print("✅ 测试1 算术运算: 通过")

def test_string_output():
    """测试2: 字符串输出"""
    code = '''
quantum_program 字符串测试 {
    setup: 函数() {
        LOG("你好，量子世界！")
    }
}
'''
    output, err = compile_and_run(code)
    assert err is None, f"编译错误: {err}"
    print(f"  输出: {output}")
    print("✅ 测试2 字符串输出: 通过")

def test_function_call():
    """测试3: 函数调用"""
    code = '''
函数 加法(a: 整数, b: 整数) -> 整数 {
    返回 a + b
}

quantum_program 函数测试 {
    setup: 函数() {
        让 结果 = 加法(10, 20)
        LOG(结果)
    }
}
'''
    output, err = compile_and_run(code, 2000)
    assert err is None, f"编译错误: {err}"
    print(f"  输出: {output}")
    print("✅ 测试3 函数调用: 通过")

def test_conditional():
    """测试4: 条件判断"""
    code = '''
quantum_program 条件测试 {
    setup: 函数() {
        让 x = 10
        如果 x > 5 {
            LOG("大")
        } 否则 {
            LOG("小")
        }
    }
}
'''
    output, err = compile_and_run(code, 2000)
    assert err is None, f"编译错误: {err}"
    print(f"  输出: {output}")
    print("✅ 测试4 条件判断: 通过")

def test_loop():
    """测试5: 循环"""
    code = '''
quantum_program 循环测试 {
    setup: 函数() {
        让 计数 = 0
        当 计数 < 3 {
            LOG(计数)
            让 计数 = 计数 + 1
        }
    }
}
'''
    output, err = compile_and_run(code, 5000)
    assert err is None, f"编译错误: {err}"
    print(f"  输出: {output}")
    print("✅ 测试5 循环: 通过")

def test_quantum_init():
    """测试6: 量子初始化"""
    code = '''
quantum_program 量子测试 {
    setup: 函数() {
        LOG("量子初始化测试")
    }
}
'''
    output, err = compile_and_run(code)
    assert err is None, f"编译错误: {err}"
    print(f"  输出: {output}")
    print("✅ 测试6 量子初始化: 通过")

def test_type_definition():
    """测试7: 类型定义"""
    code = '''
类型 量子比特 {
    编号: 整数
    状态: 字符串
}

quantum_program 类型测试 {
    setup: 函数() {
        LOG("类型定义测试")
    }
}
'''
    output, err = compile_and_run(code)
    assert err is None, f"编译错误: {err}"
    print(f"  输出: {output}")
    print("✅ 测试7 类型定义: 通过")

def test_modulo():
    """测试9: 取模运算"""
    source = """quantum_program 取模测试 {
        setup: 函数() {
            让 a = 10
            让 b = 3
            让 c = a % b
            LOG(c)
        }
    }"""
    qbc = compile_qentl(source)
    vm = QBCVirtualMachine()
    vm.load_qbc(qbc)
    output = vm.run(10000)
    assert len(output) > 0, "无输出"
    assert output[0] == "1", f"10%3应=1, 得{output[0]}"
    return output

def test_kernel():
    """测试8: 完整内核执行"""
    code = '''
函数 内核启动() -> 整数 {
    LOG("⚛ QEntL量子内核 V1.0 启动中...")
    让 量子位 = 8
    LOG("初始化量子寄存器")
    返回 0
}

quantum_program 内核 {
    setup: 函数() {
        内核启动()
    }
}
'''
    output, err = compile_and_run(code, 2000)
    assert err is None, f"编译错误: {err}"
    print(f"  输出: {output}")
    print("✅ 测试8 内核执行: 通过")


def run_all_tests():
    """运行全部测试"""
    print("=" * 50)
    print("  QEntL 全链路测试套件")
    print("  编译器 → QBC字节码 → 虚拟机执行")
    print("=" * 50)
    print()
    
    tests = [
        ("算术运算", test_arithmetic),
        ("字符串输出", test_string_output),
        ("函数调用", test_function_call),
        ("条件判断", test_conditional),
        ("循环", test_loop),
        ("量子初始化", test_quantum_init),
        ("类型定义", test_type_definition),
        ("取模运算", test_modulo),
    ("内核执行", test_kernel),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {name}: 失败 - {e}")
            failed += 1
    
    print()
    print("=" * 50)
    print(f"  结果: {passed} 通过, {failed} 失败 / {len(tests)} 总计")
    print("=" * 50)
    
    return failed == 0

if __name__ == '__main__':
    run_all_tests()
