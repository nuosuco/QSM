/**
 * 量子叠加态模型(QSM) - 量子体验演示页面
 * 处理量子体验页面的交互和功能
 */

// 全局量子UI管理器实例
const quantumUI = {
    isReady: false,
    webQuantum: null,
    storedStates: {},
    entanglementChannels: {},
    currentLayout: 'default'
};

// 在文档加载完成后初始化量子体验
document.addEventListener('DOMContentLoaded', initQuantumExperience);

// 监听量子就绪事件
document.addEventListener('quantum-ready', onQuantumReady);

/**
 * 初始化量子体验
 */
function initQuantumExperience() {
    console.log('初始化量子体验...');
    updateEnvironmentInfo();
    
    // 设置定时更新环境信息（每5秒更新一次）
    setInterval(updateEnvironmentInfo, 5000);
    
    // 设置事件监听器
    setupEventListeners();
    
    // 如果WebQuantum已经就绪（预加载），立即更新UI
    if (window.WebQuantum && window.WebQuantum.isReady) {
        const readyEvent = new CustomEvent('quantum-ready', {
            detail: { client: window.WebQuantum }
        });
        document.dispatchEvent(readyEvent);
    }
}

/**
 * 更新环境信息显示
 */
function updateEnvironmentInfo() {
    const currentTimeEl = document.getElementById('current-time');
    const lightLevelEl = document.getElementById('light-level');
    const userStateEl = document.getElementById('user-state');
    
    if (currentTimeEl) {
        const now = new Date();
        currentTimeEl.textContent = now.toLocaleTimeString();
    }
    
    if (lightLevelEl) {
        const lightLevel = getSimulatedLightLevel();
        lightLevelEl.textContent = `${lightLevel}%`;
        
        // 根据光线级别更新背景色
        document.body.style.backgroundColor = `hsl(210, ${Math.min(30, lightLevel/3)}%, ${90 - lightLevel/5}%)`;
    }
    
    if (userStateEl) {
        const userState = getSimulatedUserState();
        userStateEl.textContent = userState;
    }
    
    // 如果量子准备好了，也更新量子状态
    if (quantumUI.isReady) {
        updateQuantumState();
    }
}

/**
 * 获取模拟的光线水平（基于一天中的时间）
 * @returns {number} 光线水平百分比
 */
function getSimulatedLightLevel() {
    const now = new Date();
    const hour = now.getHours();
    
    // 模拟日出到日落的光线变化
    if (hour < 6) {
        return 10; // 凌晨，光线很低
    } else if (hour < 9) {
        return 10 + ((hour - 6) * 20); // 日出，光线逐渐增加
    } else if (hour < 18) {
        return 70 + Math.sin((hour - 9) * Math.PI / 9) * 30; // 白天，光线波动
    } else if (hour < 21) {
        return 70 - ((hour - 18) * 20); // 日落，光线逐渐减少
    } else {
        return 10; // 晚上，光线很低
    }
}

/**
 * 获取模拟的用户状态（每分钟变化一次）
 * @returns {string} 用户状态描述
 */
function getSimulatedUserState() {
    const now = new Date();
    const minute = now.getMinutes();
    
    // 基于分钟来改变状态
    const states = [
        '专注', '放松', '好奇', '思考',
        '学习', '创造', '探索', '分析'
    ];
    
    const index = minute % states.length;
    return states[index];
}

/**
 * 更新量子状态显示
 */
function updateQuantumState() {
    const stateEl = document.getElementById('quantum-state');
    
    if (!stateEl) return;
    
    if (quantumUI.webQuantum) {
        const state = quantumUI.webQuantum.getCurrentState();
        if (state) {
            const stateType = state.type || '未知';
            const complexity = state.complexity || Math.floor(Math.random() * 100);
            
            stateEl.innerHTML = `
                <div>类型: <span class="state-type">${stateType}</span></div>
                <div>复杂度: <span class="state-complexity">${complexity}</span></div>
                <div>稳定性: <span class="state-stability">${state.stability || (Math.random() * 100).toFixed(2)}%</span></div>
            `;
        } else {
            stateEl.textContent = '等待量子状态初始化...';
        }
    } else {
        stateEl.textContent = '量子模块尚未就绪';
    }
}

