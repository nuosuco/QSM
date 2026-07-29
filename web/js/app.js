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
    loadJieqi();
    loadEyeExercise();
    loadTizhiGrid();
    loadYaoshiList();
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
    const uploadBtn = document.getElementById('upload-btn');
    const imageInput = document.getElementById('image-input');
    const previewRemove = document.getElementById('preview-remove');
    
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 图片上传/拍照
    uploadBtn.addEventListener('click', () => imageInput.click());
    imageInput.addEventListener('change', handleImageSelect);
    previewRemove.addEventListener('click', clearImagePreview);
}

// 当前选中的图片 base64
let pendingImageBase64 = null;

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // 自动压缩：canvas 缩放到最大 1280px 宽，JPEG 0.8 质量
    const img = new Image();
    const objectUrl = URL.createObjectURL(file);
    img.onload = function() {
        URL.revokeObjectURL(objectUrl);
        const maxW = 1280;
        let w = img.width;
        let h = img.height;
        if (w > maxW) {
            h = Math.round(h * maxW / w);
            w = maxW;
        }
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, w, h);
        pendingImageBase64 = canvas.toDataURL('image/jpeg', 0.8);
        document.getElementById('preview-img').src = pendingImageBase64;
        document.getElementById('image-preview').style.display = 'inline-block';
    };
    img.onerror = function() {
        URL.revokeObjectURL(objectUrl);
        alert('图片加载失败，请重新选择');
    };
    img.src = objectUrl;
    // 重置 input，允许重复选同一文件
    e.target.value = '';
}

