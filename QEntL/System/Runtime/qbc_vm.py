#!/usr/bin/env python3
"""
QBC虚拟机 V1 - 执行QBC字节码
支持：算术/比较/控制流/量子操作/对象/I/O
"""

import json
import sys
from enum import Enum
from typing import Dict, List, Any, Optional

class OpCode(Enum):
    NOP = 0x00; HALT = 0x01
    LOAD_CONST = 0x10; LOAD_VAR = 0x11; STORE_VAR = 0x12; LOAD_FIELD = 0x13; STORE_FIELD = 0x14
    ADD = 0x20; SUB = 0x21; MUL = 0x22; DIV = 0x23; MOD = 0x24
    EQ = 0x30; NEQ = 0x31; LT = 0x32; GT = 0x33; LTE = 0x34; GTE = 0x35
    JUMP = 0x40; JUMP_IF_FALSE = 0x41; JUMP_IF_TRUE = 0x42; CALL = 0x43; RETURN = 0x44
    LOOP_START = 0x45; LOOP_END = 0x46
    QUANTUM_INIT = 0x50; QUANTUM_GATE = 0x51; QUANTUM_MEASURE = 0x52; QUANTUM_ENTANGLE = 0x53
    LOG = 0x60; INPUT = 0x61
    TYPE_DEF = 0x70; TYPE_CAST = 0x71
    OBJ_CREATE = 0x80; OBJ_GET = 0x81; OBJ_SET = 0x82

# Op name to enum mapping
OP_MAP = {op.name: op for op in OpCode}