/**
 * 设置事件监听器
 */
function setupEventListeners() {
    // 量子导航演示
    const navDemoBtn = document.getElementById('nav-demo-btn');
    if (navDemoBtn) {
        navDemoBtn.addEventListener('click', function() {
            const resultEl = document.getElementById('nav-demo-result');
            resultEl.textContent = '计算路径...';
            
            setTimeout(() => {
                const paths = [];
                for (let i = 0; i < 5; i++) {
                    const efficiency = 80 + Math.floor(Math.random() * 20);
                    const distance = 100 + Math.floor(Math.random() * 900);
                    paths.push(`路径 ${i+1}: 效率 ${efficiency}%, 距离 ${distance}米`);
                }
                
                resultEl.innerHTML = paths.join('<br>');
                
                // 如果量子就绪，添加动画效果
                if (quantumUI.isReady) {
                    resultEl.classList.add('quantum-enhanced');
                }
            }, 1000);
        });
    }
    
    // 量子状态搜索
    const stateSearchBtn = document.getElementById('state-search-btn');
    if (stateSearchBtn) {
        stateSearchBtn.addEventListener('click', function() {
            const searchInput = document.getElementById('state-search-input');
            const resultEl = document.getElementById('state-search-result');
            
            if (!searchInput || !searchInput.value.trim()) {
                resultEl.textContent = '请输入搜索条件';
                return;
            }
            
            resultEl.textContent = '搜索中...';
            
            setTimeout(() => {
                const searchResults = [];
                const searchCount = 3 + Math.floor(Math.random() * 3);
                
                for (let i = 0; i < searchCount; i++) {
                    const match = Math.floor(50 + Math.random() * 50);
                    searchResults.push(`匹配 ${i+1}: ${match}% 相似度, ID: QS-${Math.floor(Math.random() * 10000)}`);
                }
                
                resultEl.innerHTML = searchResults.length 
                    ? searchResults.join('<br>') 
                    : '没有找到匹配的量子状态';
            }, 1500);
        });
    }
    
    // 量子健康检查
    const healthCheckBtn = document.getElementById('health-check-btn');
    if (healthCheckBtn) {
        healthCheckBtn.addEventListener('click', function() {
            const resultEl = document.getElementById('health-check-result');
            resultEl.textContent = '检查中...';
            
            setTimeout(() => {
                const components = [
                    { name: '核心量子处理器', status: '健康', level: 100 },
                    { name: '量子存储', status: '健康', level: 95 },
                    { name: '量子纠缠网络', status: '健康', level: 92 },
                    { name: '量子抽象层', status: '健康', level: 98 }
                ];
                
                let html = '<ul class="health-list">';
                components.forEach(comp => {
                    const statusClass = comp.level > 90 ? 'healthy' : 
                                       comp.level > 70 ? 'warning' : 'critical';
                    html += `<li>
                        <span class="component-name">${comp.name}</span>
                        <span class="status-indicator ${statusClass}"></span>
                        <span class="status-text">${comp.status} (${comp.level}%)</span>
                    </li>`;
                });
                html += '</ul>';
                
                resultEl.innerHTML = html;
            }, 1000);
        });
    }
    
    // 量子并行处理
    const parallelBtn = document.getElementById('parallel-btn');
    if (parallelBtn) {
        parallelBtn.addEventListener('click', function() {
            const resultEl = document.getElementById('parallel-result');
            resultEl.textContent = '处理中...';
            
            let progress = 0;
            const progressUpdate = setInterval(() => {
                progress += 10;
                resultEl.textContent = `处理中... ${progress}%`;
                
                if (progress >= 100) {
                    clearInterval(progressUpdate);
                    
                    const tasks = [];
                    for (let i = 0; i < 8; i++) {
                        const time = (5 + Math.random() * 20).toFixed(2);
                        tasks.push(`任务 ${i+1} 完成，用时: ${time}ms`);
                    }
                    
                    resultEl.innerHTML = tasks.join('<br>') + 
                        '<br><br><strong>所有任务并行完成！</strong>';
                }
            }, 300);
        });
    }
    
    // 量子状态可视化和存储
    const storeStateBtn = document.getElementById('store-state-btn');
    if (storeStateBtn) {
        storeStateBtn.addEventListener('click', storeCurrentState);
    }
    
    const retrieveStateBtn = document.getElementById('retrieve-state-btn');
    if (retrieveStateBtn) {
        retrieveStateBtn.addEventListener('click', retrieveState);
    }
    
    // 量子纠缠通道和消息
    const createChannelBtn = document.getElementById('create-channel-btn');
    if (createChannelBtn) {
        createChannelBtn.addEventListener('click', createEntanglementChannel);
    }
    
    const sendMessageBtn = document.getElementById('send-message-btn');
    if (sendMessageBtn) {
        sendMessageBtn.addEventListener('click', sendQuantumMessage);
    }
    
    // 量子爬虫控制
    const startCrawlerBtn = document.getElementById('start-crawler-btn');
    if (startCrawlerBtn) {
        startCrawlerBtn.addEventListener('click', startQuantumCrawler);
    }
    
    const stopCrawlerBtn = document.getElementById('stop-crawler-btn');
    if (stopCrawlerBtn) {
        stopCrawlerBtn.addEventListener('click', stopQuantumCrawler);
    }
    
    // 重新排列量子交互面板
    const layoutBtns = document.querySelectorAll('.layout-btn');
    layoutBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const layout = this.dataset.layout;
            rearrangePanel(layout);
        });
    });
}

