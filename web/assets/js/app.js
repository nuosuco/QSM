// QSM量子协同创新生态系统 - 主应用
class QSMSystem {
    constructor() {
        this.tasks = [];
        this.agents = [];
        this.memories = [];
        this.entanglements = [];
        this.init();
    }

    init() {
        this.loadInitialData();
        this.bindEvents();
        this.render();
        this.startQuantumBackground();
    }

    // 加载初始数据
    loadInitialData() {
        // 初始化任务（叠加态任务）
        this.tasks = [
            {
                id: 1,
                title: 'QSM量子叠加态模型开发',
                description: '开发QSM量子叠加态模型，解决记忆和连续性问题',
                priority: 'high',
                status: 'active',
                createdAt: new Date().toISOString()
            },
            {
                id: 2,
                title: '代理培训学习考核',
                description: '完成所有代理的培训学习和考核，确保掌握核心文档',
                priority: 'high',
                status: 'active',
                createdAt: new Date().toISOString()
            },
            {
                id: 3,
                title: '量子纠缠协同网络',
                description: '建立代理间量子纠缠协同网络，实现深度关联',
                priority: 'medium',
                status: 'active',
                createdAt: new Date().toISOString()
            },
            {
                id: 4,
                title: '量子动态文件系统',
                description: '设计和实现量子动态文件系统作为QSM基础层',
                priority: 'medium',
                status: 'active',
                createdAt: new Date().toISOString()
            },
            {
                id: 5,
                title: 'QEntL量子操作系统',
                description: '开发QEntL量子操作系统作为QSM中间层',
                priority: 'medium',
                status: 'active',
                createdAt: new Date().toISOString()
            },
            {
                id: 6,
                title: 'moltbot框架移植',
                description: '将moltbot框架移植到QSM并升级为量子叠加态模型',
                priority: 'low',
                status: 'pending',
                createdAt: new Date().toISOString()
            }
        ];

        // 初始化代理
        this.agents = [
            {
                id: 1,
                name: '小趣WeQ',
                role: '主代理',
                avatar: '⚛',
                status: 'online',
                tasks: 6,
                createdAt: '2026-02-07'
            },
            {
                id: 2,
                name: '伦理监察代理',
                role: '高级代理',
                avatar: '👁',
                status: 'online',
                tasks: 3,
                createdAt: '2026-02-07'
            },
            {
                id: 3,
                name: '知识管理代理',
                role: '高级代理',
                avatar: '📚',
                status: 'online',
                tasks: 4,
                createdAt: '2026-02-07'
            },
            {
                id: 4,
                name: '项目管理代理',
                role: '基础代理',
                avatar: '📊',
                status: 'online',
                tasks: 2,
                createdAt: '2026-02-07'
            },
            {
                id: 5,
                name: '技能开发代理',
                role: '基础代理',
                avatar: '🛠',
                status: 'offline',
                tasks: 1,
                createdAt: '2026-02-07'
            },
            {
                id: 6,
                name: '沟通协调代理',
                role: '基础代理',
                avatar: '🤝',
                status: 'offline',
                tasks: 1,
                createdAt: '2026-02-07'
            }
        ];

        // 初始化记忆
        this.memories = [
            {
                id: 1,
                time: '2026-02-07 11:15',
                content: '已创建5个专业代理并分配工作：伦理监察、知识管理、项目管理、技能开发、沟通协调'
            },
            {
                id: 2,
                time: '2026-02-07 11:25',
                content: '项目管理代理完成详细项目管理计划，三阶段工作同步计划已制定'
            },
            {
                id: 3,
                time: '2026-02-07 11:52',
                content: '知识管理代理紧急完成伦理培训第一讲材料，包含三大圣律完整定义'
            },
            {
                id: 4,
                time: '2026-02-09 07:56',
                content: '制定今日工作计划v2，加入实际编程与选拔机制，目标开发QSM量子叠加态模型'
            },
            {
                id: 5,
                time: '2026-02-12 09:00',
                content: '用户指令：完成QSM项目开发，Web目录为正式服务用户目录，绑定som.top域名'
            }
        ];

        // 初始化量子纠缠
        this.entanglements = [
            { from: 1, to: 2, strength: 0.95 },
            { from: 1, to: 3, strength: 0.92 },
            { from: 1, to: 4, strength: 0.88 },
            { from: 1, to: 5, strength: 0.85 },
            { from: 1, to: 6, strength: 0.85 },
            { from: 2, to: 3, strength: 0.90 },
            { from: 3, to: 4, strength: 0.87 },
            { from: 2, to: 4, strength: 0.82 }
        ];
    }

