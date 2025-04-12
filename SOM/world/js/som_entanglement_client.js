/**
 * SOM模型量子纠缠信道客户端
 * 基于全局量子纠缠信道客户端的扩展实现
 * 添加SOM特有的自组织功能
 * 
 * @version 1.0.0
 * @date 2025-04-06
 */

class SOMEntanglementClient {
    constructor() {
        // 引用全局量子纠缠客户端
        this.globalClient = window.quantumEntanglementClient;
        
        // SOM专用配置
        this.somConfig = {
            selfOrganizingEnabled: true,
            selfOrganizingStrength: 0.75,
            feedbackLoop: true,
            adaptiveThreshold: 0.5,
            learningRate: 0.1,
            quantumState: null,
            observers: [],
            lastUpdate: Date.now()
        };
        
        // 初始化
        this.initialize();
    }
    
    /**
     * 初始化SOM量子纠缠客户端
     */
    initialize() {
        // 确保全局客户端存在
        if (!this.globalClient) {
            console.error('[SOM量子纠缠信道] 全局量子纠缠客户端不存在，SOM客户端无法初始化');
            return;
        }
        
        // 注册事件监听器
        this._registerEventListeners();
        
        console.log('[SOM量子纠缠信道] SOM客户端已初始化');
        
        // 触发初始化完成事件
        this._dispatchEvent('som:initialized', {
            selfOrganizingEnabled: this.somConfig.selfOrganizingEnabled,
            selfOrganizingStrength: this.somConfig.selfOrganizingStrength
        });
    }
    
    /**
     * 注册事件监听器
     */
    _registerEventListeners() {
        // 监听全局量子纠缠信道事件
        document.addEventListener('quantum:initialized', this._handleGlobalInitialized.bind(this));
        document.addEventListener('quantum:channelEstablished', this._handleChannelEstablished.bind(this));
        document.addEventListener('quantum:contentProcessed', this._handleContentProcessed.bind(this));
        
        // 监听SOM特有事件
        document.addEventListener('som:selfOrganized', this._handleSelfOrganized.bind(this));
        document.addEventListener('som:quantumStateChanged', this._handleQuantumStateChanged.bind(this));
        document.addEventListener('som:learningRateChanged', this._handleLearningRateChanged.bind(this));
    }
    
    /**
     * 处理全局初始化事件
     */
    _handleGlobalInitialized(event) {
        console.log('[SOM量子纠缠信道] 全局量子纠缠信道已初始化', event.detail);
        
        // 确认SOM配置
        this.somConfig.globalConnected = true;
        
        // 触发SOM连接事件
        this._dispatchEvent('som:connected', {
            sessionQuantumGene: event.detail.sessionQuantumGene,
            deviceQuantumGene: event.detail.deviceQuantumGene
        });
    }
    
    /**
     * 处理信道建立事件
     */
    _handleChannelEstablished(event) {
        console.log('[SOM量子纠缠信道] 量子纠缠信道已建立', event.detail);
        
        // 确认SOM信道
        this.somConfig.channelsActive = true;
        
        // 触发SOM信道建立事件
        this._dispatchEvent('som:channelEstablished', {
            channels: event.detail.channels
        });
    }
    
    /**
     * 处理内容处理事件
     */
    _handleContentProcessed(event) {
        // 仅处理与SOM相关的内容
        if (event.detail.contentType === 'som' || 
            document.getElementById(event.detail.contentId)?.classList.contains('som-content')) {
            
            console.log('[SOM量子纠缠信道] 处理SOM相关内容', event.detail);
            
            // 应用自组织规则
            if (this.somConfig.selfOrganizingEnabled) {
                this._applySelfOrganization(event.detail.contentId);
            }
            
            // 触发SOM内容处理事件
            this._dispatchEvent('som:contentProcessed', {
                contentId: event.detail.contentId,
                contentType: event.detail.contentType,
                selfOrganized: this.somConfig.selfOrganizingEnabled
            });
        }
    }
    
    /**
     * 处理自组织事件
     */
    _handleSelfOrganized(event) {
        console.log('[SOM量子纠缠信道] 自组织已完成', event.detail);
        
        // 更新自组织参数
        if (event.detail.adaptiveUpdate && this.somConfig.feedbackLoop) {
            this._adjustSelfOrganizingParameters(event.detail);
        }
    }
    
