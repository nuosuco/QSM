/**
 * QSM - QEntL量子虚拟机Web模拟器
 * 版本: v0.2.0-alpha
 * 量子基因编码: QGC-QVM-SIMULATOR-20260214
 * 
 * 用户可以在浏览器中体验量子计算和QBC字节码运行
 */

class QVMSimulator {
    constructor() {
        this.quantumBits = new Map();  // 量子比特状态
        this.quantumRegisters = new Map();  // 量子寄存器
        this.qbcInstructions = [];  // QBC字节码指令集
        this.executionState = 'idle';  // idle, running, paused, stopped
        this.executionHistory = [];  // 执行历史
        this.entanglementNetwork = new Map();  // 纠缠网络
        
        this.initQuantumSystem();
    }

    // 初始化量子系统
    initQuantumSystem() {
        console.log('正在初始化QEntL量子虚拟机...');
        
        // 创建默认量子比特
        for (let i = 0; i < 8; i++) {
            this.createQuantumBit(`q${i}`);
        }
        
        // 创建量子寄存器
        for (let i = 0; i < 4; i++) {
            this.createQuantumRegister(`reg${i}`);
        }
        
        console.log('量子虚拟机初始化完成，8个量子比特已就绪！');
    }

    // 创建量子比特
    createQuantumBit(name) {
        this.quantumBits.set(name, {
            name: name,
            state: '|0⟩',  // 初始状态|0⟩
            amplitude: { alpha: 1, beta: 0 },  // 狄拉克符号 α|0⟩ + β|1⟩
            entangled: [],
            measured: false
        });
    }

    // 创建量子寄存器
    createQuantumRegister(name) {
        this.quantumRegisters.set(name, {
            name: name,
            bits: [],
            capacity: 8
        });
    }

    // 量子NOT门（X门）
    quantumNOT(qubitName) {
        const qubit = this.quantumBits.get(qubitName);
        if (!qubit) return { success: false, error: '量子比特不存在' };
        
        // X门变换: |0⟩ ↔ |1⟩
        const temp = qubit.amplitude.alpha;
        qubit.amplitude.alpha = qubit.amplitude.beta;
        qubit.amplitude.beta = temp;
        
        qubit.state = qubit.state === '|0⟩' ? '|1⟩' : '|0⟩';
        
        this.addToHistory(`X门应用于 ${qubitName}: ${qubit.state}`);
        return { success: true, result: qubit.state };
    }

    // Z门（相位翻转门）
    quantumZ(qubitName) {
        const qubit = this.quantumBits.get(qubitName);
        if (!qubit) return { success: false, error: '量子比特不存在' };
        qubit.amplitude.beta = -qubit.amplitude.beta;
        this.addToHistory(`Z门应用于 ${qubitName}: 相位翻转`);
        return { success: true, result: '相位翻转' };
    }

    // Y门（泡利Y门）
    quantumY(qubitName) {
        const qubit = this.quantumBits.get(qubitName);
        if (!qubit) return { success: false, error: '量子比特不存在' };
        const alpha = qubit.amplitude.alpha;
        const beta = qubit.amplitude.beta;
        qubit.amplitude.alpha = -beta;
        qubit.amplitude.beta = alpha;
        this.addToHistory(`Y门应用于 ${qubitName}`);
        return { success: true, result: 'Y变换' };
    }

    // S门（相位门π/2）
    quantumS(qubitName) {
        const qubit = this.quantumBits.get(qubitName);
        if (!qubit) return { success: false, error: '量子比特不存在' };
        qubit.phase = (qubit.phase || 0) + Math.PI / 2;
        this.addToHistory(`S门应用于 ${qubitName}: 相位π/2`);
        return { success: true, result: '相位π/2' };
    }

    // T门（相位门π/4）
    quantumT(qubitName) {
        const qubit = this.quantumBits.get(qubitName);
        if (!qubit) return { success: false, error: '量子比特不存在' };
        qubit.phase = (qubit.phase || 0) + Math.PI / 4;
        this.addToHistory(`T门应用于 ${qubitName}: 相位π/4`);
        return { success: true, result: '相位π/4' };
    }

    // SWAP门
    quantumSWAP(q1Name, q2Name) {
        const q1 = this.quantumBits.get(q1Name);
        const q2 = this.quantumBits.get(q2Name);
        if (!q1 || !q2) return { success: false, error: '量子比特不存在' };
        const tempA = q1.amplitude.alpha, tempB = q1.amplitude.beta;
        q1.amplitude.alpha = q2.amplitude.alpha;
        q1.amplitude.beta = q2.amplitude.beta;
        q2.amplitude.alpha = tempA;
        q2.amplitude.beta = tempB;
        this.addToHistory(`SWAP: ${q1Name} ↔ ${q2Name}`);
        return { success: true, result: '交换完成' };
    }

    // Hadamard门（H门）- 创建叠加态
    quantumH(qubitName) {
        const qubit = this.quantumBits.get(qubitName);
        if (!qubit) return { success: false, error: '量子比特不存在' };
        
        // H门变换: (|0⟩ + |1⟩) / √2
        qubit.amplitude.alpha = 1 / Math.sqrt(2);
        qubit.amplitude.beta = 1 / Math.sqrt(2);
        
        qubit.state = '(|0⟩ + |1⟩) / √2';
        
        this.addToHistory(`H门应用于 ${qubitName}: 创建叠加态`);
        return { success: true, result: '叠加态' };
    }

    // 量子纠缠操作（CNOT门）
    quantumCNOT(control, target) {
        const qcontrol = this.quantumBits.get(control);
        const qtarget = this.quantumBits.get(target);
        
        if (!qcontrol || !qtarget) {
            return { success: false, error: '量子比特不存在' };
        }
        
        // 创建纠缠
        if (qcontrol.state === '|1⟩' || qcontrol.state.includes('|1⟩')) {
            qtarget.amplitude.beta = qtarget.amplitude.alpha;
            qtarget.amplitude.alpha = 0;
            qtarget.state = '|1⟩';
        }
        
        // 建立纠缠关系
        qcontrol.entangled.push(target);
        qtarget.entangled.push(control);
        
        this.entanglementNetwork.set(`${control}-${target}`, {
            pair: [control, target],
            created: Date.now()
        });
        
        this.addToHistory(`CNOT建立纠缠: ${control} ⊗ ${target}`);
        return { success: true, result: '纠缠态' };
    }

    // 量子测量
    quantumMeasure(qubitName) {
        const qubit = this.quantumBits.get(qubitName);
        if (!qubit) return { success: false, error: '量子比特不存在' };
        
        // 波函数坍缩测量
        const probability = Math.random();
        const result = probability < Math.abs(qubit.amplitude.alpha) ** 2 ? '0' : '1';
        
        qubit.measured = true;
        qubit.state = `|${result}⟩`;
        qubit.amplitude = result === '0' ? { alpha: 1, beta: 0 } : { alpha: 0, beta: 1 };
        
        // 测量会导致纠缠坍缩
        qubit.entangled.forEach(async paired => {
            await this.quantumMeasure(paired);
        });
        
        this.addToHistory(`测量 ${qubitName}: 结果 = ${result}`);
        return { success: true, result: result };
    }

    // 加载QBC字节码
    loadQBC(qbcCode) {
        try {
            // 解析简单的QBC字节码格式
            const lines = qbcCode.split('\n').filter(line => line.trim() && !line.startsWith('#'));
            this.qbcInstructions = lines.map(line => ({
                instruction: line.trim(),
                timestamp: Date.now()
            }));
            
            return {
                success: true,
                count: this.qbcInstructions.length,
                message: `成功加载 ${this.qbcInstructions.length} 条指令`
            };
        } catch (error) {
            return { success: false, error: error.message };
        }
    }

