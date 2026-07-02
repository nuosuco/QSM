/**
 * QSM - 量子计算教程系统
 * 版本: v1.0.0
 * 量子基因编码: QGC-TUTORIAL-20260303
 * 
 * 基于QEntL运行时核心概念设计的交互式教程
 */

class QuantumTutorial {
    constructor() {
        this.lessons = this.initLessons();
        this.currentLesson = 0;
        this.currentStep = 0;
        this.completedLessons = this.loadProgress();
    }
    
    // 初始化教程课程
    initLessons() {
        return [
            {
                id: 'basics',
                title: '量子计算基础',
                description: '了解量子比特、叠加态和测量',
                steps: [
                    {
                        title: '什么是量子比特？',
                        content: `量子比特（Qubit）是量子计算的基本单位。

与经典比特只能是0或1不同，量子比特可以同时处于0和1的叠加态：

|ψ⟩ = α|0⟩ + β|1⟩

其中 |α|² + |β|² = 1

在QEntL中，量子状态由QuantumState类管理。`,
                        demo: 'H q0',
                        action: '点击"执行H门"观察量子比特从|0⟩变为叠加态'
                    },
                    {
                        title: 'Hadamard门',
                        content: `Hadamard门（H门）是最重要的量子门之一。

它将|0⟩变为(|0⟩+|1⟩)/√2，将|1⟩变为(|0⟩-|1⟩)/√2

这就是"量子叠加"的核心操作！

QEntL运行时: HadamardGate.apply()`,
                        demo: 'H q0',
                        action: '尝试在编辑器中输入"H q0"并运行'
                    },
                    {
                        title: '量子测量',
                        content: `测量会让量子态"坍缩"。

测量叠加态(|0⟩+|1⟩)/√2时：
- 50%概率得到0
- 50%概率得到1

测量后量子态变为确定的|0⟩或|1⟩

QEntL运行时: QuantumState.measure()`,
                        demo: 'MEASURE q0',
                        action: '添加测量操作，观察波函数坍缩'
                    }
                ]
            },
            {
                id: 'entanglement',
                title: '量子纠缠',
                description: '学习创建和使用量子纠缠',
                steps: [
                    {
                        title: 'Bell态',
                        content: `Bell态是最简单的量子纠缠态。

创建步骤：
1. 对第一个量子比特应用H门
2. 对两个量子比特应用CNOT门

结果：|00⟩+|11⟩ 的纠缠态

测量第一个比特，第二个会立即"坍缩"到相同值！`,
                        demo: 'H q0\nCNOT q0 q1',
                        action: '创建Bell态，然后分别测量两个量子比特'
                    },
                    {
                        title: 'CNOT门',
                        content: `CNOT（受控NOT）门有两个输入：
- 控制比特
- 目标比特

当控制比特为|1⟩时，翻转目标比特。

QEntL运行时: CNOTGate.apply()`,
                        demo: 'CNOT q0 q1',
                        action: '观察CNOT门的效果'
                    }
                ]
            },
            {
                id: 'algorithms',
                title: '量子算法',
                description: '实现经典量子算法',
                steps: [
                    {
                        title: 'Grover搜索',
                        content: `Grover算法可以在√N次内找到目标。

经典搜索：需要平均N/2次
Grover搜索：只需√N次

这是量子计算的第一个"杀手级应用"！`,
                        demo: 'GROVER 5 4',
                        action: '运行Grover搜索演示'
                    },
                    {
                        title: '量子傅里叶变换',
                        content: `QFT是许多量子算法的基础。

它可以将周期性问题转化为可测量的问题。

Shor算法就用QFT来分解大数！`,
                        demo: 'QFT 4',
                        action: '运行QFT演示'
                    }
                ]
            },
            {
                id: 'qentl_basics',
                title: 'QEntL语言基础',
                description: '学习QEntL量子编程语言',
                steps: [
                    {
                        title: 'QEntL程序结构',
                        content: `QEntL支持三语编程（中文/英文/彝文）。

基本结构：
\`\`\`
quantum_function main(): Integer {
    // 创建量子叠加态
    qstate = QuantumState.createSuperposition();
    // 量子测量
    result = qstate.measure();
    return 0;
}
\`\`\``,
                        demo: '# QEntL示例\nH q0\nMEASURE q0',
                        action: '体验QBC字节码与QEntL的对应关系'
                    },
                    {
                        title: '量子类型系统',
                        content: `QEntL提供量子专用类型：

- quantum_class: 量子类
- quantum_interface: 量子接口
- quantum_enum: 量子枚举
- quantum_function: 量子函数

这些类型支持量子态的创建、操作和测量。`,
                        demo: '# 量子门操作\nX q0\nY q1\nZ q2',
                        action: '尝试不同的量子门操作'
                    }
                ]
            }
        ];
    }
    
    // 加载学习进度
    loadProgress() {
        try {
            const data = localStorage.getItem('qvm-tutorial-progress');
            return data ? JSON.parse(data) : [];
        } catch (e) {
            return [];
        }
    }
    
    // 保存学习进度
    saveProgress() {
        localStorage.setItem('qvm-tutorial-progress', JSON.stringify(this.completedLessons));
    }
    
    // 获取当前课程
    getCurrentLesson() {
        return this.lessons[this.currentLesson];
    }
    
    // 获取当前步骤
    getCurrentStep() {
        const lesson = this.getCurrentLesson();
        return lesson ? lesson.steps[this.currentStep] : null;
    }
    
    // 下一步
    nextStep() {
        const lesson = this.getCurrentLesson();
        if (this.currentStep < lesson.steps.length - 1) {
            this.currentStep++;
        } else if (this.currentLesson < this.lessons.length - 1) {
            this.currentLesson++;
            this.currentStep = 0;
        }
    }
    
    // 上一步
    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
        } else if (this.currentLesson > 0) {
            this.currentLesson--;
            const prevLesson = this.lessons[this.currentLesson];
            this.currentStep = prevLesson.steps.length - 1;
        }
    }
    
    // 标记课程完成
    completeLesson(lessonId) {
        if (!this.completedLessons.includes(lessonId)) {
            this.completedLessons.push(lessonId);
            this.saveProgress();
        }
    }
    
    // 获取进度百分比
    getProgress() {
        const total = this.lessons.length;
        const completed = this.completedLessons.length;
        return Math.round((completed / total) * 100);
    }
}

// 导出给全局使用
if (typeof window !== 'undefined') {
    window.QuantumTutorial = QuantumTutorial;
}