function clearImagePreview() {
    pendingImageBase64 = null;
    document.getElementById('image-preview').style.display = 'none';
    document.getElementById('preview-img').src = '';
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const message = input.value.trim();
    const hasImage = !!pendingImageBase64;
    
    if (!message && !hasImage) return;
    
    // 显示用户消息（带图片预览）
    const displayMsg = hasImage
        ? (message ? message + '<br><img src="' + pendingImageBase64 + '" style="max-width:160px;max-height:120px;border-radius:8px;margin-top:6px;">' : '📷 [舌苔照片]')
        : message;
    appendMessage(displayMsg, 'user', true);
    
    const imageToSend = pendingImageBase64;
    input.value = '';
    clearImagePreview();
    sendBtn.disabled = true;
    
    // 显示加载状态
    const loadingId = appendMessage('<div class="loading"></div>', 'assistant', true);
    
    try {
        let response;
        if (hasImage) {
            // 图片辨证：走 vision 接口（base64 data URI）
            response = await fetch(`${API_BASE}/api/chat/vision`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message || '请观察这张舌头照片，从中医角度分析舌色、舌苔、舌形，给出体质倾向和食养建议。',
                    image_url: imageToSend,
                    user_id: getUserId()
                })
            });
        } else {
            response = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    session_id: getSessionId(),
                    user_id: getUserId()
                })
            });
        }
        
        const data = await response.json();
        
        // 移除加载状态
        document.getElementById(loadingId).remove();
        
        // 显示AI回复
        let replyText = data.reply;
        
        // 图片辨证：直接显示回复，不走商品推荐分支
        if (hasImage) {
            appendMessage(replyText, 'assistant');
            sendBtn.disabled = false;
            return;
        }
        
        // 保存对话记录 + 同步体质到后端
        saveChatRecord(message, replyText, data.tizhi || '');
        
        // 如果有推荐商品，显示为可点击的商品卡片
        if (data.products && data.products.length > 0) {
            const chatMsgDiv = appendMessage(replyText, 'assistant');
            const chatContainer = document.getElementById('chat-messages');
            
            // 在回复消息后面插入商品卡片区域
            const productsDiv = document.createElement('div');
            productsDiv.className = 'chat-products';
            productsDiv.innerHTML = '<div class="chat-products-title">🛒 为你推荐以下有机好物：</div>';
            const productsGrid = document.createElement('div');
            productsGrid.className = 'products-grid chat-products-grid';
            productsDiv.appendChild(productsGrid);
            
            for (let i = 0; i < data.products.length; i++) {
                const product = data.products[i];
                _productIndex++;
                _productCache[_productIndex] = product;
                const card = document.createElement('div');
                card.className = 'product-card';
                card.setAttribute('data-product-idx', _productIndex);
                card.innerHTML = `
                    <img class="product-image" src="${escapeHtml(product.image)}" alt="${escapeHtml(product.title)}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23f5f7f6%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 fill=%22%237bc49f%22 font-size=%2220%22>暂无图片</text></svg>'">
                    <div class="product-info">
                        <div class="product-title">${escapeHtml(product.title)}</div>
                        <div class="product-price">¥${product.price}</div>
                        <div class="product-shop">${escapeHtml(product.shop_name || '')} · ${product.platform === 'taobao' ? '淘宝' : '京东'}</div>
                    </div>
                `;
                productsGrid.appendChild(card);
            }
            
            // 给小麦回答框添加收藏按钮
            const chatMsg = document.getElementById(chatMsgDiv);
            if (chatMsg) {
                const favBtn = document.createElement('button');
                favBtn.className = 'fav-chat-btn';
                favBtn.innerHTML = '♡ 收藏';
                favBtn.onclick = function() {
                    const isFav = this.innerHTML.includes('♥');
                    if (isFav) {
                        this.innerHTML = '♡ 收藏';
                        this.classList.remove('favorited');
                    } else {
                        this.innerHTML = '♥ 已收藏';
                        this.classList.add('favorited');
                        // 收藏内容：用户问题+小麦回答+推荐商品
                        const userMsg = document.querySelector('#chat-messages .message.user:last-of-type');
                        const favData = {
                            type: 'chat_with_products',
                            userMessage: userMsg ? userMsg.querySelector('.message-text').textContent : '',
                            assistantReply: replyText,
                            products: data.products,
                            time: new Date().toISOString()
                        };
                        let favs = JSON.parse(localStorage.getItem('som_favorites') || '[]');
                        favs.push(favData);
                        localStorage.setItem('som_favorites', JSON.stringify(favs));
                    }
                };
                chatMsg.querySelector('.message-content').appendChild(favBtn);
            }
            
            chatContainer.appendChild(productsDiv);
            // 滚到用户输入内容的底部，让用户看到自己问的+小麦回答
            const lastUserMsg = document.querySelector('#chat-messages .message.user:last-of-type');
            if (lastUserMsg) {
                lastUserMsg.scrollIntoView({ block: 'start', behavior: 'auto' });
            }
            
            return;
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
    currentKeyword = keyword;
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
    // 直接用 click_url（s.click.taobao.com）跳转，淘宝联盟链接会自动处理APP唤起
    // 不要用 taobao:// 协议，电脑浏览器不识别，手机端 click_url 本身就能唤起APP
    if (webUrl) {
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
                <div class="detail-detail-gallery">
                    ${allImgs.map(function(img, i) {
                        return '<div class="detail-detail-img"><img src="' + escapeHtml(img) + '" onclick="window.open(\'' + escapeHtml(img) + '\',\'_blank\')" style="cursor:pointer" onerror="this.style.display=\'none\'"></div>';
                    }).join('')}
                </div>
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

    // 自动轮播（3秒切换）
    var autoTimer = null;
    function startAutoSlide() {
        if (allImgs.length <= 1) return;
        stopAutoSlide();
        autoTimer = setInterval(function() {
            switchImg(currentImgIdx + 1);
        }, 3000);
    }
    function stopAutoSlide() {
        if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
    }
    // 鼠标悬停暂停，移开恢复
    overlay.addEventListener('mouseenter', stopAutoSlide);
    overlay.addEventListener('mouseleave', startAutoSlide);
    // 触摸时暂停，松手后恢复
    overlay.addEventListener('touchstart', stopAutoSlide);
    overlay.addEventListener('touchend', startAutoSlide);
    // 手动点击箭头/缩略图时，重置定时器
    var origSwitch = switchImg;
    switchImg = function(idx) {
        origSwitch(idx);
        stopAutoSlide();
        startAutoSlide();
    };
    startAutoSlide();

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

// ========== 统一认证（全球手机号 + 邮箱） ==========

let _codeCooldown = 0;

function switchLoginChannel(channel) {
    document.querySelectorAll('.login-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.login-tab[data-channel="${channel}"]`).classList.add('active');
    document.getElementById('login-form-sms').style.display = channel === 'sms' ? 'flex' : 'none';
    document.getElementById('login-form-email').style.display = channel === 'email' ? 'flex' : 'none';
    hideLoginError();
}

function showLoginError(msg) {
    const el = document.getElementById('login-error');
    el.textContent = msg;
    el.style.display = 'block';
}

function hideLoginError() {
    document.getElementById('login-error').style.display = 'none';
}

async function sendLoginCode(channel) {
    hideLoginError();
    let target, countryCode = '+86';
    if (channel === 'sms') {
        target = document.getElementById('sms-phone').value.trim();
        countryCode = document.getElementById('country-code').value;
        if (!target) { showLoginError('请输入手机号'); return; }
    } else {
        target = document.getElementById('email-addr').value.trim();
        if (!target || !target.includes('@')) { showLoginError('请输入有效邮箱'); return; }
    }

    const btnId = channel === 'sms' ? 'sms-code-btn' : 'email-code-btn';
    const btn = document.getElementById(btnId);
    btn.disabled = true;

    try {
        const resp = await fetch(`${API_BASE}/api/auth/send-code`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ target, channel, country_code: countryCode })
        });
        const data = await resp.json();
        if (data.success) {
            // 倒计时 60 秒
            _codeCooldown = 60;
            const timer = setInterval(() => {
                _codeCooldown--;
                if (_codeCooldown <= 0) {
                    clearInterval(timer);
                    btn.disabled = false;
                    btn.textContent = '获取验证码';
                } else {
                    btn.textContent = `${_codeCooldown}s`;
                }
            }, 1000);
            btn.textContent = '60s';
        } else {
            showLoginError(data.error || '发送失败');
            btn.disabled = false;
        }
    } catch (e) {
        showLoginError('网络错误，请重试');
        btn.disabled = false;
    }
}

