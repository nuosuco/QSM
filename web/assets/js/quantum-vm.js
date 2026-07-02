// QSM量子虚拟机模拟器 - Web体验版本
class QuantumVMSimulator {
    constructor() {
        this.vmState = new QuantumVMState();
        this.qbcInterpreter = new QBCInterpreter();
        this.quantumMemory = new QuantumMemory();
        this.registers = new Array(16).fill(0);
        this.instructions = [];
        this.instructionPointer = 0;
        this.output = [];
    }

    // 初始化虚拟机
    initialize() {
        console.log('⚛️ QSM量子虚拟机初始化...');
        this.vmState.reset();
        this.instructions = this.getDefaultInstructions();
        this.quantumMemory.initialize();
    }

    // 加载QBC字节码
    loadBytecode(bytecode) {
        this.instructions = bytecode;
        this.instructionPointer = 0;
        this.vmState.programLoaded = true;
    }

    // 执行指令
    executeStep() {
        if (this.instructionPointer >= this.instructions.length) {
            return { halted: true, reason: "程序执行完毕" };
        }

        const instruction = this.instructions[this.instructionPointer];
        const result = this.qbcInterpreter.execute(instruction, this);

        if (result.halted) {
            return result;
        }

        this.instructionPointer++;
        return { executed: true, instruction: instruction };
    }

    // 运行所有指令
    run() {
        while (this.instructionPointer < this.instructions.length) {
            const result = this.executeStep();
            if (result.halted) {
                break;
            }
        }
        return this.output;
    }

    // 获取虚拟机状态
    getState() {
        return {
            registers: this.registers,
            instructionPointer: this.instructionPointer,
            memorySize: this.quantumMemory.capacity,
            quantumState: this.vmState.entanglementLevel,
            output: this.output.join('\n')
        };
    }

    // 默认指令集（演示用）
    getDefaultInstructions() {
        return [
            { op: 'LOAD', arg: 42, comment: '加载常量42' },
            { op: 'STORE', reg: 0, comment: '存储到寄存器0' },
            { op: 'QENTANGLE', entangle: true, comment: '量子纠缠操作' },
            { op: 'QMEASURE', comment: '量子态测量' },
            { op: 'PRINT', comment: '输出结果' },
            { op: 'HALT', comment: '停止执行' }
        ];
    }
}

// 量子虚拟机状态管理
class QuantumVMState {
    constructor() {
        this.reset();
    }

    reset() {
        this.running = false;
        this.programLoaded = false;
        this.executionTime = 0;
        this.instructionsExecuted = 0;
        this.entanglementLevel = 0;
        this.superpositionStates = [];
        this.collapsionOccurred = false;
    }

    // 创建量子叠加态
    createSuperposition(state1, state2) {
        superpositionStates = [state1, state2];
        this.entanglementLevel = Math.max(this.entanglementLevel, 0.5);
    }

    // 测量量子态（坍缩）
    measure() {
        if (this.superpositionStates.length === 0) {
            return null;
        }

        const probabilities = this.superpositionStates.map(() => 0.5);
        const random = Math.random();
        let cumulative = 0;

        for (let i = 0; i < probabilities.length; i++) {
            cumulative += probabilities[i];
            if (random <= cumulative) {
                this.collapsionOccurred = true;
                const collapsedState = this.superpositionStates[i];
                this.superpositionStates = [];
                return collapsedState;
            }
        }

        return this.superpositionStates[0];
    }
}

// QBC字节码解释器
class QBCInterpreter {
    constructor() {
        this.opcodes = {
            'LOAD': this.loadOp.bind(this),
            'STORE': this.storeOp.bind(this),
            'ADD': this.addOp.bind(this),
            'SUB': this.subOp.bind(this),
            'MUL': this.mulOp.bind(this),
            'DIV': this.divOp.bind(this),
            'QENTANGLE': this.entangleOp.bind(this),
            'QMEASURE': this.measureOp.bind(this),
            'PRINT': this.printOp.bind(this),
            'HALT': this.haltOp.bind(this)
        };
    }

