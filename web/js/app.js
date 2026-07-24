// SOM 松麦 - 前端逻辑（兼容所有手机浏览器）

var API_BASE = '';

function qsa(sel) {
    return Array.prototype.slice.call(document.querySelectorAll(sel));
}

// ========== 初始化 ==========

document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initChat();
    initProductSearch();
    loadKnowledge();
    initProfile();
});

// ========== 导航切换 ==========

function initNavigation() {
    var navBtns = qsa('.nav-btn');
    var tabContents = qsa('.tab-content');
    
    var i;
    for (i = 0; i < navBtns.length; i++) {
        (function(btn) {
            btn.addEventListener('click', function() {
                var targetTab = btn.getAttribute('data-tab');
                var j;
                for (j = 0; j < navBtns.length; j++) {
                    navBtns[j].classList.remove('active');
                }
                btn.classList.add('active');
                for (j = 0; j < tabContents.length; j++) {
                    tabContents[j].classList.remove('active');
                }
                var targetEl = document.getElementById(targetTab + '-tab');
                if (targetEl) {
                    targetEl.classList.add('active');
                }
            });
        })(navBtns[i]);
    }
}

// ========== 对话功能 ==========

function initChat() {
    var sendBtn = document.getElementById('send-btn');
    var chatInput = document.getElementById('chat-input');
    if (!sendBtn || !chatInput) return;
    
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

async function sendMessage() {
    var input = document.getElementById('chat-input');
    var sendBtn = document.getElementById('send-btn');
    var message = input.value.trim();
    if (!message) return;
    
    appendMessage(message, 'user');
    input.value = '';
    sendBtn.disabled = true;
    
    var loadingId = appendMessage('<div class="loading"></div>', 'assistant', true);
    
    try {
        var response = await fetch(API_BASE + '/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: getSessionId()
            })
        });
        
        var data = await response.json();
        var el = document.getElementById(loadingId);
        if (el) el.remove();
        
        var replyText = data.reply || '';
        if (data.products && data.products.length > 0) {
            replyText += '\n\n为你找到以下有机好物：';
            var maxP = Math.min(data.products.length, 3);
            for (var p = 0; p < maxP; p++) {
                replyText += '\n' + (p + 1) + '. ' + data.products[p].title + ' - ¥' + data.products[p].price;
            }
        }
        
        appendMessage(replyText, 'assistant');
        
        // 保存对话记录到个人中心
        saveChatRecord(message, replyText, data.tizhi);
        
    } catch (error) {
        var el2 = document.getElementById(loadingId);
        if (el2) el2.remove();
        appendMessage('抱歉，网络出现问题，请稍后重试。', 'assistant');
        console.error('发送消息失败:', error);
    } finally {
        sendBtn.disabled = false;
    }
}

function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = String(text || '');
    return div.innerHTML;
}

function appendMessage(text, type, isHtml) {
    if (isHtml === undefined) isHtml = false;
    var container = document.getElementById('chat-messages');
    if (!container) return '';
    
    var msgDiv = document.createElement('div');
    msgDiv.className = 'message ' + type;
    var msgId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    msgDiv.id = msgId;
    
    var avatar = type === 'user' ? '你' : '麦';
    var textHtml;
    
    if (isHtml) {
        textHtml = text;
    } else {
        textHtml = '<span class="plain-text">' + escapeHtml(text) + '</span>';
    }
    
    msgDiv.innerHTML = 
        '<div class="message-avatar">' + avatar + '</div>' +
        '<div class="message-content">' +
            '<div class="message-text">' + textHtml + '</div>' +
        '</div>';
    
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
    return msgId;
}

function getSessionId() {
    var sid = sessionStorage.getItem('som_session_id');
    if (!sid) {
        sid = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        sessionStorage.setItem('som_session_id', sid);
    }
    return sid;
}

// ========== 养生谷 - 商品搜索 ==========

var currentPlatform = 'taobao';