/**
 * 处理量子就绪事件
 */
function onQuantumReady(e) {
    console.log('量子就绪事件触发!');
    quantumUI.isReady = true;
    quantumUI.webQuantum = e.detail.client;
    
    // 更新UI显示量子就绪状态
    document.body.classList.add('quantum-ready');
    const readyIndicator = document.getElementById('quantum-ready-indicator');
    if (readyIndicator) {
        readyIndicator.classList.add('ready');
        readyIndicator.textContent = '量子就绪';
    }
    
    // 启用量子特定功能
    const quantumFeatures = document.querySelectorAll('.quantum-feature');
    quantumFeatures.forEach(el => {
        el.classList.remove('disabled');
        el.removeAttribute('disabled');
    });
    
    // 显示通知
    showNotification('量子模块已就绪', '量子增强功能现已启用，可以使用全部功能。');
    
    // 初始化量子状态显示
    updateQuantumState();
}

/**
 * 显示通知消息
 * @param {string} title - 通知标题
 * @param {string} message - 通知内容
 */
function showNotification(title, message) {
    const notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        // 如果容器不存在，创建一个
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '1000';
        document.body.appendChild(container);
    }
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.innerHTML = `
        <h4>${title}</h4>
        <p>${message}</p>
    `;
    
    // 添加到页面
    document.getElementById('notification-container').appendChild(notification);
    
    // 2秒后自动消失
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
}

/**
 * 存储当前量子状态
 */
function storeCurrentState() {
    const resultEl = document.getElementById('store-state-result');
    
    if (!resultEl) return;
    
    if (!quantumUI.isReady) {
        resultEl.textContent = '量子模块尚未就绪，无法存储状态';
        return;
    }
    
    resultEl.textContent = '存储中...';
    
    // 模拟存储过程
    setTimeout(() => {
        // 生成随机状态ID
        const stateId = `QS-${Math.floor(Math.random() * 10000)}`;
        
        // 模拟存储量子状态
        const storedState = {
            id: stateId,
            timestamp: Date.now(),
            type: '用户生成',
            complexity: Math.floor(60 + Math.random() * 40),
            stability: (80 + Math.random() * 20).toFixed(2) + '%'
        };
        
        // 存储到内存和localStorage
        quantumUI.storedStates[stateId] = storedState;
        try {
            // 尝试存储到localStorage
            const states = JSON.parse(localStorage.getItem('quantumStates') || '{}');
            states[stateId] = storedState;
            localStorage.setItem('quantumStates', JSON.stringify(states));
        } catch (e) {
            console.warn('无法存储到localStorage:', e);
        }
        
        // 更新UI
        resultEl.innerHTML = `
            <div class="success-message">状态存储成功!</div>
            <div>状态ID: <strong>${stateId}</strong></div>
            <div>类型: ${storedState.type}</div>
            <div>复杂度: ${storedState.complexity}</div>
            <div>稳定性: ${storedState.stability}</div>
        `;
        
        // 添加可视化效果
        const visualEl = document.getElementById('state-visualization');
        if (visualEl) {
            visualEl.innerHTML = '';
            for (let i = 0; i < 10; i++) {
                const particle = document.createElement('div');
                particle.className = 'quantum-particle';
                particle.style.left = `${Math.random() * 100}%`;
                particle.style.top = `${Math.random() * 100}%`;
                visualEl.appendChild(particle);
            }
        }
    }, 1500);
}

