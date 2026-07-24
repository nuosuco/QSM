// SOM 松麦 - 前端逻辑

// API地址：同域部署时用相对路径，跨域时修改此处
const API_BASE = '';

// ========== 初始化 ==========

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initChat();
    initProductSearch();
    loadCategories();
    initProfile();
    loadTizhiKnowledge();
    loadYaoshiKnowledge();
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
        
        // 如果有推荐商品，添加到回复中
        if (data.products && data.products.length > 0) {
            replyText += '\n\n为你找到以下有机好物：';
            data.products.slice(0, 3).forEach((product, index) => {
                replyText += `\n${index + 1}. ${product.title} - ¥${product.price}`;
            });
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

// ========== 商品搜索 ==========

let currentPlatform = 'taobao';
let currentCategory = null;
let currentPage = 1;
let currentKeyword = '';
let currentSort = 'default'; // default, price_asc, price_desc, sales, credit
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
        
        // 距离底部200px时触发加载
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
        // 页面加载时自动显示"全部"分类的商品
        if (data.categories.length > 0) {
            const defaultCategory = data.categories[0]; // "全部"分类
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
    // 用分类名作为搜索关键词（后端会根据分类名映射到关键词）
    // 这样前端不需要传完整关键词，更简洁
    currentKeyword = categoryName;
    currentPage = 1;
    hasMore = true;
    searchProducts(true);
}

function setSort(sortType) {
    currentSort = sortType;
    currentPage = 1;
    hasMore = true;
    
    // 更新排序按钮状态
    const sortBtns = document.querySelectorAll('.sort-btn');
    sortBtns.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.sort === sortType) {
            btn.classList.add('active');
        }
    });
    
    // 重新搜索
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
            
            // 判断是否还有更多
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
        
        // 多张图片：如果有images数组，取第一张；否则用单张image
        let mainImage = product.image || '';
        if (product.images && product.images.length > 0) {
            mainImage = product.images[0];
        }
        
        // 佣金率显示
        let commissionText = '';
        if (product.commission_rate) {
            let rate = parseFloat(product.commission_rate);
            if (rate > 100) {
                commissionText = (rate / 100).toFixed(1) + '%';
            } else if (rate > 0) {
                commissionText = rate + '%';
            }
        }
        
        // 平台标签
        let platformBadge = '';
        if (product.platform === 'taobao') {
            platformBadge = '<span class="platform-badge taobao">淘宝</span>';
        } else if (product.platform === 'jd') {
            platformBadge = '<span class="platform-badge jd">京东</span>';
        }
        
        // 安全转义商品标题用于弹窗
        const safeTitle = escapeHtml(product.title);
        const safePrice = product.price || '';
        const safeShop = escapeHtml(product.shop_name || '');
        const safeBrand = escapeHtml(product.brand || '');
        
        return `
        <div class="product-card" onclick="showProductDetail('${safeTitle.replace(/'/g, "\\'")}', '${safePrice}', '${mainImage}', '${webUrl}', '${appUrl}', '${product.platform}', '${commissionText}', '${safeShop.replace(/'/g, "\\'")}')">
            <div class="product-image-wrapper">
                <img class="product-image" src="${mainImage}" alt="${safeTitle}" loading="lazy" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=\'img-placeholder\'><span>暂无图片</span></div>'">
                ${product.images && product.images.length > 1 ? '<div class="image-count">共' + product.images.length + '张</div>' : ''}
            </div>
            <div class="product-info">
                <div class="product-title">${safeTitle}</div>
                <div class="product-price">
                    <span>¥${safePrice}</span>
                    ${commissionText ? '<span class="commission-badge">' + commissionText + '</span>' : ''}
                </div>
                <div class="product-meta">
                    ${platformBadge}
                    <span class="product-shop">${safeShop}</span>
                </div>
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

// ========== 商品详情弹窗 ==========

function showProductDetail(title, price, image, webUrl, appUrl, platform, commissionText, shopName) {
    // 移除已有弹窗
    const existing = document.getElementById('product-detail-modal');
    if (existing) existing.remove();
    
    const modal = document.createElement('div');
    modal.id = 'product-detail-modal';
    modal.className = 'modal-overlay';
    modal.onclick = function(e) { if (e.target === this) this.remove(); };
    
    let platformLabel = platform === 'taobao' ? '淘宝' : platform === 'jd' ? '京东' : platform;
    
    modal.innerHTML = `
        <div class="modal-content product-detail-modal">
            <button class="modal-close" onclick="document.getElementById('product-detail-modal').remove()">×</button>
            <div class="detail-image-wrapper">
                <img src="${image}" alt="${title}" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=\'img-placeholder big\'><span>暂无图片</span></div>'">
            </div>
            <div class="detail-info">
                <h3 class="detail-title">${title}</h3>
                <div class="detail-price">
                    <span class="price-symbol">¥</span>
                    <span class="price-value">${price}</span>
                </div>
                <div class="detail-meta">
                    <span class="platform-badge ${platform}">${platformLabel}</span>
                    ${commissionText ? '<span class="commission-badge big">佣金 ' + commissionText + '</span>' : ''}
                    ${shopName ? '<span class="detail-shop">🏪 ' + shopName + '</span>' : ''}
                </div>
                <div class="detail-actions">
                    <button class="buy-btn" onclick="openProduct('${appUrl}', '${webUrl}', '${platform}')">
                        ${platform === 'taobao' ? '🛒 去淘宝购买' : '🛒 去京东购买'}
                    </button>
                </div>
                <p class="detail-note">💡 通过本链接购买，您将支持SOM松麦的发展</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);


