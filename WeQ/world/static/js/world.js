/**
 * 全局JavaScript文件
 * 为所有模型提供共享功能
 */

// 检测浏览器环境
const browserInfo = {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    cookieEnabled: navigator.cookieEnabled,
    doNotTrack: navigator.doNotTrack,
    online: navigator.onLine,
    screenSize: {
        width: window.screen.width,
        height: window.screen.height
    },
    viewportSize: {
        width: window.innerWidth,
        height: window.innerHeight
    }
};

// 全局事件处理
document.addEventListener('DOMContentLoaded', function() {
    console.log('[全局] 页面加载完成');
    
    // 初始化全局UI组件
    initGlobalUI();
    
    // 记录页面访问
    logPageView();
});

// 全局UI组件初始化
function initGlobalUI() {
    // 添加响应式导航控制
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            const mainNav = document.querySelector('.main-nav');
            if (mainNav) {
                mainNav.classList.toggle('active');
            }
        });
    }
    
    // 添加滚动到顶部按钮
    addScrollToTopButton();
    
    // 初始化深色模式切换
    initDarkModeToggle();
}

// 添加滚动到顶部按钮
function addScrollToTopButton() {
    const scrollBtn = document.createElement('button');
    scrollBtn.classList.add('scroll-to-top');
    scrollBtn.innerHTML = '↑';
    scrollBtn.title = '回到顶部';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: var(--primary-color);
        color: white;
        border: none;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s;
        z-index: 1000;
    `;
    
    document.body.appendChild(scrollBtn);
    
    // 控制按钮显示/隐藏
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollBtn.style.opacity = '1';
        } else {
            scrollBtn.style.opacity = '0';
        }
    });
    
    // 点击滚动到顶部
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 初始化深色模式切换
function initDarkModeToggle() {
    // 检查用户首选项
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedDarkMode = localStorage.getItem('darkMode');
    
    // 设置初始模式
    if (savedDarkMode === 'true' || (savedDarkMode === null && prefersDarkMode)) {
        document.documentElement.classList.add('dark-mode');
    }
    
    // 添加切换按钮
    const darkModeToggle = document.createElement('button');
    darkModeToggle.classList.add('dark-mode-toggle');
    darkModeToggle.innerHTML = document.documentElement.classList.contains('dark-mode') ? '☀️' : '🌙';
    darkModeToggle.title = document.documentElement.classList.contains('dark-mode') ? '切换到浅色模式' : '切换到深色模式';
    darkModeToggle.style.cssText = `
        position: fixed;
        bottom: 70px;
        right: 20px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: var(--dark-color);
        color: white;
        border: none;
        cursor: pointer;
        z-index: 1000;
    `;
    
    document.body.appendChild(darkModeToggle);
    
    // 切换深色模式
    darkModeToggle.addEventListener('click', function() {
        document.documentElement.classList.toggle('dark-mode');
        const isDarkMode = document.documentElement.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        darkModeToggle.innerHTML = isDarkMode ? '☀️' : '🌙';
        darkModeToggle.title = isDarkMode ? '切换到浅色模式' : '切换到深色模式';
    });
}

// 记录页面访问
function logPageView() {
    const pageData = {
        url: window.location.href,
        title: document.title,
        referrer: document.referrer,
        timestamp: new Date().toISOString(),
        browserInfo: browserInfo
    };
    
    // 如果量子纠缠信道可用，则通过信道记录
    if (window.quantumChannel && window.quantumChannel.connected) {
        window.quantumChannel.send('analytics', {
            type: 'pageView',
            data: pageData
        });
    } else {
        // 否则使用传统方式记录
        console.log('[分析] 页面访问', pageData);
        
        // 可以发送到服务器端点
        fetch('/api/v1/analytics/pageview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(pageData),
            // 使用Keep-Alive降低创建连接的开销
            keepalive: true
        }).catch(err => {
            console.warn('[分析] 无法记录页面访问', err);
        });
    }
}

// 全局工具函数
const globalUtils = {
    // 格式化日期
    formatDate: function(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },
    
    // 防抖
    debounce: function(func, wait) {
        let timeout;
        return function(...args) {
            const context = this;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    },
    
    // 节流
    throttle: function(func, limit) {
        let inThrottle;
        return function(...args) {
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // 安全地获取嵌套对象属性
    getNestedProperty: function(obj, path, defaultValue = undefined) {
        return path.split('.').reduce((prev, curr) => {
            return prev && prev[curr] !== undefined ? prev[curr] : defaultValue;
        }, obj);
    }
};

// 将全局工具函数暴露为全局变量
window.globalUtils = globalUtils;

console.log('[全局] 全局脚本已加载'); 
 * 全局JavaScript文件
 * 为所有模型提供共享功能
 */

// 检测浏览器环境
const browserInfo = {
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    language: navigator.language,
    cookieEnabled: navigator.cookieEnabled,
    doNotTrack: navigator.doNotTrack,
    online: navigator.onLine,
    screenSize: {
        width: window.screen.width,
        height: window.screen.height
    },
    viewportSize: {
        width: window.innerWidth,
        height: window.innerHeight
    }
};

// 全局事件处理
document.addEventListener('DOMContentLoaded', function() {
    console.log('[全局] 页面加载完成');
    
    // 初始化全局UI组件
    initGlobalUI();
    
    // 记录页面访问
    logPageView();
});

// 全局UI组件初始化
function initGlobalUI() {
    // 添加响应式导航控制
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            const mainNav = document.querySelector('.main-nav');
            if (mainNav) {
                mainNav.classList.toggle('active');
            }
        });
    }
    
    // 添加滚动到顶部按钮
    addScrollToTopButton();
    
    // 初始化深色模式切换
    initDarkModeToggle();
}

// 添加滚动到顶部按钮
function addScrollToTopButton() {
    const scrollBtn = document.createElement('button');
    scrollBtn.classList.add('scroll-to-top');
    scrollBtn.innerHTML = '↑';
    scrollBtn.title = '回到顶部';
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: var(--primary-color);
        color: white;
        border: none;
        cursor: pointer;
        opacity: 0;
        transition: opacity 0.3s;
        z-index: 1000;
    `;
    
    document.body.appendChild(scrollBtn);
    
    // 控制按钮显示/隐藏
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollBtn.style.opacity = '1';
        } else {
            scrollBtn.style.opacity = '0';
        }
    });
    
    // 点击滚动到顶部
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// 初始化深色模式切换
function initDarkModeToggle() {
    // 检查用户首选项
    const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedDarkMode = localStorage.getItem('darkMode');
    
    // 设置初始模式
    if (savedDarkMode === 'true' || (savedDarkMode === null && prefersDarkMode)) {
        document.documentElement.classList.add('dark-mode');
    }
    
    // 添加切换按钮
    const darkModeToggle = document.createElement('button');
    darkModeToggle.classList.add('dark-mode-toggle');
    darkModeToggle.innerHTML = document.documentElement.classList.contains('dark-mode') ? '☀️' : '🌙';
    darkModeToggle.title = document.documentElement.classList.contains('dark-mode') ? '切换到浅色模式' : '切换到深色模式';
    darkModeToggle.style.cssText = `
        position: fixed;
        bottom: 70px;
        right: 20px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: var(--dark-color);
        color: white;
        border: none;
        cursor: pointer;
        z-index: 1000;
    `;
    
    document.body.appendChild(darkModeToggle);
    
    // 切换深色模式
    darkModeToggle.addEventListener('click', function() {
        document.documentElement.classList.toggle('dark-mode');
        const isDarkMode = document.documentElement.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        darkModeToggle.innerHTML = isDarkMode ? '☀️' : '🌙';
        darkModeToggle.title = isDarkMode ? '切换到浅色模式' : '切换到深色模式';
    });
}