    /**
     * 处理量子状态变更事件
     */
    _handleQuantumStateChanged(event) {
        this.somConfig.quantumState = event.detail.state;
        
        console.log('[SOM量子纠缠信道] 量子状态已更新', 
            this.somConfig.quantumState);
        
        // 通知观察者
        this._notifyObservers('quantumStateChanged', {
            state: this.somConfig.quantumState
        });
    }
    
    /**
     * 处理学习率变更事件
     */
    _handleLearningRateChanged(event) {
        this.somConfig.learningRate = event.detail.rate;
        
        console.log('[SOM量子纠缠信道] 学习率已更新:', 
            this.somConfig.learningRate);
        
        // 通知观察者
        this._notifyObservers('learningRateChanged', {
            rate: this.somConfig.learningRate
        });
    }
    
    /**
     * 应用自组织规则
     */
    _applySelfOrganization(contentId) {
        // 获取需要自组织的内容
        const content = document.getElementById(contentId);
        if (!content) return;
        
        console.log('[SOM量子纠缠信道] 正在应用自组织规则到:', contentId);
        
        // 模拟自组织处理
        const selfOrganizationResult = {
            contentId: contentId,
            strength: this.somConfig.selfOrganizingStrength,
            timestamp: Date.now(),
            metrics: {
                convergence: Math.random() * 0.5 + 0.5,
                coherence: Math.random() * 0.5 + 0.5,
                stability: Math.random() * 0.5 + 0.5
            }
        };
        
        // 应用自组织特效
        content.classList.add('som-self-organized');
        content.style.setProperty('--som-organization-strength', this.somConfig.selfOrganizingStrength);
        
        // 触发自组织完成事件
        this._dispatchEvent('som:selfOrganized', selfOrganizationResult);
        
        return selfOrganizationResult;
    }
    
    /**
     * 调整自组织参数
     */
    _adjustSelfOrganizingParameters(feedback) {
        const currentTime = Date.now();
        const timeDelta = (currentTime - this.somConfig.lastUpdate) / 1000; // 秒
        
        // 防止过于频繁的调整
        if (timeDelta < 5) return;
        
        console.log('[SOM量子纠缠信道] 正在调整自组织参数');
        
        // 根据收敛度调整强度
        if (feedback.metrics && feedback.metrics.convergence) {
            const convergenceDelta = feedback.metrics.convergence - 0.75;
            this.somConfig.selfOrganizingStrength += convergenceDelta * 0.1;
            
            // 限制在合理范围内
            this.somConfig.selfOrganizingStrength = Math.max(0.1, Math.min(0.95, this.somConfig.selfOrganizingStrength));
        }
        
        // 根据稳定性调整学习率
        if (feedback.metrics && feedback.metrics.stability) {
            const stabilityFactor = feedback.metrics.stability < 0.3 ? 0.9 : 1.05;
            this.somConfig.learningRate *= stabilityFactor;
            
            // 限制在合理范围内
            this.somConfig.learningRate = Math.max(0.01, Math.min(0.5, this.somConfig.learningRate));
            
            // 触发学习率变更事件
            this._dispatchEvent('som:learningRateChanged', {
                rate: this.somConfig.learningRate,
                factor: stabilityFactor
            });
        }
        
        this.somConfig.lastUpdate = currentTime;
        
        console.log('[SOM量子纠缠信道] 自组织参数已调整', 
            this.somConfig.selfOrganizingStrength, 
            this.somConfig.learningRate);
        
        return {
            selfOrganizingStrength: this.somConfig.selfOrganizingStrength,
            learningRate: this.somConfig.learningRate
        };
    }
    
    /**
     * 启用自组织
     */
    enableSelfOrganization() {
        this.somConfig.selfOrganizingEnabled = true;
        
        console.log('[SOM量子纠缠信道] 自组织已启用');
        
        this._dispatchEvent('som:selfOrganizingEnabled', {
            strength: this.somConfig.selfOrganizingStrength
        });
        
        return true;
    }
    