class QBCVirtualMachine:
    """量子字节码虚拟机"""
    
    def __init__(self):
        self.constants: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.stack: List[Any] = []
        self.call_stack: List[tuple] = []  # (ip, variables_snapshot)
        self.functions: Dict[str, int] = {}
        self.instructions: List[Dict] = []
        self.ip: int = 0  # instruction pointer
        self.running: bool = False
        self.output: List[str] = []  # captured log output
        
        # Quantum state simulation
        self.quantum_register: List[complex] = []
        self.quantum_bits: int = 0
    
    def load_qbc(self, qbc: Dict):
        """加载QBC字节码程序"""
        self.constants = qbc.get('constants', [])
        self.functions = qbc.get('functions', {})
        self.instructions = qbc.get('instructions', [])
        # Initialize variables
        for var_name in qbc.get('variables', []):
            self.variables[var_name] = None
        self.ip = 0
        self.running = False
        self.stack = []
        self.output = []
    
    def load_file(self, path: str):
        """从文件加载QBC程序"""
        with open(path, 'r', encoding='utf-8') as f:
            qbc = json.load(f)
        self.load_qbc(qbc)
    
    def run(self, max_steps: int = 100000) -> List[str]:
        """执行QBC程序"""
        self.running = True
        steps = 0
        
        # Auto-detect main entry point: find QUANTUM_INIT or first non-function code
        if self.ip == 0:
            # Find main program start (after all function definitions)
            max_func_ip = max(self.functions.values()) if self.functions else 0
            # Find the next instruction after all function code
            for i in range(max_func_ip, len(self.instructions)):
                instr = self.instructions[i]
                if instr.get('op') in ('QUANTUM_INIT', 'NOP') and i > max_func_ip:
                    self.ip = i
                    break
            else:
                self.ip = max_func_ip
        
        while self.running and self.ip < len(self.instructions) and steps < max_steps:
            instr = self.instructions[self.ip]
            op_name = instr.get('op', 'NOP')
            operand = instr.get('operand')
            
            # Handle labels (skip)
            if op_name == 'LABEL':
                self.ip += 1
                steps += 1
                continue
            
            op = OP_MAP.get(op_name)
            if op is None:
                self.ip += 1
                steps += 1
                continue
            
            self._execute(op, operand)
            steps += 1
        
        return self.output
    
    def _execute(self, op: OpCode, operand):
        """执行单条指令"""
        
        if op == OpCode.NOP:
            self.ip += 1
        
        elif op == OpCode.HALT:
            self.running = False
        
        elif op == OpCode.LOAD_CONST:
            val = self.constants[operand] if operand < len(self.constants) else None
            self.stack.append(val)
            self.ip += 1
        
        elif op == OpCode.LOAD_VAR:
            val = self.variables.get(operand)
            self.stack.append(val)
            self.ip += 1
        
        elif op == OpCode.STORE_VAR:
            if self.stack:
                self.variables[operand] = self.stack.pop()
            self.ip += 1
        
        elif op == OpCode.LOAD_FIELD:
            if len(self.stack) >= 1:
                obj = self.stack.pop()
                if isinstance(obj, dict):
                    self.stack.append(obj.get(operand))
                else:
                    self.stack.append(None)
            self.ip += 1
        
        elif op in (OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD):
            if len(self.stack) >= 2:
                b = self.stack.pop()
                a = self.stack.pop()
                try:
                    if op == OpCode.ADD: result = a + b
                    elif op == OpCode.SUB: result = a - b
                    elif op == OpCode.MUL: result = a * b
                    elif op == OpCode.DIV: result = a / b if b != 0 else 0
                    elif op == OpCode.MOD: result = a % b if b != 0 else 0
                    else: result = 0
                    self.stack.append(result)
                except (TypeError, ValueError):
                    # String concatenation for ADD
                    if op == OpCode.ADD:
                        self.stack.append(str(a) + str(b))
                    else:
                        self.stack.append(0)
            self.ip += 1
        
        elif op in (OpCode.EQ, OpCode.NEQ, OpCode.LT, OpCode.GT, OpCode.LTE, OpCode.GTE):
            if len(self.stack) >= 2:
                b = self.stack.pop()
                a = self.stack.pop()
                try:
                    if op == OpCode.EQ: result = a == b
                    elif op == OpCode.NEQ: result = a != b
                    elif op == OpCode.LT: result = a < b
                    elif op == OpCode.GT: result = a > b
                    elif op == OpCode.LTE: result = a <= b
                    elif op == OpCode.GTE: result = a >= b
                    else: result = False
                    self.stack.append(result)
                except (TypeError, ValueError):
                    self.stack.append(False)
            self.ip += 1
        
        elif op == OpCode.JUMP:
            # Find label
            label = operand
            target = self._find_label(label)
            if target is not None:
                self.ip = target
            else:
                self.ip += 1
        
        elif op == OpCode.JUMP_IF_FALSE:
            if self.stack:
                cond = self.stack.pop()
                if not cond:
                    label = operand
                    target = self._find_label(label)
                    if target is not None:
                        self.ip = target
                        return
            self.ip += 1
        
        elif op == OpCode.JUMP_IF_TRUE:
            if self.stack:
                cond = self.stack.pop()
                if cond:
                    label = operand
                    target = self._find_label(label)
                    if target is not None:
                        self.ip = target
                        return
            self.ip += 1
        
        elif op == OpCode.CALL:
            # Call function
            func_name = operand
            if func_name in self.functions:
                # Save return point and current variables
                self.call_stack.append((self.ip + 1, dict(self.variables)))
                # Pop arguments from stack and bind to function parameter variables
                # The function's variables list defines parameter names
                # We need to find how many params the function has
                func_entry = self.functions[func_name]
                # Count LOAD_VAR instructions before first non-param instruction
                param_names = []
                for i in range(func_entry, min(func_entry + 10, len(self.instructions))):
                    instr = self.instructions[i]
                    if instr.get('op') == 'LOAD_VAR':
                        pname = instr.get('operand', '')
                        if pname and pname not in param_names:
                            param_names.append(pname)
                    elif instr.get('op') in ('ADD', 'SUB', 'MUL', 'DIV', 'RETURN', 'EQ'):
                        break
                # Bind arguments in reverse order (stack is LIFO)
                for pname in reversed(param_names):
                    if self.stack:
                        self.variables[pname] = self.stack.pop()
                    else:
                        self.variables[pname] = None
                self.ip = self.functions[func_name]
            else:
                # Built-in functions
                if func_name in ('LOG', 'log', '日志', 'print'):
                    if self.stack:
                        val = self.stack.pop()
                        msg = str(val) if val is not None else 'None'
                        self.output.append(msg)
                        print(msg)
                    self.stack.append(None)
                elif func_name in ('问候', 'greet', '你好'):
                    if self.stack:
                        arg = self.stack.pop()
                        self.stack.append(f"你好，{arg}！")
                elif func_name in ('加法', 'add'):
                    if len(self.stack) >= 2:
                        b = self.stack.pop()
                        a = self.stack.pop()
                        try:
                            self.stack.append(a + b)
                        except:
                            self.stack.append(0)
                elif func_name in ('长度', 'len', 'length'):
                    if self.stack:
                        val = self.stack.pop()
                        self.stack.append(len(str(val)) if val else 0)
                    else:
                        self.stack.append(0)
                elif func_name in ('随机数', 'random', 'rand'):
                    import random as _r
                    self.stack.append(_r.randint(0, 100))
                elif func_name in ('类型', 'type'):
                    if self.stack:
                        val = self.stack.pop()
                        self.stack.append(type(val).__name__)
                    else:
                        self.stack.append('None')
                else:
                    # Unknown built-in, pop args and push None
                    if self.stack:
                        self.stack.pop()
                    self.stack.append(None)
                self.ip += 1
        
        elif op == OpCode.RETURN:
            if self.call_stack:
                ret_ip, saved_vars = self.call_stack.pop()
                ret_val = self.stack[-1] if self.stack else None
                self.variables = saved_vars
                if ret_val is not None:
                    self.stack.append(ret_val)
                self.ip = ret_ip
            else:
                self.running = False
        
        elif op == OpCode.LOOP_START:
            # operand is loop variable name
            self.ip += 1
        
        elif op == OpCode.LOOP_END:
            # operand is label to jump back
            self.ip += 1  # simplified: just continue
        
        elif op == OpCode.QUANTUM_INIT:
            n_qubits = operand if operand else 1
            self.quantum_bits = n_qubits
            # Initialize |0⟩ state
            self.quantum_register = [complex(0)] * (2 ** n_qubits)
            self.quantum_register[0] = complex(1)  # |000...0⟩
            self.ip += 1
        
        elif op == OpCode.QUANTUM_GATE:
            self.ip += 1  # placeholder
        
        elif op == OpCode.QUANTUM_MEASURE:
            # Simulate measurement
            import random
            if self.quantum_register:
                probs = [abs(x)**2 for x in self.quantum_register]
                total = sum(probs)
                if total > 0:
                    probs = [p/total for p in probs]
                    r = random.random()
                    cumulative = 0
                    for i, p in enumerate(probs):
                        cumulative += p
                        if r <= cumulative:
                            self.stack.append(i)
                            break
            self.ip += 1
        
        elif op == OpCode.QUANTUM_ENTANGLE:
            self.ip += 1  # placeholder
        
        elif op == OpCode.LOG:
            if self.stack:
                val = self.stack.pop()
                msg = str(val)
                self.output.append(msg)
                print(msg)
            self.ip += 1
        
        elif op == OpCode.INPUT:
            # For VM, just push empty string
            self.stack.append("")
            self.ip += 1
        
        elif op == OpCode.TYPE_DEF:
            self.ip += 1
        
        elif op == OpCode.TYPE_CAST:
            self.ip += 1
        
        elif op == OpCode.OBJ_CREATE:
            self.stack.append({})
            self.ip += 1
        
        elif op == OpCode.OBJ_GET:
            self.ip += 1
        
        elif op == OpCode.OBJ_SET:
            self.ip += 1
        
        else:
            self.ip += 1
    
    def _find_label(self, label_name: str) -> Optional[int]:
        """Find instruction index for a label"""
        for i, instr in enumerate(self.instructions):
            if instr.get('op') == 'LABEL' and instr.get('name') == label_name:
                return i + 1  # return instruction after label
        return None


def run_qbc_file(path: str, max_steps: int = 100000) -> List[str]:
    """运行QBC文件"""
    vm = QBCVirtualMachine()
    vm.load_file(path)
    return vm.run(max_steps)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 qbc_vm.py <input.qbc> [max_steps]")
        sys.exit(1)
    
    qbc_file = sys.argv[1]
    max_steps = int(sys.argv[2]) if len(sys.argv) > 2 else 100000
    
    output = run_qbc_file(qbc_file, max_steps)
    if output:
        print("\n=== 输出 ===")
        for line in output:
            print(f"  {line}")
