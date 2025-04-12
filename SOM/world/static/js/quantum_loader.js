/**
 * 量子加载器 - 模块加载和依赖管理
 * 提供全局资源加载、动态模块管理和依赖注入功能
 */

(function() {
    'use strict';
    
    // 模块注册表
    const modules = {};
    
    // 依赖关系图
    const dependencyGraph = {};
    
    // 加载状态
    const loadStatus = {
        pending: [],
        loaded: [],
        failed: []
    };
    
    // 运行环境检测
    const environment = {
        mode: detectMode(),
        modelName: detectModelName(),
        isStandalone: false,
        basePath: ''
    };
    
    // 初始化
    function init() {
        console.log('[量子加载器] 初始化中...');
        
        // 检测环境
        environment.isStandalone = environment.mode === 'standalone';
        environment.basePath = environment.isStandalone ? './' : '/';
        
        // 添加全局错误处理
        window.addEventListener('error', handleGlobalError);
        
        // 创建加载样式
        createLoaderStyle();
        
        console.log(`[量子加载器] 运行模式: ${environment.mode}, 模型: ${environment.modelName}`);
        
        // 通知加载完成
        document.dispatchEvent(new CustomEvent('quantum:loaderReady'));
    }
    
    // 检测运行模式: integrated 或 standalone
    function detectMode() {
        const path = window.location.pathname;
        const modelPrefixes = ['/QSM/', '/WeQ/', '/SOM/', '/Ref/'];
        
        return modelPrefixes.some(prefix => path.startsWith(prefix)) ? 'integrated' : 'standalone';
    }
    
    // 检测当前模型
    function detectModelName() {
        const path = window.location.pathname;
        const models = ['QSM', 'WeQ', 'SOM', 'Ref'];
        
        for (const model of models) {
            if (path.startsWith(`/${model}/`)) {
                return model;
            }
        }
        
        // 默认值
        return 'QSM';
    }
    
    // 创建加载样式
    function createLoaderStyle() {
        const style = document.createElement('style');
        style.textContent = `
            .quantum-loader {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: linear-gradient(90deg, #3a86ff, #8338ec, #ff006e);
                z-index: 9999;
                animation: quantum-loader-progress 2s ease-in-out infinite;
            }
            
            @keyframes quantum-loader-progress {
                0% {
                    width: 0%;
                    left: 0;
                }
                50% {
                    width: 30%;
                }
                100% {
                    width: 0%;
                    left: 100%;
                }
            }
            
            .quantum-loading {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9998;
            }
            
            .quantum-loading-content {
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                text-align: center;
            }
            
            .quantum-loading-spinner {
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 4px solid rgba(0, 0, 0, 0.1);
                border-left-color: #3a86ff;
                border-radius: 50%;
                animation: quantum-spinner 1s linear infinite;
            }
            
            @keyframes quantum-spinner {
                to {
                    transform: rotate(360deg);
                }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    // 全局错误处理
    function handleGlobalError(event) {
        console.error('[量子加载器] 捕获到全局错误:', event.error || event.message);
        
        // 记录错误
        loadStatus.failed.push({
            type: 'global',
            message: event.message,
            stack: event.error ? event.error.stack : null,
            timestamp: new Date().toISOString()
        });
        
        // 防止错误传播
        event.preventDefault();
    }
    
    // 注册模块
    function registerModule(name, dependencies, factory) {
        if (modules[name]) {
            console.warn(`[量子加载器] 模块 "${name}" 已经存在，将被覆盖`);
        }
        
        modules[name] = {
            name,
            dependencies: dependencies || [],
            factory,
            instance: null,
            loaded: false
        };
        
        // 构建依赖图
        dependencyGraph[name] = dependencies || [];
        
        console.log(`[量子加载器] 注册模块: ${name}, 依赖: ${dependencies.join(', ') || '无'}`);
        
        // 返回模块API
        return {
            init: function(options) {
                return initModule(name, options);
            }
        };
    }
    
    // 初始化模块
    function initModule(name, options) {
        if (!modules[name]) {
            throw new Error(`[量子加载器] 模块 "${name}" 不存在`);
        }
        
        const module = modules[name];
        
        // 如果已经加载，直接返回实例
        if (module.loaded && module.instance) {
            return Promise.resolve(module.instance);
        }
        
        // 添加到待处理队列
        loadStatus.pending.push(name);
        
        // 加载依赖
        const dependencyPromises = module.dependencies.map(dep => {
            if (!modules[dep]) {
                return loadExternalModule(dep)
                    .then(() => {
                        if (modules[dep]) {
                            return initModule(dep);
                        }
                        throw new Error(`[量子加载器] 无法加载依赖模块: ${dep}`);
                    });
            } else {
                return initModule(dep);
            }
        });
        
        // 等待所有依赖加载完成
        return Promise.all(dependencyPromises)
            .then(instances => {
                // 创建模块实例
                try {
                    module.instance = module.factory.apply(null, instances);
                    module.loaded = true;
                    
                    // 更新状态
                    const index = loadStatus.pending.indexOf(name);
                    if (index !== -1) {
                        loadStatus.pending.splice(index, 1);
                    }
                    loadStatus.loaded.push(name);
                    
                    console.log(`[量子加载器] 模块初始化成功: ${name}`);
                    
                    return module.instance;
                } catch (error) {
                    // 记录错误
                    const index = loadStatus.pending.indexOf(name);
                    if (index !== -1) {
                        loadStatus.pending.splice(index, 1);
                    }
                    loadStatus.failed.push({
                        type: 'module',
                        name,
                        message: error.message,
                        stack: error.stack,
                        timestamp: new Date().toISOString()
                    });
                    
                    console.error(`[量子加载器] 模块初始化失败: ${name}`, error);
                    throw error;
                }
            });
    }
    
    // 加载外部模块
    function loadExternalModule(name) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = getModulePath(name);
            script.onload = () => {
                if (modules[name]) {
                    resolve();
                } else {
                    reject(new Error(`[量子加载器] 外部模块加载后未注册: ${name}`));
                }
            };
            script.onerror = () => {
                reject(new Error(`[量子加载器] 外部模块加载失败: ${name}`));
            };
            
            document.head.appendChild(script);
        });
    }
    
    // 获取模块路径
    function getModulePath(name) {
        // 判断是系统模块还是模型特定模块
        if (name.startsWith('quantum.')) {
            // 系统模块，从全局目录加载
            return `${environment.basePath}global/static/js/${name.replace('quantum.', '')}.js`;
        } else if (name.includes('.')) {
            // 含命名空间的模块
            const [namespace, moduleName] = name.split('.');
            return `${environment.basePath}${namespace}/static/js/${moduleName}.js`;
        } else {
            // 当前模型的模块
            return `${environment.basePath}${environment.modelName}/static/js/${name}.js`;
        }
    }
    
    // 显示加载指示器
    function showLoader(message) {
        // 创建加载指示器元素
        let loader = document.querySelector('.quantum-loader');
        
        if (!loader) {
            loader = document.createElement('div');
            loader.classList.add('quantum-loader');
            document.body.appendChild(loader);
        }
        
        // 如果有消息，显示加载对话框
        if (message) {
            let loadingDialog = document.querySelector('.quantum-loading');
            
            if (!loadingDialog) {
                loadingDialog = document.createElement('div');
                loadingDialog.classList.add('quantum-loading');
                loadingDialog.innerHTML = `
                    <div class="quantum-loading-content">
                        <div class="quantum-loading-spinner"></div>
                        <p id="quantum-loading-message">${message}</p>
                    </div>
                `;
                document.body.appendChild(loadingDialog);
            } else {
                document.getElementById('quantum-loading-message').textContent = message;
            }
        }
    }
    
    // 隐藏加载指示器
    function hideLoader() {
        const loader = document.querySelector('.quantum-loader');
        if (loader) {
            loader.remove();
        }
        
        const loadingDialog = document.querySelector('.quantum-loading');
        if (loadingDialog) {
            loadingDialog.remove();
        }
    }
    
    // 获取加载状态
    function getLoadStatus() {
        return {
            ...loadStatus,
            environment
        };
    }
    
    // 导出API
    window.QuantumLoader = {
        registerModule,
        initModule,
        showLoader,
        hideLoader,
        getLoadStatus,
        environment
    };
    
    // 初始化
    init();
})(); 
 * 量子加载器 - 模块加载和依赖管理
 * 提供全局资源加载、动态模块管理和依赖注入功能
 */

(function() {
    'use strict';
    
    // 模块注册表
    const modules = {};
    
    // 依赖关系图
    const dependencyGraph = {};
    
    // 加载状态
    const loadStatus = {
        pending: [],
        loaded: [],
        failed: []
    };
    
    // 运行环境检测
    const environment = {
        mode: detectMode(),
        modelName: detectModelName(),
        isStandalone: false,
        basePath: ''
    };
    
    // 初始化
    function init() {
        console.log('[量子加载器] 初始化中...');
        
        // 检测环境
        environment.isStandalone = environment.mode === 'standalone';
        environment.basePath = environment.isStandalone ? './' : '/';
        
        // 添加全局错误处理
        window.addEventListener('error', handleGlobalError);
        
        // 创建加载样式
        createLoaderStyle();
        
        console.log(`[量子加载器] 运行模式: ${environment.mode}, 模型: ${environment.modelName}`);
        
        // 通知加载完成
        document.dispatchEvent(new CustomEvent('quantum:loaderReady'));
    }
    
    // 检测运行模式: integrated 或 standalone
    function detectMode() {
        const path = window.location.pathname;
        const modelPrefixes = ['/QSM/', '/WeQ/', '/SOM/', '/Ref/'];
        
        return modelPrefixes.some(prefix => path.startsWith(prefix)) ? 'integrated' : 'standalone';
    }
    
    // 检测当前模型
    function detectModelName() {
        const path = window.location.pathname;
        const models = ['QSM', 'WeQ', 'SOM', 'Ref'];
        
        for (const model of models) {
            if (path.startsWith(`/${model}/`)) {
                return model;
            }
        }
        
        // 默认值
        return 'QSM';
    }
    
    // 创建加载样式
    function createLoaderStyle() {
        const style = document.createElement('style');
        style.textContent = `
            .quantum-loader {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 3px;
                background: linear-gradient(90deg, #3a86ff, #8338ec, #ff006e);
                z-index: 9999;
                animation: quantum-loader-progress 2s ease-in-out infinite;
            }
            
            @keyframes quantum-loader-progress {
                0% {
                    width: 0%;
                    left: 0;
                }
                50% {
                    width: 30%;
                }
                100% {
                    width: 0%;
                    left: 100%;
                }
            }
            
            .quantum-loading {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9998;
            }
            
            .quantum-loading-content {
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
                text-align: center;
            }
            
            .quantum-loading-spinner {
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 4px solid rgba(0, 0, 0, 0.1);
                border-left-color: #3a86ff;
                border-radius: 50%;
                animation: quantum-spinner 1s linear infinite;
            }
            
            @keyframes quantum-spinner {
                to {
                    transform: rotate(360deg);
                }
            }
        `;
        
        document.head.appendChild(style);
    }
    
    // 全局错误处理
    function handleGlobalError(event) {
        console.error('[量子加载器] 捕获到全局错误:', event.error || event.message);
        
        // 记录错误
        loadStatus.failed.push({
            type: 'global',
            message: event.message,
            stack: event.error ? event.error.stack : null,
            timestamp: new Date().toISOString()
        });
        
        // 防止错误传播
        event.preventDefault();
    }
    
    // 注册模块
    function registerModule(name, dependencies, factory) {
        if (modules[name]) {
            console.warn(`[量子加载器] 模块 "${name}" 已经存在，将被覆盖`);
        }
        
        modules[name] = {
            name,
            dependencies: dependencies || [],
            factory,
            instance: null,
            loaded: false
        };
        
        // 构建依赖图
        dependencyGraph[name] = dependencies || [];
        
        console.log(`[量子加载器] 注册模块: ${name}, 依赖: ${dependencies.join(', ') || '无'}`);
        
        // 返回模块API
        return {
            init: function(options) {
                return initModule(name, options);
            }
        };
    }
    
    // 初始化模块
    function initModule(name, options) {
        if (!modules[name]) {
            throw new Error(`[量子加载器] 模块 "${name}" 不存在`);
        }
        
        const module = modules[name];
        
        // 如果已经加载，直接返回实例
        if (module.loaded && module.instance) {
            return Promise.resolve(module.instance);
        }
        
        // 添加到待处理队列
        loadStatus.pending.push(name);
        
        // 加载依赖
        const dependencyPromises = module.dependencies.map(dep => {
            if (!modules[dep]) {
                return loadExternalModule(dep)
                    .then(() => {
                        if (modules[dep]) {
                            return initModule(dep);
                        }
                        throw new Error(`[量子加载器] 无法加载依赖模块: ${dep}`);
                    });
            } else {
                return initModule(dep);
            }
        });
        
        // 等待所有依赖加载完成
        return Promise.all(dependencyPromises)
            .then(instances => {
                // 创建模块实例
                try {
                    module.instance = module.factory.apply(null, instances);
                    module.loaded = true;
                    
                    // 更新状态
                    const index = loadStatus.pending.indexOf(name);
                    if (index !== -1) {
                        loadStatus.pending.splice(index, 1);
                    }
                    loadStatus.loaded.push(name);
                    
                    console.log(`[量子加载器] 模块初始化成功: ${name}`);
                    
                    return module.instance;
                } catch (error) {
                    // 记录错误
                    const index = loadStatus.pending.indexOf(name);
                    if (index !== -1) {
                        loadStatus.pending.splice(index, 1);
                    }
                    loadStatus.failed.push({
                        type: 'module',
                        name,
                        message: error.message,
                        stack: error.stack,
                        timestamp: new Date().toISOString()
                    });
                    
                    console.error(`[量子加载器] 模块初始化失败: ${name}`, error);
                    throw error;
                }
            });
    }
    
    // 加载外部模块
    function loadExternalModule(name) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = getModulePath(name);
            script.onload = () => {
                if (modules[name]) {
                    resolve();
                } else {
                    reject(new Error(`[量子加载器] 外部模块加载后未注册: ${name}`));
                }
            };
            script.onerror = () => {
                reject(new Error(`[量子加载器] 外部模块加载失败: ${name}`));
            };
            
            document.head.appendChild(script);
        });
    }
    
    // 获取模块路径
    function getModulePath(name) {
        // 判断是系统模块还是模型特定模块
        if (name.startsWith('quantum.')) {
            // 系统模块，从全局目录加载
            return `${environment.basePath}global/static/js/${name.replace('quantum.', '')}.js`;
        } else if (name.includes('.')) {
            // 含命名空间的模块
            const [namespace, moduleName] = name.split('.');
            return `${environment.basePath}${namespace}/static/js/${moduleName}.js`;
        } else {
            // 当前模型的模块
            return `${environment.basePath}${environment.modelName}/static/js/${name}.js`;
        }
    }
    
    // 显示加载指示器
    function showLoader(message) {
        // 创建加载指示器元素
        let loader = document.querySelector('.quantum-loader');
        
        if (!loader) {
            loader = document.createElement('div');
            loader.classList.add('quantum-loader');
            document.body.appendChild(loader);
        }
        
        // 如果有消息，显示加载对话框
        if (message) {
            let loadingDialog = document.querySelector('.quantum-loading');
            
            if (!loadingDialog) {
                loadingDialog = document.createElement('div');
                loadingDialog.classList.add('quantum-loading');
                loadingDialog.innerHTML = `
                    <div class="quantum-loading-content">
                        <div class="quantum-loading-spinner"></div>
                        <p id="quantum-loading-message">${message}</p>
                    </div>
                `;
                document.body.appendChild(loadingDialog);
            } else {
                document.getElementById('quantum-loading-message').textContent = message;
            }
        }
    }
    
    // 隐藏加载指示器
    function hideLoader() {
        const loader = document.querySelector('.quantum-loader');
        if (loader) {
            loader.remove();
        }
        
        const loadingDialog = document.querySelector('.quantum-loading');
        if (loadingDialog) {
            loadingDialog.remove();
        }
    }
    
    // 获取加载状态
    function getLoadStatus() {
        return {
            ...loadStatus,
            environment
        };
    }
    
    // 导出API
    window.QuantumLoader = {
        registerModule,
        initModule,
        showLoader,
        hideLoader,
        getLoadStatus,
        environment
    };
    
    // 初始化
    init();
})(); 

/*
/*
量子基因编码: QE-QUA-EB7B748504BB
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