    /**
     * 禁用自组织
     */
    disableSelfOrganization() {
        this.somConfig.selfOrganizingEnabled = false;
        
        console.log('[SOM量子纠缠信道] 自组织已禁用');
        
        this._dispatchEvent('som:selfOrganizingDisabled', {});
        
        return true;
    }
    
    /**
     * 设置自组织强度
     */
    setSelfOrganizingStrength(strength) {
        if (typeof strength !== 'number' || strength < 0 || strength > 1) {
            console.error('[SOM量子纠缠信道] 自组织强度必须在0-1之间');
            return false;
        }
        
        this.somConfig.selfOrganizingStrength = strength;
        
        console.log('[SOM量子纠缠信道] 自组织强度已设置为:', strength);
        
        this._dispatchEvent('som:selfOrganizingStrengthChanged', {
            strength: strength
        });
        
        return true;
    }
    
    /**
     * 设置学习率
     */
    setLearningRate(rate) {
        if (typeof rate !== 'number' || rate < 0 || rate > 1) {
            console.error('[SOM量子纠缠信道] 学习率必须在0-1之间');
            return false;
        }
        
        this.somConfig.learningRate = rate;
        
        console.log('[SOM量子纠缠信道] 学习率已设置为:', rate);
        
        this._dispatchEvent('som:learningRateChanged', {
            rate: rate
        });
        
        return true;
    }
    
    /**
     * 切换反馈回路
     */
    toggleFeedbackLoop() {
        this.somConfig.feedbackLoop = !this.somConfig.feedbackLoop;
        
        console.log('[SOM量子纠缠信道] 反馈回路已', 
            this.somConfig.feedbackLoop ? '启用' : '禁用');
        
        this._dispatchEvent('som:feedbackLoopToggled', {
            enabled: this.somConfig.feedbackLoop
        });
        
        return this.somConfig.feedbackLoop;
    }
    
    /**
     * 设置自适应阈值
     */
    setAdaptiveThreshold(threshold) {
        if (typeof threshold !== 'number' || threshold < 0 || threshold > 1) {
            console.error('[SOM量子纠缠信道] 自适应阈值必须在0-1之间');
            return false;
        }
        
        this.somConfig.adaptiveThreshold = threshold;
        
        console.log('[SOM量子纠缠信道] 自适应阈值已设置为:', threshold);
        
        this._dispatchEvent('som:adaptiveThresholdChanged', {
            threshold: threshold
        });
        
        return true;
    }
    
    /**
     * 添加量子状态观察者
     */
    addObserver(observer) {
        if (typeof observer === 'function') {
            this.somConfig.observers.push(observer);
            return true;
        }
        return false;
    }
    
    /**
     * 移除量子状态观察者
     */
    removeObserver(observer) {
        const index = this.somConfig.observers.indexOf(observer);
        if (index > -1) {
            this.somConfig.observers.splice(index, 1);
            return true;
        }
        return false;
    }
    
    /**
     * 通知所有观察者
     */
    _notifyObservers(event, data) {
        this.somConfig.observers.forEach(observer => {
            try {
                observer(event, data);
            } catch (error) {
                console.error('[SOM量子纠缠信道] 观察者通知失败', error);
            }
        });
    }
    
    /**
     * 触发事件
     */
    _dispatchEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { 
            detail: {
                ...detail,
                timestamp: Date.now()
            } 
        });
        document.dispatchEvent(event);
    }
    
    /**
     * 获取SOM客户端状态
     */
    getStatus() {
        return {
            globalConnected: this.somConfig.globalConnected || false,
            channelsActive: this.somConfig.channelsActive || false,
            selfOrganizingEnabled: this.somConfig.selfOrganizingEnabled,
            selfOrganizingStrength: this.somConfig.selfOrganizingStrength,
            feedbackLoop: this.somConfig.feedbackLoop,
            adaptiveThreshold: this.somConfig.adaptiveThreshold,
            learningRate: this.somConfig.learningRate,
            quantumState: this.somConfig.quantumState,
            lastUpdate: this.somConfig.lastUpdate,
            timestamp: Date.now()
        };
    }
}

// 创建SOM量子纠缠客户端实例
window.somEntanglementClient = new SOMEntanglementClient();