function initProductSearch() {
    var searchBtn = document.getElementById('search-btn');
    var searchInput = document.getElementById('product-search');
    var filterBtns = qsa('.filter-btn');
    
    if (searchBtn) searchBtn.addEventListener('click', searchProducts);
    if (searchInput) {
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') searchProducts();
        });
    }
    
    var i;
    for (i = 0; i < filterBtns.length; i++) {
        (function(btn) {
            btn.addEventListener('click', function() {
                var j;
                for (j = 0; j < filterBtns.length; j++) {
                    filterBtns[j].classList.remove('active');
                }
                btn.classList.add('active');
                currentPlatform = btn.getAttribute('data-platform');
            });
        })(filterBtns[i]);
    }
}

async function searchProducts() {
    var searchInput = document.getElementById('product-search');
    var keyword = searchInput.value.trim();
    if (!keyword) { alert('请输入搜索关键词'); return; }
    
    var grid = document.getElementById('products-grid');
    grid.innerHTML = '<div class="empty-state"><div class="loading"></div><p>搜索中...</p></div>';
    
    try {
        var url = API_BASE + '/api/products/search?keyword=' + encodeURIComponent(keyword) + '&platform=' + currentPlatform + '&page=1&page_size=20';
        var resp = await fetch(url);
        var data = await resp.json();
        
        if (data.items && data.items.length > 0) {
            displayProducts(data.items);
            // 记录浏览商品
            saveProductBrowse(keyword, data.items.length);
        } else {
            grid.innerHTML = '<div class="empty-state"><p>未找到相关商品</p></div>';
        }
    } catch (error) {
        grid.innerHTML = '<div class="empty-state"><p>搜索失败，请稍后重试</p></div>';
        console.error('搜索失败:', error);
    }
}

function displayProducts(products) {
    var grid = document.getElementById('products-grid');
    if (!grid) return;
    
    var html = '';
    var i;
    for (i = 0; i < products.length; i++) {
        var p = products[i];
        var imgErr = "this.onerror=null;this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23f5f7f6%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 fill=%22%237bc49f%22 font-size=%2220%22>暂无图片</text></svg>'";
        var platformLabel = p.platform === 'jd' ? '京东' : '淘宝';
        html += '<div class="product-card" onclick="window.open(\'' + escapeAttr(p.url || '#') + '\', \'_blank\')" style="cursor:pointer">';
        html += '  <img class="product-image" src="' + (p.image || '') + '" alt="" onerror="' + imgErr + '">';
        html += '  <div class="product-info">';
        html += '    <div class="product-title">' + escapeHtml(p.title || '') + '</div>';
        html += '    <div class="product-price">¥' + (p.price || '0') + '</div>';
        html += '    <div class="product-shop">' + escapeHtml(p.shop_name || '') + ' · ' + platformLabel + '</div>';
        html += '  </div>';
        html += '</div>';
    }
    grid.innerHTML = html;
}

