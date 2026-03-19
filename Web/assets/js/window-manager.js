/**
 * QEntL Web操作系统 - 窗口管理器
 * 支持三语界面（中/英/彝）
 */

class WindowManager {
    constructor() {
        this.windows = new Map();
        this.zIndex = 100;
        this.activeWindow = null;
    }
    
    // 创建窗口
    createWindow(options) {
        const id = options.id || 'window-' + Date.now();
        const window = {
            id: id,
            title: options.title || '窗口',
            icon: options.icon || '📄',
            width: options.width || 800,
            height: options.height || 600,
            x: options.x || 100 + this.windows.size * 30,
            y: options.y || 50 + this.windows.size * 30,
            url: options.url || '',
            minimized: false,
            maximized: false
        };
        
        this.windows.set(id, window);
        this.renderWindow(window);
        return window;
    }
    
    // 渲染窗口
    renderWindow(window) {
        const container = document.getElementById('windows-container') || document.body;
        
        const windowEl = document.createElement('div');
        windowEl.className = 'q-window';
        windowEl.id = window.id;
        windowEl.style.cssText = `
            width: ${window.width}px;
            height: ${window.height}px;
            left: ${window.x}px;
            top: ${window.y}px;
            z-index: ${++this.zIndex};
        `;
        
        windowEl.innerHTML = `
            <div class="q-window-header">
                <div class="q-window-title">
                    <span>${window.icon}</span>
                    <span class="window-title-text">${window.title}</span>
                </div>
                <div class="q-window-controls">
                    <div class="q-window-btn minimize" title="最小化"></div>
                    <div class="q-window-btn maximize" title="最大化"></div>
                    <div class="q-window-btn close" title="关闭"></div>
                </div>
            </div>
            <div class="q-window-content">
                ${window.url ? `<iframe src="${window.url}" style="width:100%;height:100%;border:none;"></iframe>` : ''}
            </div>
        `;
        
        this.setupWindowEvents(windowEl, window);
        container.appendChild(windowEl);
    }
    
    // 设置窗口事件
    setupWindowEvents(windowEl, window) {
        const header = windowEl.querySelector('.q-window-header');
        const closeBtn = windowEl.querySelector('.q-window-btn.close');
        const minBtn = windowEl.querySelector('.q-window-btn.minimize');
        const maxBtn = windowEl.querySelector('.q-window-btn.maximize');
        
        // 关闭
        closeBtn.onclick = () => this.closeWindow(window.id);
        
        // 最小化
        minBtn.onclick = () => this.minimizeWindow(window.id);
        
        // 最大化
        maxBtn.onclick = () => this.maximizeWindow(window.id);
        
        // 拖拽
        this.makeDraggable(windowEl, header);
        
        // 聚焦
        windowEl.onmousedown = () => this.focusWindow(window.id);
    }
    
    // 使窗口可拖拽
    makeDraggable(windowEl, handle) {
        let isDragging = false;
        let startX, startY, startLeft, startTop;
        
        handle.onmousedown = (e) => {
            if (e.target.classList.contains('q-window-btn')) return;
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            startLeft = windowEl.offsetLeft;
            startTop = windowEl.offsetTop;
            e.preventDefault();
        };
        
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            windowEl.style.left = (startLeft + e.clientX - startX) + 'px';
            windowEl.style.top = (startTop + e.clientY - startY) + 'px';
        });
        
        document.addEventListener('mouseup', () => {
            isDragging = false;
        });
    }
    
    // 聚焦窗口
    focusWindow(id) {
        const window = this.windows.get(id);
        if (window) {
            const windowEl = document.getElementById(id);
            if (windowEl) {
                windowEl.style.zIndex = ++this.zIndex;
                this.activeWindow = window;
            }
        }
    }
    
    // 最小化窗口
    minimizeWindow(id) {
        const windowEl = document.getElementById(id);
        if (windowEl) {
            windowEl.style.display = 'none';
            this.windows.get(id).minimized = true;
        }
    }
    
    // 最大化窗口
    maximizeWindow(id) {
        const window = this.windows.get(id);
        const windowEl = document.getElementById(id);
        if (window && windowEl) {
            if (window.maximized) {
                windowEl.style.width = window.width + 'px';
                windowEl.style.height = window.height + 'px';
                windowEl.style.left = window.x + 'px';
                windowEl.style.top = window.y + 'px';
                window.maximized = false;
            } else {
                windowEl.style.width = '100%';
                windowEl.style.height = 'calc(100% - 48px)';
                windowEl.style.left = '0';
                windowEl.style.top = '0';
                window.maximized = true;
            }
        }
    }
    
    // 关闭窗口
    closeWindow(id) {
        const windowEl = document.getElementById(id);
        if (windowEl) {
            windowEl.remove();
            this.windows.delete(id);
        }
    }
    
    // 更新标题（多语言）
    updateTitle(id, titles) {
        const windowEl = document.getElementById(id);
        if (windowEl) {
            const titleText = windowEl.querySelector('.window-title-text');
            titleText.textContent = titles[currentLang] || titles.zh;
        }
    }
}

// 导出
window.WindowManager = WindowManager;
