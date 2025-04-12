/**
 * 量子测试页面JavaScript
 * 提供量子测试页面所需的交互和可视化功能
 */

document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const qubitCountSelect = document.getElementById('qubit-count');
    const testTypeSelect = document.getElementById('test-type');
    const initializeBtn = document.getElementById('initialize-btn');
    const runTestBtn = document.getElementById('run-test-btn');
    const resetBtn = document.getElementById('reset-btn');
    const resultDisplay = document.getElementById('result-display');
    const canvas = document.getElementById('quantum-canvas');
    const ctx = canvas.getContext('2d');
    
    // 量子测试状态
    let testState = {
        initialized: false,
        qubitCount: 2,
        testType: 'entanglement',
        results: null
    };
    
    // 初始化按钮事件
    initializeBtn.addEventListener('click', function() {
        testState.qubitCount = parseInt(qubitCountSelect.value);
        testState.testType = testTypeSelect.value;
        testState.initialized = true;
        testState.results = null;
        
        // 更新结果显示
        resultDisplay.innerHTML = `
            <p>量子系统已初始化</p>
            <p>量子比特数量: ${testState.qubitCount}</p>
            <p>测试类型: ${getTestTypeName(testState.testType)}</p>
            <p>系统状态: 准备就绪</p>
        `;
        
        // 绘制初始状态
        drawQuantumState();
        
        // 启用运行按钮
        runTestBtn.disabled = false;
    });
    
    // 运行测试按钮事件
    runTestBtn.addEventListener('click', function() {
        if (!testState.initialized) {
            resultDisplay.innerHTML = '<p class="error">错误: 系统未初始化，请先初始化系统</p>';
            return;
        }
        
        // 执行测试
        executeTest();
        
        // 绘制测试结果
        drawTestResults();
    });
    
    // 重置按钮事件
    resetBtn.addEventListener('click', function() {
        testState.initialized = false;
        testState.results = null;
        
        // 更新结果显示
        resultDisplay.innerHTML = '<p class="placeholder-text">运行测试后，结果将显示在这里...</p>';
        
        // 清除画布
        clearCanvas();
        
        // 禁用运行按钮
        runTestBtn.disabled = true;
    });
    
    // 执行测试
    function executeTest() {
        switch (testState.testType) {
            case 'superposition':
                executeSuperpositionTest();
                break;
            case 'entanglement':
                executeEntanglementTest();
                break;
            case 'interference':
                executeInterferenceTest();
                break;
        }
    }
    
    // 执行量子叠加测试
    function executeSuperpositionTest() {
        // 创建叠加态
        const superpositionResults = [];
        const measurements = 100;
        
        for (let i = 0; i < measurements; i++) {
            // 模拟测量结果
            let result = '';
            for (let q = 0; q < testState.qubitCount; q++) {
                result += Math.random() < 0.5 ? '0' : '1';
            }
            superpositionResults.push(result);
        }
        
        // 统计结果
        const resultStats = {};
        superpositionResults.forEach(result => {
            if (!resultStats[result]) {
                resultStats[result] = 0;
            }
            resultStats[result]++;
        });
        
        testState.results = {
            type: 'superposition',
            measurements,
            results: superpositionResults,
            stats: resultStats
        };
        
        // 更新结果显示
        let resultHTML = `
            <h3>量子叠加测试结果</h3>
            <p>完成了 ${measurements} 次测量</p>
            <div class="result-stats">
                <h4>测量结果统计</h4>
                <table>
                    <thead>
                        <tr>
                            <th>量子态</th>
                            <th>次数</th>
                            <th>概率</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        Object.keys(resultStats).sort().forEach(state => {
            const count = resultStats[state];
            const probability = (count / measurements * 100).toFixed(2);
            resultHTML += `
                <tr>
                    <td>|${state}⟩</td>
                    <td>${count}</td>
                    <td>${probability}%</td>
                </tr>
            `;
        });
        
        resultHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        resultDisplay.innerHTML = resultHTML;
    }
    
    // 执行量子纠缠测试
    function executeEntanglementTest() {
        // 模拟贝尔态测量
        const measurements = 100;
        const entanglementResults = [];
        
        for (let i = 0; i < measurements; i++) {
            // 在贝尔态中，测量结果总是相关的
            const firstQubit = Math.random() < 0.5 ? '0' : '1';
            // 对于贝尔态 |00⟩ + |11⟩，第二个量子比特总是与第一个相同
            const secondQubit = firstQubit;
            
            entanglementResults.push({
                first: firstQubit,
                second: secondQubit,
                correlated: firstQubit === secondQubit
            });
        }
        
        // 统计结果
        const correlatedCount = entanglementResults.filter(r => r.correlated).length;
        const correlationPercentage = (correlatedCount / measurements * 100).toFixed(2);
        
        testState.results = {
            type: 'entanglement',
            measurements,
            results: entanglementResults,
            correlatedCount,
            correlationPercentage
        };
        
        // 更新结果显示
        let resultHTML = `
            <h3>量子纠缠测试结果</h3>
            <p>完成了 ${measurements} 次测量</p>
            <div class="result-stats">
                <h4>纠缠相关性</h4>
                <p>相关测量: ${correlatedCount} (${correlationPercentage}%)</p>
                <p>非相关测量: ${measurements - correlatedCount} (${(100 - parseFloat(correlationPercentage)).toFixed(2)}%)</p>
            </div>
        `;
        
        resultDisplay.innerHTML = resultHTML;
    }
    
    // 执行量子干涉测试
    function executeInterferenceTest() {
        // 模拟量子干涉模式
        const patterns = [];
        const patternSize = 10;
        
        for (let i = 0; i < patternSize; i++) {
            patterns[i] = [];
            for (let j = 0; j < patternSize; j++) {
                // 计算干涉强度
                const distance = Math.sqrt((i - patternSize/2)**2 + (j - patternSize/2)**2);
                const angle = Math.atan2(j - patternSize/2, i - patternSize/2);
                const interference = Math.cos(distance * 2 + angle * 4)**2;
                patterns[i][j] = interference;
            }
        }
        
        testState.results = {
            type: 'interference',
            patternSize,
            patterns
        };
        
        // 更新结果显示
        let resultHTML = `
            <h3>量子干涉测试结果</h3>
            <p>生成了 ${patternSize}x${patternSize} 大小的干涉模式</p>
            <div class="interference-pattern">
                <canvas id="interference-canvas" width="200" height="200"></canvas>
            </div>
            <p>干涉模式展示了量子波函数的干涉现象，这在经典计算中是不可能出现的。</p>
        `;
        
        resultDisplay.innerHTML = resultHTML;
        
        // 绘制干涉模式
        setTimeout(() => {
            const interferenceCanvas = document.getElementById('interference-canvas');
            if (interferenceCanvas) {
                const ictx = interferenceCanvas.getContext('2d');
                const cellSize = interferenceCanvas.width / patternSize;
                
                for (let i = 0; i < patternSize; i++) {
                    for (let j = 0; j < patternSize; j++) {
                        const intensity = patterns[i][j];
                        ictx.fillStyle = `rgba(64, 128, 255, ${intensity})`;
                        ictx.fillRect(i * cellSize, j * cellSize, cellSize, cellSize);
                    }
                }
            }
        }, 10);
    }
    
    // 清除画布
    function clearCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    // 绘制量子状态
    function drawQuantumState() {
        clearCanvas();
        
        // 绘制背景
        ctx.fillStyle = '#f0f8ff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // 绘制量子比特
        const qubitRadius = 30;
        const spacing = canvas.width / (testState.qubitCount + 1);
        
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        for (let i = 0; i < testState.qubitCount; i++) {
            const x = spacing * (i + 1);
            const y = canvas.height / 2;
            
            // 绘制量子比特圆形
            ctx.beginPath();
            ctx.arc(x, y, qubitRadius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(64, 128, 255, 0.8)';
            ctx.fill();
            ctx.strokeStyle = '#2c5282';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // 绘制量子比特标签
            ctx.fillStyle = 'white';
            ctx.fillText(`Q${i}`, x, y);
            
            // 如果是纠缠测试，绘制纠缠线
            if (testState.testType === 'entanglement' && i < testState.qubitCount - 1) {
                ctx.beginPath();
                ctx.moveTo(x + qubitRadius, y);
                ctx.lineTo(x + spacing - qubitRadius, y);
                ctx.strokeStyle = 'rgba(64, 128, 255, 0.6)';
                ctx.lineWidth = 3;
                ctx.stroke();
            }
        }
    }
    
    // 绘制测试结果
    function drawTestResults() {
        if (!testState.results) return;
        
        drawQuantumState();
        
        switch (testState.results.type) {
            case 'superposition':
                drawSuperpositionResults();
                break;
            case 'entanglement':
                drawEntanglementResults();
                break;
            case 'interference':
                // 干涉结果在结果区域的canvas中绘制
                break;
        }
    }
    
    // 绘制叠加测试结果
    function drawSuperpositionResults() {
        const stats = testState.results.stats;
        const total = testState.results.measurements;
        
        // 绘制概率分布
        const barWidth = canvas.width / Object.keys(stats).length;
        const maxBarHeight = canvas.height / 3;
        
        ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
        ctx.fillRect(0, canvas.height - maxBarHeight - 20, canvas.width, maxBarHeight + 20);
        
        let i = 0;
        Object.keys(stats).sort().forEach(state => {
            const probability = stats[state] / total;
            const barHeight = probability * maxBarHeight;
            
            ctx.fillStyle = 'rgba(64, 128, 255, 0.7)';
            ctx.fillRect(
                i * barWidth,
                canvas.height - barHeight - 20,
                barWidth - 2,
                barHeight
            );
            
            ctx.fillStyle = 'black';
            ctx.fillText(
                `|${state}⟩`,
                i * barWidth + barWidth / 2,
                canvas.height - 10
            );
            
            i++;
        });
    }
    
    // 绘制纠缠测试结果
    function drawEntanglementResults() {
        const spacing = canvas.width / (testState.qubitCount + 1);
        const qubitRadius = 30;
        
        // 绘制纠缠波
        ctx.strokeStyle = 'rgba(255, 64, 128, 0.3)';
        ctx.lineWidth = 2;
        
        for (let i = 0; i < 5; i++) {
            const amplitude = 20 + i * 5;
            const frequency = 0.05 - i * 0.01;
            const phase = i * 0.2;
            
            ctx.beginPath();
            
            for (let x = 0; x < canvas.width; x++) {
                const y = Math.sin(x * frequency + phase) * amplitude + canvas.height / 2;
                
                if (x === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            
            ctx.stroke();
        }
        
        // 绘制相关性标识
        const correlationPercentage = testState.results.correlationPercentage;
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.font = 'bold 16px Arial';
        ctx.fillText(
            `纠缠相关性: ${correlationPercentage}%`,
            canvas.width / 2,
            40
        );
    }
    
    // 获取测试类型名称
    function getTestTypeName(testType) {
        switch (testType) {
            case 'superposition': return '量子叠加';
            case 'entanglement': return '量子纠缠';
            case 'interference': return '量子干涉';
            default: return testType;
        }
    }
    
    // 初始化界面
    clearCanvas();
    runTestBtn.disabled = true;
}); 

/*
/*
量子基因编码: QE-QUA-2B5E4D4DC976
纠缠状态: 活跃
纠缠对象: ['test/test_common.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