    // 绑定事件
    bindEvents() {
        // 导航按钮
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.dataset.view;
                this.switchView(view);
            });
        });

        // 添加任务按钮
        document.getElementById('addTaskBtn').addEventListener('click', () => {
            this.showModal('taskModal');
        });

        // 创建代理按钮
        document.getElementById('createAgentBtn').addEventListener('click', () => {
            this.alert('代理创建功能开发中...');
        });

        // 保存任务按钮
        document.getElementById('saveTaskBtn').addEventListener('click', () => {
            this.createTask();
        });

        // 关闭模态框
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.hideModal(btn.closest('.modal'));
            });
        });

        // 点击模态框外部关闭
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal(modal);
                }
            });
        });
    }

    // 切换视图
    switchView(viewName) {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.view === viewName) {
                btn.classList.add('active');
            }
        });

        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });

        document.getElementById(viewName + 'View').classList.add('active');

        // 特殊处理：切换到纠缠视图时绘制画布
        if (viewName === 'entanglement') {
            setTimeout(() => this.drawEntanglement(), 100);
        }
    }

    // 显示模态框
    showModal(modalId) {
        document.getElementById(modalId).classList.add('active');
    }

    // 隐藏模态框
    hideModal(modal) {
        modal.classList.remove('active');
    }

    // 创建任务
    createTask() {
        const title = document.getElementById('taskTitle').value;
        const desc = document.getElementById('taskDesc').value;
        const priority = document.getElementById('taskPriority').value;

        if (!title) {
            this.alert('请输入任务名称');
            return;
        }

        const task = {
            id: Date.now(),
            title,
            description: desc || '无描述',
            priority,
            status: 'active',
            createdAt: new Date().toISOString()
        };

        this.tasks.push(task);
        this.renderTasks();
        this.hideModal(document.getElementById('taskModal'));

        // 清空表单
        document.getElementById('taskTitle').value = '';
        document.getElementById('taskDesc').value = '';
        document.getElementById('taskPriority').value = 'medium';

        this.alert('✅ 叠加态任务创建成功！');
    }

    // 渲染
    render() {
        this.renderTasks();
        this.renderAgents();
        this.renderMemory();
        this.drawEntanglement();
    }

    // 渲染任务
    renderTasks() {
        const taskGrid = document.getElementById('taskGrid');
        const activeTasks = this.tasks.filter(t => t.status === 'active');

        taskGrid.innerHTML = activeTasks.map(task => `
            <div class="task-card">
                <div class="task-header">
                    <div>
                        <div class="task-title">${task.title}</div>
                        <div class="priority-indicator priority-${task.priority}">
                            ${task.priority === 'high' ? '⚡ 高优先级' : task.priority === 'medium' ? '🔵 中优先级' : '⚪ 低优先级'}
                        </div>
                    </div>
                </div>
                <div class="task-desc">${task.description}</div>
                <div class="task-meta">
                    <span>🕐 ${new Date(task.createdAt).toLocaleString('zh-CN')}</span>
                    <span>🔄 叠加态运行中</span>
                </div>
            </div>
        `).join('');
    }

    // 渲染代理
    renderAgents() {
        const agentsGrid = document.getElementById('agentsGrid');

        agentsGrid.innerHTML = this.agents.map(agent => `
            <div class="agent-card">
                <div class="agent-avatar">${agent.avatar}</div>
                <div class="agent-name">${agent.name}</div>
                <div class="agent-role">${agent.role}</div>
                <div class="agent-status ${agent.status === 'online' ? 'online' : 'offline'}">
                    ${agent.status === 'online' ? '● 在线 - 叠加态工作' : '● 离线'}
                </div>
                <div class="agent-meta">
                    📊 参与任务: ${agent.tasks} 个<br>
                    🎯 创建时间: ${agent.createdAt}
                </div>
            </div>
        `).join('');
    }

    // 渲染记忆
    renderMemory() {
        // 更新统计
        document.getElementById('memoryCount').textContent = this.memories.length;
        document.getElementById('continuityScore').textContent = '95%';

        // 渲染时间线
        const timeline = document.getElementById('memoryTimeline');
        timeline.innerHTML = this.memories.map(memory => `
            <div class="timeline-item">
                <div class="timeline-time">${memory.time}</div>
                <div class="timeline-content">${memory.content}</div>
            </div>
        `).join('');
    }

    // 绘制量子纠缠网络
    drawEntanglement() {
        const canvas = document.getElementById('entanglementCanvas');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;

        // 清空画布
        ctx.clearRect(0, 0, width, height);

        // 代理节点位置
        const nodePositions = [];
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = 150;

        this.agents.forEach((agent, index) => {
            const angle = (index / this.agents.length) * 2 * Math.PI - Math.PI / 2;
            nodePositions.push({
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle),
                agent
            });
        });

        // 绘制纠缠线
        this.entanglements.forEach(entanglement => {
            const fromNode = nodePositions.find(n => n.agent.id === entanglement.from);
            const toNode = nodePositions.find(n => n.agent.id === entanglement.to);

            if (fromNode && toNode) {
                const gradient = ctx.createLinearGradient(fromNode.x, fromNode.y, toNode.x, toNode.y);
                gradient.addColorStop(0, 'rgba(102, 126, 234, 0.8)');
                gradient.addColorStop(1, 'rgba(118, 75, 162, 0.8)');

                ctx.beginPath();
                ctx.moveTo(fromNode.x, fromNode.y);
                ctx.lineTo(toNode.x, toNode.y);
                ctx.strokeStyle = gradient;
                ctx.lineWidth = entanglement.strength * 3;
                ctx.stroke();

                // 绘制纠缠强度标签
                const midX = (fromNode.x + toNode.x) / 2;
                const midY = (fromNode.y + toNode.y) / 2;
                ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
                ctx.font = '11px Arial';
                ctx.textAlign = 'center';
                ctx.fillText(`${(entanglement.strength * 100).toFixed(0)}%`, midX, midY);
            }
        });

        // 绘制节点
        nodePositions.forEach(pos => {
            // 节点圆圈
            ctx.beginPath();
            ctx.arc(pos.x, pos.y, 30, 0, 2 * Math.PI);
            ctx.fillStyle = pos.agent.status === 'online' ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)';
            ctx.fill();
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
            ctx.lineWidth = 2;
            ctx.stroke();

            // 头像
            ctx.fillStyle = 'white';
            ctx.font = '28px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(pos.agent.avatar, pos.x, pos.y);

            // 名称
            ctx.fillStyle = 'white';
            ctx.font = '12px Arial';
            ctx.fillText(pos.agent.name, pos.x, pos.y + 45);
        });
    }

    // 启动量子背景动画
    startQuantumBackground() {
        setInterval(() => {
            // 模拟量子态波动
            const overlay = document.getElementById('quantumOverlay');
            if (overlay) {
                const opacity = 0.3 + Math.random() * 0.3;
                overlay.style.opacity = opacity;
            }
        }, 2000);

        // 模拟实时工作广播
        setInterval(() => {
            if (this.tasks.filter(t => t.status === 'active').length > 0) {
                const activeTask = this.tasks.filter(t => t.status === 'active')[Math.floor(Math.random() * this.tasks.filter(t => t.status === 'active').length)];
                // 可以在这里添加实时通知
            }
        }, 10000);
    }

    // 简单的alert函数
    alert(message) {
        const alertBox = document.createElement('div');
        alertBox.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(34, 197, 94, 0.95);
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            animation: fadeIn 0.3s ease;
            max-width: 300px;
        `;
        alertBox.textContent = message;
        document.body.appendChild(alertBox);

        setTimeout(() => {
            alertBox.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(alertBox);
            }, 300);
        }, 3000);
    }
}

// 初始化系统
document.addEventListener('DOMContentLoaded', () => {
    window.qsmSystem = new QSMSystem();
});