function escapeAttr(s) {
    return String(s || '').replace(/'/g, "\\'").replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ========== 养生知识 ==========

async function loadKnowledge() {
    try {
        var tizhiResp = await fetch(API_BASE + '/api/knowledge/tizhi');
        var tizhiData = await tizhiResp.json();
        displayTizhi(tizhiData.items || []);
        
        var yaoshiResp = await fetch(API_BASE + '/api/knowledge/yaoshi');
        var yaoshiData = await yaoshiResp.json();
        displayYaoshi(yaoshiData.items || {});
    } catch (error) {
        console.error('加载知识库失败:', error);
    }
}

function displayTizhi(items) {
    var grid = document.getElementById('tizhi-grid');
    if (!grid || !items.length) return;
    
    var html = '';
    var i;
    for (i = 0; i < items.length; i++) {
        var t = items[i];
        html += '<div class="tizhi-card">';
        html += '  <h3>' + escapeHtml(t.name || '') + '</h3>';
        html += '  <p><strong>特征：</strong>' + escapeHtml(t.desc || '') + '</p>';
        html += '  <p><strong>养生：</strong>' + escapeHtml(t.yangsheng || '') + '</p>';
        html += '</div>';
    }
    grid.innerHTML = html;
}

function displayYaoshi(items) {
    var list = document.getElementById('yaoshi-list');
    if (!list) return;
    
    var html = '';
    var keys = Object.keys(items || {});
    var i;
    for (i = 0; i < keys.length; i++) {
        var name = keys[i];
        var info = items[name] || {};
        html += '<div class="yaoshi-item">';
        html += '  <h4>' + escapeHtml(name) + '</h4>';
        html += '  <p><strong>性味：</strong>' + escapeHtml(info.xingwei || '') + '</p>';
        html += '  <p><strong>归经：</strong>' + escapeHtml(info.guijing || '') + '</p>';
        html += '  <p><strong>功效：</strong>' + escapeHtml(info.gongxiao || '') + '</p>';
        html += '  <p><strong>禁忌：</strong>' + escapeHtml(info.jinji || '') + '</p>';
        html += '</div>';
    }
    list.innerHTML = html;
}

// ========== 个人中心 ==========

function initProfile() {
    loadProfile();
}

function getUserId() {
    var uid = localStorage.getItem('som_user_id');
    if (!uid) {
        uid = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('som_user_id', uid);
    }
    return uid;
}

function getUserData() {
    var key = 'som_user_data_' + getUserId();
    var dataStr = localStorage.getItem(key);
    var data;
    if (dataStr) {
        try { data = JSON.parse(dataStr); } catch(e) { data = {}; }
    } else {
        data = {};
    }
    // 默认值
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
    var key = 'som_user_data_' + getUserId();
    localStorage.setItem(key, JSON.stringify(data));
}

function loadProfile() {
    var data = getUserData();
    
    document.getElementById('profile-name').textContent = data.name;
    document.getElementById('profile-tizhi').textContent = '体质：' + (data.tizhi || '未检测');
    document.getElementById('profile-points').textContent = '积分：' + (data.points || 0);
    
    // 签到状态
    var today = new Date().toISOString().split('T')[0];
    var checkedInToday = data.checkins && data.checkins.indexOf(today) >= 0;
    document.getElementById('profile-checkin').textContent = checkedInToday ? '✅ 今天已签到' : '签到：今天未签到';
    
    // 统计
    document.getElementById('stat-chats').textContent = (data.chats || []).length;
    document.getElementById('stat-checkins').textContent = (data.checkins || []).length;
    document.getElementById('stat-products').textContent = data.productBrowses || 0;
    
    // 体质记录
    loadTizhiRecords(data);
}

function loadTizhiRecords(data) {
    var history = document.getElementById('profile-history');
    if (!history) return;
    
    var records = data.tizhiRecords || [];
    if (records.length === 0) {
        history.innerHTML = '<p class="empty-hint">暂无体质记录，快去和小麦SOM对话吧</p>';
        return;
    }
    
    // 显示最近5条
    var html = '';
    var maxShow = Math.min(records.length, 5);
    for (var i = records.length - maxShow; i < records.length; i++) {
        var r = records[i];
        html += '<div class="history-item">';
        html += '  <span class="history-date">' + escapeHtml(r.date || '') + '</span>';
        html += '  <span class="history-tizhi">' + escapeHtml(r.tizhi || '') + '</span>';
        html += '  <span class="history-desc">' + escapeHtml(r.desc || '') + '</span>';
        html += '</div>';
    }
    history.innerHTML = html;
}

function saveChatRecord(message, reply, tizhi) {
    var data = getUserData();
    if (!data.chats) data.chats = [];
    
    data.chats.push({
        date: new Date().toISOString(),
        message: message.substring(0, 100),
        tizhi: tizhi || ''
    });
    
    // 如果辨证结果有体质信息，记录体质
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
    var data = getUserData();
    if (!data.productBrowses) data.productBrowses = 0;
    data.productBrowses += count;
    saveUserData(data);
}