/**
 * 检索量子状态
 */
function retrieveState() {
    const idInput = document.getElementById('state-id-input');
    const resultEl = document.getElementById('retrieve-state-result');
    
    if (!resultEl) return;
    
    // 获取输入的状态ID或使用之前存储的
    let stateId = '';
    if (idInput && idInput.value.trim()) {
        stateId = idInput.value.trim();
    } else {
        // 尝试获取最近存储的ID
        try {
            const states = JSON.parse(localStorage.getItem('quantumStates') || '{}');
            const ids = Object.keys(states);
            if (ids.length > 0) {
                stateId = ids[ids.length - 1];
            }
        } catch (e) {
            console.warn('无法从localStorage获取状态:', e);
        }
        
        if (!stateId && Object.keys(quantumUI.storedStates).length > 0) {
            stateId = Object.keys(quantumUI.storedStates)[0];
        }
    }
    
    if (!stateId) {
        resultEl.textContent = '请输入有效的状态ID或先存储一个状态';
        return;
    }
    
    resultEl.textContent = '检索中...';
    
    // 模拟检索过程
    setTimeout(() => {
        // 尝试从内存和localStorage获取
        let state = quantumUI.storedStates[stateId];
        
        if (!state) {
            try {
                const states = JSON.parse(localStorage.getItem('quantumStates') || '{}');
                state = states[stateId];
            } catch (e) {
                console.warn('无法从localStorage获取状态:', e);
            }
        }
        
        if (state) {
            resultEl.innerHTML = `
                <div class="success-message">状态检索成功!</div>
                <div>状态ID: <strong>${state.id}</strong></div>
                <div>存储时间: ${new Date(state.timestamp).toLocaleString()}</div>
                <div>类型: ${state.type}</div>
                <div>复杂度: ${state.complexity}</div>
                <div>稳定性: ${state.stability}</div>
            `;
        } else {
            resultEl.innerHTML = `
                <div class="error-message">状态检索失败</div>
                <div>未找到ID为 <strong>${stateId}</strong> 的量子状态</div>
            `;
        }
    }, 1000);
}

/**
 * 创建量子纠缠通道
 */
function createEntanglementChannel() {
    const resultEl = document.getElementById('channel-result');
    
    if (!resultEl) return;
    
    if (!quantumUI.isReady) {
        resultEl.textContent = '量子模块尚未就绪，无法创建纠缠通道';
        return;
    }
    
    resultEl.textContent = '创建纠缠通道中...';
    
    // 模拟通道创建过程
    setTimeout(() => {
        // 生成随机通道ID和强度
        const channelId = `CH-${Math.floor(Math.random() * 1000)}`;
        const strength = (80 + Math.random() * 20).toFixed(2);
        
        // 存储通道信息
        quantumUI.entanglementChannels[channelId] = {
            id: channelId,
            strength: strength,
            created: Date.now(),
            status: '活跃'
        };
        
        // 更新UI
        resultEl.innerHTML = `
            <div class="success-message">纠缠通道创建成功!</div>
            <div>通道ID: <strong>${channelId}</strong></div>
            <div>纠缠强度: ${strength}%</div>
            <div>状态: <span class="channel-status active">活跃</span></div>
        `;
        
        // 创建可视化
        const visualEl = document.getElementById('channel-visualization');
        if (visualEl) {
            visualEl.innerHTML = '';
            createChannelVisualization(visualEl);
        }
        
        // 启用发送消息按钮
        const sendBtn = document.getElementById('send-message-btn');
        if (sendBtn) {
            sendBtn.removeAttribute('disabled');
            sendBtn.classList.remove('disabled');
        }
    }, 2000);
}

/**
 * 创建通道可视化效果
 * @param {HTMLElement} container - 可视化容器元素
 */