console.log('[SOM量子纠缠信道] SOM客户端已加载'); 
 * SOM模型量子纠缠信道客户端
 * 基于全局量子纠缠信道客户端的扩展实现
 * 添加SOM特有的自组织功能
 * 
 * @version 1.0.0
 * @date 2025-04-06
 */

class SOMEntanglementClient {
    constructor() {
        // 引用全局量子纠缠客户端
        this.globalClient = window.quantumEntanglementClient;
        
        // SOM专用配置
        this.somConfig = {
            selfOrganizingEnabled: true,
            selfOrganizingStrength: 0.75,
            feedbackLoop: true,
            adaptiveThreshold: 0.5,
            learningRate: 0.1,
            quantumState: null,
            observers: [],
            lastUpdate: Date.now()
        };
        
        // 初始化
        this.initialize();
    }
    
    /**
     * 初始化SOM量子纠缠客户端
     */
    initialize() {
        // 确保全局客户端存在
        if (!this.globalClient) {
            console.error('[SOM量子纠缠信道] 全局量子纠缠客户端不存在，SOM客户端无法初始化');
            return;
        }
        
        // 注册事件监听器
        this._registerEventListeners();
        
        console.log('[SOM量子纠缠信道] SOM客户端已初始化');
        
        // 触发初始化完成事件
        this._dispatchEvent('som:initialized', {
            selfOrganizingEnabled: this.somConfig.selfOrganizingEnabled,
            selfOrganizingStrength: this.somConfig.selfOrganizingStrength
        });
    }
    
    /**
     * 注册事件监听器
     */
    _registerEventListeners() {
        // 监听全局量子纠缠信道事件
        document.addEventListener('quantum:initialized', this._handleGlobalInitialized.bind(this));
        document.addEventListener('quantum:channelEstablished', this._handleChannelEstablished.bind(this));
        document.addEventListener('quantum:contentProcessed', this._handleContentProcessed.bind(this));
        
        // 监听SOM特有事件
        document.addEventListener('som:selfOrganized', this._handleSelfOrganized.bind(this));
        document.addEventListener('som:quantumStateChanged', this._handleQuantumStateChanged.bind(this));
        document.addEventListener('som:learningRateChanged', this._handleLearningRateChanged.bind(this));
    }
    
    /**
     * 处理全局初始化事件
     */
    _handleGlobalInitialized(event) {
        console.log('[SOM量子纠缠信道] 全局量子纠缠信道已初始化', event.detail);
        
        // 确认SOM配置
        this.somConfig.globalConnected = true;
        
        // 触发SOM连接事件
        this._dispatchEvent('som:connected', {
            sessionQuantumGene: event.detail.sessionQuantumGene,
            deviceQuantumGene: event.detail.deviceQuantumGene
        });
    }
    
    /**
     * 处理信道建立事件
     */
    _handleChannelEstablished(event) {
        console.log('[SOM量子纠缠信道] 量子纠缠信道已建立', event.detail);
        
        // 确认SOM信道
        this.somConfig.channelsActive = true;
        
        // 触发SOM信道建立事件
        this._dispatchEvent('som:channelEstablished', {
            channels: event.detail.channels
        });
    }
    
    /**
     * 处理内容处理事件
     */
    _handleContentProcessed(event) {
        // 仅处理与SOM相关的内容
        if (event.detail.contentType === 'som' || 
            document.getElementById(event.detail.contentId)?.classList.contains('som-content')) {
            
            console.log('[SOM量子纠缠信道] 处理SOM相关内容', event.detail);
            
            // 应用自组织规则
            if (this.somConfig.selfOrganizingEnabled) {
                this._applySelfOrganization(event.detail.contentId);
            }
            
            // 触发SOM内容处理事件
            this._dispatchEvent('som:contentProcessed', {
                contentId: event.detail.contentId,
                contentType: event.detail.contentType,
                selfOrganized: this.somConfig.selfOrganizingEnabled
            });
        }
    }
    
    /**
     * 处理自组织事件
     */
    _handleSelfOrganized(event) {
        console.log('[SOM量子纠缠信道] 自组织已完成', event.detail);
        
        // 更新自组织参数
        if (event.detail.adaptiveUpdate && this.somConfig.feedbackLoop) {
            this._adjustSelfOrganizingParameters(event.detail);
        }
    }
    
