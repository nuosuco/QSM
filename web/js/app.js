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
    // 用分类名称作为搜索框显示，但实际搜索用后端关键词
    // 取关键词的第一个词作为搜索关键词，避免太长
    currentKeyword = keyword.split(' ')[0];
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

// 商品数据缓存，用ID索引
let _productCache = {};
let _productIndex = 0;

function displayProducts(products, append = false) {
    const productsGrid = document.getElementById('products-grid');
    
    const productHtml = products.map(product => {
        // 用唯一索引存数据，避免JSON.stringify嵌入HTML导致特殊字符炸掉
        _productIndex++;
        _productCache[_productIndex] = product;
        
        return `
        <div class="product-card" data-product-idx="${_productIndex}">
            <img class="product-image" src="${escapeHtml(product.image)}" alt="${escapeHtml(product.title)}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23f5f7f6%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 fill=%22%237bc49f%22 font-size=%2220%22>暂无图片</text></svg>'">
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

// 事件委托：商品卡片点击
document.addEventListener('click', (e) => {
    const card = e.target.closest('.product-card');
    if (card) {
        const idx = parseInt(card.dataset.productIdx);
        const product = _productCache[idx];
        if (product) {
            showProductDetail(product);
        }
        return;
    }
});

function openProduct(webUrl, platform) {
    // 手机跳APP，电脑跳淘宝详情页
    var isMobile = /Android|iPhone|iPad|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    if (isMobile) {
        // 手机端：尝试唤起淘宝APP
        if (platform === 'taobao' && webUrl) {
            // 淘宝APP协议
            var appUrl = 'taobao://' + webUrl.replace(/^https?:\/\//, '');
            window.location.href = appUrl;
            // 2秒后如果没跳转成功，fallback到浏览器
            setTimeout(function() {
                window.open(webUrl, '_blank');
            }, 2000);
        } else {
            window.open(webUrl, '_blank');
        }
    } else {
        // 电脑端：直接打开淘宝详情页
        window.open(webUrl, '_blank');
    }
}

// ========== 商品详情弹窗 ==========

function showProductDetail(product) {
    closeProductDetail();

    const overlay = document.createElement('div');
    overlay.className = 'detail-overlay show';
    overlay.onclick = (e) => { if (e.target === overlay) closeProductDetail(); };

    const imgSrc = product.image || '';
    const itemId = product.item_id || '';
    const detailUrl = product.url || '';
    const allImgs = [imgSrc, ...(product.images || [])].filter(Boolean);
    var currentImgIdx = 0;

    overlay.innerHTML = `
        <button class="detail-close" onclick="closeProductDetail()">✕</button>
        <div class="detail-modal detail-modal-full">
            <div class="detail-img-wrap">
                <button class="detail-arrow detail-arrow-left" data-arrow="prev">‹</button>
                <img id="detail-main-img" src="${escapeHtml(imgSrc)}" alt="${escapeHtml(product.title || '')}" onclick="window.open('${escapeHtml(imgSrc)}','_blank')" style="cursor:pointer" onerror="this.parentElement.innerHTML+='<div class=\'detail-no-img\'>暂无图片</div>'">
                <button class="detail-arrow detail-arrow-right" data-arrow="next">›</button>
                <div class="detail-img-counter"><span id="detail-img-cur">1</span>/<span id="detail-img-total">${allImgs.length}</span></div>
            </div>
            ${allImgs.length > 1 ? `<div class="detail-thumbs" id="detail-thumbs">${allImgs.map(function(img, i) {
                return '<div class="detail-thumb' + (i === 0 ? ' active' : '') + '" data-thumb-idx="' + i + '"><img src="' + escapeHtml(img) + '" onerror="this.style.display=\'none\'"></div>';
            }).join('')}</div>` : ''}
            <div class="detail-body">
                <div class="detail-title">${escapeHtml(product.title || '')}</div>
                <div class="detail-price"><span class="sym">¥</span>${product.price || '0'}</div>
                <div class="detail-shop">${escapeHtml(product.shop_name || '')} · ${product.platform === 'taobao' ? '淘宝' : '京东'}</div>
                ${product.brand ? `<div class="detail-brand">品牌：${escapeHtml(product.brand)}</div>` : ''}
                ${product.sales ? `<div class="modal-sales">月销：${product.sales}</div>` : ''}
                <div class="detail-actions">
                    <button class="detail-buy" onclick="openProduct('${escapeHtml(product.url || '#')}', '${product.platform}')">点击购买</button>
                    <button class="detail-fav" id="detail-fav-btn" data-item-id="${escapeHtml(itemId)}" onclick="toggleFavorite(this, '${escapeHtml(itemId)}', '${escapeHtml(product.title || '')}', '${product.price || ''}', '${escapeHtml(imgSrc)}', '${escapeHtml(product.url || '')}', '${product.platform || 'taobao'}', '${escapeHtml(product.shop_name || '')}')">♡ 收藏</button>
                </div>
            </div>
            <div class="detail-detail-section">
                <div class="detail-detail-title">— 商品详情 —</div>
                <div class="detail-detail-footer">
                    <button class="detail-detail-btn" onclick="openProduct('${escapeHtml(detailUrl || '#')}', '${product.platform}')">点击购买</button>
                </div>
            </div>
        </div>
    `;

    // 轮播逻辑
    var mainImg = overlay.querySelector('#detail-main-img');
    var curSpan = overlay.querySelector('#detail-img-cur');

    function switchImg(idx) {
        if (idx < 0) idx = allImgs.length - 1;
        if (idx >= allImgs.length) idx = 0;
        currentImgIdx = idx;
        if (mainImg) mainImg.src = allImgs[idx];
        if (curSpan) curSpan.textContent = idx + 1;
        overlay.querySelectorAll('.detail-thumb').forEach(function(t) {
            t.classList.toggle('active', parseInt(t.getAttribute('data-thumb-idx')) === idx);
        });
    }

    overlay.addEventListener('click', function(e) {
        var arrow = e.target.getAttribute('data-arrow');
        if (arrow === 'prev') { switchImg(currentImgIdx - 1); e.stopPropagation(); }
        else if (arrow === 'next') { switchImg(currentImgIdx + 1); e.stopPropagation(); }
        var thumbIdx = e.target.getAttribute('data-thumb-idx');
        if (thumbIdx !== null) { switchImg(parseInt(thumbIdx)); e.stopPropagation(); }
    });

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    // 弹窗动画：延迟添加slide-up类
    requestAnimationFrame(() => {
        overlay.classList.add('slide-up');
    });

    // 异步检查收藏状态
    if (itemId) {
        fetch(`${API_BASE}/api/favorites/check?user_id=${encodeURIComponent(getUserId())}&item_id=${encodeURIComponent(itemId)}`)
            .then(r => r.json())
            .then(data => {
                const favBtn = document.getElementById('detail-fav-btn');
                if (favBtn && data.favorited) {
                    favBtn.textContent = '♥ 已收藏';
                    favBtn.classList.add('favorited');
                }
            })
            .catch(() => {});
    }

    saveProductBrowse(product.title || '', 1);
}

function closeProductDetail() {
    const existing = document.querySelector('.detail-overlay');
    if (existing) existing.remove();
    document.body.style.overflow = '';
}

// ========== 收藏功能 ==========

globalThis.toggleFavorite = function(btn, itemId, title, price, image, url, platform, shopName) {
    if (!itemId) return;
    var userId = getUserId();
    var isFav = btn.classList.contains('favorited');
    
    if (isFav) {
        fetch(API_BASE + '/api/favorites/remove', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: userId, item_id: itemId})
        }).then(function() {
            btn.classList.remove('favorited');
            btn.textContent = '♡ 收藏';
        }).catch(function() {});
    } else {
        fetch(API_BASE + '/api/favorites/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: userId,
                item_id: itemId,
                title: title || '',
                price: price || '',
                image: image || '',
                url: url || '',
                platform: platform || 'taobao',
                shop_name: shopName || ''
            })
        }).then(function() {
            btn.classList.add('favorited');
            btn.textContent = '♥ 已收藏';
        }).catch(function() {});
    }
};

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