function createChannelVisualization(container) {
    // 创建粒子和连接线
    const particleCount = 8;
    const particles = [];
    
    // 创建粒子
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'quantum-particle';
        
        // 计算位置（围绕中心的圆形）
        const angle = (i / particleCount) * Math.PI * 2;
        const radius = 40 + Math.random() * 10;
        const x = 50 + Math.cos(angle) * radius;
        const y = 50 + Math.sin(angle) * radius;
        
        particle.style.left = `${x}%`;
        particle.style.top = `${y}%`;
        container.appendChild(particle);
        
        particles.push({
            element: particle,
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 0.2,
            vy: (Math.random() - 0.5) * 0.2
        });
    }
    
    // 创建连接线
    for (let i = 0; i < particleCount; i++) {
        for (let j = i + 1; j < particleCount; j++) {
            if (Math.random() > 0.7) continue; // 只连接部分粒子
            
            const connection = document.createElement('div');
            connection.className = 'quantum-connection';
            container.appendChild(connection);
            
            // 更新连接线位置
            const updateConnection = () => {
                const p1 = particles[i];
                const p2 = particles[j];
                
                // 计算连接线的位置和角度
                const dx = p2.x - p1.x;
                const dy = p2.y - p1.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const angle = Math.atan2(dy, dx) * 180 / Math.PI;
                
                connection.style.width = `${distance}%`;
                connection.style.left = `${p1.x}%`;
                connection.style.top = `${p1.y}%`;
                connection.style.transform = `rotate(${angle}deg)`;
                connection.style.transformOrigin = '0 0';
            };
            
            updateConnection();
            
            // 存储更新函数以便动画
            connection.updatePosition = updateConnection;
        }
    }
    
    // 添加脉冲效果
    const pulse = document.createElement('div');
    pulse.className = 'quantum-pulse';
    container.appendChild(pulse);
}

/**
 * 发送量子消息
 */
function sendQuantumMessage() {
    const messageInput = document.getElementById('message-input');
    const resultEl = document.getElementById('message-result');
    
    if (!resultEl) return;
    
    // 检查是否有活跃通道
    if (Object.keys(quantumUI.entanglementChannels).length === 0) {
        resultEl.textContent = '没有活跃的量子纠缠通道，请先创建通道';
        return;
    }
    
    // 获取消息内容
    const message = messageInput && messageInput.value ? 
        messageInput.value : '测试量子消息';
    
    resultEl.textContent = '传送中...';
    
    // 模拟消息发送过程
    let progress = 0;
    const progressUpdate = setInterval(() => {
        progress += 10;
        resultEl.textContent = `传送中... ${progress}%`;
        
        if (progress >= 100) {
            clearInterval(progressUpdate);
            
            // 完成传输
            resultEl.innerHTML = `
                <div class="success-message">量子消息传送成功!</div>
                <div>消息: <strong>${message}</strong></div>
                <div>传输模式: 量子纠缠态</div>
                <div>传输时间: ${(Math.random() * 0.1).toFixed(3)}秒</div>
            `;
            
            // 如果有输入框，清空它
            if (messageInput) {
                messageInput.value = '';
            }
            
            // 触发接收动画
            const visual = document.getElementById('channel-visualization');
            if (visual) {
                const particles = visual.querySelectorAll('.quantum-particle');
                particles.forEach(p => p.classList.add('send-effect'));
                
                setTimeout(() => {
                    particles.forEach(p => p.classList.remove('send-effect'));
                }, 1000);
            }
        }
    }, 100);
}

/**
 * 启动量子爬虫
 */
