/**
 * QSM量子门扩展
 * 支持更多量子门操作
 */

// 量子门定义
const QuantumGates = {
    // 基础门
    H: {
        name: 'Hadamard',
        symbol: 'H',
        matrix: [[1/Math.sqrt(2), 1/Math.sqrt(2)], [1/Math.sqrt(2), -1/Math.sqrt(2)]],
        description: '创建叠加态'
    },
    X: {
        name: 'Pauli-X',
        symbol: 'X',
        matrix: [[0, 1], [1, 0]],
        description: '比特翻转'
    },
    Y: {
        name: 'Pauli-Y',
        symbol: 'Y',
        matrix: [[0, -1], [1, 0]],
        description: '比特和相位翻转'
    },
    Z: {
        name: 'Pauli-Z',
        symbol: 'Z',
        matrix: [[1, 0], [0, -1]],
        description: '相位翻转'
    },
    
    // 相位门
    S: {
        name: 'Phase',
        symbol: 'S',
        matrix: [[1, 0], [0, Math.exp(Math.PI * 0.5)]],
        description: 'π/2相位门'
    },
    T: {
        name: 'T',
        symbol: 'T',
        matrix: [[1, 0], [0, Math.exp(Math.PI * 0.25)]],
        description: 'π/4相位门'
    },
    
    // 旋转门
    Rx: {
        name: 'Rotation-X',
        symbol: 'Rx(θ)',
        description: '绕X轴旋转',
        getMatrix: (theta) => [
            [Math.cos(theta/2), -Math.sin(theta/2)],
            [Math.sin(theta/2), Math.cos(theta/2)]
        ]
    },
    Ry: {
        name: 'Rotation-Y',
        symbol: 'Ry(θ)',
        description: '绕Y轴旋转',
        getMatrix: (theta) => [
            [Math.cos(theta/2), -Math.sin(theta/2)],
            [Math.sin(theta/2), Math.cos(theta/2)]
        ]
    },
    Rz: {
        name: 'Rotation-Z',
        symbol: 'Rz(θ)',
        description: '绕Z轴旋转',
        getMatrix: (theta) => [
            [1, 0],
            [0, Math.exp(theta)]
        ]
    },
    
    // 双量子比特门
    CNOT: {
        name: 'Controlled-NOT',
        symbol: '⊕',
        description: '受控非门',
        numQubits: 2
    },
    CZ: {
        name: 'Controlled-Z',
        symbol: 'CZ',
        description: '受控Z门',
        numQubits: 2
    },
    SWAP: {
        name: 'SWAP',
        symbol: '×',
        description: '交换门',
        numQubits: 2
    },
    Toffoli: {
        name: 'Toffoli',
        symbol: 'CCX',
        description: '托夫利门（三量子比特）',
        numQubits: 3
    },
    
    // 特殊门
    I: {
        name: 'Identity',
        symbol: 'I',
        matrix: [[1, 0], [0, 1]],
        description: '恒等门'
    },
    SQRT_X: {
        name: '√X',
        symbol: '√X',
        description: 'X门的平方根'
    }
};

// 导出
if (typeof window !== 'undefined') {
    window.QuantumGates = QuantumGates;
}