async function doLogin(channel) {
    hideLoginError();
    let target, code, countryCode = '+86';
    if (channel === 'sms') {
        target = document.getElementById('sms-phone').value.trim();
        code = document.getElementById('sms-code').value.trim();
        countryCode = document.getElementById('country-code').value;
        if (!target) { showLoginError('请输入手机号'); return; }
        if (!code) { showLoginError('请输入验证码'); return; }
    } else {
        target = document.getElementById('email-addr').value.trim();
        code = document.getElementById('email-code').value.trim();
        if (!target) { showLoginError('请输入邮箱'); return; }
        if (!code) { showLoginError('请输入验证码'); return; }
    }

    try {
        const resp = await fetch(`${API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                target, code, channel,
                country_code: countryCode,
                anonymous_user_id: getUserId()
            })
        });
        const data = await resp.json();
        if (data.success) {
            // 保存登录态
            localStorage.setItem('som_auth_token', data.token);
            localStorage.setItem('som_auth_user', JSON.stringify(data.user));
            // 更新 user_id 为正式账号
            if (data.user && data.user.user_id) {
                localStorage.setItem('som_user_id', data.user.user_id);
            }
            updateLoginUI();
            loadProfile();
        } else {
            showLoginError(data.error || '登录失败');
        }
    } catch (e) {
        showLoginError('网络错误，请重试');
    }
}

function doLogout() {
    localStorage.removeItem('som_auth_token');
    localStorage.removeItem('som_auth_user');
    updateLoginUI();
}

function isLoggedIn() {
    return !!localStorage.getItem('som_auth_token');
}

function updateLoginUI() {
    const loginSection = document.getElementById('login-section');
    const profileCard = document.getElementById('profile-card');
    if (isLoggedIn()) {
        loginSection.style.display = 'none';
        profileCard.style.display = 'flex';
        // 显示昵称
        try {
            const user = JSON.parse(localStorage.getItem('som_auth_user') || '{}');
            if (user.nickname) {
                document.getElementById('profile-name').textContent = user.nickname;
            }
        } catch(e) {}
    } else {
        loginSection.style.display = 'block';
        profileCard.style.display = 'none';
    }
}

// ========== 个人中心 ==========

function initProfile() {
    updateLoginUI();
    loadProfile();
}

function getUserId() {
    let uid = localStorage.getItem('som_user_id');
    if (!uid) {
        uid = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('som_user_id', uid);
        // 首次生成时，向后端注册匿名用户
        registerUserToBackend(uid);
    }
    return uid;
}

// 向后端注册用户（匿名，无需登录）
async function registerUserToBackend(uid) {
    try {
        await fetch(`${API_BASE}/api/user/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: uid })
        });
    } catch (e) {
        console.error('后端用户注册失败:', e);
    }
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
    
    // 优先从后端加载体质记录，失败则用本地
    loadTizhiRecordsFromBackend().catch(() => loadTizhiRecords(data));
}

