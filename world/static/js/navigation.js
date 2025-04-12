// 导航栏交互脚本

document.addEventListener('DOMContentLoaded', function() {
    // 用户菜单交互
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userMenu = document.getElementById('userMenu');
    
    if (userMenuBtn && userMenu) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userMenu.classList.toggle('show');
        });
        
        document.addEventListener('click', function(e) {
            if (!userMenu.contains(e.target) && !userMenuBtn.contains(e.target)) {
                userMenu.classList.remove('show');
            }
        });
    }
    
    // 移动端菜单交互
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileNavMenu = document.getElementById('mobileNavMenu');
    const navOverlay = document.getElementById('navOverlay');
    
    if (mobileMenuBtn && mobileNavMenu && navOverlay) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileNavMenu.classList.toggle('show');
            navOverlay.classList.toggle('show');
            document.body.classList.toggle('menu-open');
        });
        
        navOverlay.addEventListener('click', function() {
            mobileNavMenu.classList.remove('show');
            navOverlay.classList.remove('show');
            document.body.classList.remove('menu-open');
        });
    }
    
    // 量子态矩阵按钮交互
    const quantumStateBtn = document.querySelector('.quantum-state-btn');
    const quantumStateMatrix = document.querySelector('.quantum-state-matrix');
    
    if (quantumStateBtn && quantumStateMatrix) {
        quantumStateBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // 如果WeQMultimodal已加载，使用其显示矩阵方法
            if (window.WeQMultimodal && window.WeQMultimodal.interactions) {
                window.WeQMultimodal.interactions.showInteractionMatrix();
            } else {
                // 否则使用简单的显示/隐藏切换
                if (quantumStateMatrix.classList.contains('matrix-show')) {
                    quantumStateMatrix.classList.remove('matrix-show');
                    quantumStateMatrix.classList.add('matrix-hide');
                } else {
                    quantumStateMatrix.classList.remove('matrix-hide');
                    quantumStateMatrix.classList.add('matrix-show');
                    
                    // 填充矩阵内容（如果尚未填充）
                    if (quantumStateMatrix.children.length <= 0) {
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
                            { icon: 'fas fa-comment', label: '文本' },
                            { icon: 'fas fa-microphone', label: '语音' },
                            { icon: 'fas fa-image', label: '图像' },
                            { icon: 'fas fa-video', label: '视频' },
                            { icon: 'fas fa-code', label: '代码' },
                            { icon: 'fas fa-file', label: '文件' },
                            { icon: 'fas fa-chart-bar', label: '数据' },
                            { icon: 'fas fa-paint-brush', label: '绘画' },
                            { icon: 'fas fa-cogs', label: '系统' }
                        ];
                        
                        interactionTypes.forEach(type => {
                            const cell = document.createElement('div');
                            cell.className = 'matrix-cell';
                            cell.innerHTML = `
                                <i class="${type.icon}"></i>
                                <span>${type.label}</span>
                            `;
                            interactionMatrix.appendChild(cell);
                        });
                        
                        quantumStateMatrix.appendChild(matrixHeader);
                        quantumStateMatrix.appendChild(interactionMatrix);
                        
                        // 关闭按钮事件
                        const closeBtn = matrixHeader.querySelector('.close-matrix-btn');
                        if (closeBtn) {
                            closeBtn.addEventListener('click', function() {
                                quantumStateMatrix.classList.remove('matrix-show');
                                quantumStateMatrix.classList.add('matrix-hide');
                            });
                        }
                    }
                }
            }
        });
        
        // 点击页面其他区域关闭矩阵
        document.addEventListener('click', function(e) {
            if (!quantumStateMatrix.contains(e.target) && !quantumStateBtn.contains(e.target)) {
                quantumStateMatrix.classList.remove('matrix-show');
                quantumStateMatrix.classList.add('matrix-hide');
            }
        });
    }
    
    // 高亮当前活动页面
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
}); 

/*
/*
量子基因编码: QE-NAV-6788F0085F55
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
