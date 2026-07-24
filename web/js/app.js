// SOM 松麦 - 前端逻辑 v3 (迭代7：搜索历史+收藏+对话持久化)

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
            const targetEl = document.getElementById(`${targetTab}-tab`);
            if (targetEl) {
                targetEl.classList.add('active');
            }

            // 进入养生谷时加载数据
            if (targetTab === 'yangshenggu') {
                initYangshengGu();
            }
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

    // 对话页激活时加载每日养生建议
    const firstNavBtn = document.querySelector('.nav-btn[data-tab="chat"]');
    if (firstNavBtn) {
        const clickEvent = new MouseEvent('click', { bubbles: true });
        firstNavBtn.dispatchEvent(clickEvent);
        loadDailyTip();
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const message = input.value.trim();

    if (!message) return;

    appendMessage(message, 'user');
    input.value = '';
    input.style.height = 'auto';
    sendBtn.disabled = true;

    const loadingId = appendMessage('<div class="loading"></div>', 'assistant', true);

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: getSessionId(),
                user_id: getUserId()
            })
        });

        const data = await response.json();
        document.getElementById(loadingId).remove();
        displayChatResult(data);
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

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-text">${isHtml ? text : escapeHtml(text)}</div>
        </div>
    `;

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

function displayChatResult(data) {
    const messagesContainer = document.getElementById('chat-messages');

    // 1. 文字回复
    const replyText = data.reply || '没有获取到回复，请重试。';
    appendMessage(replyText, 'assistant');

    // 2. 推荐食材标签
    if (data.recommendations && data.recommendations.length > 0) {
        const recTags = data.recommendations.slice(0, 6).map(r =>
            `<span class="rec-tag"><strong>${escapeHtml(r.name)}</strong>${r.xingwei ? ' · ' + escapeHtml(r.xingwei) : ''}</span>`
        ).join('');
        appendMessage(`💡 推荐药食同源：${recTags}`, 'assistant');
    }

    // 3. 商品卡片
    if (data.products && data.products.length > 0) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message assistant';
        msgDiv.innerHTML = `
            <div class="message-avatar">麦</div>
            <div class="message-content" style="width:100%">
                <div class="message-text" style="margin-bottom:8px">🛒 为你精选以下有机好物：</div>
                <div class="chat-product-grid" id="chat-products">
                    ${data.products.map(p => `
                        <div class="product-card mini" onclick="showProductDetail(${JSON.stringify(p).replace(/"/g, '&quot;')})">
                            <img class="product-image" src="${p.image || ''}" alt="" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23f5f7f6%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 fill=%22%237bc49f%22 font-size=%2216%22>暂无图片</text></svg>'">
                            <div class="product-info">
                                <div class="product-title">${escapeHtml(p.title)}</div>
                                <div class="product-price">¥${p.price}</div>
                                <div class="product-shop">${escapeHtml(p.shop_name || '')} · ${p.platform === 'taobao' ? '淘宝' : '京东'}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // 4. 保存对话记录
    saveChatRecord(document.getElementById('chat-input').value, data.reply, data.tizhi || '');
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
    const sortBtns = document.querySelectorAll('.sort-btn');

    searchBtn.addEventListener('click', () => {
        currentKeyword = searchInput.value.trim();
        currentPage = 1;
        hasMore = true;
        if (currentKeyword) {
            addSearchHistory(currentKeyword, currentPlatform);
        }
        searchProducts(true);
    });

    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            currentKeyword = searchInput.value.trim();
            currentPage = 1;
            hasMore = true;
            if (currentKeyword) {
                addSearchHistory(currentKeyword, currentPlatform);
            }
            searchProducts(true);
        }
    });

    // 搜索框聚焦时显示搜索历史
    searchInput.addEventListener('focus', () => {
        showSearchHistory();
    });

    // 点击其他地方关闭搜索历史
    document.addEventListener('click', (e) => {
        const historyEl = document.getElementById('search-history-dropdown');
        if (historyEl && !e.target.closest('.search-box')) {
            historyEl.remove();
        }
    });

    // 搜索框输入时实时搜索（防抖500ms，输入2字以上触发）
    let searchDebounceTimer;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            const val = searchInput.value.trim();
            if (val.length >= 2 && val !== currentKeyword) {
                currentKeyword = val;
                currentPage = 1;
                hasMore = true;
                searchProducts(true);
            }
        }, 500);
    });

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentPlatform = btn.dataset.platform;
            currentPage = 1;
            hasMore = true;
            if (currentCategory || currentKeyword) searchProducts(true);
        });
    });

    sortBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            sortBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentSort = btn.dataset.sort;
            currentPage = 1;
            hasMore = true;
            if (currentCategory || currentKeyword) searchProducts(true);
        });
    });

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

// ========== 搜索历史 ==========

async function addSearchHistory(keyword, platform) {
    try {
        await fetch(`${API_BASE}/api/search/history/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: getUserId(), keyword, platform })
        }).catch(() => {});
    } catch(e) { /* ignore */ }
}

