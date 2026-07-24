// SOM 松麦 - 前端逻辑 v2

// API地址：同域部署时用相对路径，跨域时修改此处
const API_BASE = '';

// ========== 初始化 ==========

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initChat();
    initProductSearch();
    initYangshengGu();
    initProfile();
    initCheckin();
    loadDailyTip();
    loadCategories();
});

// ========== 导航切换 ==========

function initNavigation() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.dataset.tab;
            
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            tabContents.forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`${targetTab}-tab`).classList.add('active');
        });
    });
}

// ========== 对话功能 ==========

function initChat() {
    const sendBtn = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const message = input.value.trim();
    
    if (!message) return;
    
    // 显示用户消息
    appendMessage(message, 'user');
    input.value = '';
    sendBtn.disabled = true;
    
    // 显示加载状态
    const loadingId = appendMessage('<div class="loading"></div>', 'assistant', true);
    
    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: getSessionId()
            })
        });
        
        const data = await response.json();
        
        // 移除加载状态
        document.getElementById(loadingId).remove();
        
        // 显示AI回复
        let replyText = data.reply;
        
        // 如果有推荐食材，添加到回复中
        if (data.recommendations && data.recommendations.length > 0) {
            let recHtml = '<div class="rec-list">';
            data.recommendations.forEach(rec => {
                recHtml += `<div class="rec-item">
                    <strong>${esc(rec.name)}</strong>
                    ${rec.xingwei ? '· ' + esc(rec.xingwei) : ''}
                </div>`;
            });
            recHtml += '</div>';
            appendMessage(recHtml, 'assistant');
        }
        
        // 如果有推荐商品，添加到回复中
        if (data.products && data.products.length > 0) {
            replyText += '\n\n为你找到以下有机好物：';
            data.products.slice(0, 6).forEach((product, index) => {
                replyText += `\n${index + 1}. ${product.title} - ¥${product.price}`;
            });
        } else if (data.zhengxing || data.tizhi) {
            // 保存辨证结果到用户数据
            saveTizhiRecord(data.tizhi, message);
        }
        
        appendMessage(replyText, 'assistant');
        
    } catch (error) {
        document.getElementById(loadingId).remove();
        appendMessage('抱歉，网络出现问题，请稍后重试。', 'assistant');
        console.error('发送消息失败:', error);
    } finally {
        sendBtn.disabled = false;
    }
}

