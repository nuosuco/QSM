/**
 * QEntL Web操作系统 - 量子态可视化模块
 * 基于量子叠加态神经网络引擎
 */

class QuantumVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.canvas = null;
        this.ctx = null;
        this.quantumStates = [];
        this.animationId = null;
        this.init();
    }
    
    init() {
        // 创建画布
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.container.clientWidth || 400;
        this.canvas.height = this.container.clientHeight || 300;
        this.container.appendChild(this.canvas);
        this.ctx = this.canvas.getContext('2d');
        
        // 初始化量子态
        this.quantumStates = [
            { state: '|0⟩', probability: 0.5, phase: 0, color: '#4ecdc4' },
            { state: '|1⟩', probability: 0.5, phase: Math.PI, color: '#ff6b6b' },
            { state: '|+⟩', probability: 0.3, phase: Math.PI/4, color: '#45b7d1' },
            { state: '|-⟩', probability: 0.3, phase: -Math.PI/4, color: '#96ceb4' }
        ];
        
        this.animate();
    }
    
    // 绘制量子态球（Bloch球简化版）
    drawBlochSphere() {
        const cx = this.canvas.width / 2;
        const cy = this.canvas.height / 2;
        const r = Math.min(cx, cy) * 0.7;
        
        // 清空画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制背景
        this.ctx.fillStyle = 'rgba(10, 10, 26, 0.5)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制球体轮廓
        this.ctx.strokeStyle = 'rgba(138, 135, 255, 0.3)';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.arc(cx, cy, r, 0, Math.PI * 2);
        this.ctx.stroke();
        
        // 绘制坐标轴
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        this.ctx.beginPath();
        // X轴
        this.ctx.moveTo(cx - r, cy);
        this.ctx.lineTo(cx + r, cy);
        // Y轴
        this.ctx.moveTo(cx, cy - r);
        this.ctx.lineTo(cx, cy + r);
        this.ctx.stroke();
        
        // 绘制量子态点
        const time = Date.now() / 1000;
        this.quantumStates.forEach((qs, i) => {
            const angle = qs.phase + time;
            const x = cx + Math.cos(angle) * r * 0.6 * qs.probability;
            const y = cy + Math.sin(angle) * r * 0.6 * qs.probability;
            
            // 发光效果
            const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, 20);
            gradient.addColorStop(0, qs.color);
            gradient.addColorStop(1, 'transparent');
            this.ctx.fillStyle = gradient;
            this.ctx.beginPath();
            this.ctx.arc(x, y, 15, 0, Math.PI * 2);
            this.ctx.fill();
            
            // 核心点
            this.ctx.fillStyle = qs.color;
            this.ctx.beginPath();
            this.ctx.arc(x, y, 5, 0, Math.PI * 2);
            this.ctx.fill();
            
            // 标签
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '12px monospace';
            this.ctx.fillText(qs.state, x + 10, y - 10);
        });
    }
    
    // 绘制量子概率条
    drawProbabilityBars() {
        const barWidth = 60;
        const barSpacing = 20;
        const startX = 20;
        const startY = this.canvas.height - 30;
        const maxHeight = this.canvas.height - 60;
        
        this.quantumStates.forEach((qs, i) => {
            const x = startX + i * (barWidth + barSpacing);
            const height = qs.probability * maxHeight;
            
            // 渐变条
            const gradient = this.ctx.createLinearGradient(x, startY, x, startY - height);
            gradient.addColorStop(0, qs.color);
            gradient.addColorStop(1, 'rgba(138, 135, 255, 0.3)');
            
            this.ctx.fillStyle = gradient;
            this.ctx.fillRect(x, startY - height, barWidth, height);
            
            // 边框
            this.ctx.strokeStyle = qs.color;
            this.ctx.strokeRect(x, startY - height, barWidth, height);
            
            // 标签
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '12px monospace';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(qs.state, x + barWidth/2, startY + 15);
            this.ctx.fillText((qs.probability * 100).toFixed(0) + '%', x + barWidth/2, startY - height - 5);
        });
    }
    
    // 动画循环
    animate() {
        this.drawBlochSphere();
        this.drawProbabilityBars();
        this.animationId = requestAnimationFrame(() => this.animate());
    }
    
    // 更新量子态
    updateStates(newStates) {
        this.quantumStates = newStates;
    }
    
    // 停止动画
    stop() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
    }
}

// 导出
window.QuantumVisualizer = QuantumVisualizer;