async function showSearchHistory() {
    // 移除旧的
    const old = document.getElementById('search-history-dropdown');
    if (old) old.remove();

    const searchBox = document.querySelector('.search-box');
    if (!searchBox) return;

    try {
        const res = await fetch(`${API_BASE}/api/search/history?user_id=${encodeURIComponent(getUserId())}&limit=10`);
        const data = await res.json();
        if (!data.history || data.history.length === 0) return;

        const dropdown = document.createElement('div');
        dropdown.id = 'search-history-dropdown';
        dropdown.className = 'search-history-dropdown';
        dropdown.innerHTML = `
            <div class="search-history-header">
                <span>搜索历史</span>
                <button class="clear-history-btn" onclick="clearSearchHistory(event)">清空</button>
            </div>
            ${data.history.map(h => `
                <div class="search-history-item" onclick="useSearchHistory('${escapeHtml(h.keyword)}')">
                    <span class="history-keyword">${escapeHtml(h.keyword)}</span>
                    <span class="history-platform">${h.platform === 'taobao' ? '淘宝' : '京东'}</span>
                </div>
            `).join('')}
        `;
        searchBox.appendChild(dropdown);
    } catch(e) { /* ignore */ }
}

function useSearchHistory(keyword) {
    const input = document.getElementById('product-search');
    if (input) {
        input.value = keyword;
        currentKeyword = keyword;
        currentPage = 1;
        hasMore = true;
        searchProducts(true);
    }
    const dropdown = document.getElementById('search-history-dropdown');
    if (dropdown) dropdown.remove();
}

function clearSearchHistory(e) {
    if (e) e.stopPropagation();
    fetch(`${API_BASE}/api/search/history/clear`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: getUserId() })
    }).catch(() => {});
    const dropdown = document.getElementById('search-history-dropdown');
    if (dropdown) dropdown.remove();
}

