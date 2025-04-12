/**
 * 量子加载器 - 负责加载量子纠缠通道和多模态交互功能
 */

(function() {
    'use strict';

    // 全局命名空间
    window.QuantumLoader = {
        config: {
            // 是否已加载量子通道
            channelLoaded: false,
            // 是否已加载多模态交互
            multimodalLoaded: false,
            // 基础路径
            basePath: '/world/static/',
            // 调试模式
            debug: false
        },
        
        /**
         * 初始化加载器
         */
        init: function() {
            // 如果在调试模式下，输出日志
            this.log('量子加载器初始化');
            
            // 检查并加载量子通道脚本
            this.loadQuantumChannel();
            
            // 绑定量子状态矩阵按钮事件
            this.bindQuantumStateButton();
            
            // 加载多模态交互
            this.loadMultimodalInteractions();
            
            // 检查并处理图片加载错误
            this.handleImageErrors();
        },
        
        /**
         * 加载量子通道脚本
         */
        loadQuantumChannel: function() {
            // 如果已经加载过，则不再重复加载
            if (this.config.channelLoaded) {
                this.log('量子通道已加载，跳过');
                return;
            }
            
            var self = this;
            
            // 创建script元素
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.async = true;
            script.src = this.config.basePath + 'js/quantum/web_quantum_client.js';
            
            // 加载成功回调
            script.onload = function() {
                self.log('量子通道脚本加载成功');
                self.config.channelLoaded = true;
                
                // 如果存在WebQuantum对象，则初始化通道
                if (typeof WebQuantum !== 'undefined') {
                    self.log('初始化量子通道');
                    WebQuantum.init({
                        channelId: 'global-quantum-channel',
                        notifyContainer: '.quantum-notifications'
                    });
                }
            };
            
            // 加载失败回调
            script.onerror = function() {
                self.log('量子通道脚本加载失败', true);
                self.showNotification('量子通道加载失败，部分功能可能无法使用', 'error');
            };
            
            // 将脚本添加到文档中
            document.body.appendChild(script);
        },
        
        /**
         * 加载多模态交互脚本
         */
        loadMultimodalInteractions: function() {
            // 如果已经加载过，则不再重复加载
            if (this.config.multimodalLoaded) {
                this.log('多模态交互已加载，跳过');
            return;
        }
        
            var self = this;
            
            // 创建script元素
            var script = document.createElement('script');
            script.type = 'text/javascript';
            script.async = true;
            script.src = this.config.basePath + 'js/multimodal/weq_multimodal_interactions.js';
            
            // 加载成功回调
            script.onload = function() {
                self.log('多模态交互脚本加载成功');
                self.config.multimodalLoaded = true;
                
                // 如果存在WeQMultimodal对象，则初始化多模态交互
                if (typeof WeQMultimodal !== 'undefined' && 
                    typeof WeQMultimodal.InteractionManager !== 'undefined') {
                    self.log('初始化多模态交互');
                    // 创建交互管理器实例
                    window.multimodalManager = new WeQMultimodal.InteractionManager();
                    window.multimodalManager.init();
                }
            };
            
            // 加载失败回调
            script.onerror = function() {
                self.log('多模态交互脚本加载失败', true);
                self.showNotification('多模态交互加载失败，矩阵功能可能无法使用', 'error');
            };
            
            // 将脚本添加到文档中
            document.body.appendChild(script);
        },
        
        /**
         * 绑定量子状态矩阵按钮事件
         */
        bindQuantumStateButton: function() {
            var self = this;
            var stateBtn = document.querySelector('.quantum-state-btn');
            
            if (!stateBtn) {
                this.log('未找到量子状态按钮，跳过绑定', true);
                return;
            }
            
            stateBtn.addEventListener('click', function() {
                self.log('量子状态按钮被点击');
                
                // 如果多模态交互已加载且已初始化
                if (window.multimodalManager) {
                    window.multimodalManager.showInteractionMatrix();
                } else {
                    // 如果多模态交互尚未加载，则先加载
                    if (!self.config.multimodalLoaded) {
                        self.log('多模态交互尚未加载，正在加载...');
                        self.loadMultimodalInteractions();
                        
                        // 500ms后再次尝试显示交互矩阵
                        setTimeout(function() {
                            if (window.multimodalManager) {
                                window.multimodalManager.showInteractionMatrix();
                            } else {
                                self.showNotification('多模态交互尚未准备好，请稍后再试', 'warning');
                            }
                        }, 500);
                    } else {
                        self.showNotification('多模态交互尚未准备好，请稍后再试', 'warning');
                    }
                }
            });
        },
        
        /**
         * 处理图片加载错误
         */
        handleImageErrors: function() {
            var images = document.querySelectorAll('img');
            var self = this;
            
            images.forEach(function(img) {
                // 为所有图片添加错误处理
                img.addEventListener('error', function() {
                    // 根据图片类型提供默认替代图片
                    if (img.classList.contains('user-avatar')) {
                        img.src = self.config.basePath + 'images/default-avatar.svg';
                    } else if (img.classList.contains('nav-logo')) {
                        img.src = self.config.basePath + 'images/logo.svg';
                    }
                });
            });
        },
        
        /**
         * 显示通知消息
         * @param {string} message 消息内容
         * @param {string} type 通知类型: info, success, warning, error
         */
        showNotification: function(message, type) {
            type = type || 'info';
            
            // 创建通知容器，如果不存在
            var container = document.querySelector('.quantum-notifications');
            if (!container) {
                container = document.createElement('div');
                container.className = 'quantum-notifications';
                document.body.appendChild(container);
            }
            
            // 创建通知元素
            var notification = document.createElement('div');
            notification.className = 'notification ' + type;
            notification.innerHTML = '<span class="message">' + message + '</span>' +
                                   '<button class="close-btn">&times;</button>';
            
            // 添加到容器
            container.appendChild(notification);
            
            // 设置自动消失
            setTimeout(function() {
                notification.classList.add('hide');
                setTimeout(function() {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            }, 5000);
            
            // 点击关闭按钮立即关闭
            notification.querySelector('.close-btn').addEventListener('click', function() {
                notification.classList.add('hide');
                setTimeout(function() {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                }, 300);
            });
        },
        
        /**
         * 日志输出
         * @param {string} message 日志消息
         * @param {boolean} isError 是否是错误日志
         */
        log: function(message, isError) {
            if (!this.config.debug) {
                return;
            }
            
            if (isError) {
                console.error('[量子加载器]', message);
        } else {
                console.log('[量子加载器]', message);
            }
        }
    };
    
    // 当DOM内容加载完成后初始化加载器
    document.addEventListener('DOMContentLoaded', function() {
        QuantumLoader.init();
    });
})(); 


/*
/*
量子基因编码: QE-QUA-D5E5EE980381
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 