    /**
     * 处理量子状态变更事件
     */
    _handleQuantumStateChanged(event) {
        this.somConfig.quantumState = event.detail.state;
        
        console.log('[SOM量子纠缠信道] 量子状态已更新', 
            this.somConfig.quantumState);
        
        // 通知观察者
        this._notifyObservers('quantumStateChanged', {
            state: this.somConfig.quantumState
        });
    }
    
    /**
     * 处理学习率变更事件
     */
    _handleLearningRateChanged(event) {
        this.somConfig.learningRate = event.detail.rate;
        
        console.log('[SOM量子纠缠信道] 学习率已更新:', 
            this.somConfig.learningRate);
        
        // 通知观察者
        this._notifyObservers('learningRateChanged', {
            rate: this.somConfig.learningRate
        });
    }
    
    /**
     * 应用自组织规则
     */
    _applySelfOrganization(contentId) {
        // 获取需要自组织的内容
        const content = document.getElementById(contentId);
        if (!content) return;
        
        console.log('[SOM量子纠缠信道] 正在应用自组织规则到:', contentId);
        
        // 模拟自组织处理
        const selfOrganizationResult = {
            contentId: contentId,
            strength: this.somConfig.selfOrganizingStrength,
            timestamp: Date.now(),
            metrics: {
                convergence: Math.random() * 0.5 + 0.5,
                coherence: Math.random() * 0.5 + 0.5,
                stability: Math.random() * 0.5 + 0.5
            }
        };
        
        // 应用自组织特效
        content.classList.add('som-self-organized');
        content.style.setProperty('--som-organization-strength', this.somConfig.selfOrganizingStrength);
        
        // 触发自组织完成事件
        this._dispatchEvent('som:selfOrganized', selfOrganizationResult);
        
        return selfOrganizationResult;
    }
    
    /**
     * 调整自组织参数
     */
    _adjustSelfOrganizingParameters(feedback) {
        const currentTime = Date.now();
        const timeDelta = (currentTime - this.somConfig.lastUpdate) / 1000; // 秒
        
        // 防止过于频繁的调整
        if (timeDelta < 5) return;
        
        console.log('[SOM量子纠缠信道] 正在调整自组织参数');
        
        // 根据收敛度调整强度
        if (feedback.metrics && feedback.metrics.convergence) {
            const convergenceDelta = feedback.metrics.convergence - 0.75;
            this.somConfig.selfOrganizingStrength += convergenceDelta * 0.1;
            
            // 限制在合理范围内
            this.somConfig.selfOrganizingStrength = Math.max(0.1, Math.min(0.95, this.somConfig.selfOrganizingStrength));
        }
        
        // 根据稳定性调整学习率
        if (feedback.metrics && feedback.metrics.stability) {
            const stabilityFactor = feedback.metrics.stability < 0.3 ? 0.9 : 1.05;
            this.somConfig.learningRate *= stabilityFactor;
            
            // 限制在合理范围内
            this.somConfig.learningRate = Math.max(0.01, Math.min(0.5, this.somConfig.learningRate));
            
            // 触发学习率变更事件
            this._dispatchEvent('som:learningRateChanged', {
                rate: this.somConfig.learningRate,
                factor: stabilityFactor
            });
        }
        
        this.somConfig.lastUpdate = currentTime;
        
        console.log('[SOM量子纠缠信道] 自组织参数已调整', 
            this.somConfig.selfOrganizingStrength, 
            this.somConfig.learningRate);
        
        return {
            selfOrganizingStrength: this.somConfig.selfOrganizingStrength,
            learningRate: this.somConfig.learningRate
        };
    }
    
    /**
     * 启用自组织
     */
    enableSelfOrganization() {
        this.somConfig.selfOrganizingEnabled = true;
        
        console.log('[SOM量子纠缠信道] 自组织已启用');
        
        this._dispatchEvent('som:selfOrganizingEnabled', {
            strength: this.somConfig.selfOrganizingStrength
        });
        
        return true;
    }
    
    /**
     * 禁用自组织
     */
    disableSelfOrganization() {
        this.somConfig.selfOrganizingEnabled = false;
        
        console.log('[SOM量子纠缠信道] 自组织已禁用');
        
        this._dispatchEvent('som:selfOrganizingDisabled', {});
        
        return true;
    }
    