// 记录页面访问
function logPageView() {
    const pageData = {
        url: window.location.href,
        title: document.title,
        referrer: document.referrer,
        timestamp: new Date().toISOString(),
        browserInfo: browserInfo
    };
    
    // 如果量子纠缠信道可用，则通过信道记录
    if (window.quantumChannel && window.quantumChannel.connected) {
        window.quantumChannel.send('analytics', {
            type: 'pageView',
            data: pageData
        });
    } else {
        // 否则使用传统方式记录
        console.log('[分析] 页面访问', pageData);
        
        // 可以发送到服务器端点
        fetch('/api/v1/analytics/pageview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(pageData),
            // 使用Keep-Alive降低创建连接的开销
            keepalive: true
        }).catch(err => {
            console.warn('[分析] 无法记录页面访问', err);
        });
    }
}

// 全局工具函数
const globalUtils = {
    // 格式化日期
    formatDate: function(date, format = 'YYYY-MM-DD') {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    },
    
    // 防抖
    debounce: function(func, wait) {
        let timeout;
        return function(...args) {
            const context = this;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    },
    
    // 节流
    throttle: function(func, limit) {
        let inThrottle;
        return function(...args) {
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // 安全地获取嵌套对象属性
    getNestedProperty: function(obj, path, defaultValue = undefined) {
        return path.split('.').reduce((prev, curr) => {
            return prev && prev[curr] !== undefined ? prev[curr] : defaultValue;
        }, obj);
    }
};

// 将全局工具函数暴露为全局变量
window.globalUtils = globalUtils;

console.log('[全局] 全局脚本已加载'); 

/*
/*
量子基因编码: QE-WOR-993637B214BA
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
