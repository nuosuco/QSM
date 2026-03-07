#!/usr/bin/env python3
"""
QEntL编译器错误处理模块
提供详细的错误信息和位置定位
"""

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class CompileError:
    """编译错误"""
    message: str
    line: int
    column: int
    source_line: str = ""
    error_type: str = "Error"
    suggestion: str = ""
    
    def __str__(self):
        result = f"\n{self.error_type} (行 {self.line}, 列 {self.column}): {self.message}"
        if self.source_line:
            result += f"\n  {self.source_line}"
            result += f"\n  {' ' * (self.column - 1)}^"
        if self.suggestion:
            result += f"\n  建议: {self.suggestion}"
        return result

class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.lines = source_code.split('\n')
        self.errors: List[CompileError] = []
    
    def error(self, message: str, line: int, column: int, 
              error_type: str = "Error", suggestion: str = ""):
        """记录错误"""
        source_line = self.lines[line - 1] if 0 < line <= len(self.lines) else ""
        err = CompileError(
            message=message,
            line=line,
            column=column,
            source_line=source_line,
            error_type=error_type,
            suggestion=suggestion
        )
        self.errors.append(err)
        return err
    
    def syntax_error(self, message: str, line: int, column: int, suggestion: str = ""):
        """语法错误"""
        return self.error(message, line, column, "语法错误", suggestion)
    
    def type_error(self, message: str, line: int, column: int, suggestion: str = ""):
        """类型错误"""
        return self.error(message, line, column, "类型错误", suggestion)
    
    def undefined_error(self, name: str, line: int, column: int):
        """未定义错误"""
        return self.error(
            f"未定义: '{name}'",
            line, column, 
            "未定义错误",
            f"确保 '{name}' 已声明或导入"
        )
    
    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[CompileError]:
        """获取所有错误"""
        return self.errors
    
    def print_errors(self):
        """打印所有错误"""
        for err in self.errors:
            print(err)


def test_error_handler():
    """测试错误处理器"""
    source = '''
配置 {
    版本: "1.0.0"
}

函数 测试( {
    返回 "测试"
}
'''
    
    handler = ErrorHandler(source)
    
    # 模拟错误
    handler.syntax_error("缺少右括号 ')'", 6, 10, "在函数参数后添加 ')'")
    handler.undefined_error("未定义的变量", 7, 5)
    
    print("编译错误检测测试:")
    handler.print_errors()
    
    print(f"\n总错误数: {len(handler.errors)}")
    return handler.has_errors()


if __name__ == "__main__":
    test_error_handler()