    execute(instruction, vm) {
        const opcode = instruction.op;
        const handler = this.opcodes[opcode];

        if (!handler) {
            return { halted: true, reason: `未知指令: ${opcode}` };
        }

        return handler(instruction, vm);
    }

    loadOp(instruction, vm) {
        vm.registers[0] = instruction.arg || 0;
        vm.vmState.instructionsExecuted++;
    }

    storeOp(instruction, vm) {
        if (instruction.reg !== undefined) {
            vm.registers[instruction.reg] = vm.registers[0];
        }
        vm.vmState.instructionsExecuted++;
    }

    addOp(instruction, vm) {
        vm.registers[0] += vm.registers[instruction.reg || 1] || 0;
        vm.vmState.instructionsExecuted++;
    }

    subOp(instruction, vm) {
        vm.registers[0] -= vm.registers[instruction.reg || 1] || 0;
        vm.vmState.instructionsExecuted++;
    }

    mulOp(instruction, vm) {
        vm.registers[0] *= vm.registers[instruction.reg || 1] || 0;
        vm.vmState.instructionsExecuted++;
    }

    divOp(instruction, vm) {
        const divisor = vm.registers[instruction.reg || 1] || 1;
        vm.registers[0] /= divisor;
        vm.vmState.instructionsExecuted++;
    }

    entangleOp(instruction, vm) {
        if (instruction.entangle) {
            vm.vmState.createSuperposition(
                vm.registers[0],
                instruction.arg || 0
            );
            vm.output.push(`⚛️ 量子纠缠: [${vm.registers[0]} | ${instruction.arg || 0}]`);
        }
        vm.vmState.instructionsExecuted++;
    }

    measureOp(instruction, vm) {
        const result = vm.vmState.measure();
        if (result !== null) {
            vm.registers[0] = result;
            vm.output.push(`📏 量子测量结果: ${result}`);
        } else {
            vm.output.push('📏 无叠加态，直接测量');
        }
        vm.vmState.instructionsExecuted++;
    }

    printOp(instruction, vm) {
        vm.output.push(`📤 输出寄存器0: ${vm.registers[0]}`);
        vm.vmState.instructionsExecuted++;
    }

    haltOp(instruction, vm) {
        return { halted: true, reason: "程序正常停止" };
    }
}

// 量子内存系统
class QuantumMemory {
    constructor() {
        this.capacity = 1024;
        this.cells = new Array(this.capacity).fill(0);
        this.entanglementMap = new Map();
    }

    initialize() {
        console.log('💿 量子内存系统初始化...');
        console.log(`   容量: ${this.capacity} 量子单元`);
    }

    // 量子读取
    readQuantum(address) {
        const value = this.cells[address] || 0;
        const entangled = this.entanglementMap.get(address);

        if (entangled) {
            // 读取纠缠关联的值
            return this.cells[entangled] || 0;
        }

        return value;
    }

    // 量子写入
    writeQuantum(address, value) {
        this.cells[address] = value;

        // 纠缠传播
        for (const [addr, entangledWith] of this.entanglementMap) {
            if (entangledWith === address) {
                this.cells[addr] = value;
            }
        }
    }

    // 建立纠缠
    entangle(addr1, addr2) {
        this.entanglementMap.set(addr1, addr2);
        this.entanglementMap.set(addr2, addr1);
    }

    // 断开纠缠
    disentangle(addr1, addr2) {
        this.entanglementMap.delete(addr1);
        this.entanglementMap.delete(addr2);
    }
}

// 导出
if (typeof window !== 'undefined') {
    window.QuantumVMSimulator = QuantumVMSimulator;
    window.QuantumVMState = QuantumVMState;
    window.QBCInterpreter = QBCInterpreter;
    window.QuantumMemory = QuantumMemory;
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        QuantumVMSimulator,
        QuantumVMState,
        QBCInterpreter,
        QuantumMemory
    };
}
