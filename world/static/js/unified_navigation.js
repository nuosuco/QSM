// 统一导航交互脚本
// 负责导航栏、量子态矩阵和模块导航的交互逻辑

class UnifiedNavigation {
    constructor() {
        this.initialized = false;
        this.quantumStateBtn = null;
        this.quantumStateMatrix = null;
        this.userMenuBtn = null;
        this.userMenu = null;
        this.mobileMenuBtn = null;
        this.mobileNavMenu = null;
        this.navOverlay = null;
        this.currentModel = window.appConfig ? window.appConfig.currentModel : 'SYSTEM';
    }

    initialize() {
        if (this.initialized) return;
        
        // 获取元素引用
        this.quantumStateBtn = document.querySelector('.quantum-state-btn');
        this.quantumStateMatrix = document.querySelector('.quantum-state-matrix');
        this.userMenuBtn = document.getElementById('userMenuBtn');
        this.userMenu = document.getElementById('userMenu');
        this.mobileMenuBtn = document.getElementById('mobileMenuBtn');
        this.mobileNavMenu = document.getElementById('mobileNavMenu');
        this.navOverlay = document.getElementById('navOverlay');
        
        // 初始化事件
        this._initializeEvents();
        this._highlightCurrentPage();
        
        this.initialized = true;
        console.log('统一导航已初始化');
    }
    
    _initializeEvents() {
        // 用户菜单交互
        if (this.userMenuBtn && this.userMenu) {
            this.userMenuBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.userMenu.classList.toggle('show');
            });
            
            document.addEventListener('click', (e) => {
                if (!this.userMenu.contains(e.target) && !this.userMenuBtn.contains(e.target)) {
                    this.userMenu.classList.remove('show');
                }
            });
        }
        
        // 移动端菜单交互
        if (this.mobileMenuBtn && this.mobileNavMenu && this.navOverlay) {
            this.mobileMenuBtn.addEventListener('click', () => {
                this.mobileNavMenu.classList.toggle('show');
                this.navOverlay.classList.toggle('show');
                document.body.classList.toggle('menu-open');
            });
            
            this.navOverlay.addEventListener('click', () => {
                this.mobileNavMenu.classList.remove('show');
                this.navOverlay.classList.remove('show');
                document.body.classList.remove('menu-open');
            });
        }
        
        // 量子态矩阵按钮交互
        if (this.quantumStateBtn && this.quantumStateMatrix) {
            this.quantumStateBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this._toggleQuantumStateMatrix();
            });
            
            // 点击页面其他区域关闭矩阵
            document.addEventListener('click', (e) => {
                if (!this.quantumStateMatrix.contains(e.target) && !this.quantumStateBtn.contains(e.target)) {
                    this._hideQuantumStateMatrix();
                }
            });
        }
    }
    
    _toggleQuantumStateMatrix() {
        // 如果WeQMultimodal已加载，使用其显示矩阵方法
        if (window.WeQMultimodal && window.WeQMultimodal.interactions) {
            window.WeQMultimodal.interactions.showInteractionMatrix();
            return;
        }
        
        // 否则使用简单的显示/隐藏切换
        if (this.quantumStateMatrix.classList.contains('matrix-show')) {
            this._hideQuantumStateMatrix();
        } else {
            this._showQuantumStateMatrix();
        }
    }
    
    _showQuantumStateMatrix() {
        this.quantumStateMatrix.classList.remove('matrix-hide');
        this.quantumStateMatrix.classList.add('matrix-show');
        
        // 如果矩阵尚未创建，则创建
        if (this.quantumStateMatrix.children.length <= 0) {
            this._createSimpleInteractionMatrix();
        }
    }
    
    _hideQuantumStateMatrix() {
        this.quantumStateMatrix.classList.remove('matrix-show');
        this.quantumStateMatrix.classList.add('matrix-hide');
    }
    
    _createSimpleInteractionMatrix() {
        const matrixHeader = document.createElement('div');
        matrixHeader.className = 'matrix-header';
        matrixHeader.innerHTML = `
            <h3>量子态交互矩阵</h3>
            <button class="close-matrix-btn">&times;</button>
        `;
        
        const interactionMatrix = document.createElement('div');
        interactionMatrix.className = 'interaction-matrix';
        
        // 简易模式下的交互类型
        const interactionTypes = [
            { icon: 'fas fa-comment', label: '文本', mode: 'text' },
            { icon: 'fas fa-microphone', label: '语音', mode: 'voice' },
            { icon: 'fas fa-image', label: '图像', mode: 'image' },
            { icon: 'fas fa-video', label: '视频', mode: 'video' },
            { icon: 'fas fa-code', label: '代码', mode: 'code' },
            { icon: 'fas fa-file', label: '文件', mode: 'file' },
            { icon: 'fas fa-chart-bar', label: '数据', mode: 'data' },
            { icon: 'fas fa-paint-brush', label: '绘画', mode: 'drawing' },
            { icon: 'fas fa-cogs', label: '系统', mode: 'system' }
        ];
        
        interactionTypes.forEach(type => {
            const cell = document.createElement('div');
            cell.className = 'matrix-cell';
            cell.dataset.mode = type.mode;
            cell.innerHTML = `
                <i class="${type.icon}"></i>
                <span>${type.label}</span>
            `;
            
            // 简单的点击处理
            cell.addEventListener('click', () => {
                alert(`已选择${type.label}交互模式。请加载高级交互模块以使用完整功能。`);
                this._hideQuantumStateMatrix();
            });
            
            interactionMatrix.appendChild(cell);
        });
        
        this.quantumStateMatrix.appendChild(matrixHeader);
        this.quantumStateMatrix.appendChild(interactionMatrix);
        
        // 关闭按钮事件
        const closeBtn = matrixHeader.querySelector('.close-matrix-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this._hideQuantumStateMatrix();
            });
        }
    }
    
    _highlightCurrentPage() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (currentPath === href || (href !== '/' && currentPath.startsWith(href))) {
                link.classList.add('active');
            } else if (href === '/' && currentPath === '/') {
                link.classList.add('active');
            }
        });
    }
}

// 初始化统一导航
document.addEventListener('DOMContentLoaded', function() {
    window.unifiedNavigation = new UnifiedNavigation();
    window.unifiedNavigation.initialize();
}); 

/*
/*
量子基因编码: QE-UNI-44E92BEA552A
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
