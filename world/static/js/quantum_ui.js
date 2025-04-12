/**
 * 量子叠加态模型（QSM）用户界面管理器
 * 负责量子UI元素的行为、状态和交互
 */

class QuantumUIManager {
    constructor(options = {}) {
        this.options = Object.assign({
            debugMode: false,
            autoInitialize: true,
            defaultTheme: 'light',
            quantumEffectsEnabled: true
        }, options);
        
        this.webQuantumInstance = null;
        this.initialized = false;
        this.theme = this.options.defaultTheme;
        this.components = new Map();
        
        // 自动初始化
        if (this.options.autoInitialize) {
            this.initialize();
        }
    }
    
    /**
     * 初始化量子UI管理器
     */
    async initialize() {
        this._log('初始化量子UI管理器');
        
        // 添加量子UI状态类
        document.body.classList.add('quantum-ui');
        document.body.classList.add(`theme-${this.theme}`);
        
        // 监听WebQuantum就绪事件
        this._setupWebQuantumListener();
        
        // 初始化UI组件
        this._initComponents();
        
        // 设置主题切换
        this._setupThemeToggle();
        
        this.initialized = true;
        this._log('量子UI管理器初始化完成');
        
        // 触发初始化完成事件
        this._dispatchEvent('quantum-ui:initialized', {
            theme: this.theme,
            components: Array.from(this.components.keys())
        });
    }
    
    /**
     * 设置WebQuantum监听器
     */
    _setupWebQuantumListener() {
        // 监听WebQuantum就绪事件
        document.addEventListener('quantum:ready', (e) => {
            this._log('WebQuantum已就绪，获取实例');
            this.webQuantumInstance = window.webQuantumInstance;
            
            // 激活量子增强UI功能
            this._activateQuantumEnhancedUI();
            
            // 触发量子UI就绪事件
            this._dispatchEvent('quantum-ui:quantum-ready', {
                quantumStatus: this.webQuantumInstance.getStatus()
            });
        });
    }
    
    /**
     * 激活量子增强UI功能
     */
    _activateQuantumEnhancedUI() {
        if (!this.webQuantumInstance) return;
        
        this._log('激活量子增强UI功能');
        
        // 添加量子增强UI类
        document.body.classList.add('quantum-enhanced-ui');
        
        // 更新所有组件的量子状态
        for (const [name, component] of this.components.entries()) {
            if (typeof component.activateQuantumFeatures === 'function') {
                component.activateQuantumFeatures(this.webQuantumInstance);
            }
        }
    }
    
    /**
     * 初始化UI组件
     */
    _initComponents() {
        this._log('初始化UI组件');
        
        // 查找页面上所有具有data-quantum-component属性的元素
        const componentElements = document.querySelectorAll('[data-quantum-component]');
        
        componentElements.forEach(element => {
            const componentType = element.dataset.quantumComponent;
            const componentId = element.id || `quantum-component-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
            
            // 确保元素有ID
            if (!element.id) {
                element.id = componentId;
            }
            
            // 创建组件实例
            let component;
            switch (componentType) {
                case 'navbar':
                    component = new QuantumNavbar(element, this);
                    break;
                case 'search':
                    component = new QuantumSearch(element, this);
                    break;
                case 'health-check':
                    component = new QuantumHealthCheck(element, this);
                    break;
                case 'parallel-process':
                    component = new QuantumParallelProcess(element, this);
                    break;
                case 'visualization':
                    component = new QuantumVisualization(element, this);
                    break;
                case 'storage':
                    component = new QuantumStorage(element, this);
                    break;
                case 'retrieval':
                    component = new QuantumRetrieval(element, this);
                    break;
                case 'channel':
                    component = new QuantumChannel(element, this);
                    break;
                case 'crawler':
                    component = new QuantumCrawler(element, this);
                    break;
                case 'panel':
                    component = new QuantumPanel(element, this);
                    break;
                default:
                    this._log(`未知组件类型: ${componentType}`);
                    return;
            }
            
            // 存储组件实例
            this.components.set(componentId, component);
            
            // 初始化组件
            if (component && typeof component.initialize === 'function') {
                component.initialize();
            }
        });
    }
    
    /**
     * 设置主题切换
     */
    _setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (!themeToggle) return;
        
        themeToggle.addEventListener('click', () => {
            this.toggleTheme();
        });
    }
    
    /**
     * 切换主题
     */
    toggleTheme() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }
    
    /**
     * 设置主题
     */
    setTheme(theme) {
        this._log(`设置主题: ${theme}`);
        
        // 移除旧主题类
        document.body.classList.remove(`theme-${this.theme}`);
        
        // 设置新主题
        this.theme = theme;
        document.body.classList.add(`theme-${this.theme}`);
        
        // 通知所有组件主题变化
        for (const [name, component] of this.components.entries()) {
            if (typeof component.onThemeChange === 'function') {
                component.onThemeChange(this.theme);
            }
        }
        
        // 触发主题变化事件
        this._dispatchEvent('quantum-ui:theme-changed', {
            theme: this.theme
        });
        
        // 存储用户主题偏好
        localStorage.setItem('quantum-ui-theme', this.theme);
    }
    
    /**
     * 获取组件
     */
    getComponent(componentId) {
        return this.components.get(componentId);
    }
    
    /**
     * 记录日志
     */
    _log(...args) {
        if (this.options.debugMode) {
            console.log('[QuantumUI]', ...args);
        }
    }
    
    /**
     * 分发事件
     */
    _dispatchEvent(name, detail) {
        const event = new CustomEvent(name, { detail });
        document.dispatchEvent(event);
    }
}

// 创建全局量子UI管理器实例
document.addEventListener('DOMContentLoaded', () => {
    // 初始化全局量子UI管理器
    window.quantumUI = {
        manager: new QuantumUIManager({
            debugMode: false,
            defaultTheme: localStorage.getItem('quantum-ui-theme') || 'light'
        })
    };
    
    // 监听WebQuantum就绪事件，以协调UI与量子状态
    document.addEventListener('quantum:ready', (e) => {
        document.body.classList.add('quantum-ready');
        console.log('量子状态就绪，UI已更新');
    });
}); 

/*
/*
量子基因编码: QE-QUA-2C42451E0864
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