// ========== 分类加载 ==========

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/api/products/categories`);
        const data = await response.json();
        displayCategories(data.categories);
        if (data.categories.length > 0) {
            searchByCategory(data.categories[0].keyword, data.categories[0].name);
        }
    } catch (error) {
        console.error('加载分类失败:', error);
        const el = document.getElementById('category-nav');
        if (el) el.innerHTML = '<div class="category-loading">分类加载失败</div>';
    }
}

function displayCategories(categories) {
    const categoryNav = document.getElementById('category-nav');
    if (!categoryNav) return;
    categoryNav.innerHTML = categories.map(cat => `
        <div class="category-item" data-keyword="${encodeURIComponent(cat.keyword)}" data-name="${cat.name}">
            <div class="category-icon">${cat.icon}</div>
            <div class="category-name">${cat.name}</div>
        </div>
    `).join('');

    categoryNav.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', () => {
            const keyword = decodeURIComponent(item.dataset.keyword || '');
            const name = item.dataset.name || '';
            searchByCategory(keyword, name);
        });
    });
}

function searchByCategory(keyword, categoryName = '') {
    currentCategory = keyword;
    currentKeyword = keyword.split(' ')[0];
    currentPage = 1;
    hasMore = true;
    const searchInput = document.getElementById('product-search');
    if (searchInput && categoryName) {
        searchInput.value = categoryName;
    }
    searchProducts(true);
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
        const kw = encodeURIComponent(currentKeyword);
        const response = await fetch(
            `${API_BASE}/api/products/search?keyword=${kw}&platform=${currentPlatform}&page=${currentPage}&page_size=20${sortParam}`
        );

        const data = await response.json();
        if (data.items && data.items.length > 0) {
            if (clear) productsGrid.innerHTML = '';
            displayProducts(data.items, !clear);
            if (data.items.length < 20) hasMore = false;
            currentPage++;
        } else {
            if (clear) productsGrid.innerHTML = '<div class="empty-state"><p>未找到相关有机产品</p></div>';
            hasMore = false;
        }
    } catch (error) {
        if (clear) productsGrid.innerHTML = '<div class="empty-state"><p>搜索失败，请稍后重试</p></div>';
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
    if (indicator) indicator.remove();
}

function displayProducts(products, append = false) {
    const productsGrid = document.getElementById('products-grid');
    const productHtml = products.map(product => {
        const webUrl = product.url || '#';
        const itemId = product.item_id || '';
        return `
        <div class="product-card" data-id="${escapeHtml(itemId)}" data-url="${webUrl}" data-platform="${product.platform || ''}">
            <button class="fav-btn" onclick="event.stopPropagation(); toggleFavorite(this, '${escapeHtml(itemId)}', '${escapeHtml(product.title || '')}', '${escapeHtml(product.price || '')}', '${escapeHtml(product.image || '')}', '${escapeHtml(webUrl)}', '${product.platform || 'taobao'}', '${escapeHtml(product.shop_name || '')}')" title="收藏">♡</button>
            <img class="product-image" src="${product.image || ''}" alt="${escapeHtml(product.title || '')}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23f5f7f6%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 fill=%22%237bc49f%22 font-size=%2220%22>暂无图片</text></svg>'">
            <div class="product-info">
                <div class="product-title">${escapeHtml(product.title || '')}</div>
                <div class="product-price">¥${product.price || ''}</div>
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

    // 绑定点击事件
    productsGrid.querySelectorAll('.product-card[data-id]').forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.closest('.fav-btn')) return;
            showProductDetail({
                item_id: this.dataset.id,
                title: this.querySelector('.product-title').textContent,
                price: this.querySelector('.product-price').textContent.replace('¥', ''),
                image: this.querySelector('.product-image').src,
                url: this.dataset.url,
                platform: this.dataset.platform,
                shop_name: this.querySelector('.product-shop')?.textContent?.split('·')[0]?.trim() || ''
            });
        });
    });
}

function openProduct(webUrl, platform) {
    if (webUrl && webUrl !== '#') {
        window.open(webUrl, '_blank');
    }
}

// ========== 商品收藏 ==========

async function toggleFavorite(btn, itemId, title, price, image, url, platform, shopName) {
    if (!itemId) return;
    
    const isFav = btn.textContent === '♥' || btn.classList.contains('favorited');
    const uid = getUserId();
    
    try {
        let res, data;
        if (isFav) {
            res = await fetch(`${API_BASE}/api/favorites/remove?user_id=${encodeURIComponent(uid)}&item_id=${encodeURIComponent(itemId)}`, { method: 'POST' });
            data = await res.json();
            if (data.success) { btn.textContent = '♡'; btn.classList.remove('favorited'); showToast('已取消收藏'); }
        } else {
            res = await fetch(`${API_BASE}/api/favorites/add`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: uid, item_id: itemId, title: title, price: price, image: image, url: url, platform: platform, shop_name: shopName })
            });
            data = await res.json();
            if (data.success) { btn.textContent = '♥'; btn.classList.add('favorited'); showToast('收藏成功'); }
        }
    } catch(e) { console.error('收藏操作失败:', e); }
}

// ========== 商品详情弹窗 ==========

