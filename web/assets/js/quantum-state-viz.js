/**
 * QSM - 量子态可视化组件
 * 版本: v0.1.0
 * 量子基因编码: QGC-STATE-VIZ-20260302
 * 
 * 布洛赫球和量子态可视化
 */

class QuantumStateVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        this.radius = 100;
        this.centerX = 150;
        this.centerY = 150;
    }

    // 绘制布洛赫球
    drawBlochSphere(state = { alpha: 1, beta: 0 }) {
        if (!this.ctx) return;

        const ctx = this.ctx;
        const cx = this.centerX;
        const cy = this.centerY;
        const r = this.radius;

        // 清空画布
        ctx.clearRect(0, 0, 300, 300);

        // 绘制球体框架
        ctx.strokeStyle = 'rgba(138, 135, 255, 0.3)';
        ctx.lineWidth = 1;

        // 外圆
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.stroke();

        // XY平面圆
        ctx.beginPath();
        ctx.ellipse(cx, cy, r, r * 0.3, 0, 0, Math.PI * 2);
        ctx.stroke();

        // XZ平面圆
        ctx.beginPath();
        ctx.ellipse(cx, cy, r * 0.3, r, 0, 0, Math.PI * 2);
        ctx.stroke();

        // YZ平面圆
        ctx.beginPath();
        ctx.ellipse(cx, cy, r, r * 0.3, Math.PI / 2, 0, Math.PI * 2);
        ctx.stroke();

        // 坐标轴
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.beginPath();
        ctx.moveTo(cx - r - 20, cy);
        ctx.lineTo(cx + r + 20, cy);
        ctx.moveTo(cx, cy - r - 20);
        ctx.lineTo(cx, cy + r + 20);
        ctx.stroke();

        // 轴标签
        ctx.fillStyle = '#8a87ff';
        ctx.font = '12px monospace';
        ctx.fillText('|0⟩', cx - 10, cy - r - 25);
        ctx.fillText('|1⟩', cx - 10, cy + r + 35);
        ctx.fillText('+x', cx + r + 25, cy + 5);
        ctx.fillText('-x', cx - r - 35, cy + 5);

        // 计算量子态在布洛赫球上的位置
        const alpha = state.alpha;
        const beta = state.beta;
        const theta = 2 * Math.acos(Math.abs(alpha));
        const phi = Math.atan2(beta.imag || 0, beta.real || beta);

        // 球面坐标转平面坐标（简化的正交投影）
        const x = r * Math.sin(theta) * Math.cos(phi);
        const y = r * Math.cos(theta);
        const z = r * Math.sin(theta) * Math.sin(phi);

        // 绘制量子态点
        const px = cx + x * 0.8;
        const py = cy - y * 0.8;

        // 绘制状态向量
        ctx.strokeStyle = '#4ecdc4';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(px, py);
        ctx.stroke();

        // 绘制状态点
        ctx.fillStyle = '#4ecdc4';
        ctx.beginPath();
        ctx.arc(px, py, 8, 0, Math.PI * 2);
        ctx.fill();

        // 绘制概率指示
        const prob0 = Math.abs(alpha) ** 2;
        const prob1 = Math.abs(beta) ** 2;

        ctx.fillStyle = 'rgba(78, 205, 196, 0.3)';
        ctx.fillRect(10, 270, 280, 25);

        ctx.fillStyle = '#4ecdc4';
        ctx.fillRect(10, 270, 280 * prob0, 25);

        ctx.fillStyle = '#fff';
        ctx.font = '11px monospace';
        ctx.fillText(`P(|0⟩) = ${(prob0 * 100).toFixed(1)}%`, 15, 287);
        ctx.fillText(`P(|1⟩) = ${(prob1 * 100).toFixed(1)}%`, 150, 287);

        return { theta, phi, prob0, prob1 };
    }

    // 绘制量子比特网格
    drawQubitGrid(qubits) {
        if (!this.ctx) return;

        const ctx = this.ctx;
        ctx.clearRect(0, 0, 300, 300);

        const cols = Math.ceil(Math.sqrt(qubits.length));
        const cellSize = 280 / cols;

        qubits.forEach((qubit, i) => {
            const row = Math.floor(i / cols);
            const col = i % cols;
            const x = 10 + col * cellSize;
            const y = 10 + row * cellSize;

            // 背景
            ctx.fillStyle = 'rgba(138, 135, 255, 0.1)';
            ctx.fillRect(x, y, cellSize - 5, cellSize - 5);

            // 量子比特名称
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 14px monospace';
            ctx.fillText(qubit.name, x + 10, y + 25);

            // 状态
            ctx.fillStyle = '#8a87ff';
            ctx.font = '12px monospace';
            ctx.fillText(qubit.state, x + 10, y + 45);

            // 振幅条
            const alphaWidth = Math.abs(qubit.amplitude.alpha) * (cellSize - 30);
            const betaWidth = Math.abs(qubit.amplitude.beta) * (cellSize - 30);

            ctx.fillStyle = '#4ecdc4';
            ctx.fillRect(x + 10, y + 55, alphaWidth, 8);

            ctx.fillStyle = '#ff6b6b';
            ctx.fillRect(x + 10, y + 68, betaWidth, 8);

            // 标签
            ctx.fillStyle = 'rgba(255,255,255,0.5)';
            ctx.font = '10px monospace';
            ctx.fillText('α', x + 10, y + 63);
            ctx.fillText('β', x + 10, y + 76);
        });
    }

    // 绘制纠缠网络图
    drawEntanglementNetwork(nodes, edges) {
        if (!this.ctx) return;

        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;

        ctx.clearRect(0, 0, width, height);

        // 计算节点位置（圆形布局）
        const positions = {};
        const nodeCount = nodes.length;
        const radius = Math.min(width, height) / 2 - 50;
        const cx = width / 2;
        const cy = height / 2;

        nodes.forEach((node, i) => {
            const angle = (2 * Math.PI * i) / nodeCount - Math.PI / 2;
            positions[node.id] = {
                x: cx + radius * Math.cos(angle),
                y: cy + radius * Math.sin(angle)
            };
        });

        // 绘制边
        edges.forEach(edge => {
            const from = positions[edge.from];
            const to = positions[edge.to];
            if (!from || !to) return;

            ctx.strokeStyle = `rgba(255, 107, 107, ${edge.strength || 0.5})`;
            ctx.lineWidth = 2 * (edge.strength || 0.5);
            ctx.beginPath();
            ctx.moveTo(from.x, from.y);
            ctx.lineTo(to.x, to.y);
            ctx.stroke();

            // 纠缠强度标签
            const midX = (from.x + to.x) / 2;
            const midY = (from.y + to.y) / 2;
            ctx.fillStyle = 'rgba(255, 107, 107, 0.8)';
            ctx.font = '10px monospace';
            ctx.fillText((edge.strength || 1).toFixed(2), midX, midY);
        });

        // 绘制节点
        nodes.forEach(node => {
            const pos = positions[node.id];
            if (!pos) return;

            // 节点圆
            ctx.fillStyle = node.entangled ? '#ff6b6b' : '#8a87ff';
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, 20, 0, Math.PI * 2);
            ctx.fill();

            // 节点标签
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 12px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(node.id, pos.x, pos.y + 5);

            // 状态标签
            ctx.font = '10px monospace';
            ctx.fillText(node.state || '|0⟩', pos.x, pos.y + 35);
        });

        ctx.textAlign = 'left';
    }
}

window.QuantumStateVisualizer = QuantumStateVisualizer;