function openProduct(appUrl, webUrl, platform) {
    if (platform === 'taobao' && appUrl) {
        // 先尝试打开淘宝APP
        window.location.href = appUrl;
        // 2.5秒后如果页面还可见（APP没安装），回退到网页版
        setTimeout(() => {
            if (!document.hidden) {
                window.open(webUrl, '_blank');
            }
        }, 2500);
    } else {
        window.open(webUrl, '_blank');
    }
}

// ========== 个人中心 ==========

function initProfile() {
    loadProfile();
}

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

function loadProfile() {
    const data = getUserData();
    
    document.getElementById('profile-name').textContent = data.name;
    document.getElementById('profile-tizhi').textContent = '体质：' + (data.tizhi || '未检测');
    document.getElementById('profile-points').textContent = '积分：' + (data.points || 0);
    
    const today = new Date().toISOString().split('T')[0];
    const checkedInToday = data.checkins && data.checkins.indexOf(today) >= 0;
    const checkinEl = document.getElementById('profile-checkin');
    checkinEl.textContent = checkedInToday ? '✅ 今天已签到' : '📅 签到：今天未签到';
    if (!checkedInToday) {
        checkinEl.style.cursor = 'pointer';
        checkinEl.onclick = doCheckin;
    } else {
        checkinEl.style.cursor = 'default';
        checkinEl.onclick = null;
    }
    
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

// ========== 签到功能 ==========

function doCheckin() {
    const data = getUserData();
    const today = new Date().toISOString().split('T')[0];
    
    if (data.checkins && data.checkins.indexOf(today) >= 0) {
        return;
    }
    
    if (!data.checkins) data.checkins = [];
    data.checkins.push(today);
    
    // 签到奖励积分
    if (!data.points) data.points = 0;
    data.points += 10;
    
    saveUserData(data);
    
    // 更新显示
    const checkinEl = document.getElementById('profile-checkin');
    checkinEl.textContent = '✅ 今天已签到';
    checkinEl.style.cursor = 'default';
    checkinEl.onclick = null;
    
    document.getElementById('profile-points').textContent = '积分：' + data.points;
    document.getElementById('stat-checkins').textContent = data.checkins.length;
    
    alert('🎉 签到成功！获得10积分');
}

// ========== 养生谷知识库加载 ==========

async function loadTizhiKnowledge() {
    try {
        const response = await fetch(`${API_BASE}/api/knowledge/tizhi`);
        const data = await response.json();
        const grid = document.getElementById('tizhi-grid');
        if (data && data.length > 0) {
            grid.innerHTML = data.map(t => `
                <div class="tizhi-card">
                    <h3>${escapeHtml(t.name || '')}</h3>
                    <p><strong>特征：</strong>${escapeHtml(t.features || '')}</p>
                    <p><strong>调养：</strong>${escapeHtml(t.diet || '')}</p>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('加载体质知识失败:', e);
    }
}

async function loadYaoshiKnowledge() {
    try {
        const response = await fetch(`${API_BASE}/api/knowledge/yaoshi`);
        const data = await response.json();
        const list = document.getElementById('yaoshi-list');
        if (data && data.length > 0) {
            list.innerHTML = data.map(y => `
                <div class="yaoshi-item">
                    <h4>${escapeHtml(y.name || '')}</h4>
                    <p><strong>性味：</strong>${escapeHtml(y.xingwei || '')}</p>
                    <p><strong>功效：</strong>${escapeHtml(y.gongxiao || '')}</p>
                    <p><strong>禁忌：</strong>${escapeHtml(y.jinji || '')}</p>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('加载药食同源知识失败:', e);
    }
}

// ========== 商品详情弹窗 ==========
let currentDetailProduct = null;

function showDetail(product) {
    currentDetailProduct = product;
    
    // 主图
    let mainImage = product.image || '';
    if (product.images && product.images.length > 0) {
        mainImage = product.images[0];
    }
    document.getElementById('detail-main-image').innerHTML = 
        `<img src="${mainImage}" alt="${escapeHtml(product.title)}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23f5f7f6%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 fill=%22%237bc49f%22 font-size=%2220%22>暂无图片</text></svg>'">`;
    
    // 缩略图
    let thumbnails = '';
    const images = product.images || [mainImage];
    images.forEach((img, i) => {
        thumbnails += `<img src="${img}" class="detail-thumb${i === 0 ? ' active' : ''}" onclick="switchDetailImage(this, '${img}')" onerror="this.style.display='none'">`;
    });
    document.getElementById('detail-thumbnails').innerHTML = thumbnails;
    
    // 标题
    document.getElementById('detail-title').textContent = product.title;
    
    // 价格
    document.getElementById('detail-price').innerHTML = `<span class="price-symbol">¥</span>${product.price}`;
    
    // 店铺
    let shopHtml = '';
    if (product.shop_name) {
        shopHtml += `<span>🏪 ${escapeHtml(product.shop_name)}</span>`;
    }
    if (product.brand) {
        shopHtml += `<span>🏷️ ${escapeHtml(product.brand)}</span>`;
    }
    document.getElementById('detail-shop').innerHTML = shopHtml;
    
    // 参数（从数据库取）
    document.getElementById('detail-params').innerHTML = '<div class="detail-section-title">商品参数</div><div class="detail-params-list"><span>暂无详细参数</span></div>';
    
    // 描述
    document.getElementById('detail-desc').innerHTML = '<div class="detail-section-title">商品描述</div><p>点击下方按钮查看淘宝详情</p>';
    
    // 购买按钮
    const buyBtn = document.getElementById('detail-buy-btn');
    const platform = product.platform || 'taobao';
    const platformName = platform === 'taobao' ? '淘宝' : '京东';
    buyBtn.textContent = `去${platformName}购买`;
    buyBtn.onclick = function() {
        let url = product.url || '#';
        if (url && url !== '#') {
            window.open(url, '_blank');
        }
    };
    
    // 显示弹窗
    document.getElementById('product-detail-overlay').style.display = 'flex';
}

function closeDetail() {
    document.getElementById('product-detail-overlay').style.display = 'none';
    currentDetailProduct = null;
}

function switchDetailImage(el, imgUrl) {
    document.querySelectorAll('.detail-thumb').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    document.getElementById('detail-main-image').innerHTML = 
        `<img src="${imgUrl}" alt="商品图片">`;
}

function goToBuy() {
    if (currentDetailProduct) {
        let url = currentDetailProduct.url || '#';
        if (url && url !== '#') {
            window.open(url, '_blank');
        }
    }
}

// 点击遮罩层关闭
document.addEventListener('click', function(e) {
    const overlay = document.getElementById('product-detail-overlay');
    if (e.target === overlay) {
        closeDetail();
    }
});