function showProductDetail(product) {
    closeProductDetail();

    const overlay = document.createElement('div');
    overlay.className = 'detail-overlay show';
    overlay.onclick = (e) => { if (e.target === overlay) closeProductDetail(); };

    const imgSrc = product.image || '';
    const fullImages = (product.images || []).map(img =>
        `<div class="detail-thumb" onclick="window.open('${img}','_blank')"><img src="${img}" onerror="this.style.display='none'"></div>`
    ).join('');

    overlay.innerHTML = `
        <button class="detail-close" onclick="closeProductDetail()">✕</button>
        <div class="detail-modal">
            <div class="detail-img-wrap">
                <img src="${imgSrc}" alt="${escapeHtml(product.title || '')}" onerror="this.parentElement.innerHTML='<div style=\\'height:200px;display:flex;align-items:center;justify-content:center;color:#aaa\\'>暂无图片</div>'">
            </div>
            ${fullImages ? `<div class="detail-thumbs">${fullImages}</div>` : ''}
            <div class="detail-body">
                <div class="detail-title">${escapeHtml(product.title || '')}</div>
                <div class="detail-price"><span class="sym">¥</span>${product.price || '0'}</div>
                <div class="detail-shop">${escapeHtml(product.shop_name || '')} · ${product.platform === 'taobao' ? '淘宝' : '京东'}</div>
                ${product.commission_rate ? `<div class="modal-commission">佣金比例：${product.commission_rate}%</div>` : ''}
                <div class="detail-actions">
                    <button class="detail-buy" onclick="openProduct('${product.url}', '${product.platform}')">立即购买 →</button>
                    <button class="detail-fav" onclick="toggleFavorite(this, '${product.item_id || ''}', '${escapeHtml(product.title || '')}', '${product.price || ''}', '${imgSrc}', '${product.url || ''}', '${product.platform || 'taobao'}', '${escapeHtml(product.shop_name || '')}')">♡ 收藏</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';

    saveProductBrowse(product.title || '', 1);
}

function closeProductDetail() {
    const existing = document.querySelector('.detail-overlay');
    if (existing) existing.remove();
    document.body.style.overflow = '';
}

// ========== 养生谷页面 ==========

async function initYangshengGu() {
    const tizhiGrid = document.getElementById('tizhi-grid');
    const yaoshiList = document.getElementById('yaoshi-list');

    if (tizhiGrid) tizhiGrid.innerHTML = '<div class="knowledge-loading">加载中...</div>';
    if (yaoshiList) yaoshiList.innerHTML = '<div class="knowledge-loading">加载中...</div>';

    try {
        const [tizhiRes, yaoshiRes] = await Promise.all([
            fetch(`${API_BASE}/api/knowledge/tizhi`),
            fetch(`${API_BASE}/api/knowledge/yaoshi`)
        ]);

        const tizhiData = await tizhiRes.json();
        const yaoshiData = await yaoshiRes.json();

        renderTizhiCards(tizhiData.items || []);
        renderYaoshiCards(yaoshiData.items || []);
    } catch (error) {
        console.error('加载养生谷数据失败:', error);
        if (tizhiGrid) tizhiGrid.innerHTML = '<div class="knowledge-empty">加载失败，请刷新重试</div>';
        if (yaoshiList) yaoshiList.innerHTML = '<div class="knowledge-empty">加载失败，请刷新重试</div>';
    }
}

function renderTizhiCards(items) {
    const tizhiGrid = document.getElementById('tizhi-grid');
    if (!tizhiGrid) return;

    tizhiGrid.innerHTML = items.map(t => `
        <div class="knowledge-card tizhi-card">
            <div class="knowledge-card-title">${t.name}</div>
            <div class="knowledge-card-desc">${t.desc || ''}</div>
            <div class="knowledge-card-diet">💊 ${t.diet || ''}</div>
        </div>
    `).join('');
}

function renderYaoshiCards(items) {
    const yaoshiList = document.getElementById('yaoshi-list');
    if (!yaoshiList) return;

    yaoshiList.innerHTML = items.map(y => `
        <div class="knowledge-card yaoshi-card">
            <div class="knowledge-card-title">${y.name}</div>
            <div class="knowledge-card-meta">性味：${y.xingwei || '—'} · 归经：${y.guijing || '—'}</div>
            <div class="knowledge-card-desc">${y.gongxiao || ''}</div>
            <div class="knowledge-card-jinji">⚠️ ${y.jinji || '无特殊禁忌'}</div>
        </div>
    `).join('');
}

// ========== 每日养生建议 ==========

async function loadDailyTip() {
    try {
        const response = await fetch(`${API_BASE}/api/daily-tip`);
        if (!response.ok) return;
        const data = await response.json();

        const container = document.getElementById('daily-tip-area');
        if (!container) return;

        container.innerHTML = `
            <div class="daily-tip-card">
                <div class="daily-tip-header">${data.emoji || ''} ${data.title || ''}</div>
                <div class="daily-tip-content">${data.content || ''}</div>
                <div class="daily-tip-type">${data.tip_type || ''}</div>
            </div>
        `;
    } catch (error) {
        console.error('加载每日建议失败:', error);
    }
}

// ========== 个人中心 ==========

function initProfile() {
    loadProfile();
    bindCheckin();
    loadFavorites();
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

async function loadProfile() {
    const uid = getUserId();

    try {
        const res = await fetch(`${API_BASE}/api/checkin/status?user_id=${encodeURIComponent(uid)}`);
        if (res.ok) {
            const checkin = await res.json();
            updateProfileFromBackend(checkin);
        }
    } catch(e) {
        console.log('后端签到状态获取失败');
    }

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

function updateProfileFromBackend(checkin) {
    if (!checkin) return;
    const data = getUserData();
    if (checkin.total_points) data.totalPoints = checkin.total_points;
    if (checkin.streak) data.streak = checkin.streak;
    if (checkin.checked_in_today) data.localCheckedIn = true;
    saveUserData(data);
}

async function bindCheckin() {
    const checkinBtn = document.getElementById('checkin-btn');
    if (!checkinBtn) return;

    checkinBtn.addEventListener('click', async () => {
        const uid = getUserId();
        checkinBtn.disabled = true;
        checkinBtn.textContent = '签到中...';

        try {
            const res = await fetch(`${API_BASE}/api/checkin/do`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: uid })
            });
            const result = await res.json();

            if (result.success) {
                checkinBtn.textContent = `✅ 已连续签到${result.streak || 1}天`;
                checkinBtn.disabled = true;
                showToast(result.message);
            } else {
                checkinBtn.textContent = '今天已签到';
                checkinBtn.disabled = true;
                showToast(result.message);
            }
        } catch (error) {
            checkinBtn.textContent = '签到失败';
            console.error('签到失败:', error);
        }

        loadProfile();
    });
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
    const maxShow = Math.min(records.length, 10);
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

// ========== 收藏列表 ==========

async function loadFavorites() {
    try {
        const res = await fetch(`${API_BASE}/api/favorites?user_id=${encodeURIComponent(getUserId())}&limit=10`);
        const data = await res.json();
        const favList = document.getElementById('favorites-list');
        if (!favList) return;

        if (!data.favorites || data.favorites.length === 0) {
            favList.innerHTML = '<p class="empty-hint">暂无收藏商品</p>';
            return;
        }

        favList.innerHTML = data.favorites.map(f => `
            <div class="history-item">
                <span class="history-date">${escapeHtml(f.title || '').substring(0, 20)}</span>
                <span class="history-tizhi">¥${f.price || '0'}</span>
                <span class="history-desc">${f.platform === 'taobao' ? '淘宝' : '京东'}</span>
            </div>
        `).join('');
    } catch(e) {
        console.log('加载收藏列表失败:', e);
    }
}

// ========== Toast 提示 ==========

function showToast(msg) {
    const existing = document.querySelector('.toast-msg');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = 'toast-msg';
    toast.textContent = msg;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 2500);
}