    // 运行QBC字节码
    async runQBC() {
        if (this.executionState === 'running') {
            return { success: false, error: '已经在运行中' };
        }
        
        this.executionState = 'running';
        this.addToHistory('开始执行QBC字节码...');
        
        try {
            for (let code of this.qbcInstructions) {
                const result = await this.executeInstruction(code.instruction);
                if (!result.success) {
                    this.executionState = 'stopped';
                    return result;
                }
                
                // 模拟量子执行延迟
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            this.executionState = 'idle';
            this.addToHistory('QBC字节码执行完成');
            return { success: true, message: '执行完成' };
        } catch (error) {
            this.executionState = 'stopped';
            return { success: false, error: error.message };
        }
    }

    // 执行单条指令
    async executeInstruction(instruction) {
        const parts = instruction.split(/\s+/);
        const opcode = parts[0].toUpperCase();
        const params = parts.slice(1);
        
        switch (opcode) {
            case 'X':
            case 'NOT':
                return this.quantumNOT(params[0]);
            case 'Z':
                return this.quantumZ(params[0]);
            case 'Y':
                return this.quantumY(params[0]);
            case 'S':
                return this.quantumS(params[0]);
            case 'T':
                return this.quantumT(params[0]);
            case 'SWAP':
                return this.quantumSWAP(params[0], params[1]);
            case 'H':
                return this.quantumH(params[0]);
            case 'CNOT':
                return this.quantumCNOT(params[0], params[1]);
            case 'MEASURE':
                return this.quantumMeasure(params[0]);
            case 'INIT':
                this.createQuantumBit(params[0]);
                return { success: true };
            case 'RESET':
                this.quantumBits.clear();
                this.quantumRegisters.clear();
                this.initQuantumSystem();
                return { success: true };
            case 'RANDOM':
                const randMin = parseFloat(params[0]) || 0;
                const randMax = parseFloat(params[1]) || 1;
                return { success: true, result: this.quantumRandom(randMin, randMax) };
            case 'RANDINT':
                return { success: true, result: this.quantumRandomInt(parseInt(params[0]), parseInt(params[1])) };
            case 'COIN':
                return { success: true, result: this.quantumCoinFlip() };
            case 'DICE':
                return { success: true, result: this.quantumDice(parseInt(params[0]) || 6) };
            case 'UUID':
                return { success: true, result: this.quantumUUID() };
            default:
                return { success: false, error: `未知指令: ${opcode}` };
        }
    }

    // 获取量子系统状态
    getQuantumState() {
        return {
            executionState: this.executionState,
            quantumBits: Array.from(this.quantumBits.values()),
            entanglements: Array.from(this.entanglementNetwork.values()),
            registers: Array.from(this.quantumRegisters.values()),
            history: this.executionHistory
        };
    }

    // 重置量子系统
    resetSystem() {
        this.quantumBits.clear();
        this.quantumRegisters.clear();
        this.qbcInstructions = [];
        this.executionHistory = [];
        this.executionState = 'idle';
        this.initQuantumSystem();
        
        this.addToHistory('量子系统已重置');
        return { success: true };
    }

    // 添加到执行历史
    addToHistory(message) {
        this.executionHistory.unshift({
            message: message,
            timestamp: Date.now(),
            time: new Date().toLocaleTimeString()
        });
        
        // 最多保留100条历史
        if (this.executionHistory.length > 100) {
            this.executionHistory.pop();
        }
    }

    // 获取示例QBC代码
    getExampleQBC() {
        return `# QBC量子字节码示例
# 贝尔态创建

# 初始化量子比特
INIT q0
INIT q1

# 应用H门创建叠加态
H q0

# 应用CNOT建立纠缠
CNOT q0 q1

# 测量结果
MEASURE q0
MEASURE q1`;
    }

    // Grover搜索算法
    async groverSearch(targetIndex, numBits, iterations = null) {
        if (!iterations) {
            // 计算最优迭代次数：G ≈ (π/4) * sqrt(N)
            const N = Math.pow(2, numBits);
            iterations = Math.floor((Math.PI / 4) * Math.sqrt(N));
        }
        
        this.executionState = 'running';
        this.addToHistory(`🔍 开始Grover搜索：目标 = ${targetIndex}，比特数 = ${numBits}，迭代 = ${iterations}`);
        
        // 步骤1：重置系统
        this.quantumBits.clear();
        for (let i = 0; i < numBits; i++) {
            this.createQuantumBit(`q${i}`);
        }
        
        // 步骤2：对量子比特应用H门创建均匀叠加态
        for (let i = 0; i < numBits; i++) {
            this.quantumH(`q${i}`);
        }
        this.addToHistory('✓ 创建均匀叠加态');
        
        // 获取目标状态的二进制表示
        const targetBinary = targetIndex.toString(2).padStart(numBits, '0');
        this.addToHistory(`📌 目标状态: |${targetBinary}⟩`);
        
        // 步骤3：Grover迭代
        for (let i = 0; i < iterations; i++) {
            // 3a: Oracle操作（标记目标状态）
            this.oracle(targetIndex, numBits);
            
            // 3b: 扩散算子（反相围绕平均值）
            this.diffusionOperator(numBits);
            
            this.addToHistory(`🔄 迭代 ${i + 1}/${iterations} 完成`);
            
            // 模拟延迟
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        // 步骤4：测量结果
        this.addToHistory('📏 开始测量...');
        const results = [];
        let successCount = 0;
        const trials = 100; // 多次 trials 统计成功率
        
        for (let t = 0; t < trials; t++) {
            // 克隆当前量子状态进行测量
            const trialResult = [];
            for (let i = 0; i < numBits; i++) {
                const qubit = this.quantumBits.get(`q${i}`);
                const prob0 = Math.abs(qubit.amplitude.alpha) ** 2;
                const result = Math.random() < prob0 ? 0 : 1;
                trialResult.push(result);
            }
            const measuredIndex = parseInt(trialResult.join(''), 2);
            results.push(measuredIndex);
            if (measuredIndex === targetIndex) successCount++;
        }
        
        const successRate = (successCount / trials * 100).toFixed(1);
        this.executionState = 'idle';
        this.addToHistory(`✅ Grover搜索完成！成功找到目标 ${successRate}%`);
        
        return {
            success: true,
            result: {
                targetIndex,
                results,
                successRate,
                iterations,
                numBits
            }
        };
    }
    
    // Oracle操作（标记目标状态）
    oracle(targetIndex, numBits) {
        // 在真实量子计算机中，这需要相位翻转
        // 这里我们模拟Oracle的效果：给目标状态赋予更高的振幅
        
        const targetBinary = targetIndex.toString(2).padStart(numBits, '0');
        
        // 简化的Oracle实现：通过调整振幅来模拟
        for (let i = 0; i < numBits; i++) {
            const qubit = this.quantumBits.get(`q${i}`);
            if (!qubit) continue;
            
            // 根据目标状态调整振幅（简化模型）
            const targetBit = parseInt(targetBinary[i]);
            
            // 这里使用简化的方法：应用Z门来翻转相位
            // 真正的实现需要控制相位门
            if (targetBit === 1) {
                // 如果目标是1，调整振幅比例
                const currentAlpha = qubit.amplitude.alpha;
                const currentBeta = qubit.amplitude.beta;
                qubit.amplitude.alpha = currentAlpha * 0.95;
                qubit.amplitude.beta = currentBeta * 1.05;
            } else {
                // 如果目标是0，调整振幅比例
                const currentAlpha = qubit.amplitude.alpha;
                const currentBeta = qubit.amplitude.beta;
                qubit.amplitude.alpha = currentAlpha * 1.05;
                qubit.amplitude.beta = currentBeta * 0.95;
            }
        }
    }
    
    // 扩散算子（反相围绕平均值）
    diffusionOperator(numBits) {
        // 计算平均振幅
        let totalAlpha = 0;
        let totalBeta = 0;
        let count = 0;
        
        for (let i = 0; i < numBits; i++) {
            const qubit = this.quantumBits.get(`q${i}`);
            if (qubit) {
                totalAlpha += qubit.amplitude.alpha;
                totalBeta += qubit.amplitude.beta;
                count++;
            }
        }
        
        const avgAlpha = count > 0 ? totalAlpha / count : 0;
        const avgBeta = count > 0 ? totalBeta / count : 0;
        
        // 应用反相围绕平均值
        for (let i = 0; i < numBits; i++) {
            const qubit = this.quantumBits.get(`q${i}`);
            if (qubit) {
                // 反相并围绕平均值
                qubit.amplitude.alpha = 2 * avgAlpha - qubit.amplitude.alpha;
                qubit.amplitude.beta = 2 * avgBeta - qubit.amplitude.beta;
                
                // 归一化
                const norm = Math.sqrt(
                    Math.abs(qubit.amplitude.alpha) ** 2 +
                    Math.abs(qubit.amplitude.beta) ** 2
                );
                if (norm > 0) {
                    qubit.amplitude.alpha /= norm;
                    qubit.amplitude.beta /= norm;
                }
            }
        }
    }
    
    // 量子傅里叶变换（QFT）
    async quantumFourierTransform(numBits) {
        this.executionState = 'running';
        this.addToHistory(`🌊 开始QFT：比特数 = ${numBits}`);
        
        // 确保有足够的量子比特
        if (this.quantumBits.size < numBits) {
            this.quantumBits.clear();
            for (let i = 0; i < numBits; i++) {
                this.createQuantumBit(`q${i}`);
            }
        }
        
        // QFT算法
        for (let i = 0; i < numBits; i++) {
            // 应用H门到第i个量子比特
            this.quantumH(`q${i}`);
            
            // 应用控制旋转门
            for (let j = i + 1; j < numBits; j++) {
                const angle = Math.PI / Math.pow(2, j - i);
                this.controlledPhaseRotation(`q${j}`, `q${i}`, angle);
            }
            
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        // 交换量子比特顺序（SWAP门）
        for (let i = 0; i < numBits / 2; i++) {
            this.swapGate(`q${i}`, `q${numBits - 1 - i}`);
        }
        
        this.executionState = 'idle';
        this.addToHistory('✅ QFT完成！');
        
        return {
            success: true,
            message: `QFT应用于 ${numBits} 个量子比特`
        };
    }
    
    // 控制相位旋转门
    controlledPhaseRotation(control, target, angle) {
        // 简化的相位旋转实现
        const qcontrol = this.quantumBits.get(control);
        const qtarget = this.quantumBits.get(target);
        
        if (!qcontrol || !qtarget) return;
        
        // 如果控制是|1⟩，对目标应用相位旋转
        if (qcontrol.state === '|1⟩' || qcontrol.state.includes('|1⟩')) {
            const cos_a = Math.cos(angle / 2);
            const sin_a = Math.sin(angle / 2);
            
            const newBeta = qtarget.amplitude.beta * cos_a + qtarget.amplitude.alpha * sin_a;
            const newAlpha = qtarget.amplitude.alpha * cos_a - qtarget.amplitude.beta * sin_a;
            
            qtarget.amplitude.alpha = newAlpha;
            qtarget.amplitude.beta = newBeta;
        }
    }
    
    // 交换门（SWAP）
    swapGate(qubit1, qubit2) {
        const q1 = this.quantumBits.get(qubit1);
        const q2 = this.quantumBits.get(qubit2);
        
        if (!q1 || !q2) return;
        
        // 简化：交换alpha和beta（忽略纠缠的复杂情况）
        const tempAlpha = q1.amplitude.alpha;
        const tempBeta = q1.amplitude.beta;
        
        q1.amplitude.alpha = q2.amplitude.alpha;
        q1.amplitude.beta = q2.amplitude.beta;
        q2.amplitude.alpha = tempAlpha;
        q2.amplitude.beta = tempBeta;
    }
    
    // 超密编码演示
    async superdenseCoding(message) {
        // 将消息编码为2位（00, 01, 10, 11）
        const messageMap = { '00': 0, '01': 1, '10': 2, '11': 3 };
        const messageNum = messageMap[message];
        
        if (messageNum === undefined) {
            return { success: false, error: '无效的消息，必须是00, 01, 10或11' };
        }
        
        this.executionState = 'running';
        this.addToHistory(`💬 超密编码：发送消息 "${message}"`);
        
        // 创建贝尔态对
        this.quantumBits.clear();
        this.createQuantumBit('q0');
        this.createQuantumBit('q1');
        
        // 创建|Φ+⟩贝尔态
        this.quantumH('q0');
        this.quantumCNOT('q0', 'q1');
        this.addToHistory('✓ 创建贝尔态对');
        
        // 根据消息编码应用操作
        switch (messageNum) {
            case 1: // 01 -> Z门
                this.quantumNOT('q0');
                break;
            case 2: // 10 -> X门
                this.quantumNOT('q0');
                break;
            case 3: // 11 -> XZ门（X然后Z）
                this.quantumH('q0');
                break;
            // 00 不需要额外操作
        }
        
        this.addToHistory(`✓ 编码消息 "${message}"`);
        
        // 解码
        this.quantumCNOT('q0', 'q1');
        this.quantumH('q0');
        this.addToHistory('✓ 解码消息');
        
        // 测量结果
        const result0 = await this.quantumMeasure('q0');
        const result1 = await this.quantumMeasure('q1');
        
        const received = result0.result + result1.result;
        const success = received === message ? '成功' : '失败';
        
        this.executionState = 'idle';
        this.addToHistory(`✅ 解码结果: ${received} (${success})`);
        
        return {
            success: true,
            message,
            received,
            success
        };
    }

    // 获取帮助信息
    getHelp() {
        return {
            instructions: [
                { opcode: 'INIT <qubit>', description: '初始化量子比特' },
                { opcode: 'X <qubit>', description: '量子NOT门，|0⟩↔|1⟩' },
                { opcode: 'Y <qubit>', description: '泡利Y门，比特翻转+相位翻转' },
                { opcode: 'Z <qubit>', description: '泡利Z门，相位翻转|1⟩→-|1⟩' },
                { opcode: 'H <qubit>', description: 'Hadamard门，创建叠加态' },
                { opcode: 'S <qubit>', description: 'S门，相位旋转π/2' },
                { opcode: 'T <qubit>', description: 'T门，相位旋转π/4' },
                { opcode: 'CNOT <ctrl> <tgt>', description: '控制NOT门，创建纠缠' },
                { opcode: 'SWAP <q1> <q2>', description: '交换两个量子比特状态' },
                { opcode: 'MEASURE <qubit>', description: '量子测量，波函数坍缩' },
                { opcode: 'RESET', description: '重置整个量子系统' },
                { opcode: 'GROVER <target> <bits>', description: 'Grover搜索算法' },
                { opcode: 'QFT <bits>', description: '量子傅里叶变换' },
                { opcode: 'SUPERDENSE <msg>', description: '超密编码（00/01/10/11）' },
                { opcode: 'RANDOM <min> <max>', description: '量子随机数' },
                { opcode: 'RANDINT <min> <max>', description: '量子随机整数' },
                { opcode: 'COIN', description: '量子抛硬币' },
                { opcode: 'DICE <sides>', description: '量子掷骰子' },
                { opcode: 'UUID', description: '量子UUID生成' }
            ],
            concepts: [
                { name: '叠加态', desc: '量子比特同时处于0和1状态' },
                { name: '纠缠', desc: '两个量子比特之间的深度关联' },
                { name: '测量', desc: '波函数坍缩，得到确定结果' },
                { name: 'QBC', desc: 'QEntL量子字节码' },
                { name: 'Grover', desc: '量子搜索算法，速度O(√N)' },
                { name: 'QFT', desc: '量子傅里叶变换，用于周期发现' },
                { name: '超密编码', desc: '用1个量子比特传输2位信息' }
            ]
        };
    }
    
    // 获取算法演示列表
    getAlgorithmDemos() {
        return [
            {
                name: 'Grover搜索',
                description: '在N个元素中搜索目标，速度O(√N)',
                qbc: '# Grover搜索演示\nGROVER 5 4',
                category: 'search'
            },
            {
                name: '量子傅里叶变换',
                description: '量子傅里叶变换，用于周期发现',
                qbc: '# QFT演示\nQFT 4',
                category: 'transform'
            },
            {
                name: '超密编码',
                description: '使用1个量子比特传输2位信息',
                qbc: '# 超密编码演示\nSUPERDENSE 11',
                category: 'communication'
            }
        ];
    }
}

// 导出供全局使用
window.QVMSimulator = QVMSimulator;

    // ========== 量子随机数生成器 ==========
    
    // 生成量子随机数
    quantumRandom(min = 0, max = 1) {
        // 使用量子叠加态原理生成真随机数
        const qubit = {
            amplitude: { alpha: 1/Math.sqrt(2), beta: 1/Math.sqrt(2) }
        };
        
        // 模拟量子测量
        const measurement = Math.random() < Math.abs(qubit.amplitude.alpha) ** 2 ? 0 : 1;
        
        // 扩展到指定范围
        return min + measurement * (max - min);
    }
    
    // 生成量子随机整数
    quantumRandomInt(min, max) {
        return Math.floor(this.quantumRandom(min, max + 1));
    }
    
    // 生成量子随机比特序列
    quantumRandomBits(count) {
        let bits = '';
        for (let i = 0; i < count; i++) {
            bits += this.quantumRandomInt(0, 1).toString();
        }
        return bits;
    }
    
    // 生成量子随机UUID
    quantumUUID() {
        const hex = '0123456789abcdef';
        let uuid = '';
        for (let i = 0; i < 36; i++) {
            if (i === 8 || i === 13 || i === 18 || i === 23) {
                uuid += '-';
            } else if (i === 14) {
                uuid += '4'; // UUID版本4
            } else if (i === 19) {
                uuid += hex.substr(this.quantumRandomInt(8, 11), 1); // 变体
            } else {
                uuid += hex[this.quantumRandomInt(0, 15)];
            }
        }
        return uuid;
    }
    
    // 量子掷骰子
    quantumDice(sides = 6) {
        return this.quantumRandomInt(1, sides);
    }
    
    // 量子抛硬币
    quantumCoinFlip() {
        return this.quantumRandomInt(0, 1) === 1 ? '正面' : '反面';
    }
    
    // 量子洗牌（Fisher-Yates算法 + 量子随机）
    quantumShuffle(array) {
        const result = [...array];
        for (let i = result.length - 1; i > 0; i--) {
            const j = this.quantumRandomInt(0, i);
            [result[i], result[j]] = [result[j], result[i]];
        }
        return result;
    }
    
    // 量子抽样（不放回）
    quantumSample(array, count) {
        const shuffled = this.quantumShuffle(array);
        return shuffled.slice(0, Math.min(count, array.length));
    }

    // 量子高斯分布随机数
    quantumGaussian(mean = 0, stdDev = 1) {
        // Box-Muller变换 + 量子随机
        let u1, u2;
        do {
            u1 = this.quantumRandom();
        } while (u1 === 0);
        u2 = this.quantumRandom();
        
        const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
        return z0 * stdDev + mean;
    }

    // ========== 量子纠缠可视化 ==========
    
    // 获取纠缠网络可视化数据
    getEntanglementVisualization() {
        const nodes = [];
        const edges = [];
        
        // 添加量子比特节点
        this.quantumBits.forEach((qubit, name) => {
            nodes.push({
                id: name,
                label: name,
                state: qubit.state,
                measured: qubit.measured,
                amplitude: qubit.amplitude,
                entangled: qubit.entangled.length > 0
            });
            
            // 添加纠缠边
            qubit.entangled.forEach(target => {
                edges.push({
                    from: name,
                    to: target,
                    strength: this.entanglementNetwork.get(`${name}-${target}`)?.strength || 1.0
                });
            });
        });
        
        return { nodes, edges };
    }
    
    // 计算纠缠熵
    calculateEntanglementEntropy(qubit1, qubit2) {
        const q1 = this.quantumBits.get(qubit1);
        const q2 = this.quantumBits.get(qubit2);
        if (!q1 || !q2) return 0;
        
        // 简化的纠缠熵计算
        const p = Math.abs(q1.amplitude.alpha * q2.amplitude.alpha);
        const entropy = -p * Math.log2(p + 0.0001) - (1-p) * Math.log2(1-p + 0.0001);
        return Math.max(0, Math.min(1, entropy));
    }
    
    // 获取量子态布洛赫球坐标
    getBlochSphereCoordinates(qubitName) {
        const qubit = this.quantumBits.get(qubitName);
        if (!qubit) return null;
        
        const alpha = qubit.amplitude.alpha;
        const beta = qubit.amplitude.beta;
        
        // 布洛赫球坐标 (x, y, z)
        return {
            x: 2 * Math.real(alpha * Math.conj(beta)),
            y: 2 * Math.imag(alpha * Math.conj(beta)),
            z: Math.abs(alpha) ** 2 - Math.abs(beta) ** 2,
            theta: 2 * Math.acos(Math.abs(alpha)),
            phi: Math.atan2(Math.imag(beta), Math.real(beta))
        };
    }
    
    // 量子态保真度计算
    calculateFidelity(qubit1, qubit2) {
        const q1 = this.quantumBits.get(qubit1);
        const q2 = this.quantumBits.get(qubit2);
        if (!q1 || !q2) return 0;
        
        // 简化的保真度计算
        const dot = q1.amplitude.alpha * q2.amplitude.alpha + q1.amplitude.beta * q2.amplitude.beta;
        return Math.abs(dot) ** 2;
    }
    
    // 获取量子系统统计
    getQuantumStatistics() {
        let superpositionCount = 0;
        let entangledCount = 0;
        let measuredCount = 0;
        let groundCount = 0;
        
        this.quantumBits.forEach(qubit => {
            if (qubit.state.includes('叠加')) superpositionCount++;
            if (qubit.entangled.length > 0) entangledCount++;
            if (qubit.measured) measuredCount++;
            if (qubit.state === '|0⟩') groundCount++;
        });
        
        return {
            totalQubits: this.quantumBits.size,
            superposition: superpositionCount,
            entangled: entangledCount,
            measured: measuredCount,
            ground: groundCount,
            entanglementNetworkSize: this.entanglementNetwork.size
        };
    }

// 复数运算辅助函数
Math.real = (x) => typeof x === 'number' ? x : x.re || x;
Math.imag = (x) => typeof x === 'number' ? 0 : x.im || 0;
Math.conj = (x) => typeof x === 'number' ? x : { re: x.re || x, im: -(x.im || 0) };

    // ========== 更多量子算法演示 ==========
    
    // Deutsch算法 - 判断函数是常数还是平衡
    async deutschAlgorithm(oracleType = 'constant') {
        this.executionState = 'running';
        this.addToHistory('🔬 Deutsch算法启动');
        
        // 重置量子比特
        this.quantumBits.clear();
        this.createQuantumBit('q0');
        this.createQuantumBit('q1');
        
        // 初始化 |0⟩|1⟩
        this.quantumH('q0');
        this.quantumNOT('q1');
        this.quantumH('q1');
        
        // 应用Oracle
        if (oracleType === 'balanced') {
            this.quantumCNOT('q0', 'q1');
        }
        
        // 应用H门到第一个量子比特
        this.quantumH('q0');
        
        // 测量
        const result = await this.quantumMeasure('q0');
        
        this.executionState = 'idle';
        const isConstant = result.result === '0';
        this.addToHistory(`✅ Deutsch算法: 函数是${isConstant ? '常数型' : '平衡型'}`);
        
        return {
            success: true,
            oracleType,
            result: result.result,
            classification: isConstant ? 'constant' : 'balanced'
        };
    }
    
    // 量子隐形传态模拟
    async quantumTeleportation() {
        this.executionState = 'running';
        this.addToHistory('📡 量子隐形传态启动');
        
        // 创建三个量子比特
        this.quantumBits.clear();
        this.createQuantumBit('q0'); // 要传送的状态
        this.createQuantumBit('q1'); // Alice的EPR半边
        this.createQuantumBit('q2'); // Bob的EPR半边
        
        // 准备要传送的状态（叠加态）
        this.quantumH('q0');
        
        // 创建EPR对
        this.quantumH('q1');
        this.quantumCNOT('q1', 'q2');
        
        // Alice操作
        this.quantumCNOT('q0', 'q1');
        this.quantumH('q0');
        
        // 测量Alice的量子比特
        const m0 = await this.quantumMeasure('q0');
        const m1 = await this.quantumMeasure('q1');
        
        // Bob根据测量结果应用门
        if (m1.result === '1') {
            this.quantumNOT('q2');
        }
        if (m0.result === '1') {
            this.quantumZ('q2');
        }
        
        this.executionState = 'idle';
        this.addToHistory('✅ 量子隐形传态完成');
        
        return {
            success: true,
            classicalBits: m0.result + m1.result,
            message: '状态已传送到q2'
        };
    }
    
    // Bernstein-Vazirani算法
    async bernsteinVazirani(secretString) {
        this.executionState = 'running';
        const n = secretString.length;
        this.addToHistory(`🔐 Bernstein-Vazirani算法: 密串长度=${n}`);
        
        // 重置量子比特
        this.quantumBits.clear();
        for (let i = 0; i <= n; i++) {
            this.createQuantumBit(`q${i}`);
        }
        
        // 初始化
        this.quantumNOT(`q${n}`);
        for (let i = 0; i <= n; i++) {
            this.quantumH(`q${i}`);
        }
        
        // 应用Oracle
        for (let i = 0; i < n; i++) {
            if (secretString[i] === '1') {
                this.quantumCNOT(`q${i}`, `q${n}`);
            }
        }
        
        // 应用H门
        for (let i = 0; i < n; i++) {
            this.quantumH(`q${i}`);
        }
        
        // 测量
        let result = '';
        for (let i = 0; i < n; i++) {
            const m = await this.quantumMeasure(`q${i}`);
            result += m.result;
        }
        
        this.executionState = 'idle';
        this.addToHistory(`✅ Bernstein-Vazirani完成: 密串=${result}`);
        
        return {
            success: true,
            secretString,
            foundString: result,
            correct: result === secretString
        };
    }
    
    // Simon算法简化版
    async simonAlgorithm(n = 2) {
        this.executionState = 'running';
        this.addToHistory(`🎲 Simon算法: n=${n}`);
        
        // 简化演示
        this.quantumBits.clear();
        for (let i = 0; i < 2 * n; i++) {
            this.createQuantumBit(`q${i}`);
        }
        
        // 应用H门到前n个量子比特
        for (let i = 0; i < n; i++) {
            this.quantumH(`q${i}`);
        }
        
        // 测量
        let result = '';
        for (let i = 0; i < n; i++) {
            const m = await this.quantumMeasure(`q${i}`);
            result += m.result;
        }
        
        this.executionState = 'idle';
        this.addToHistory(`✅ Simon算法完成: 结果=${result}`);
        
        return {
            success: true,
            n,
            result
        };
    }

    // 获取所有算法演示
    getAllAlgorithmDemos() {
        return [
            { name: 'Grover搜索', fn: 'groverSearch', params: [5, 4], category: 'search', qbc: '# Grover搜索演示\nGROVER 5 4' },
            { name: 'QFT变换', fn: 'quantumFourierTransform', params: [4], category: 'transform', qbc: '# QFT演示\nQFT 4' },
            { name: '超密编码', fn: 'superdenseCoding', params: ['11'], category: 'communication', qbc: '# 超密编码演示\nSUPERDENSE 11' },
            { name: 'Deutsch算法', fn: 'deutschAlgorithm', params: ['balanced'], category: 'algorithm', qbc: '# 算法演示' },
            { name: '量子隐形传态', fn: 'quantumTeleportation', params: [], category: 'communication', qbc: '# 超密编码演示\nSUPERDENSE 11' },
            { name: 'Bernstein-Vazirani', fn: 'bernsteinVazirani', params: ['101'], category: 'algorithm', qbc: '# 算法演示' },
            { name: '量子随机数', fn: 'quantumRandom', params: [0, 100], category: 'utility', qbc: '# 实用工具' },
            { name: '量子掷骰子', fn: 'quantumDice', params: [6], category: 'utility', qbc: '# 实用工具' }
        ];
    }

    // ========== 量子错误纠正 ==========
    
    // 简化的比特翻转码（3量子比特重复码）
    async bitFlipCode(inputState = '0') {
        this.executionState = 'running';
        this.addToHistory('🛡️ 比特翻转码编码启动');
        
        // 创建3个量子比特用于编码
        this.quantumBits.clear();
        this.createQuantumBit('q0');
        this.createQuantumBit('q1');
        this.createQuantumBit('q2');
        
        // 编码：将输入状态复制到3个量子比特
        if (inputState === '1') {
            this.quantumNOT('q0');
            this.quantumNOT('q1');
            this.quantumNOT('q2');
        }
        
        // 模拟噪声：随机翻转一个量子比特
        const errorPos = this.quantumRandomInt(0, 2);
        if (Math.random() > 0.7) { // 30%概率发生错误
            this.quantumNOT(`q${errorPos}`);
            this.addToHistory(`⚠️ 模拟噪声：q${errorPos}发生比特翻转`);
        }
        
        // 错误检测：多数投票
        const results = [];
        for (let i = 0; i < 3; i++) {
            const m = await this.quantumMeasure(`q${i}`);
            results.push(parseInt(m.result));
        }
        
        // 纠正：取多数结果
        const ones = results.filter(r => r === 1).length;
        const corrected = ones >= 2 ? 1 : 0;
        
        this.executionState = 'idle';
        this.addToHistory(`✅ 比特翻转码纠正完成: 输入=${inputState}, 纠正后=${corrected}`);
        
        return {
            success: true,
            inputState,
            measurements: results,
            corrected,
            errorOccurred: results.some((r, i) => i === errorPos && r !== parseInt(inputState))
        };
    }
    
    // 相位翻转码
    async phaseFlipCode() {
        this.executionState = 'running';
        this.addToHistory('🛡️ 相位翻转码编码启动');
        
        // 创建3个量子比特
        this.quantumBits.clear();
        for (let i = 0; i < 3; i++) {
            this.createQuantumBit(`q${i}`);
        }
        
        // 应用H门创建叠加态
        this.quantumH('q0');
        
        // 编码（使用相位）
        this.quantumH('q0');
        this.quantumH('q1');
        this.quantumH('q2');
        
        // 模拟相位错误
        if (Math.random() > 0.7) {
            const errorPos = this.quantumRandomInt(0, 2);
            this.quantumZ(`q${errorPos}`);
            this.addToHistory(`⚠️ 模拟相位错误：q${errorPos}`);
        }
        
        // 解码
        this.quantumH('q0');
        this.quantumH('q1');
        this.quantumH('q2');
        
        this.executionState = 'idle';
        this.addToHistory('✅ 相位翻转码处理完成');
        
        return { success: true };
    }
    
    // Shor码（9量子比特）
    async shorCode() {
        this.executionState = 'running';
        this.addToHistory('🛡️ Shor码编码启动（9量子比特）');
        
        // 创建9个量子比特
        this.quantumBits.clear();
        for (let i = 0; i < 9; i++) {
            this.createQuantumBit(`q${i}`);
        }
        
        // 简化的Shor编码
        this.quantumH('q0');
        
        // 模拟编码过程
        for (let i = 0; i < 9; i++) {
            if (i > 0) {
                this.quantumH(`q${i}`);
            }
        }
        
        this.executionState = 'idle';
        this.addToHistory('✅ Shor码编码完成');
        
        return {
            success: true,
            qubits: 9,
            protection: 'bit flip + phase flip'
        };
    }
    
    // Steane码（7量子比特CSS码）
    async steaneCode() {
        this.executionState = 'running';
        this.addToHistory('🛡️ Steane码编码启动（7量子比特）');
        
        this.quantumBits.clear();
        for (let i = 0; i < 7; i++) {
            this.createQuantumBit(`q${i}`);
        }
        
        // 简化的Steane编码
        this.quantumH('q0');
        
        this.executionState = 'idle';
        this.addToHistory('✅ Steane码编码完成');
        
        return {
            success: true,
            qubits: 7,
            type: 'CSS code'
        };
    }

    // ========== 量子态序列化与导入导出 ==========
    
    // 导出量子状态为JSON
    exportQuantumState() {
        const state = {
            version: '1.0',
            timestamp: new Date().toISOString(),
            quantumBits: {},
            entanglements: [],
            history: this.executionHistory.slice(0, 50) // 最近50条历史
        };
        
        this.quantumBits.forEach((qubit, name) => {
            state.quantumBits[name] = {
                name: qubit.name,
                state: qubit.state,
                amplitude: {
                    alpha: qubit.amplitude.alpha,
                    beta: qubit.amplitude.beta
                },
                phase: qubit.phase || 0,
                entangled: [...qubit.entangled],
                measured: qubit.measured
            };
        });
        
        this.entanglementNetwork.forEach((value, key) => {
            state.entanglements.push({
                key: key,
                ...value
            });
        });
        
        return JSON.stringify(state, null, 2);
    }
    
    // 导入量子状态
    importQuantumState(jsonString) {
        try {
            const state = JSON.parse(jsonString);
            
            if (state.version !== '1.0') {
                return { success: false, error: '不支持的版本' };
            }
            
            // 清空当前状态
            this.quantumBits.clear();
            this.entanglementNetwork.clear();
            this.executionHistory = [];
            
            // 恢复量子比特
            for (const [name, qubit] of Object.entries(state.quantumBits)) {
                this.quantumBits.set(name, {
                    name: qubit.name,
                    state: qubit.state,
                    amplitude: qubit.amplitude,
                    phase: qubit.phase || 0,
                    entangled: qubit.entangled || [],
                    measured: qubit.measured
                });
            }
            
            // 恢复纠缠网络
            state.entanglements.forEach(ent => {
                this.entanglementNetwork.set(ent.key, {
                    pair: ent.pair,
                    created: ent.created,
                    strength: ent.strength || 1.0
                });
            });
            
            // 恢复历史
            this.executionHistory = state.history || [];
            
            this.addToHistory('📥 量子状态已导入');
            return { success: true, qubits: this.quantumBits.size };
        } catch (e) {
            return { success: false, error: e.message };
        }
    }
    
    // 生成量子状态报告
    generateQuantumReport() {
        const stats = this.getQuantumStatistics();
        const report = {
            title: 'QSM量子系统状态报告',
            generated: new Date().toISOString(),
            statistics: stats,
            quantumBits: [],
            entanglements: [],
            recommendations: []
        };
        
        // 详细量子比特信息
        this.quantumBits.forEach((qubit, name) => {
            report.quantumBits.push({
                name: name,
                state: qubit.state,
                measured: qubit.measured,
                entangledCount: qubit.entangled.length,
                probability: {
                    zero: Math.abs(qubit.amplitude.alpha) ** 2,
                    one: Math.abs(qubit.amplitude.beta) ** 2
                }
            });
        });
        
        // 纠缠信息
        this.entanglementNetwork.forEach((value, key) => {
            report.entanglements.push({
                key: key,
                pair: value.pair,
                age: Date.now() - value.created
            });
        });
        
        // 建议
        if (stats.superposition < 2) {
            report.recommendations.push('建议应用H门创建更多叠加态');
        }
        if (stats.entangled < 1) {
            report.recommendations.push('建议使用CNOT门创建量子纠缠');
        }
        
        return report;
    }
    
    // 打印量子状态报告
    printQuantumReport() {
        const report = this.generateQuantumReport();
        let output = `\n${'='.repeat(50)}\n`;
        output += `  ${report.title}\n`;
        output += `  生成时间: ${report.generated}\n`;
        output += `${'='.repeat(50)}\n\n`;
        
        output += `📊 统计信息:\n`;
        output += `  总量子比特: ${report.statistics.totalQubits}\n`;
        output += `  叠加态: ${report.statistics.superposition}\n`;
        output += `  纠缠: ${report.statistics.entangled}\n`;
        output += `  已测量: ${report.statistics.measured}\n\n`;
        
        output += `🔬 量子比特详情:\n`;
        report.quantumBits.forEach(qb => {
            output += `  ${qb.name}: ${qb.state} `;
            output += `[P(0)=${(qb.probability.zero * 100).toFixed(1)}%, `;
            output += `P(1)=${(qb.probability.one * 100).toFixed(1)}%]\n`;
        });
        
        if (report.entanglements.length > 0) {
            output += `\n🔗 纠缠关系:\n`;
            report.entanglements.forEach(ent => {
                output += `  ${ent.pair[0]} ↔ ${ent.pair[1]}\n`;
            });
        }
        
        if (report.recommendations.length > 0) {
            output += `\n💡 建议:\n`;
            report.recommendations.forEach(rec => {
                output += `  • ${rec}\n`;
            });
        }
        
        output += `\n${'='.repeat(50)}\n`;
        
        console.log(output);
        return output;
    }

    // ========== 量子门组合宏 ==========
    
    // Bell态创建宏
    async createBellState(q1, q2) {
        this.addToHistory(`📦 创建Bell态: ${q1}, ${q2}`);
        this.quantumH(q1);
        this.quantumCNOT(q1, q2);
        return { success: true, state: 'Bell态' };
    }
    
    // GHZ态创建宏（三量子比特纠缠）
    async createGHZState(q1, q2, q3) {
        this.addToHistory(`📦 创建GHZ态: ${q1}, ${q2}, ${q3}`);
        this.quantumH(q1);
        this.quantumCNOT(q1, q2);
        this.quantumCNOT(q2, q3);
        return { success: true, state: 'GHZ态' };
    }
    
    // W态创建宏
    async createWState(q1, q2, q3) {
        this.addToHistory(`📦 创建W态: ${q1}, ${q2}, ${q3}`);
        // 简化的W态创建
        this.quantumH(q1);
        // 复杂的旋转组合（简化版）
        this.quantumH(q2);
        this.quantumCNOT(q1, q2);
        this.quantumH(q3);
        this.quantumCNOT(q2, q3);
        return { success: true, state: 'W态' };
    }
    
    // 量子傅里叶变换宏（简化版）
    async qftMacro(qubits) {
        this.addToHistory(`📦 QFT宏: ${qubits.join(', ')}`);
        const n = qubits.length;
        
        for (let i = 0; i < n; i++) {
            this.quantumH(qubits[i]);
            for (let j = i + 1; j < n; j++) {
                // 控制相位旋转（简化）
                const angle = Math.PI / Math.pow(2, j - i);
                this.quantumCNOT(qubits[j], qubits[i]);
            }
        }
        
        // 交换顺序
        for (let i = 0; i < Math.floor(n / 2); i++) {
            this.quantumSWAP(qubits[i], qubits[n - 1 - i]);
        }
        
        return { success: true, qubits: n };
    }
    
    // 逆量子傅里叶变换宏
    async inverseQftMacro(qubits) {
        this.addToHistory(`📦 逆QFT宏: ${qubits.join(', ')}`);
        const n = qubits.length;
        
        // 交换顺序
        for (let i = 0; i < Math.floor(n / 2); i++) {
            this.quantumSWAP(qubits[i], qubits[n - 1 - i]);
        }
        
        // 逆变换
        for (let i = n - 1; i >= 0; i--) {
            for (let j = n - 1; j > i; j--) {
                this.quantumCNOT(qubits[j], qubits[i]);
            }
            this.quantumH(qubits[i]);
        }
        
        return { success: true, qubits: n };
    }
    
    // 相位估计宏
    async phaseEstimation(unitaryQubit, eigenstateQubits, precision) {
        this.addToHistory(`📦 相位估计: 精度=${precision}`);
        
        const n = eigenstateQubits.length;
        
        // 初始化
        for (let i = 0; i < n; i++) {
            this.quantumH(eigenstateQubits[i]);
        }
        
        // 受控酉操作（简化）
        for (let i = 0; i < n; i++) {
            this.quantumCNOT(eigenstateQubits[i], unitaryQubit);
        }
        
        // 逆QFT
        await this.inverseQftMacro(eigenstateQubits);
        
        // 测量
        const results = [];
        for (let i = 0; i < n; i++) {
            const m = await this.quantumMeasure(eigenstateQubits[i]);
            results.push(m.result);
        }
        
        const phase = parseInt(results.join(''), 2) / Math.pow(2, n);
        
        return {
            success: true,
            phase: phase,
            binaryResult: results.join('')
        };
    }
    
    // 量子隐形传态完整流程
    async teleportFullWorkflow() {
        this.addToHistory('📦 量子隐形传态完整流程');
        
        // 创建三个量子比特
        this.quantumBits.clear();
        this.createQuantumBit('psi');  // 要传送的状态
        this.createQuantumBit('alice'); // Alice的EPR半边
        this.createQuantumBit('bob');   // Bob的EPR半边
        
        // 准备要传送的状态
        this.quantumH('psi');
        this.addToHistory('  1. 准备待传送状态 |ψ⟩');
        
        // 创建EPR对
        this.quantumH('alice');
        this.quantumCNOT('alice', 'bob');
        this.addToHistory('  2. 创建EPR对');
        
        // Alice操作
        this.quantumCNOT('psi', 'alice');
        this.quantumH('psi');
        this.addToHistory('  3. Alice执行Bell测量');
        
        // Alice测量
        const mPsi = await this.quantumMeasure('psi');
        const mAlice = await this.quantumMeasure('alice');
        const classicalBits = mPsi.result + mAlice.result;
        this.addToHistory(`  4. 经典比特: ${classicalBits}`);
        
        // Bob根据结果修正
        if (mAlice.result === '1') {
            this.quantumNOT('bob');
        }
        if (mPsi.result === '1') {
            this.quantumZ('bob');
        }
        this.addToHistory('  5. Bob完成状态修正');
        
        // 验证
        const mBob = await this.quantumMeasure('bob');
        
        return {
            success: true,
            classicalBits,
            bobResult: mBob.result,
            message: '量子态已成功传送'
        };
    }
    
    // 获取所有宏命令
    getMacros() {
        return [
            { name: 'Bell态', fn: 'createBellState', params: ['q0', 'q1'], desc: '创建两量子比特Bell纠缠态' },
            { name: 'GHZ态', fn: 'createGHZState', params: ['q0', 'q1', 'q2'], desc: '创建三量子比特GHZ纠缠态' },
            { name: 'W态', fn: 'createWState', params: ['q0', 'q1', 'q2'], desc: '创建三量子比特W纠缠态' },
            { name: 'QFT', fn: 'qftMacro', params: [['q0', 'q1', 'q2', 'q3']], desc: '量子傅里叶变换' },
            { name: '相位估计', fn: 'phaseEstimation', params: ['q0', ['q1', 'q2'], 3], desc: '量子相位估计算法' },
            { name: '隐形传态', fn: 'teleportFullWorkflow', params: [], desc: '完整的量子隐形传态流程' }
        ];
    }

// ========== QBC字节码解析增强 ==========

// QBC指令集定义（基于QEntL规范）
static getQBCInstructionSet() {
  return {
    // 量子门指令
    'H': { opcode: 0x01, params: ['qubit'], desc: 'Hadamard门' },
    'X': { opcode: 0x02, params: ['qubit'], desc: 'NOT门/X门' },
    'Y': { opcode: 0x03, params: ['qubit'], desc: 'Pauli Y门' },
    'Z': { opcode: 0x04, params: ['qubit'], desc: 'Pauli Z门' },
    'S': { opcode: 0x05, params: ['qubit'], desc: '相位门π/2' },
    'T': { opcode: 0x06, params: ['qubit'], desc: '相位门π/4' },
    'CNOT': { opcode: 0x10, params: ['control', 'target'], desc: '受控NOT门' },
    'CZ': { opcode: 0x11, params: ['control', 'target'], desc: '受控Z门' },
    'SWAP': { opcode: 0x12, params: ['qubit1', 'qubit2'], desc: '交换门' },
    
    // 测量指令
    'MEASURE': { opcode: 0x20, params: ['qubit'], desc: '量子测量' },
    'MEASURE_ALL': { opcode: 0x21, params: [], desc: '测量所有量子比特' },
    
    // 算法指令
    'GROVER': { opcode: 0x30, params: ['target', 'bits'], desc: 'Grover搜索' },
    'QFT': { opcode: 0x31, params: ['bits'], desc: '量子傅里叶变换' },
    'SUPERDENSE': { opcode: 0x32, params: ['message'], desc: '超密编码' },
    'DEUTSCH': { opcode: 0x33, params: ['type'], desc: 'Deutsch算法' },
    'BV': { opcode: 0x34, params: ['secret'], desc: 'Bernstein-Vazirani算法' },
    'TELEPORT': { opcode: 0x35, params: [], desc: '量子隐形传态' },
    
    // 工具指令
    'RAND': { opcode: 0x40, params: ['min', 'max'], desc: '量子随机数' },
    'DICE': { opcode: 0x50, params: ['sides'], desc: '量子掷骰子' },
    
    // 控制指令
    'RESET': { opcode: 0xF0, params: [], desc: '重置量子态' },
    'NOP': { opcode: 0x00, params: [], desc: '空操作' }
  };
}

// 解析QBC代码
parseQBC(qbcCode) {
  const instructions = [];
  const lines = qbcCode.split('\n');
  
  for (let line of lines) {
    line = line.trim();
    
    // 跳过空行和注释
    if (!line || line.startsWith('#')) continue;
    
    // 解析指令
    const parts = line.split(/\s+/);
    const opcode = parts[0].toUpperCase();
    const params = parts.slice(1);
    
    const instructionSet = QVMSimulator.getQBCInstructionSet();
    if (instructionSet[opcode]) {
      instructions.push({
        opcode: opcode,
        params: params,
        info: instructionSet[opcode]
      });
    }
  }
  
  return instructions;
}

// 验证QBC代码
validateQBC(qbcCode) {
  const errors = [];
  const warnings = [];
  const instructions = this.parseQBC(qbcCode);
  
  for (let inst of instructions) {
    const expectedParams = inst.info.params.length;
    const actualParams = inst.params.length;
    
    if (actualParams < expectedParams) {
      errors.push(`${inst.opcode}: 需要${expectedParams}个参数，实际${actualParams}个`);
    }
    
    // 验证量子比特范围
    if (inst.info.params.includes('qubit') || inst.info.params.includes('control')) {
      for (let p of inst.params) {
        const qubitNum = parseInt(p.replace('q', ''));
        if (isNaN(qubitNum) || qubitNum < 0 || qubitNum >= 8) {
          warnings.push(`${inst.opcode}: 量子比特${p}超出范围(0-7)`);
        }
      }
    }
  }
  
  return {
    valid: errors.length === 0,
    errors: errors,
    warnings: warnings,
    instructionCount: instructions.length
  };
}

// 编译为简化QBC字节码
compileToBytecode(qbcCode) {
  const instructions = this.parseQBC(qbcCode);
  const bytecode = [];
  
  // QBC文件头
  bytecode.push(0x51); // 'Q'
  bytecode.push(0x42); // 'B'
  bytecode.push(0x43); // 'C'
  bytecode.push(0x31); // '1'
  bytecode.push(0x00); // 版本
  bytecode.push(0x01); // 子版本
  
  // 指令数量
  bytecode.push(instructions.length & 0xFF);
  bytecode.push((instructions.length >> 8) & 0xFF);
  
  // 编译每条指令
  for (let inst of instructions) {
    bytecode.push(inst.info.opcode);
    for (let p of inst.params) {
      const num = parseInt(p.toString().replace('q', '').replace('qubit', ''));
      bytecode.push(isNaN(num) ? 0 : num);
    }
  }
  
  return bytecode;
}

// 反编译字节码
decompileBytecode(bytecode) {
  const instructions = [];
  const instructionSet = QVMSimulator.getQBCInstructionSet();
  
  // 验证文件头
  if (bytecode[0] !== 0x51 || bytecode[1] !== 0x42 || 
      bytecode[2] !== 0x43 || bytecode[3] !== 0x31) {
    return { error: '无效的QBC文件格式' };
  }
  
  // 解析指令
  let pos = 8; // 跳过头部
  const count = bytecode[6] | (bytecode[7] << 8);
  
  for (let i = 0; i < count && pos < bytecode.length; i++) {
    const opcode = bytecode[pos++];
    
    // 查找指令信息
    for (let [name, info] of Object.entries(instructionSet)) {
      if (info.opcode === opcode) {
        const params = [];
        for (let j = 0; j < info.params.length && pos < bytecode.length; j++) {
          params.push(bytecode[pos++].toString());
        }
        instructions.push({ opcode: name, params: params });
        break;
      }
    }
  }
  
  return instructions;
}

// ========== QEntL运行时API模拟 ==========

// 类型系统（对应QENTL_TYPE_*）
static getTypeSystem() {
  return {
    NULL: 0,
    INTEGER: 1,
    FLOAT: 2,
    BOOLEAN: 3,
    STRING: 4,
    ARRAY: 5,
    OBJECT: 6,
    FUNCTION: 7,
    QUANTUM_STATE: 8,  // 量子态类型（扩展）
    QUANTUM_GATE: 9    // 量子门类型（扩展）
  };
}

// 值表示（对应QentlValue）
createValue(type, value) {
  return {
    type: type,
    value: value,
    timestamp: Date.now()
  };
}

// 内存管理模拟
getMemoryStats() {
  return {
    totalQubits: this.quantumBits.size,
    totalRegisters: this.quantumRegisters.size,
    historyLength: this.executionHistory.length,
    entanglementCount: this.entanglementNetwork.size,
    estimatedMemory: JSON.stringify(this).length
  };
}

// 垃圾回收模拟
gcCollect() {
  // 清理已测量的量子比特状态
  let collected = 0;
  this.quantumBits.forEach((qubit, name) => {
    if (qubit.measured && Date.now() - qubit.measureTime > 60000) {
      this.quantumBits.delete(name);
      collected++;
    }
  });
  
  // 清理过期历史
  if (this.executionHistory.length > 100) {
    this.executionHistory = this.executionHistory.slice(-50);
    collected += 50;
  }
  
  return { collected: collected };
}

// 类型判断
valueGetType(value) {
  if (value === null || value === undefined) return 'NULL';
  if (typeof value === 'number') return Number.isInteger(value) ? 'INTEGER' : 'FLOAT';
  if (typeof value === 'boolean') return 'BOOLEAN';
  if (typeof value === 'string') return 'STRING';
  if (Array.isArray(value)) return 'ARRAY';
  if (typeof value === 'object') return 'OBJECT';
  if (typeof value === 'function') return 'FUNCTION';
  return 'UNKNOWN';
}

// 真值判断
valueIsTruthy(value) {
  if (value === null || value === undefined) return false;
  if (typeof value === 'boolean') return value;
  if (typeof value === 'number') return value !== 0;
  if (typeof value === 'string') return value.length > 0;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

// 标准库函数
stdlib = {
  // 数学函数
  abs: (x) => Math.abs(x),
  sqrt: (x) => Math.sqrt(x),
  pow: (base, exp) => Math.pow(base, exp),
  sin: (x) => Math.sin(x),
  cos: (x) => Math.cos(x),
  exp: (x) => Math.exp(x),
  log: (x) => Math.log(x),
  
  // 字符串操作
  length: (s) => s.length,
  concat: (s1, s2) => s1 + s2,
  substring: (s, start, end) => s.substring(start, end),
  indexOf: (s, search) => s.indexOf(search),
  
  // 数组操作
  push: (arr, item) => arr.push(item),
  pop: (arr) => arr.pop(),
  shift: (arr) => arr.shift(),
  slice: (arr, start, end) => arr.slice(start, end),
  map: (arr, fn) => arr.map(fn),
  filter: (arr, fn) => arr.filter(fn),
  reduce: (arr, fn, init) => arr.reduce(fn, init),
  
  // 量子扩展函数
  hadamard: (n) => 1 / Math.sqrt(2) * n,
  fidelity: (state1, state2) => {
    // 计算量子态保真度（简化版）
    return Math.abs(state1.alpha * state2.alpha + state1.beta * state2.beta);
  },
  normalize: (amplitudes) => {
    const norm = Math.sqrt(amplitudes.reduce((sum, a) => sum + a * a, 0));
    return amplitudes.map(a => a / norm);
  }
};

// 运行时初始化
runtimeInit() {
  console.log('QEntL运行时初始化...');
  this.initQuantumSystem();
  this.executionState = 'idle';
  console.log('运行时初始化完成');
}

// 运行时清理
runtimeCleanup() {
  console.log('运行时清理中...');
  this.quantumBits.clear();
  this.quantumRegisters.clear();
  this.executionHistory = [];
  this.entanglementNetwork.clear();
  this.executionState = 'stopped';
  console.log('运行时清理完成');
}

// 运行时重置
runtimeReset() {
  this.runtimeCleanup();
  this.runtimeInit();
}

// ========== 量子基因编码系统 ==========

// 量子基因编码生成器
generateQuantumGeneId(modelType, functionName, version) {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 6);
  return `QG-${modelType}-${functionName}-${version}-${timestamp}-${random}`;
}

// 量子纠缠信道生成
generateQuantumChannel(source, target) {
  const timestamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\..*/, '');
  return `QE-${source}-${target}-${timestamp}`;
}

// 量子基因结构
createQuantumGene(type, content) {
  return {
    quantum_gene_id: this.generateQuantumGeneId(type, 'quantum_operation', 'v1'),
    quantum_channel: this.generateQuantumChannel('qvm', 'user'),
    superposition_states: ['active', 'dormant', 'evolving', 'entangled'],
    content: content,
    created_at: new Date().toISOString(),
    neural_weights: {
      adjustment_enabled: true,
      learning_rate: 0.01,
      momentum: 0.9
    },
    os_integration: 'full_kernel_access'
  };
}

// 量子基因分类
static getQuantumGeneCategories() {
  return {
    SYSTEM: {
      name: '系统基因',
      types: ['KERNEL', 'DRIVER', 'SERVICE', 'SECURITY']
    },
    MODEL: {
      name: '模型基因',
      types: ['QSM', 'SOM', 'WEQ', 'REF']
    },
    NEURAL: {
      name: '神经基因',
      types: ['PERCEPTION', 'COGNITION', 'DECISION', 'EXECUTION']
    },
    TOOL: {
      name: '工具基因',
      types: ['COMPILER', 'DEBUGGER', 'OPTIMIZER', 'MONITOR']
    }
  };
}

// 为执行操作添加量子基因标记
tagExecutionWithGene(operation, result) {
  const gene = this.createQuantumGene('EXECUTION', {
    operation: operation,
    result: result,
    qubit_states: Array.from(this.quantumBits.entries()).map(([k, v]) => ({
      name: k,
      state: v.state
    }))
  });
  
  this.addToHistory(`🧬 量子基因: ${gene.quantum_gene_id}`);
  return gene;
}

// 量子基因编码导出
exportQuantumGenes() {
  const genes = [];
  
  // 导出当前量子态
  this.quantumBits.forEach((qubit, name) => {
    genes.push(this.createQuantumGene('QUBIT_STATE', {
      qubit_name: name,
      state: qubit.state,
      amplitude: qubit.amplitude
    }));
  });
  
  // 导出纠缠网络
  this.entanglementNetwork.forEach((partners, name) => {
    if (partners.length > 0) {
      genes.push(this.createQuantumGene('ENTANGLEMENT', {
        qubit: name,
        entangled_with: partners
      }));
    }
  });
  
  // 导出执行历史
  genes.push(this.createQuantumGene('EXECUTION_HISTORY', {
    history: this.executionHistory.slice(-20)
  }));
  
  return genes;
}

// 量子基因报告生成
generateQuantumGeneReport() {
  const genes = this.exportQuantumGenes();
  
  let report = '# QVM量子基因编码报告\n\n';
  report += `生成时间: ${new Date().toISOString()}\n`;
  report += `量子基因数量: ${genes.length}\n\n`;
  
  report += '## 量子基因列表\n\n';
  genes.forEach(gene => {
    report += `### ${gene.quantum_gene_id}\n`;
    report += `- 信道: ${gene.quantum_channel}\n`;
    report += `- 状态: ${gene.superposition_states.join(', ')}\n`;
    report += `- 内容类型: ${gene.content.constructor.name}\n\n`;
  });
  
  report += '---\n';
  report += '中华Zhoho，小趣WeQ，GLM5\n';
  
  return report;
}
