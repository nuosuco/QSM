/**
 * 量子纠缠客户端
 * 处理量子通道建立和量子态交互
 */

(function() {
    // 全局量子纠缠管理器
    window.QuantumEntanglement = window.QuantumEntanglement || {};

    // 量子通道状态
    var CHANNEL_STATE = {
        DISCONNECTED: 'disconnected',
        CONNECTING: 'connecting',
        CONNECTED: 'connected',
        ERROR: 'error'
    };

    // 量子纠缠管理器
    function QuantumEntanglementManager() {
        this.channelState = CHANNEL_STATE.DISCONNECTED;
        this.initialized = false;
        this.channelStateEl = null;
        this.notificationEl = null;
        this.quantumStateBtn = null;
        
        // 初始化
        this.initialize();
    }

    // 初始化方法
    QuantumEntanglementManager.prototype.initialize = function() {
        console.log('量子纠缠管理器: 正在初始化');
        
        // 获取DOM元素
        this.channelStateEl = document.getElementById('quantum-channel-state');
        this.notificationEl = document.getElementById('quantum-notification');
        this.quantumStateBtn = document.querySelector('.quantum-state-btn');
        
        // 检查是否能找到所需元素
        if (!this.channelStateEl) {
            console.warn('量子纠缠管理器: 无法找到量子信道状态元素');
        }
        
        if (!this.notificationEl) {
            console.warn('量子纠缠管理器: 无法找到通知元素');
        }
        
        // 添加事件监听
        this._addEventListeners();
        
        // 连接量子信道
        this._connectQuantumChannel();
        
        // 标记为已初始化
        this.initialized = true;
        console.log('量子纠缠管理器: 初始化完成');
    };

    // 添加事件监听
    QuantumEntanglementManager.prototype._addEventListeners = function() {
        var self = this;
        
        // 监听量子态按钮点击
        if (this.quantumStateBtn) {
            this.quantumStateBtn.addEventListener('click', function(e) {
                if (!self._isChannelConnected()) {
                    self._showNotification('需要先建立量子纠缠信道');
                    return;
                }
                
                // 如果WeQMultimodal已加载则使用它的显示矩阵方法
                if (window.WeQMultimodal && window.WeQMultimodal.interactions) {
                    window.WeQMultimodal.interactions.showInteractionMatrix();
                }
            });
        }
        
        // 关闭通知按钮
        if (this.notificationEl) {
            var closeBtn = this.notificationEl.querySelector('.notification-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    self._hideNotification();
                });
            }
        }
        
        // 页面卸载前断开信道
        window.addEventListener('beforeunload', function() {
            self._disconnectQuantumChannel();
        });
    };

    // 连接量子信道
    QuantumEntanglementManager.prototype._connectQuantumChannel = function() {
        var self = this;
        
        console.log('量子纠缠管理器: 正在连接量子信道');
        this._updateChannelState(CHANNEL_STATE.CONNECTING);
        
        // 模拟连接过程
        setTimeout(function() {
            // 80%概率成功建立信道
            if (Math.random() > 0.2) {
                self._updateChannelState(CHANNEL_STATE.CONNECTED);
                self._showNotification('量子纠缠信道已建立');
                console.log('量子纠缠管理器: 量子信道已连接');
            } else {
                self._updateChannelState(CHANNEL_STATE.ERROR);
                self._showNotification('量子纠缠信道建立失败', true);
                console.error('量子纠缠管理器: 量子信道连接失败');
                
                // 5秒后重试
                setTimeout(function() {
                    self._connectQuantumChannel();
                }, 5000);
            }
        }, 1500);
    };

    // 断开量子信道
    QuantumEntanglementManager.prototype._disconnectQuantumChannel = function() {
        console.log('量子纠缠管理器: 正在断开量子信道');
        this._updateChannelState(CHANNEL_STATE.DISCONNECTED);
    };

    // 更新信道状态
    QuantumEntanglementManager.prototype._updateChannelState = function(state) {
        this.channelState = state;
        
        if (this.channelStateEl) {
            // 移除所有状态类
            this.channelStateEl.classList.remove(
                'state-connected',
                'state-connecting',
                'state-disconnected',
                'state-error'
            );
            
            // 添加当前状态类
            this.channelStateEl.classList.add('state-' + state);
            
            // 更新文本
            switch (state) {
                case CHANNEL_STATE.CONNECTED:
                    this.channelStateEl.textContent = '已连接';
                    break;
                case CHANNEL_STATE.CONNECTING:
                    this.channelStateEl.textContent = '连接中';
                    break;
                case CHANNEL_STATE.DISCONNECTED:
                    this.channelStateEl.textContent = '未连接';
                    break;
                case CHANNEL_STATE.ERROR:
                    this.channelStateEl.textContent = '连接错误';
                    break;
            }
        }
    };

    // 显示通知
    QuantumEntanglementManager.prototype._showNotification = function(message, isError) {
        if (!this.notificationEl) return;
        
        var messageEl = this.notificationEl.querySelector('.notification-message');
        if (messageEl) {
            messageEl.textContent = message;
        }
        
        // 添加错误样式
        if (isError) {
            this.notificationEl.classList.add('error');
        } else {
            this.notificationEl.classList.remove('error');
        }
        
        // 显示通知
        this.notificationEl.style.display = 'flex';
        
        var self = this;
        // 5秒后自动隐藏
        setTimeout(function() {
            self._hideNotification();
        }, 5000);
    };

    // 隐藏通知
    QuantumEntanglementManager.prototype._hideNotification = function() {
        if (!this.notificationEl) return;
        this.notificationEl.style.display = 'none';
    };

    // 检查信道是否已连接
    QuantumEntanglementManager.prototype._isChannelConnected = function() {
        return this.channelState === CHANNEL_STATE.CONNECTED;
    };

    // 初始化全局实例
    document.addEventListener('DOMContentLoaded', function() {
        window.QuantumEntanglement.manager = new QuantumEntanglementManager();
    });
})();
/*
量子基因编码: QE-QUA-3DE7352EEC9D
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/