    /**
     * 设置自组织强度
     */
    setSelfOrganizingStrength(strength) {
        if (typeof strength !== 'number' || strength < 0 || strength > 1) {
            console.error('[SOM量子纠缠信道] 自组织强度必须在0-1之间');
            return false;
        }
        
        this.somConfig.selfOrganizingStrength = strength;
        
        console.log('[SOM量子纠缠信道] 自组织强度已设置为:', strength);
        
        this._dispatchEvent('som:selfOrganizingStrengthChanged', {
            strength: strength
        });
        
        return true;
    }
    
    /**
     * 设置学习率
     */
    setLearningRate(rate) {
        if (typeof rate !== 'number' || rate < 0 || rate > 1) {
            console.error('[SOM量子纠缠信道] 学习率必须在0-1之间');
            return false;
        }
        
        this.somConfig.learningRate = rate;
        
        console.log('[SOM量子纠缠信道] 学习率已设置为:', rate);
        
        this._dispatchEvent('som:learningRateChanged', {
            rate: rate
        });
        
        return true;
    }
    
    /**
     * 切换反馈回路
     */
    toggleFeedbackLoop() {
        this.somConfig.feedbackLoop = !this.somConfig.feedbackLoop;
        
        console.log('[SOM量子纠缠信道] 反馈回路已', 
            this.somConfig.feedbackLoop ? '启用' : '禁用');
        
        this._dispatchEvent('som:feedbackLoopToggled', {
            enabled: this.somConfig.feedbackLoop
        });
        
        return this.somConfig.feedbackLoop;
    }
    
    /**
     * 设置自适应阈值
     */
    setAdaptiveThreshold(threshold) {
        if (typeof threshold !== 'number' || threshold < 0 || threshold > 1) {
            console.error('[SOM量子纠缠信道] 自适应阈值必须在0-1之间');
            return false;
        }
        
        this.somConfig.adaptiveThreshold = threshold;
        
        console.log('[SOM量子纠缠信道] 自适应阈值已设置为:', threshold);
        
        this._dispatchEvent('som:adaptiveThresholdChanged', {
            threshold: threshold
        });
        
        return true;
    }
    
    /**
     * 添加量子状态观察者
     */
    addObserver(observer) {
        if (typeof observer === 'function') {
            this.somConfig.observers.push(observer);
            return true;
        }
        return false;
    }
    
    /**
     * 移除量子状态观察者
     */
    removeObserver(observer) {
        const index = this.somConfig.observers.indexOf(observer);
        if (index > -1) {
            this.somConfig.observers.splice(index, 1);
            return true;
        }
        return false;
    }
    
    /**
     * 通知所有观察者
     */
    _notifyObservers(event, data) {
        this.somConfig.observers.forEach(observer => {
            try {
                observer(event, data);
            } catch (error) {
                console.error('[SOM量子纠缠信道] 观察者通知失败', error);
            }
        });
    }
    
    /**
     * 触发事件
     */
    _dispatchEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { 
            detail: {
                ...detail,
                timestamp: Date.now()
            } 
        });
        document.dispatchEvent(event);
    }
    
    /**
     * 获取SOM客户端状态
     */
    getStatus() {
        return {
            globalConnected: this.somConfig.globalConnected || false,
            channelsActive: this.somConfig.channelsActive || false,
            selfOrganizingEnabled: this.somConfig.selfOrganizingEnabled,
            selfOrganizingStrength: this.somConfig.selfOrganizingStrength,
            feedbackLoop: this.somConfig.feedbackLoop,
            adaptiveThreshold: this.somConfig.adaptiveThreshold,
            learningRate: this.somConfig.learningRate,
            quantumState: this.somConfig.quantumState,
            lastUpdate: this.somConfig.lastUpdate,
            timestamp: Date.now()
        };
    }
}

// 创建SOM量子纠缠客户端实例
window.somEntanglementClient = new SOMEntanglementClient();

console.log('[SOM量子纠缠信道] SOM客户端已加载'); 

/*
/*
量子基因编码: QE-SOM-59D20708EB4C
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