// 从后端加载体质记录
async function loadTizhiRecordsFromBackend() {
    const resp = await fetch(`${API_BASE}/api/tizhi/records?user_id=${encodeURIComponent(getUserId())}&limit=5`);
    const result = await resp.json();
    const history = document.getElementById('profile-history');
    if (!history) return;
    
    const records = result.records || [];
    if (records.length === 0) {
        history.innerHTML = '<p class="empty-hint">暂无体质记录，快去和小麦SOM对话吧</p>';
        return;
    }
    
    let html = '';
    for (const r of records) {
        html += '<div class="history-item">';
        html += '  <span class="history-date">' + escapeHtml((r.created_at || '').split('T')[0]) + '</span>';
        html += '  <span class="history-tizhi">' + escapeHtml(r.tizhi || '') + '</span>';
        html += '  <span class="history-desc">' + escapeHtml((r.symptoms || '').substring(0, 30)) + '</span>';
        html += '</div>';
    }
    history.innerHTML = html;
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
        // 同步体质记录到后端
        saveTizhiToBackend(tizhi, message);
    }
    
    saveUserData(data);
}

// 同步体质评测结果到后端
async function saveTizhiToBackend(tizhi, symptoms) {
    try {
        await fetch(`${API_BASE}/api/tizhi/save`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: getUserId(),
                tizhi: tizhi,
                symptoms: (symptoms || '').substring(0, 200),
                source: 'web_chat'
            })
        });
    } catch (e) {
        console.error('体质记录同步失败:', e);
    }
}

function saveProductBrowse(keyword, count) {
    const data = getUserData();
    if (!data.productBrowses) data.productBrowses = 0;
    data.productBrowses += count;
    saveUserData(data);
}

// ========== 养生谷：体质 + 药食同源 ==========

async function loadTizhiGrid() {
    const grid = document.getElementById('tizhi-grid');
    if (!grid) return;
    try {
        const resp = await fetch(`${API_BASE}/api/knowledge/tizhi`);
        const data = await resp.json();
        const items = data.items || [];
        grid.innerHTML = items.map(t => `
            <div class="tizhi-card">
                <div class="tizhi-name">${escapeHtml(t.name)}</div>
                <div class="tizhi-desc">${escapeHtml(t.desc || t.features || '')}</div>
                <div class="tizhi-diet">调养：${escapeHtml(t.diet || t.yangsheng || '')}</div>
            </div>
        `).join('');
    } catch (e) {
        grid.innerHTML = '<p class="empty-hint">加载失败，请刷新重试</p>';
    }
}

