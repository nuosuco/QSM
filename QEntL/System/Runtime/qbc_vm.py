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
    

    # === Quantum State Simulation (Real Quantum Mechanics) ===
    def _init_quantum_state(self, n_bits: int):
        """Initialize quantum state as |0...0⟩ using complex vectors"""
        import math
        self.quantum_bits = n_bits
        dim = 2 ** n_bits
        # |0...0⟩ state: first basis vector
        self.quantum_register = [0.0+0.0j] * dim
        self.quantum_register[0] = 1.0+0.0j
    
    def _apply_hadamard(self, target: int):
        """Apply Hadamard gate to target qubit"""
        import math
        sqrt2 = 1.0 / math.sqrt(2)
        dim = 2 ** self.quantum_bits
        new_state = [0.0+0.0j] * dim
        
        for i in range(dim):
            # Get bit value at target position
            bit = (i >> target) & 1
            # Partner index (flipped target bit)
            partner = i ^ (1 << target)
            
            if bit == 0:
                new_state[i] = sqrt2 * (self.quantum_register[i] + self.quantum_register[partner])
            else:
                new_state[i] = sqrt2 * (self.quantum_register[i] - self.quantum_register[partner])
        
        self.quantum_register = new_state
    
    def _apply_cnot(self, control: int, target: int):
        """Apply CNOT gate: flip target if control is |1⟩"""
        dim = 2 ** self.quantum_bits
        new_state = [0.0+0.0j] * dim
        
        for i in range(dim):
            control_bit = (i >> control) & 1
            if control_bit == 1:
                # Flip target bit
                partner = i ^ (1 << target)
                new_state[partner] = self.quantum_register[i]
            else:
                new_state[i] = self.quantum_register[i]
        
        self.quantum_register = new_state
    
    def _apply_pauli_x(self, target: int):
        """Apply Pauli-X (NOT) gate"""
        dim = 2 ** self.quantum_bits
        new_state = [0.0+0.0j] * dim
        
        for i in range(dim):
            partner = i ^ (1 << target)
            new_state[partner] = self.quantum_register[i]
        
        self.quantum_register = new_state
    
    def _measure_qubit(self, target: int) -> int:
        """Measure a single qubit with probabilistic outcome"""
        import random
        dim = 2 ** self.quantum_bits
        
        # Calculate probability of measuring |1⟩
        prob_one = 0.0
        for i in range(dim):
            if (i >> target) & 1:
                prob_one += abs(self.quantum_register[i]) ** 2
        
        # Probabilistic measurement
        result = 1 if random.random() < prob_one else 0
        
        # Collapse state
        new_state = [0.0+0.0j] * dim
        norm = 0.0
        for i in range(dim):
            if ((i >> target) & 1) == result:
                new_state[i] = self.quantum_register[i]
                norm += abs(self.quantum_register[i]) ** 2
        
        # Normalize
        if norm > 0:
            import math
            factor = 1.0 / math.sqrt(norm)
            for i in range(dim):
                new_state[i] *= factor
        
        self.quantum_register = new_state
        return result
    
    def _get_state_info(self) -> str:
        """Get quantum state information string"""
        dim = 2 ** self.quantum_bits
        non_zero = [(i, self.quantum_register[i]) for i in range(dim) 
                     if abs(self.quantum_register[i]) > 1e-10]
        if len(non_zero) <= 4:
            parts = []
            for idx, amp in non_zero:
                bits = format(idx, f'0{self.quantum_bits}b')
                parts.append(f"{amp:.3f}|{bits}⟩")
            return " + ".join(parts)
        return f"{len(non_zero)} non-zero amplitudes"

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
        
        # Auto-detect main entry point
        if self.ip == 0:
            # Priority 1: If 'setup' function exists, call it
            if 'setup' in self.functions:
                # Find QUANTUM_INIT before setup and start there
                # The setup function will be called via CALL at its entry
                # Look for the first QUANTUM_INIT
                for i, instr in enumerate(self.instructions):
                    if instr.get('op') == 'QUANTUM_INIT':
                        self.ip = i
                        break
                else:
                    self.ip = self.functions['setup']
            else:
                # No setup - find QUANTUM_INIT or start at beginning
                for i, instr in enumerate(self.instructions):
                    if instr.get('op') == 'QUANTUM_INIT':
                        self.ip = i
                        break
                else:
                    self.ip = 0
        
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
            n_qubits = operand if operand else 2
            self._init_quantum_state(n_qubits)
            self.ip += 1

        elif op == OpCode.QUANTUM_GATE:
            # operand is dict-like or string describing the gate
            if operand and isinstance(operand, str):
                gate_info = operand.split()
                gate_name = gate_info[0]
                target = int(gate_info[1]) if len(gate_info) > 1 else 0
                if gate_name == 'H':
                    self._apply_hadamard(target)
                elif gate_name == 'X' or gate_name == 'NOT':
                    self._apply_pauli_x(target)
                elif gate_name == 'CNOT':
                    control = target
                    target2 = int(gate_info[2]) if len(gate_info) > 2 else (target + 1)
                    self._apply_cnot(control, target2)
                else:
                    self._apply_hadamard(target)  # default to H
            self.ip += 1

        elif op == OpCode.QUANTUM_MEASURE:
            target = operand if isinstance(operand, int) else 0
            if self.quantum_bits > 0:
                result = self._measure_qubit(target)
                self.stack.append(result)
                state_info = self._get_state_info()
                msg = f"测量比特{target}: {result} (状态: {state_info})"
                self.output.append(msg)
                print(msg)
            else:
                self.stack.append(0)
            self.ip += 1
        elif op == OpCode.QUANTUM_ENTANGLE:
            if self.quantum_bits >= 2:
                if isinstance(operand, str) and operand:
                    parts = operand.split()
                    control = int(parts[0]) if parts else 0
                    target = int(parts[1]) if len(parts) > 1 else 1
                else:
                    control = 0
                    target = 1
                self._apply_hadamard(control)
                self._apply_cnot(control, target)
                msg = f"创建纠缠对: 比特{control} ↔ 比特{target}"
                self.output.append(msg)
                print(msg)
            self.ip += 1
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