function startQuantumCrawler() {
    const urlInput = document.getElementById('crawler-url-input');
    const resultEl = document.getElementById('crawler-result');
    const progressEl = document.getElementById('crawler-progress');
    
    if (!resultEl) return;
    
    // 获取目标URL
    const url = urlInput && urlInput.value ? 
        urlInput.value : 'https://example.com';
    
    // 禁用开始按钮，启用停止按钮
    const startBtn = document.getElementById('start-crawler-btn');
    const stopBtn = document.getElementById('stop-crawler-btn');
    
    if (startBtn) startBtn.setAttribute('disabled', 'disabled');
    if (stopBtn) stopBtn.removeAttribute('disabled');
    
    resultEl.textContent = `启动量子爬虫... 目标: ${url}`;
    
    // 存储爬虫状态
    quantumUI.crawlerRunning = true;
    quantumUI.crawledItems = 0;
    
    // 更新进度条
    if (progressEl) {
        progressEl.style.width = '0%';
        progressEl.textContent = '0%';
    }
    
    // 模拟爬虫进度
    quantumUI.crawlerInterval = setInterval(() => {
        if (!quantumUI.crawlerRunning) {
            clearInterval(quantumUI.crawlerInterval);
            return;
        }
        
        // 增加爬取项目数
        quantumUI.crawledItems += Math.floor(1 + Math.random() * 5);
        const progress = Math.min(100, Math.floor(quantumUI.crawledItems / 2));
        
        // 更新进度条
        if (progressEl) {
            progressEl.style.width = `${progress}%`;
            progressEl.textContent = `${progress}%`;
        }
        
        // 更新结果文本
        resultEl.textContent = `已爬取 ${quantumUI.crawledItems} 个项目...`;
        
        // 完成时
        if (progress >= 100) {
            stopQuantumCrawler();
            
            // 显示总结
            resultEl.innerHTML = `
                <div class="success-message">爬取完成!</div>
                <div>URL: ${url}</div>
                <div>爬取项目: ${quantumUI.crawledItems}</div>
                <div>用时: ${(quantumUI.crawledItems * 0.05).toFixed(2)}秒</div>
                <div>
                    <strong>发现:</strong>
                    <ul>
                        <li>数据点: ${Math.floor(quantumUI.crawledItems * 0.7)}</li>
                        <li>连接: ${Math.floor(quantumUI.crawledItems * 0.2)}</li>
                        <li>资源: ${Math.floor(quantumUI.crawledItems * 0.1)}</li>
                    </ul>
                </div>
            `;
        }
    }, 200);
}

/**
 * 停止量子爬虫
 */
function stopQuantumCrawler() {
    quantumUI.crawlerRunning = false;
    
    if (quantumUI.crawlerInterval) {
        clearInterval(quantumUI.crawlerInterval);
    }
    
    // 启用开始按钮，禁用停止按钮
    const startBtn = document.getElementById('start-crawler-btn');
    const stopBtn = document.getElementById('stop-crawler-btn');
    
    if (startBtn) startBtn.removeAttribute('disabled');
    if (stopBtn) stopBtn.setAttribute('disabled', 'disabled');
    
    // 如果未完成，显示中断消息
    const resultEl = document.getElementById('crawler-result');
    if (resultEl && !resultEl.textContent.includes('完成')) {
        resultEl.innerHTML += '<br><div class="warning-message">爬虫已手动停止</div>';
    }
}

/**
 * 重新排列量子交互面板
 * @param {string} layout - 布局类型 (circle, grid, flow, importance)
 */
function rearrangePanel(layout) {
    const panelContainer = document.getElementById('quantum-panel-container');
    
    if (!panelContainer) return;
    
    // 存储当前布局
    quantumUI.currentLayout = layout;
    
    // 移除所有布局类
    panelContainer.classList.remove('layout-circle', 'layout-grid', 'layout-flow', 'layout-importance');
    
    // 添加新布局类
    panelContainer.classList.add(`layout-${layout}`);
    
    // 更新活跃布局按钮
    const layoutBtns = document.querySelectorAll('.layout-btn');
    layoutBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.layout === layout) {
            btn.classList.add('active');
        }
    });
    
    // 为转换添加动画效果
    const panels = panelContainer.querySelectorAll('.quantum-panel');
    panels.forEach(panel => {
        panel.classList.add('transitioning');
        setTimeout(() => {
            panel.classList.remove('transitioning');
        }, 500);
    });
    
    // 显示通知
    showNotification('布局已更改', `量子面板已切换到${getLayoutName(layout)}布局`);
}

/**
 * 获取布局名称
 * @param {string} layout - 布局代码
 * @returns {string} 布局名称
 */
function getLayoutName(layout) {
    const names = {
        'circle': '环形',
        'grid': '网格',
        'flow': '流程',
        'importance': '重要性'
    };
    
    return names[layout] || '默认';
}

/*
/*
量子基因编码: QE-QUA-952C23B9C4D5
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