function appendMessage(text, type, isHtml = false) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const messageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    messageDiv.id = messageId;
    
    const avatar = type === 'user' ? '你' : '麦';
    
    if (isHtml) {
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${text}</div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-text">${escapeHtml(text)}</div>
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageId;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getSessionId() {
    let sessionId = sessionStorage.getItem('som_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('som_session_id', sessionId);
    }
    return sessionId;
}

// ========== 工具函数 =========

function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

// ========== 商品搜索 ==========

let currentPlatform = 'taobao';
let currentCategory = null;
let currentPage = 1;
let currentKeyword = '';
let currentSort = 'default';
let isLoading = false;
let hasMore = true;

function initProductSearch() {
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('product-search');
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    searchBtn.addEventListener('click', () => {
        currentKeyword = searchInput.value.trim();
        currentPage = 1;
        hasMore = true;
        searchProducts(true);
    });
    
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            currentKeyword = searchInput.value.trim();
            currentPage = 1;
            hasMore = true;
            searchProducts(true);
        }
    });
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentPlatform = btn.dataset.platform;
            currentPage = 1;
            hasMore = true;
            if (currentCategory) {
                searchProducts(true);
            } else if (currentKeyword) {
                searchProducts(true);
            }
        });
    });
    
    // 排序按钮事件
    const sortBtns = document.querySelectorAll('.sort-btn');
    sortBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            sortBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentSort = btn.dataset.sort;
            currentPage = 1;
            hasMore = true;
            searchProducts(true);
        });
    });
    
    // 无限滚动加载
    window.addEventListener('scroll', () => {
        if (isLoading || !hasMore) return;
        
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        if (scrollTop + windowHeight >= documentHeight - 200) {
            loadMoreProducts();
        }
    });
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/api/products/categories`);
        const data = await response.json();
        displayCategories(data.categories);
        if (data.categories.length > 0) {
            const defaultCategory = data.categories[0];
            searchByCategory(defaultCategory.keyword, defaultCategory.name);
        }
    } catch (error) {
        console.error('加载分类失败:', error);
        document.getElementById('category-nav').innerHTML = '<div class="category-loading">分类加载失败</div>';
    }
}

function displayCategories(categories) {
    const categoryNav = document.getElementById('category-nav');
    
    categoryNav.innerHTML = categories.map(cat => `
        <div class="category-item" onclick="searchByCategory('${cat.keyword}', '${cat.name}')">
            <div class="category-icon">${cat.icon}</div>
            <div class="category-name">${cat.name}</div>
        </div>
    `).join('');
}

function searchByCategory(keyword, categoryName = '') {
    currentCategory = keyword;
    currentKeyword = keyword.split(' ')[0];
    currentPage = 1;
    hasMore = true;
    searchProducts(true);
}

function setSort(sortType) {
    currentSort = sortType;
    currentPage = 1;
    hasMore = true;
    
    const sortBtns = document.querySelectorAll('.sort-btn');
    sortBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.sort === sortType) {
            btn.classList.add('active');
        }
    });
    
    if (currentCategory) {
        searchByCategory(currentCategory);
    } else if (currentKeyword) {
        searchProducts(true);
    }
}

async function searchProducts(clear = false) {
    if (isLoading) return;
    
    isLoading = true;
    const productsGrid = document.getElementById('products-grid');
    
    if (clear) {
        productsGrid.innerHTML = '<div class="empty-state"><div class="loading"></div><p>搜索中...</p></div>';
    }
    
    try {
        const sortParam = currentSort !== 'default' ? `&sort=${currentSort}` : '';
        const response = await fetch(
            `${API_BASE}/api/products/search?keyword=${encodeURIComponent(currentKeyword)}&platform=${currentPlatform}&page=${currentPage}&page_size=20${sortParam}`
        );
        
        const data = await response.json();
        
        if (data.items && data.items.length > 0) {
            if (clear) {
                productsGrid.innerHTML = '';
            }
            displayProducts(data.items, !clear);
            
            if (data.items.length < 20) {
                hasMore = false;
            }
            currentPage++;
        } else {
            if (clear) {
                productsGrid.innerHTML = '<div class="empty-state"><p>未找到相关有机产品</p></div>';
            }
            hasMore = false;
        }
        
    } catch (error) {
        if (clear) {
            productsGrid.innerHTML = '<div class="empty-state"><p>搜索失败，请稍后重试</p></div>';
        }
        console.error('搜索商品失败:', error);
    } finally {
        isLoading = false;
    }
}

async function loadMoreProducts() {
    if (!hasMore || isLoading) return;
    
    const productsGrid = document.getElementById('products-grid');
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'empty-state';
    loadingIndicator.id = 'loading-more';
    loadingIndicator.innerHTML = '<div class="loading"></div><p>加载更多...</p>';
    productsGrid.appendChild(loadingIndicator);
    
    await searchProducts(false);
    
    const indicator = document.getElementById('loading-more');
    if (indicator) {
        indicator.remove();
    }
}

function displayProducts(products, append = false) {
    const productsGrid = document.getElementById('products-grid');
    
    const productHtml = products.map(product => {
        let appUrl = product.app_url || '';
        let webUrl = product.url || '#';
        
        return `
        <div class="product-card" onclick="openProduct('${appUrl}', '${webUrl}', '${product.platform}')">
            <img class="product-image" src="${product.image}" alt="${escapeHtml(product.title)}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23f5f7f6%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 fill=%22%237bc49f%22 font-size=%2220%22>暂无图片</text></svg>'">
            <div class="product-info">
                <div class="product-title">${escapeHtml(product.title)}</div>
                <div class="product-price">¥${product.price}</div>
                <div class="product-shop">${escapeHtml(product.shop_name || '')} · ${product.platform === 'taobao' ? '淘宝' : '京东'}</div>
            </div>
        </div>
        `;
    }).join('');
    
    if (append) {
        productsGrid.insertAdjacentHTML('beforeend', productHtml);
    } else {
        productsGrid.innerHTML = productHtml;
    }
}

function openProduct(appUrl, webUrl, platform) {
    if (platform === 'taobao' && appUrl) {
        window.location.href = appUrl;
        setTimeout(() => {
            if (!document.hidden) {
                window.open(webUrl, '_blank');
            }
        }, 2500);
    } else {
        window.open(webUrl, '_blank');
    }
}

// ========== 养生谷 =========

async function initYangshengGu() {
    await Promise.all([
        loadTizhi(),
        loadYaoshi()
    ]);
    await loadDailyTip();
}

async function loadTizhi() {
    try {
        const res = await fetch(`${API_BASE}/api/knowledge/tizhi`);
        const data = await res.json();
        const grid = document.getElementById('tizhi-grid');
        if (!grid || !data.items) return;
        
        grid.innerHTML = data.items.map(t => `
            <div class="tizhi-card">
                <h3>${esc(t.name)}</h3>
                <p>💡 ${esc(t.desc)}</p>
                <p style="margin-top:8px;color:var(--primary-color)">🍵 调养：${esc(t.diet || t.yangsheng || '')}</p>
            </div>
        `).join('');
    } catch(e) {
        console.error('加载体质数据失败', e);
    }
}

async function loadYaoshi() {
    try {
        const res = await fetch(`${API_BASE}/api/knowledge/yaoshi`);
        const data = await res.json();
        const list = document.getElementById('yaoshi-list');
        if (!list || !data.items) return;
        
        list.innerHTML = data.items.map(y => `
            <div class="yaoshi-item">
                <h4>${esc(y.name)}</h4>
                <p><strong>性味：</strong>${esc(y.xingwei)}</p>
                <p><strong>归经：</strong>${esc(y.guijing)}</p>
                <p><strong>功效：</strong>${esc(y.gongxiao)}</p>
                <p style="color:#e74c3c;font-size:11px"><strong>⚠️ 禁忌：</strong>${esc(y.jinji)}</p>
            </div>
        `).join('');
    } catch(e) {
        console.error('加载药食同源数据失败', e);
    }
}

// ========== 个人中心 ==========

function getUserId() {
    let uid = localStorage.getItem('som_user_id');
    if (!uid) {
        uid = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('som_user_id', uid);
    }
    return uid;
}

function getUserData() {
    const key = 'som_user_data_' + getUserId();
    const dataStr = localStorage.getItem(key);
    let data;
    if (dataStr) {
        try { data = JSON.parse(dataStr); } catch(e) { data = {}; }
    } else {
        data = {};
    }
    if (!data.name) data.name = '养生用户';
    if (!data.tizhi) data.tizhi = '未检测';
    if (!data.points) data.points = 0;
    if (!data.chats) data.chats = [];
    if (!data.checkins) data.checkins = [];
    if (!data.productBrowses) data.productBrowses = 0;
    if (!data.tizhiRecords) data.tizhiRecords = [];
    return data;
}

function saveUserData(data) {
    const key = 'som_user_data_' + getUserId();
    localStorage.setItem(key, JSON.stringify(data));
}

function initProfile() {
    loadProfile();
}

function loadProfile() {
    const data = getUserData();
    
    document.getElementById('profile-name').textContent = data.name;
    document.getElementById('profile-tizhi').textContent = '体质：' + (data.tizhi || '未检测');
    document.getElementById('profile-points').textContent = '积分：' + (data.points || 0);
    
    const today = new Date().toISOString().split('T')[0];
    const checkedInToday = data.checkins && data.checkins.indexOf(today) >= 0;
    document.getElementById('profile-checkin').textContent = checkedInToday ? '✅ 今天已签到' : '签到：今天未签到';
    
    document.getElementById('stat-chats').textContent = (data.chats || []).length;
    document.getElementById('stat-checkins').textContent = (data.checkins || []).length;
    document.getElementById('stat-products').textContent = data.productBrowses || 0;
    
    loadTizhiRecords(data);
}

function loadTizhiRecords(data) {
    const history = document.getElementById('profile-history');
    if (!history) return;
    
    const records = data.tizhiRecords || [];
    if (records.length === 0) {
        history.innerHTML = '<p class="empty-hint">暂无体质记录，快去和小麦SOM对话吧</p>';
        return;
    }
    
    let html = '';
    const maxShow = Math.min(records.length, 5);
    for (let i = records.length - maxShow; i < records.length; i++) {
        const r = records[i];
        html += '<div class="history-item">';
        html += '  <span class="history-date">' + escapeHtml(r.date || '') + '</span>';
        html += '  <span class="history-tizhi">' + escapeHtml(r.tizhi || '') + '</span>';
        html += '  <span class="history-desc">' + escapeHtml(r.desc || '') + '</span>';
        html += '</div>';
    }
    history.innerHTML = html;
}

function saveChatRecord(message, reply, tizhi) {
    const data = getUserData();
    if (!data.chats) data.chats = [];
    
    data.chats.push({
        date: new Date().toISOString(),
        message: message.substring(0, 100),
        tizhi: tizhi || ''
    });
    
    if (tizhi && tizhi !== '未检测') {
        if (!data.tizhiRecords) data.tizhiRecords = [];
        data.tizhiRecords.push({
            date: new Date().toISOString().split('T')[0],
            tizhi: tizhi,
            desc: message.substring(0, 50)
        });
        data.tizhi = tizhi;
    }
    
    saveUserData(data);
}

function saveProductBrowse(keyword, count) {
    const data = getUserData();
    if (!data.productBrowses) data.productBrowses = 0;
    data.productBrowses += count;
    saveUserData(data);
}

function initCheckin() {
    const userId = getUserId();
    const statusBtn = document.getElementById('checkin-btn');
    if (statusBtn) {
        statusBtn.addEventListener('click', doCheckin);
    }
    refreshCheckinUI();
}

async function refreshCheckinUI() {
    const userId = getUserId();
    try {
        const res = await fetch(`${API_BASE}/api/checkin/status?user_id=${userId}`);
        const data = await res.json();
        const checkinText = document.getElementById('profile-checkin-status');
        const checkinBtn = document.getElementById('checkin-btn');
        if (checkinText) {
            checkinText.textContent = data.checked_in_today ? '✅ 今日已签到' : '今天还未签到';
        }
        if (checkinBtn) {
            checkinBtn.textContent = data.checked_in_today ? '✅ 已签到' : '去签到';
            checkinBtn.disabled = data.checked_in_today;
        }
    } catch(e) {
        console.error('获取签到状态失败', e);
    }
}

async function doCheckin() {
    const userId = getUserId();
    const btn = document.getElementById('checkin-btn');
    if (btn) btn.disabled = true;
    
    try {
        const res = await fetch(`${API_BASE}/api/checkin/do`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });
        const data = await res.json();
        
        const dataObj = getUserData();
        dataObj.points = data.total_points || (dataObj.points || 0) + (data.success ? 10 : 0);
        saveUserData(dataObj);
        loadProfile();
        
        await refreshCheckinUI();
        
        alert(data.message || '签到成功！');
    } catch(e) {
        alert('签到失败，请稍后重试');
        if (btn) btn.disabled = false;
    }
}

// ========== 每日养生建议 ==========

async function loadDailyTip() {
    try {
        const res = await fetch(`${API_BASE}/api/daily-tip`);
        const tip = await res.json();
        
        // 顶部每日建议卡片
        const tipEl = document.getElementById('daily-tip');
        if (tipEl && tip.title) {
            tipEl.innerHTML = `
                <div class="daily-tip-card">
                    <div class="daily-tip-header">${tip.emoji} ${esc(tip.title)}</div>
                    <div class="daily-tip-content">${esc(tip.content)}</div>
                </div>
            `;
        }
        
        // 养生谷页面内每日建议
        const tipContentEl = document.getElementById('daily-tip-content');
        if (tipContentEl && tip.title) {
            tipContentEl.innerHTML = `
                <div class="daily-tip-card">
                    <div class="daily-tip-header">${tip.emoji} ${esc(tip.title)}</div>
                    <div class="daily-tip-content">${esc(tip.content)}</div>
                </div>
            `;
        }
    } catch(e) {
        console.error('加载每日建议失败', e);
    }
}

// ========== 保存辨证记录 =========

function saveTizhiRecord(tizhi, msg) {
    const data = getUserData();
    if (tizhi && tizhi !== '未检测') {
        if (!data.tizhiRecords) data.tizhiRecords = [];
        data.tizhiRecords.push({
            date: new Date().toISOString().split('T')[0],
            tizhi: tizhi,
            desc: (msg || '').substring(0, 50)
        });
        data.tizhi = tizhi;
        saveUserData(data);
    }
}