async function loadYaoshiList() {
    const list = document.getElementById('yaoshi-list');
    if (!list) return;
    try {
        const resp = await fetch(`${API_BASE}/api/knowledge/yaoshi`);
        const data = await resp.json();
        const items = data.items || [];
        list.innerHTML = items.map(y => `
            <div class="yaoshi-item">
                <div class="yaoshi-name">${escapeHtml(y.name)}</div>
                <div class="yaoshi-info">
                    <span class="yaoshi-xingwei">性味：${escapeHtml(y.xingwei || '')}</span>
                    <span class="yaoshi-guijing">归经：${escapeHtml(y.guijing || '')}</span>
                </div>
                <div class="yaoshi-gongxiao">功效：${escapeHtml(y.gongxiao || '')}</div>
                ${y.jinji ? `<div class="yaoshi-jinji">⚠️ ${escapeHtml(y.jinji)}</div>` : ''}
            </div>
        `).join('');
    } catch (e) {
        list.innerHTML = '<p class="empty-hint">加载失败，请刷新重试</p>';
    }
}

// ========== 节气养生 ==========

async function loadJieqi() {
    const card = document.getElementById('jieqi-card');
    if (!card) return;
    try {
        const resp = await fetch(`${API_BASE}/api/jieqi/current`);
        const data = await resp.json();
        card.innerHTML = `
            <div class="jieqi-header">
                <span class="jieqi-name">${escapeHtml(data.jieqi)}</span>
                <span class="jieqi-season">${escapeHtml(data.season)}季</span>
                <span class="jieqi-next">下一节气：${escapeHtml(data.next_jieqi)} ${escapeHtml(data.next_date)}</span>
            </div>
            <div class="jieqi-desc">${escapeHtml(data.desc)}</div>
            <div class="jieqi-yangsheng">${escapeHtml(data.yangsheng)}</div>
            <div class="jieqi-foods">
                <span class="jieqi-label">🥬 当季食材：</span>
                ${data.foods.map(f => `<span class="jieqi-food-tag">${escapeHtml(f)}</span>`).join('')}
            </div>
            <div class="jieqi-tea">🍵 推荐茶饮：${escapeHtml(data.tea)}</div>
            <div class="jieqi-avoid">⚠️ 注意：${escapeHtml(data.avoid)}</div>
        `;
    } catch (e) {
        card.innerHTML = '<div class="jieqi-loading">加载失败，请刷新重试</div>';
    }
}

// ========== 护眼训练 ==========

async function loadEyeExercise() {
    const container = document.getElementById('eye-exercise');
    if (!container) return;
    try {
        const resp = await fetch(`${API_BASE}/api/eye-exercise`);
        const data = await resp.json();
        let html = '<div class="eye-exercise-list">';
        for (const ex of data.exercises) {
            html += `
                <div class="eye-exercise-item">
                    <div class="eye-exercise-name">${escapeHtml(ex.name)} <span class="eye-exercise-duration">${escapeHtml(ex.duration)}</span></div>
                    <div class="eye-exercise-steps">${escapeHtml(ex.steps)}</div>
                    <div class="eye-exercise-benefit">${escapeHtml(ex.benefit)}</div>
                </div>
            `;
        }
        html += '</div>';
        html += `<div class="eye-foods">🥕 护眼食材：${data.foods.map(f => escapeHtml(f)).join('、')}</div>`;
        html += `<div class="eye-tea">🍵 护眼茶饮：${escapeHtml(data.tea)}</div>`;
        html += `<div class="eye-tips">💡 ${escapeHtml(data.tips)}</div>`;
        container.innerHTML = html;
    } catch (e) {
        container.innerHTML = '<div class="jieqi-loading">加载失败，请刷新重试</div>';
    }
}
