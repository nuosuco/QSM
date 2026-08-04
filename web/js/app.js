// SOM 松麦 - 前端逻辑

// API地址：同域部署时用相对路径，跨域时修改此处
const API_BASE = '';

// ========== 初始化 ==========

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initChat();
    initHealthTest();
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
            
            // 切换到健康测评时渲染
            if (targetTab === 'health-test') {
                renderHealthTestPage();
            }
        });
    });
}

// ========== 对话功能 ==========

// 新用户引导标记（是否已引导过）
let _guidedNewUser = false;

function initChat() {
    const sendBtn = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    const uploadBtn = document.getElementById('upload-btn');
    const imageInput = document.getElementById('image-input');
    
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 图片上传/拍照（支持多张，连续拍）
    uploadBtn.addEventListener('click', () => {
        imageInput.value = ''; // 重置，确保取消后能再次拍照
        // 移除 capture 属性，让系统文件选择器支持多选
        imageInput.removeAttribute('capture');
        imageInput.setAttribute('multiple', 'multiple');
        imageInput.click();
    });
    imageInput.addEventListener('change', handleImageSelect);
    
    // 连拍按钮：预览区底部有"＋继续拍"按钮，点击直接打开拍照
    document.addEventListener('click', function(e) {
        if (e.target.closest('.preview-add')) {
            imageInput.value = '';
            imageInput.removeAttribute('capture');
            imageInput.setAttribute('multiple', 'multiple');
            imageInput.click();
        }
    });
    
    // 新用户引导：检查是否第一次进来
    setTimeout(checkNewUserGuide, 500);
}

// 每次进入都显示体质评测引导（拍照+测评入口常驻，不限新用户）
async function checkNewUserGuide() {
    if (_guidedNewUser) return;
    _guidedNewUser = true;
    
    // 替换欢迎消息为引导版本（每次刷新/打开都显示，确保体质评测入口随时可见）
    const chatMessages = document.getElementById('chat-messages');
    const welcome = chatMessages.querySelector('.message.assistant');
    if (welcome) {
        const msgDiv = welcome.querySelector('.message-content');
        if (msgDiv) {
            msgDiv.innerHTML = `
                <div class="message-text">
                    你好呀！我是小麦 🌾<br>
                    想知道自己是什么体质、该吃什么养生吗？<br>
                    📷 拍个照（舌苔/面色/皮肤/患处）<br>
                    📝 或做3分钟测评<br>
                    我帮你辨证，给你食疗方案！
                </div>
                <div class="guide-actions">
                    <button class="guide-btn photo" onclick="showGuideScan()">📷 拍照扫描<br><span class="guide-btn-sub">（舌苔/面色/皮肤/患处）</span></button>
                    <button class="guide-btn test" onclick="switchToHealthTest('chat')">📝 3分钟健康测评</button>
                </div>
            `;
        }
    }
}

// 引导按钮：拍照扫描（上传图片）
function showGuideScan() {
    document.getElementById('image-input').click();
}

// 跳转到健康测评页（养生谷banner / 小麦引导按钮 / 快捷问题共用）
function switchToHealthTest(from) {
    // 记录来源：'chat' 或 'yangshenggu'，决定返回按钮文案
    _healthTestFrom = from || 'yangshenggu';
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    navBtns.forEach(b => b.classList.remove('active'));
    tabContents.forEach(c => c.classList.remove('active'));
    const healthTab = document.getElementById('health-test-tab');
    if (healthTab) {
        healthTab.classList.add('active');
        renderHealthTestPage();
        // 更新返回按钮文案
        const backBtn = document.querySelector('.test-back-nav');
        if (backBtn) {
            backBtn.textContent = _healthTestFrom === 'chat' ? '← 返回小麦' : '← 返回养生谷';
        }
    }
}

let _healthTestFrom = 'yangshenggu';

// 从健康测评页返回（根据来源决定回哪里）
function goBackFromTest() {
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    navBtns.forEach(b => b.classList.remove('active'));
    tabContents.forEach(c => c.classList.remove('active'));
    const targetTab = _healthTestFrom === 'chat' ? 'chat' : 'yangshenggu';
    const tab = document.getElementById(targetTab + '-tab');
    const btn = document.querySelector('.nav-btn[data-tab="' + targetTab + '"]');
    if (tab) tab.classList.add('active');
    if (btn) btn.classList.add('active');
}

// 当前选中的图片 base64 列表（支持多张）
let pendingImages = [];

function handleImageSelect(e) {
    const files = Array.from(e.target.files || []);
    // 重置 input，允许重复选同一文件 / 取消后再拍
    e.target.value = '';
    if (files.length === 0) return; // 用户取消，不做任何事，可再次点击拍照

    files.forEach(file => {
        const img = new Image();
        const objectUrl = URL.createObjectURL(file);
        img.onload = function() {
            URL.revokeObjectURL(objectUrl);
            const maxW = 1280;
            let w = img.width, h = img.height;
            if (w > maxW) { h = Math.round(h * maxW / w); w = maxW; }
            const canvas = document.createElement('canvas');
            canvas.width = w; canvas.height = h;
            canvas.getContext('2d').drawImage(img, 0, 0, w, h);
            pendingImages.push(canvas.toDataURL('image/jpeg', 0.8));
            renderImagePreviews();
        };
        img.onerror = function() { URL.revokeObjectURL(objectUrl); };
        img.src = objectUrl;
    });
}

function renderImagePreviews() {
    const list = document.getElementById('image-preview-list');
    if (!list) return;
    if (pendingImages.length === 0) { list.style.display = 'none'; list.innerHTML = ''; return; }
    list.style.display = 'flex';
    list.innerHTML = pendingImages.map((src, i) =>
        '<div class="preview-item">' +
          '<img src="' + src + '" alt="预览">' +
          '<button class="preview-remove" onclick="removePreviewImage(' + i + ')">✕</button>' +
        '</div>'
    ).join('') +
    '<button class="preview-add">＋</button>' +
    '<div class="preview-hint">已选' + pendingImages.length + '张，点发送一起分析</div>';
}

function removePreviewImage(idx) {
    pendingImages.splice(idx, 1);
    renderImagePreviews();
}

function clearImagePreview() {
    pendingImages = [];
    renderImagePreviews();
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const message = input.value.trim();
    const hasImage = pendingImages.length > 0;
    
    if (!message && !hasImage) return;
    
    // 显示用户消息（带图片预览）
    let displayMsg = message;
    if (hasImage) {
        const imgsHtml = pendingImages.map(src => '<img src="' + src + '" style="width:60px;height:60px;border-radius:6px;object-fit:cover;margin:2px 2px 0 0;">').join('');
        displayMsg = (message ? message + '<br>' : '📷 ') + imgsHtml;
    }
    appendMessage(displayMsg, 'user', true);
    
    const imagesToSend = pendingImages.slice();
    input.value = '';
    clearImagePreview();
    sendBtn.disabled = true;
    
    // 显示加载状态（带超时倒计时提示）
    const loadingId = appendMessage('<div class="loading"></div>', 'assistant', true);
    
    // 如果30秒还没返回，更新loading提示告知用户还在处理
    let slowTimer = setTimeout(() => {
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) {
            const textEl = loadingEl.querySelector('.message-text');
            if (textEl) textEl.innerHTML = '<div class="loading"></div><div style="color:#999;font-size:13px;margin-top:8px">正在分析图片，请稍候…可能需要30-60秒</div>';
        }
    }, 30000);
    
    try {
        let response;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 90000); // 90秒超时（LLM 45s + 商品搜索 10s + 余量）
        if (hasImage) {
            // 图片辨证：走 vision 接口（支持多图）
            response = await fetch(`${API_BASE}/api/chat/vision`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                signal: controller.signal,
                body: JSON.stringify({
                    message: message || '请综合观察这些照片（舌苔/面色/皮肤/患处），从中医角度分析，给出体质倾向和食养建议。',
                    images: imagesToSend,
                    user_id: getUserId(),
                    session_id: getSessionId()
                })
            });
        } else {
            response = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                signal: controller.signal,
                body: JSON.stringify({
                    message: message,
                    session_id: getSessionId(),
                    user_id: getUserId()
                })
            });
        }
        clearTimeout(timeoutId);
        clearTimeout(slowTimer);
        
        const data = await response.json();
        
        // 移除加载状态
        const loadingEl = document.getElementById(loadingId);
        if (loadingEl) loadingEl.remove();
        
        // 显示AI回复
        let replyText = data.reply;
        
        // 图片辨证：显示回复 + 商品推荐 + 多轮引导（3个建议问题）+ 收藏分享
        if (hasImage) {
            const msgId = appendMessage(replyText, 'assistant', false, false);
            // 渲染商品推荐（和小麦对话一样的逻辑）
            if (data.products && data.products.length > 0) {
                const chatContainer = document.getElementById('chat-messages');
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
                chatContainer.appendChild(productsDiv);
            }
            appendFollowUpSuggestions(hasImage);
            appendMessageActions(msgId, replyText);
            saveChatRecord('[图片辨证x' + imagesToSend.length + '] ' + message, replyText, '');
            scrollToLastUserMessage();
            sendBtn.disabled = false;
            return;
        }
        
        // 保存对话记录 + 同步体质到后端
        saveChatRecord(message, replyText, data.tizhi || '');
        
        // 如果有推荐商品，显示为可点击的商品卡片
        if (data.products && data.products.length > 0) {
            // 不自动滚底！等商品全部渲染完后一次性定位
            const chatMsgDiv = appendMessage(replyText, 'assistant', false, false);
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
            
            // 给小麦回答框添加收藏+分享图按钮
            const chatMsg = document.getElementById(chatMsgDiv);
            if (chatMsg) {
                const bar = document.createElement('div');
                bar.className = 'msg-action-bar';

                const favBtn = document.createElement('button');
                favBtn.className = 'msg-action-btn';
                favBtn.innerHTML = '♡ 收藏';
                favBtn.onclick = function() {
                    const isFav = this.classList.contains('favorited');
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

                const shareBtn = document.createElement('button');
                shareBtn.className = 'msg-action-btn';
                shareBtn.innerHTML = '🖼️ 分享图';
                shareBtn.onclick = function() { generateShareImage(replyText); };

                bar.appendChild(favBtn);
                bar.appendChild(shareBtn);
                chatMsg.querySelector('.message-content').appendChild(bar);
            }
            
            chatContainer.appendChild(productsDiv);
            appendFollowUpSuggestions(false);
            scrollToLastUserMessage();
            
            return;
        }
        
        // 无商品：定位到用户消息 + 收藏分享
        const plainMsgId = appendMessage(replyText, 'assistant', false, false);
        appendMessageActions(plainMsgId, replyText);
        scrollToLastUserMessage();
        
    } catch (error) {
        document.getElementById(loadingId).remove();
        let errMsg = '抱歉，出了点问题：';
        if (error.name === 'AbortError' || (error.message && error.message.includes('aborted'))) {
            errMsg += 'AI 思考超时，请重试。';
        } else if (error instanceof TypeError && error.message.includes('fetch')) {
            errMsg += '网络连接失败，请检查网络后重试。';
        } else {
            errMsg += (error.message || '未知错误') + '，请重试。';
        }
        const errId = appendMessage(errMsg, 'assistant', false, false);
        // 添加重试按钮
        const errDiv = document.getElementById(errId);
        if (errDiv) {
            const retryBtn = document.createElement('button');
            retryBtn.className = 'msg-action-btn';
            retryBtn.innerHTML = '🔄 重试';
            retryBtn.style.cssText = 'margin:8px 0 0 48px;padding:6px 16px;border:1px solid #7bc49f;border-radius:16px;background:#f0f7f2;color:#3a7d5c;font-size:14px;cursor:pointer;';
            retryBtn.onclick = function() {
                errDiv.remove();
                input.value = message;
                if (imagesToSend.length) { pendingImages = imagesToSend; }
                sendMessage();
            };
            errDiv.querySelector('.message-content').appendChild(retryBtn);
        }
        console.error('发送消息失败:', error);
    } finally {
        sendBtn.disabled = false;
    }
}

// ========== 多轮引导：小麦回复末尾留 3 个建议问题 ==========
// 用户点一个就自动提交给小麦，引导继续拍照/补充症状，最终多维辩证
function appendFollowUpSuggestions(afterImage) {
    const container = document.getElementById('chat-messages');
    // 统一末尾引导问题（无论是否拍过照，同一套）
    const suggestions = [
        '📷 再拍一张其他部位（面色/皮肤/患处）',
        '📝 帮我再做个3分钟体质评测',
        '🌾 给我推荐药膳食疗方案'
    ];

    const wrap = document.createElement('div');
    wrap.className = 'followup-suggestions';
    wrap.innerHTML = '<div class="followup-title">你可以继续：</div>' +
        suggestions.map(s => '<button class="followup-chip">' + s + '</button>').join('');
    container.appendChild(wrap);

    wrap.querySelectorAll('.followup-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const text = chip.textContent.trim();
            // 拍照类：直接唤起图片选择
            if (text.indexOf('📷') === 0) {
                document.getElementById('image-input').click();
                return;
            }
            // 测评类：跳养生谷测评（兼容"评测"和"测评"两种写法）
            if (text.indexOf('体质评') >= 0) {
                switchToHealthTest('chat');
                return;
            }
            // 其他：填入输入框并发送
            const input = document.getElementById('chat-input');
            input.value = text.replace(/^[\u{1F300}-\u{1FAFF}\u2600-\u27BF]\s*/u, '');
            sendMessage();
        });
    });
}

// ========== 收藏 + 图片分享（裂变） ==========
// 给小麦的每条回复加「收藏」和「生成分享图」按钮
function appendMessageActions(msgId, replyText) {
    const chatMsg = document.getElementById(msgId);
    if (!chatMsg) return;
    const content = chatMsg.querySelector('.message-content');
    if (!content) return;

    const bar = document.createElement('div');
    bar.className = 'msg-action-bar';

    const favBtn = document.createElement('button');
    favBtn.className = 'msg-action-btn';
    favBtn.innerHTML = '♡ 收藏';
    favBtn.onclick = function() {
        const isFav = this.classList.contains('favorited');
        if (isFav) {
            this.innerHTML = '♡ 收藏';
            this.classList.remove('favorited');
        } else {
            this.innerHTML = '♥ 已收藏';
            this.classList.add('favorited');
            const userMsg = document.querySelector('#chat-messages .message.user:last-of-type');
            const favData = {
                type: 'chat',
                userMessage: userMsg ? userMsg.querySelector('.message-text').textContent : '',
                assistantReply: replyText,
                time: new Date().toISOString()
            };
            let favs = JSON.parse(localStorage.getItem('som_favorites') || '[]');
            favs.push(favData);
            localStorage.setItem('som_favorites', JSON.stringify(favs));
        }
    };

    const shareBtn = document.createElement('button');
    shareBtn.className = 'msg-action-btn';
    shareBtn.innerHTML = '🖼️ 分享图';
    shareBtn.onclick = function() { generateShareImage(replyText); };

    bar.appendChild(favBtn);
    bar.appendChild(shareBtn);
    content.appendChild(bar);
}

// 用 canvas 把小麦回答画成分享卡片图，长按可保存/转发
function generateShareImage(text) {
    const W = 750, padding = 50, lineHeight = 40, fontSize = 28;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // 先算文字换行，确定高度
    ctx.font = fontSize + 'px "PingFang SC", "Microsoft YaHei", sans-serif';
    const maxTextW = W - padding * 2;
    const rawLines = String(text).split('\n');
    const lines = [];
    rawLines.forEach(raw => {
        if (raw.trim() === '') { lines.push(''); return; }
        let cur = '';
        for (const ch of raw) {
            if (ctx.measureText(cur + ch).width > maxTextW) {
                lines.push(cur); cur = ch;
            } else cur += ch;
        }
        if (cur) lines.push(cur);
    });

    const headerH = 130, footerH = 240;
    const bodyH = lines.length * lineHeight + 40;
    const H = headerH + bodyH + footerH;
    canvas.width = W; canvas.height = H;

    // 背景
    const grad = ctx.createLinearGradient(0, 0, 0, H);
    grad.addColorStop(0, '#f0f7f2'); grad.addColorStop(1, '#e3f0e8');
    ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);

    // 头部
    ctx.fillStyle = '#3a7d5c';
    ctx.font = 'bold 40px "PingFang SC", sans-serif';
    ctx.fillText('🌾 小麦SOM · 养生辨证', padding, 75);
    ctx.fillStyle = '#7ba892'; ctx.font = '24px sans-serif';
    ctx.fillText('中医辨证 · 有机养生', padding, 110);

    // 正文
    ctx.fillStyle = '#2d3b33'; ctx.font = fontSize + 'px "PingFang SC", "Microsoft YaHei", sans-serif';
    let y = headerH + 30;
    lines.forEach(l => { ctx.fillText(l, padding, y); y += lineHeight; });

    // 底部
    ctx.textAlign = 'center';
    ctx.fillStyle = '#3a7d5c'; ctx.font = 'bold 26px sans-serif';
    ctx.fillText('扫码体验 SOM 松麦 · 你的养生助手', W / 2, H - 195);
    ctx.fillStyle = '#9bb8a8'; ctx.font = '22px sans-serif';
    ctx.fillText('som.top · 以上为养生文化参考，不构成医疗诊断', W / 2, H - 160);

    // 小程序码
    const qrImg = new Image();
    qrImg.onload = () => {
        const qrSize = 130;
        ctx.drawImage(qrImg, W / 2 - qrSize / 2, H - 145, qrSize, qrSize);
        showSharePreview(canvas.toDataURL('image/png'));
    };
    qrImg.onerror = () => {
        // 二维码加载失败也要能分享
        showSharePreview(canvas.toDataURL('image/png'));
    };
    qrImg.src = '/public/qrcode.jpg';
}

function showSharePreview(dataUrl) {
    let mask = document.getElementById('share-preview-mask');
    if (mask) mask.remove();
    mask = document.createElement('div');
    mask.id = 'share-preview-mask';
    mask.className = 'share-preview-mask';
    mask.innerHTML =
        '<div class="share-preview-box">' +
          '<img src="' + dataUrl + '" alt="分享图">' +
          '<div class="share-preview-tip">长按图片保存，或点击下方按钮分享 💚</div>' +
          '<div class="share-preview-btns">' +
            '<button class="share-native-btn" onclick="nativeShareImage()">📤 分享给朋友</button>' +
            '<a class="share-dl-btn" href="' + dataUrl + '" download="xiaomai-share.png">⬇️ 保存图片</a>' +
            '<button class="share-close-btn" onclick="document.getElementById(\'share-preview-mask\').remove()">关闭</button>' +
          '</div>' +
        '</div>';
    mask.addEventListener('click', (e) => { if (e.target === mask) mask.remove(); });
    document.body.appendChild(mask);
}

// 调用系统原生分享（手机浏览器支持）
async function nativeShareImage() {
    const img = document.querySelector('#share-preview-mask img');
    if (!img) return;
    try {
        const blob = await (await fetch(img.src)).blob();
        const file = new File([blob], 'xiaomai-share.png', { type: 'image/png' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) {
            await navigator.share({
                title: '小麦SOM · 养生辨证',
                text: '我用小麦SOM做了中医养生辨证，结果超准！',
                files: [file]
            });
        } else {
            // 当前浏览器/APP不支持 Web Share API 文件分享，提示长按保存
            const tip = document.querySelector('#share-preview-mask .share-preview-tip');
            if (tip) tip.textContent = '当前环境不支持直接分享，请长按图片保存后，再去微信/QQ手动分享 💚';
        }
    } catch (e) {
        // 用户取消分享（AbortError）不提示
        if (e.name !== 'AbortError') {
            const tip = document.querySelector('#share-preview-mask .share-preview-tip');
            if (tip) tip.textContent = '分享失败，请长按图片保存后手动分享到微信/QQ 💚';
        }
    }
}

// 滚动定位：把最后一条用户消息放到聊天区顶部
// 用户能看到：自己的输入 + 小麦回答，往下滑才看到商品/更多内容
function scrollToLastUserMessage() {
    const chatContainer = document.getElementById('chat-messages');
    const allUserMsgs = chatContainer.querySelectorAll('.message.user');
    const lastUserMsg = allUserMsgs[allUserMsgs.length - 1];
    if (lastUserMsg) {
        // 用 offsetTop 定位：用户消息在容器中的偏移量
        // 容器顶部留10px边距，用户能看到自己输入 + 小麦回答
        chatContainer.scrollTop = lastUserMsg.offsetTop - 10;
    }
}

function appendMessage(text, type, isHtml = false, autoScroll = true) {
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
    if (autoScroll) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    return messageId;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getSessionId() {
    // 用 localStorage 持久化，关闭浏览器再打开也不丢会话
    let sessionId = localStorage.getItem('som_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('som_session_id', sessionId);
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
    if (!webUrl) return;
    
    // 判断是否电脑浏览器（电脑浏览器直接跳转淘宝商品页，手机端走淘口令）
    var isMobile = /Android|iPhone|iPad|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (platform === 'taobao' || !platform) {
        if (isMobile) {
            // 手机端：走淘口令方案
            var tpwdUrl = '/api/products/tpwd?url=' + encodeURIComponent(webUrl) + '&text=' + encodeURIComponent('');
            fetch(tpwdUrl)
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    var tpwd = data.model || data.tpwd || '';
                    if (tpwd) {
                        copyToClipboard(tpwd, '淘口令已复制，打开淘宝APP即可查看');
                    } else {
                        copyToClipboard(webUrl, '链接已复制，打开淘宝APP即可查看');
                    }
                })
                .catch(function() {
                    copyToClipboard(webUrl, '链接已复制，打开淘宝APP即可查看');
                });
        } else {
            // 电脑端：直接跳转淘宝商品详情页
            window.open(webUrl, '_blank');
        }
    } else {
        // 京东等平台：直接复制链接
        copyToClipboard(webUrl, '链接已复制，打开' + (platform === 'jd' ? '京东' : 'APP') + '即可查看');
    }
}

// 复制到剪贴板
function copyToClipboard(text, toast) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function() {
            showToast(toast || '已复制');
        }).catch(function() {
            fallbackCopy(text, toast);
        });
    } else {
        fallbackCopy(text, toast);
    }
}

function fallbackCopy(text, toast) {
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        showToast(toast || '已复制');
    } catch(e) {
        window.open(text, '_blank');
    }
    document.body.removeChild(textarea);
}

// Toast 提示
function showToast(msg) {
    var el = document.createElement('div');
    el.textContent = msg;
    el.style.cssText = 'position:fixed;bottom:100px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.8);color:#fff;padding:12px 24px;border-radius:8px;font-size:14px;z-index:99999;max-width:80%;text-align:center;transition:opacity 0.3s;';
    document.body.appendChild(el);
    setTimeout(function() {
        el.style.opacity = '0';
        setTimeout(function() { el.remove(); }, 300);
    }, 2500);
}

// ========== 二维码弹窗 ==========
function showQRCode(url, title) {
    if (!url || url === '#') return;
    
    var existing = document.getElementById('qr-overlay');
    if (existing) existing.remove();
    
    var overlay = document.createElement('div');
    overlay.id = 'qr-overlay';
    overlay.className = 'detail-overlay show';
    overlay.onclick = function(e) { if (e.target === overlay) overlay.remove(); };
    
    var modal = document.createElement('div');
    modal.className = 'qr-modal';
    
    var closeBtn = document.createElement('button');
    closeBtn.className = 'qr-close';
    closeBtn.textContent = '\u2715';
    closeBtn.onclick = function() { overlay.remove(); };
    modal.appendChild(closeBtn);
    
    var h3 = document.createElement('h3');
    h3.textContent = '手机扫码购买';
    modal.appendChild(h3);
    
    var hint = document.createElement('p');
    hint.className = 'qr-hint';
    hint.innerHTML = '<span class="qr-hint-icon">📱</span> 用手机淘宝APP扫描购买';
    modal.appendChild(hint);
    
    var container = document.createElement('div');
    container.id = 'qr-code-container';
    container.className = 'qr-code-container';
    modal.appendChild(container);
    
    var titleDiv = document.createElement('div');
    titleDiv.className = 'qr-title';
    titleDiv.textContent = title || '';
    modal.appendChild(titleDiv);
    
    var footer = document.createElement('div');
    footer.className = 'qr-footer';
    var copyBtn = document.createElement('button');
    copyBtn.className = 'detail-buy';
    copyBtn.textContent = '复制链接';
    copyBtn.onclick = function() {
        copyToClipboard(url, '链接已复制');
        overlay.remove();
    };
    footer.appendChild(copyBtn);
    modal.appendChild(footer);
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // 生成二维码 - 用 canvas 转 img 方便长按保存
    setTimeout(function() {
        var c = document.getElementById('qr-code-container');
        if (c && typeof QRCode !== 'undefined') {
            c.innerHTML = '';
            try {
                // 直接让 qrcodejs 渲染到容器中（它自动选择 canvas/svg/table）
                var qr = new QRCode(c, {
                    text: url,
                    width: 200,
                    height: 200,
                    colorDark: '#000000',
                    colorLight: '#ffffff',
                    correctLevel: QRCode.CorrectLevel.L
                });
                // 加一个保存按钮（用 canvas 转 dataURL 下载）
                var qrCanvas = c.querySelector('canvas');
                if (qrCanvas) {
                    var dataUrl = qrCanvas.toDataURL('image/png');
                    var saveBtn = document.createElement('a');
                    saveBtn.href = dataUrl;
                    saveBtn.download = 'qrcode.png';
                    saveBtn.textContent = '⬇️ 保存二维码';
                    saveBtn.style.cssText = 'display:block;margin-top:10px;color:#4a9d6e;font-size:14px;text-decoration:none;font-weight:600;';
                    saveBtn.onclick = function(e) {
                        var link = document.createElement('a');
                        link.href = dataUrl;
                        link.download = 'qrcode.png';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    };
                    c.appendChild(saveBtn);
                }
            } catch(e) {
                c.innerHTML = '<p style="color:#e85d2c;padding:40px;text-align:center;font-size:14px;">📱 二维码生成失败，请点击下方「复制链接」<br>然后在手机淘宝中粘贴打开</p>';
            }
        } else if (c) {
            c.innerHTML = '<p style="color:#e85d2c;padding:40px;text-align:center;font-size:14px;">📱 二维码加载失败，请点击下方「复制链接」<br>然后在手机淘宝中粘贴打开</p>';
        }
    }, 100);
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
                    <button class="detail-qr-btn" onclick="showQRCode('${escapeHtml(product.url || '#')}', '${escapeHtml(product.title || '')}')" title="手机扫码购买">📱 用手机淘宝APP扫描购买</button>
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
                    <button class="detail-detail-qr-btn" onclick="showQRCode('${escapeHtml(detailUrl || '#')}', '${escapeHtml(product.title || '')}')" title="手机扫码购买">📱 用手机淘宝APP扫描购买</button>
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

// ========== 健康测评（AI拍照扫描 + 答题测评） ==========

// 九种体质测评题目
const TIZHI_QUESTIONS = [
  { q: '你容易感到疲乏、气短吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { qixu: [0, 1, 2, 3] } },
  { q: '你手脚容易发凉、怕冷吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { yangxu: [0, 1, 2, 3] } },
  { q: '你手心脚心容易发热、口干吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { yinxu: [0, 1, 2, 3] } },
  { q: '你体型偏胖、腹部松软、痰多吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { tanshi: [0, 1, 2, 3] } },
  { q: '你面部容易出油、口苦、大便黏滞吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { shire: [0, 1, 2, 3] } },
  { q: '你皮肤容易出现瘀斑、面色晦暗吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { xueyu: [0, 1, 2, 3] } },
  { q: '你容易情绪低落、多愁善感、胸闷叹气吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { qiyu: [0, 1, 2, 3] } },
  { q: '你容易过敏（食物、药物、花粉等）吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { tebing: [0, 1, 2, 3] } },
  { q: '你精力充沛、睡眠好、适应力强吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { pinghe: [0, 1, 2, 3] } },
  { q: '你容易头晕、站起时眼前发黑吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { qixu: [0, 1, 2, 3], yangxu: [0, 0, 1, 2] } }
];

// 症状自评题目
const SYMPTOM_QUESTIONS = [
  { q: '你经常头晕、头痛、耳鸣吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaoya: [0, 1, 2, 3] } },
  { q: '你容易面红耳赤、急躁易怒吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaoya: [0, 1, 2, 3] } },
  { q: '你经常口渴、多饮、多尿吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaotang: [0, 1, 2, 3] } },
  { q: '你容易饿、吃得多但体重下降吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaotang: [0, 1, 2, 3] } },
  { q: '你视力模糊、伤口愈合慢、手脚发麻吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { tangniao: [0, 1, 2, 3] } },
  { q: '你体检发现血脂偏高、容易胸闷吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaozhi: [0, 1, 2, 3] } },
  { q: '你关节（尤其大脚趾）红肿热痛、夜间发作过吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { tongfeng: [0, 1, 2, 3] } },
  { q: '你爱吃海鲜、喝啤酒、吃动物内脏吗？', options: ['很少', '偶尔', '经常', '天天'], scores: { tongfeng: [0, 1, 2, 3] } },
  { q: '你关节晨僵、遇冷疼痛加重、游走性疼痛吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { fengshi: [0, 1, 2, 3] } },
  { q: '你入睡困难、易醒、多梦、睡眠质量差吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { shimian: [0, 1, 2, 3] } },
  { q: '你持续疲倦、注意力下降、怎么睡都不够吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { pilao: [0, 1, 2, 3] } },
  { q: '你容易腹胀、大便稀溏、食欲差吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { piwei: [0, 1, 2, 3] } },
  { q: '你肢体麻木、沉重、像裹了湿布吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { fengshi: [0, 1, 2, 3], piwei: [0, 0, 1, 2] } },
  { q: '你体检发现尿酸偏高吗？', options: ['正常', '临界', '偏高', '很高'], scores: { tongfeng: [0, 1, 2, 3] } },
  { q: '你血压测量经常超过 140/90 吗？', options: ['正常', '临界', '偏高', '很高'], scores: { gaoya: [0, 1, 2, 3] } },
  { q: '你空腹血糖经常超过 6.1 吗？', options: ['正常', '临界', '偏高', '很高'], scores: { gaotang: [0, 1, 2, 3] } },
  { q: '你已被诊断为糖尿病或糖耐量异常吗？', options: ['没有', '临界', '已确诊', '多年'], scores: { tangniao: [0, 1, 2, 3] } },
  { q: '你尿频、尿急、夜尿多、排尿无力吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { qianlie: [0, 1, 2, 3] } },
  { q: '你会阴部坠胀、腰骶酸痛、久坐加重吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { qianlie: [0, 1, 2, 3] } },
  { q: '你皮肤瘙痒、起疹、反复发作吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { pifu: [0, 1, 2, 3] } },
  { q: '你皮肤干燥脱屑、遇热或出汗加重吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { pifu: [0, 1, 2, 3] } },
  { q: '你手脚冰凉、麻木、青筋凸起、静脉曲张吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { xueye: [0, 1, 2, 3] } },
  { q: '你蹲下站起头晕、面色苍白、心悸气短吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { xueye: [0, 1, 2, 3] } }
];

// 体质结果模板
const TIZHI_RESULTS = {
  qixu: { name: '气虚质', emoji: '😮‍💨', symptoms: ['容易累', '气短懒言', '爱感冒', '面色偏黄'], desc: '元气不足，脏腑功能偏弱。', diet: '黄芪炖鸡、山药薏米粥、红枣桂圆茶', avoid: '生冷寒凉、过度劳累、大汗运动', life: '早睡早起，适度散步，避免过劳' },
  yangxu: { name: '阳虚质', emoji: '🥶', symptoms: ['怕冷', '手脚冰凉', '喜热饮', '大便稀溏'], desc: '阳气不足，畏寒怕冷。', diet: '当归生姜羊肉汤、桂圆红枣茶、韭菜炒核桃', avoid: '冰饮、寒凉水果、空调直吹', life: '多晒太阳，温水泡脚，冬季进补' },
  yinxu: { name: '阴虚质', emoji: '🔥', symptoms: ['手心发热', '口干', '盗汗', '失眠多梦'], desc: '阴液亏少，虚火内生。', diet: '银耳百合羹、枸杞菊花茶、桑葚粥', avoid: '辛辣煎炸、熬夜、过度出汗', life: '早睡养阴，静养为主，避免燥热' },
  tanshi: { name: '痰湿质', emoji: '🫧', symptoms: ['体型偏胖', '痰多', '身体沉重', '面部油腻'], desc: '痰湿凝聚，脾运不健。', diet: '薏米赤小豆汤、陈皮茯苓茶、冬瓜荷叶汤', avoid: '甜腻油炸、酒、久坐不动', life: '多运动出汗，饮食清淡，控制体重' },
  shire: { name: '湿热质', emoji: '🌡️', symptoms: ['面油口苦', '大便黏滞', '小便黄', '易长痘'], desc: '湿热内蕴，缠绵难解。', diet: '绿豆薏米汤、苦瓜凉拌、茵陈茶', avoid: '辛辣油腻、酒、熬夜', life: '清淡饮食，多运动，避免潮湿环境' },
  xueyu: { name: '血瘀质', emoji: '🩸', symptoms: ['面色晦暗', '皮肤瘀斑', '痛经', '唇色暗'], desc: '血行不畅，瘀血内阻。', diet: '山楂红糖水、玫瑰花茶、黑木耳炒山药', avoid: '久坐不动、寒凉收引、情绪压抑', life: '多运动促循环，保持心情舒畅' },
  qiyu: { name: '气郁质', emoji: '😔', symptoms: ['情绪低落', '胸闷叹气', '多愁善感', '咽中异物感'], desc: '气机郁滞，情志不畅。', diet: '玫瑰花茶、佛手柑粥、合欢花饮', avoid: '压抑情绪、独处过久、咖啡因过量', life: '多社交，培养爱好，适当运动释放' },
  tebing: { name: '特禀质', emoji: '🤧', symptoms: ['易过敏', '打喷嚏', '皮肤起疹', '适应力差'], desc: '先天禀赋异常，易过敏。', diet: '黄芪红枣粥、蜂蜜水、山药莲子汤', avoid: '已知过敏原、辛辣刺激、环境突变', life: '远离过敏原，增强体质，规律作息' },
  pinghe: { name: '平和质', emoji: '😊', symptoms: ['精力充沛', '睡眠好', '适应力强', '面色红润'], desc: '阴阳气血调和，最健康的体质。', diet: '均衡饮食即可，无需特殊调理', avoid: '暴饮暴食、熬夜、过度劳累', life: '保持现有好习惯，顺应节气养生' }
};

// 症状结果模板
const SYMPTOM_RESULTS = {
  gaoya: { name: '高血压倾向', emoji: '🔴', symptoms: ['头晕头痛', '耳鸣', '面红易怒', '血压偏高'], desc: '肝阳上亢或痰湿阻络，血压调节失衡。', diet: '芹菜汁、山楂决明子茶、天麻炖鱼头', avoid: '高盐饮食、烟酒、情绪激动、熬夜', life: '低盐低脂，每日散步30分钟，监测血压' },
  gaotang: { name: '高血糖倾向', emoji: '🟠', symptoms: ['多饮多尿', '容易饿', '体重下降', '血糖偏高'], desc: '阴虚燥热，脾失运化，糖代谢异常。', diet: '苦瓜炒蛋、山药薏米粥、玉米须茶', avoid: '甜食精米面、含糖饮料、油炸食品', life: '控制碳水，餐后散步，定期测血糖' },
  tangniao: { name: '糖尿病倾向', emoji: '🔶', symptoms: ['三多一少', '视力模糊', '伤口愈合慢', '手脚发麻'], desc: '消渴证，阴虚燥热日久，累及肝肾，并发症风险高。', diet: '苦瓜排骨汤、黄精枸杞茶、荞麦面、山药薏米粥', avoid: '白糖红糖、精白米面、高糖水果、油炸食品', life: '严格控糖，餐后步行20分钟，定期查糖化血红蛋白' },
  gaozhi: { name: '高血脂倾向', emoji: '🟡', symptoms: ['头晕胸闷', '肢体麻木', '血脂偏高', '体型偏胖'], desc: '痰浊瘀阻，脂代谢紊乱。', diet: '山楂荷叶茶、黑木耳炒洋葱、燕麦粥', avoid: '动物内脏、油炸食品、奶油甜点', life: '有氧运动，控制体重，少油少盐' },
  tongfeng: { name: '高尿酸/痛风倾向', emoji: '🟣', symptoms: ['关节红肿热痛', '夜间发作', '尿酸偏高', '爱吃海鲜啤酒'], desc: '湿热瘀阻，尿酸代谢异常，浊毒留滞关节。', diet: '薏米赤小豆汤、芹菜汁、玉米须茶、冬瓜汤', avoid: '海鲜、啤酒、动物内脏、浓肉汤、火锅', life: '多喝水（每日2000ml+），低嘌呤饮食，控制体重' },
  fengshi: { name: '风湿/类风湿倾向', emoji: '🔵', symptoms: ['关节晨僵', '遇冷加重', '游走性疼痛', '肢体沉重'], desc: '风寒湿邪痹阻经络，气血运行不畅。', diet: '当归生姜羊肉汤、薏米粥、桂枝茶', avoid: '寒凉食物、冷水、潮湿环境', life: '保暖避寒，适度关节活动，热敷缓解' },
  shimian: { name: '失眠倾向', emoji: '⚪', symptoms: ['入睡困难', '易醒多梦', '白天疲倦', '心烦焦虑'], desc: '心脾两虚或肝火扰心，神不安舍。', diet: '酸枣仁百合汤、桂圆莲子粥、小米红枣粥', avoid: '咖啡浓茶（下午后）、睡前刷手机、过饱', life: '固定作息时间，睡前泡脚，避免睡前兴奋' },
  pilao: { name: '慢性疲劳倾向', emoji: '🟤', symptoms: ['持续疲倦', '注意力下降', '怎么睡都不够', '动力不足'], desc: '气血亏虚，脾肾不足，精力化生无源。', diet: '黄芪党参炖鸡、红枣枸杞茶、山药薏米粥', avoid: '过度劳累、熬夜、久坐不动', life: '劳逸结合，适度运动，午间小憩' },
  piwei: { name: '脾胃虚弱倾向', emoji: '🟢', symptoms: ['腹胀', '大便稀溏', '食欲差', '面色萎黄'], desc: '脾失健运，胃纳不佳，气血生化不足。', diet: '山药莲子粥、四神汤、小米南瓜粥', avoid: '生冷寒凉、油腻难消化、暴饮暴食', life: '少食多餐，细嚼慢咽，饭后散步' },
  qianlie: { name: '前列腺问题倾向', emoji: '🔷', symptoms: ['尿频尿急', '夜尿多', '排尿无力', '会阴坠胀'], desc: '肾气不固，湿热下注，膀胱气化不利。', diet: '南瓜子粥、枸杞山药汤、冬瓜薏米汤、番茄炒蛋', avoid: '久坐、憋尿、辛辣酒、冷饮', life: '避免久坐（每小时起身），温水坐浴，适度运动' },
  pifu: { name: '皮肤问题倾向', emoji: '🩹', symptoms: ['皮肤瘙痒', '起疹反复', '干燥脱屑', '遇热加重'], desc: '血虚风燥或湿热蕴肤，肌肤失养。', diet: '银耳百合羹、绿豆薏米汤、黑芝麻核桃粥、土茯苓煲汤', avoid: '辛辣海鲜、酒、热水烫洗、化纤衣物', life: '保湿润肤，避免搔抓，穿纯棉宽松衣物' },
  xueye: { name: '血液循环问题倾向', emoji: '🫀', symptoms: ['手脚冰凉', '肢体麻木', '青筋凸起', '蹲起头晕'], desc: '气虚血瘀，寒凝经脉，血行不畅。', diet: '当归生姜羊肉汤、山楂红糖水、黑木耳炒洋葱、桂圆红枣茶', avoid: '久坐不动、寒凉收引、紧身衣物、吸烟', life: '每日有氧运动30分钟，睡前泡脚，避免久站久坐' }
};

// 健康测评状态
let _healthTestState = {
  phase: 'start',
  mode: '',
  questions: [],
  currentIndex: 0,
  selectedAnswer: -1,
  answers: [],
  result: null,
  testCount: 0,
  scanPart: '',
  scanResult: ''
};

function initHealthTest() {
  fetch(API_BASE + '/api/tizhi-test/count')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (data && data.count) _healthTestState.testCount = data.count;
    })
    .catch(function() {});
}

function renderHealthTestPage() {
  var container = document.getElementById('test-container');
  if (!container) return;
  renderHealthTestStart(container);
}

function renderHealthTestStart(container) {
  _healthTestState.phase = 'start';
  _healthTestState.mode = '';
  _healthTestState.questions = [];
  _healthTestState.currentIndex = 0;
  _healthTestState.answers = [];
  _healthTestState.result = null;

  var count = _healthTestState.testCount || 1286;

  container.innerHTML =
    '<div class="test-page">' +
      '<div class="test-start-icon">🌿</div>' +
      '<div class="test-start-title">测测你的健康</div>' +
      '<div class="test-start-desc">答题3分钟<br>了解自己的身体，才能对症养生</div>' +
      '<button class="test-start-btn" onclick="startHealthQuiz(\'tizhi\')">📝 体质测评（九种体质）</button>' +
      '<button class="test-start-btn symptom" onclick="startHealthQuiz(\'symptom\')">⚠️ 症状自评（三高/痛风/风湿等）</button>' +
      '<div class="test-start-tip">已有 ' + count + ' 人完成测评</div>' +
    '</div>';
}

// AI拍照扫描（支持多张 + 取消后可重拍）
function startHealthScan(part) {
  var container = document.getElementById('test-container');
  if (!container) return;

  _healthTestState.phase = 'scanning';
  _healthTestState.scanPart = part;

  container.innerHTML =
    '<div class="test-page">' +
      '<div class="test-scan-preview">' +
        '<div class="test-scan-placeholder">📷 请选择 ' + part + ' 照片（可多张）</div>' +
      '</div>' +
      '<div class="test-scan-status">' +
        '<div class="loading"></div>' +
        '<div>选择图片后AI自动分析...</div>' +
      '</div>' +
      '<button class="test-back-btn" onclick="renderHealthTestPage()" style="margin-top:12px;">← 取消，返回</button>' +
      '<input type="file" id="scan-image-input" accept="image/*" multiple style="display:none;">' +
    '</div>';

  setTimeout(function() {
    var input = document.getElementById('scan-image-input');
    if (input) {
      input.onchange = function(e) {
        var files = Array.from(e.target.files || []);
        if (files.length === 0) {
          // 取消后显示继续拍照按钮，不自动返回首页
          container.innerHTML =
            '<div class="test-page">' +
              '<div class="test-scan-preview">' +
                '<div class="test-scan-placeholder">📷 请选择 ' + part + ' 照片（可多张）</div>' +
              '</div>' +
              '<button class="test-scan-btn" onclick="startHealthScan(\'' + part + '\')" style="width:100%;margin-top:16px;">📷 重新拍照</button>' +
              '<button class="test-back-btn" onclick="renderHealthTestPage()" style="width:100%;margin-top:8px;">← 返回首页</button>' +
              '<input type="file" id="scan-image-input" accept="image/*" multiple style="display:none;">' +
            '</div>';
          return;
        }
        analyzeHealthPhotos(files, part);
      };
      input.click();
    }
  }, 100);
}

async function analyzeHealthPhotos(files, part) {
  var container = document.getElementById('test-container');
  if (!container) return;

  // 显示所有图片预览
  var previewHtml = files.map(function(f) {
    return '<img class="test-scan-image" src="' + URL.createObjectURL(f) + '" style="max-width:45%;max-height:120px;border-radius:12px;margin:4px;">';
  }).join('');

  container.innerHTML =
    '<div class="test-page">' +
      '<div class="test-scan-preview" style="flex-wrap:wrap;">' + previewHtml + '</div>' +
      '<div class="test-scan-status">' +
        '<div class="loading"></div>' +
        '<div>AI正在分析你的' + part + '（' + files.length + '张）...</div>' +
      '</div>' +
    '</div>';

  try {
    // 所有图片转base64
    var base64Promises = files.map(function(f) { return imageFileToBase64(f); });
    var base64Uris = await Promise.all(base64Promises);

    var prompts = {
      '舌苔': '请从中医角度分析这些舌苔照片：舌色、舌苔、舌形、齿痕等，判断体质倾向和可能的健康问题，给出食疗建议。',
      '面色': '请从中医角度分析这些面色照片：面色、光泽、唇色等，判断气血状况和体质倾向，给出食疗建议。',
      '皮肤': '请从中医角度分析这些皮肤照片：肤色、皮疹、干燥程度等，判断可能的体质问题和调理方向，给出食疗建议。',
      '患处': '请从中医角度分析这些照片中的症状表现，判断可能的健康问题，给出食疗调理建议。'
    };
    var prompt = prompts[part] || prompts['患处'];

    var resp = await fetch(API_BASE + '/api/chat/vision', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: prompt,
        images: base64Uris,
        user_id: getUserId()
      })
    });
    var data = await resp.json();
    var result = data.reply || '分析完成，建议咨询小麦获取详细方案。';

    _healthTestState.phase = 'scan-result';
    _healthTestState.scanResult = result;

    fetch(API_BASE + '/api/tizhi-test/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: getUserId(),
        mode: 'scan',
        result_key: part,
        result_name: 'AI拍照扫描-' + part,
        score: 0,
        answers: [result.substring(0, 500)]
      })
    }).catch(function() {});

    renderScanResult(container, part, result);

  } catch (err) {
    console.error('AI分析失败:', err);
    container.innerHTML =
      '<div class="test-page">' +
        '<div class="test-scan-status" style="color:#e74c3c;">⚠️ AI分析失败，请重试</div>' +
        '<button class="test-scan-btn" onclick="startHealthScan(\'' + part + '\')" style="width:100%;margin-top:12px;">🔄 重新拍照</button>' +
        '<button class="test-back-btn" onclick="renderHealthTestPage()" style="width:100%;margin-top:8px;">← 返回首页</button>' +
      '</div>';
  }
}

function renderScanResult(container, part, result) {
  container.innerHTML =
    '<div class="test-page">' +
      '<div class="test-result-card">' +
        '<div class="test-result-badge">📷</div>' +
        '<div class="test-result-title">AI分析：' + part + '</div>' +
        '<div class="test-scan-result-text">' + escapeHtml(result).replace(/\n/g, '<br>') + '</div>' +
      '</div>' +
      '<div class="test-result-actions">' +
        '<button class="test-scan-btn" onclick="startHealthScan(\'' + part + '\')" style="width:100%;">📷 继续拍照</button>' +
        '<button class="test-ask-btn" onclick="goAskXiaomaiScan()">💬 问小麦怎么调理</button>' +
        '<button class="test-share-btn" onclick="shareScanResult()">🖼️ 生成分享图</button>' +
        '<button class="test-back-btn" onclick="renderHealthTestPage()">🔄 重新测评</button>' +
      '</div>' +
      '<div class="test-result-tip">分享给朋友，一起养生 💚</div>' +
    '</div>';
}

function goAskXiaomaiScan() {
  var hint = '我刚用AI拍照扫描了' + _healthTestState.scanPart + '，分析结果：' + (_healthTestState.scanResult || '') + '\n请给我食疗调理方案';
  localStorage.setItem('som_tizhi_hint', hint);
  var chatBtn = document.querySelector('.nav-btn[data-tab="chat"]');
  if (chatBtn) chatBtn.click();
  setTimeout(function() {
    var input = document.getElementById('chat-input');
    if (input) {
      input.value = hint;
      sendMessage();
    }
  }, 500);
}

function imageFileToBase64(file) {
  return new Promise(function(resolve, reject) {
    var img = new Image();
    var url = URL.createObjectURL(file);
    img.onload = function() {
      URL.revokeObjectURL(url);
      var maxW = 1280;
      var w = img.width, h = img.height;
      if (w > maxW) { h = Math.round(h * maxW / w); w = maxW; }
      var canvas = document.createElement('canvas');
      canvas.width = w; canvas.height = h;
      var ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, w, h);
      resolve(canvas.toDataURL('image/jpeg', 0.8));
    };
    img.onerror = reject;
    img.src = url;
  });
}

// 答题测评
function startHealthQuiz(mode) {
  var questions = mode === 'tizhi' ? TIZHI_QUESTIONS : SYMPTOM_QUESTIONS;
  _healthTestState.phase = 'quiz';
  _healthTestState.mode = mode;
  _healthTestState.questions = questions;
  _healthTestState.currentIndex = 0;
  _healthTestState.selectedAnswer = -1;
  _healthTestState.answers = [];

  var container = document.getElementById('test-container');
  if (container) renderQuizQuestion(container);
}

function renderQuizQuestion(container) {
  var questions = _healthTestState.questions;
  var currentIndex = _healthTestState.currentIndex;
  var q = questions[currentIndex];
  var progress = ((currentIndex + 1) / questions.length * 100).toFixed(0);

  var optionsHtml = '';
  for (var i = 0; i < q.options.length; i++) {
    optionsHtml += '<div class="test-option' + (_healthTestState.selectedAnswer === i ? ' selected' : '') + '" onclick="selectQuizAnswer(' + i + ')">' + q.options[i] + '</div>';
  }

  container.innerHTML =
    '<div class="test-page">' +
      '<div class="test-quiz-progress">' +
        '<div class="test-quiz-progress-bar">' +
          '<div class="test-quiz-progress-fill" style="width:' + progress + '%"></div>' +
        '</div>' +
        '<div class="test-quiz-progress-text">' + (currentIndex + 1) + ' / ' + questions.length + '</div>' +
      '</div>' +
      '<div class="test-question-card">' +
        '<div class="test-question-text">' + q.q + '</div>' +
        '<div class="test-options">' + optionsHtml + '</div>' +
      '</div>' +
    '</div>';
}

function selectQuizAnswer(idx) {
  var currentIndex = _healthTestState.currentIndex;
  var questions = _healthTestState.questions;
  var newAnswers = _healthTestState.answers.slice();
  newAnswers[currentIndex] = idx;
  _healthTestState.selectedAnswer = idx;

  if (currentIndex < questions.length - 1) {
    _healthTestState.answers = newAnswers;
    _healthTestState.currentIndex = currentIndex + 1;
    _healthTestState.selectedAnswer = -1;
    var container = document.getElementById('test-container');
    if (container) renderQuizQuestion(container);
  } else {
    _healthTestState.answers = newAnswers;
    var container = document.getElementById('test-container');
    if (container) calcHealthResult(newAnswers, container);
  }
}

function calcHealthResult(answers, container) {
  var mode = _healthTestState.mode;
  var questions = _healthTestState.questions;
  var templates = mode === 'tizhi' ? TIZHI_RESULTS : SYMPTOM_RESULTS;
  var scores = {};

  questions.forEach(function(q, i) {
    var ansIdx = answers[i] || 0;
    var qScores = q.scores;
    for (var key in qScores) {
      if (!scores[key]) scores[key] = 0;
      scores[key] += qScores[key][ansIdx] || 0;
    }
  });

  var maxKey = '';
  var maxScore = -1;
  for (var key in scores) {
    if (scores[key] > maxScore) {
      maxScore = scores[key];
      maxKey = key;
    }
  }

  if (maxScore <= 1) {
    maxKey = mode === 'tizhi' ? 'pinghe' : 'piwei';
  }

  var result = templates[maxKey] || templates[Object.keys(templates)[0]];
  result.key = maxKey;
  result.score = maxScore;

  // 兼夹
  var sorted = Object.entries(scores).sort(function(a, b) { return b[1] - a[1]; });
  if (sorted.length > 1 && sorted[1][1] >= maxScore * 0.6) {
    var secondary = templates[sorted[1][0]];
    if (secondary) result.secondary = secondary.name;
  }

  _healthTestState.phase = 'result';
  _healthTestState.result = result;

  // 保存到后端
  fetch(API_BASE + '/api/tizhi-test/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: getUserId(),
      mode: mode,
      result_key: maxKey,
      result_name: result.name,
      score: maxScore,
      answers: answers
    })
  }).catch(function() {});

  renderQuizResult(container, result, mode);
}

function renderQuizResult(container, result, mode) {
  var emoji = result.emoji || '🌿';
  var symptomsHtml = result.symptoms.map(function(s) { return '<span class="test-symptom-tag">' + s + '</span>'; }).join('');

  container.innerHTML =
    '<div class="test-page">' +
      '<div class="test-result-card">' +
        '<div class="test-result-badge">' + emoji + '</div>' +
        '<div class="test-result-title">你是【' + result.name + '】</div>' +
        '<div class="test-result-symptoms">' + symptomsHtml + '</div>' +
        '<div class="test-result-desc">' + result.desc + '</div>' +
        '<div class="test-result-advice">' +
          '<div class="test-advice-title">🌾 小麦建议</div>' +
          '<div class="test-advice-diet">✅ 食疗：' + result.diet + '</div>' +
          '<div class="test-advice-avoid">❌ 忌口：' + result.avoid + '</div>' +
          '<div class="test-advice-life">🏠 起居：' + result.life + '</div>' +
          (result.secondary ? '<div class="test-advice-secondary">兼夹倾向：' + result.secondary + '</div>' : '') +
        '</div>' +
      '</div>' +
      '<div class="test-result-actions">' +
        '<button class="test-ask-btn" onclick="goAskXiaomaiResult()">💬 问小麦怎么调理</button>' +
        '<button class="test-share-btn" onclick="shareQuizResult()">🖼️ 生成分享图</button>' +
        '<button class="test-back-btn" onclick="renderHealthTestPage()">🔄 重新测评</button>' +
      '</div>' +
      '<div class="test-result-tip">分享给朋友，一起养生 💚</div>' +
    '</div>';
}

function goAskXiaomaiResult() {
  var result = _healthTestState.result;
  var mode = _healthTestState.mode;
  var hint;
  if (mode === 'tizhi') {
    hint = '我刚做了体质测评，结果是【' + result.name + '】\n'
      + '体质特征：' + result.desc + '\n'
      + '食疗建议：' + result.diet + '\n'
      + '忌口：' + result.avoid + '\n'
      + '起居建议：' + result.life
      + (result.secondary ? '\n兼夹倾向：' + result.secondary : '')
      + '\n请给我详细的食疗调理方案';
  } else {
    hint = '我刚做了症状自评，倾向【' + result.name + '】\n'
      + '症状表现：' + result.desc + '\n'
      + '食疗建议：' + result.diet + '\n'
      + '忌口：' + result.avoid + '\n'
      + '起居建议：' + result.life
      + (result.secondary ? '\n兼夹倾向：' + result.secondary : '')
      + '\n请给我详细的食疗调理方案';
  }
  localStorage.setItem('som_tizhi_hint', hint);
  var chatBtn = document.querySelector('.nav-btn[data-tab="chat"]');
  if (chatBtn) chatBtn.click();
  setTimeout(function() {
    var input = document.getElementById('chat-input');
    if (input) {
      input.value = hint;
      sendMessage();
    }
  }, 500);
}

// ========== 测评结果分享图（问题5） ==========
function generateTestShareImage(result, mode) {
  var W = 750, padding = 50;
  var canvas = document.createElement('canvas');
  var ctx = canvas.getContext('2d');
  var H = 1040;
  canvas.width = W; canvas.height = H;

  // 背景渐变
  var grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, '#f0f7f2'); grad.addColorStop(1, '#e3f0e8');
  ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);

  // 顶部绿条
  ctx.fillStyle = '#4a9d6e'; ctx.fillRect(0, 0, W, 12);

  // 标题
  ctx.textAlign = 'center';
  ctx.fillStyle = '#2c3e50'; ctx.font = 'bold 40px "PingFang SC", sans-serif';
  ctx.fillText('🌿 我的健康自测报告', W / 2, 80);

  // 体质/症状名
  ctx.fillStyle = '#4a9d6e'; ctx.font = 'bold 52px "PingFang SC", sans-serif';
  ctx.fillText((result.emoji || '🌿') + ' ' + result.name, W / 2, 160);

  // 症状标签
  ctx.font = '26px "PingFang SC", sans-serif'; ctx.fillStyle = '#666';
  ctx.fillText(result.symptoms.join(' · '), W / 2, 210);

  // 描述
  ctx.fillStyle = '#555'; ctx.font = '24px "PingFang SC", sans-serif';
  wrapCanvasText(ctx, result.desc, W / 2, 260, W - 100, 36);

  // 小麦建议白框
  var boxY = 330, boxH = 340;
  ctx.fillStyle = '#ffffff';
  roundRectPath(ctx, 40, boxY, W - 80, boxH, 20); ctx.fill();
  ctx.strokeStyle = '#4a9d6e'; ctx.lineWidth = 2;
  roundRectPath(ctx, 40, boxY, W - 80, boxH, 20); ctx.stroke();

  ctx.textAlign = 'left';
  ctx.fillStyle = '#4a9d6e'; ctx.font = 'bold 30px "PingFang SC", sans-serif';
  ctx.fillText('🌾 小麦建议', 70, boxY + 50);

  ctx.fillStyle = '#333'; ctx.font = '26px "PingFang SC", sans-serif';
  wrapCanvasTextLeft(ctx, '✅ 食疗：' + result.diet, 70, boxY + 100, W - 140, 38);
  wrapCanvasTextLeft(ctx, '❌ 忌口：' + result.avoid, 70, boxY + 190, W - 140, 38);
  wrapCanvasTextLeft(ctx, '🏠 起居：' + result.life, 70, boxY + 280, W - 140, 38);

  if (result.secondary) {
    ctx.fillStyle = '#999'; ctx.font = '22px "PingFang SC", sans-serif';
    ctx.fillText('兼夹倾向：' + result.secondary, 70, boxY + boxH - 15);
  }

  // 底部引导
  ctx.textAlign = 'center';
  ctx.fillStyle = '#4a9d6e'; ctx.font = 'bold 28px "PingFang SC", sans-serif';
  ctx.fillText('扫码问小麦，对症食疗 →', W / 2, 740);

  ctx.fillStyle = '#999'; ctx.font = '22px "PingFang SC", sans-serif';
  ctx.fillText('松麦SOM · 中医养生 · 有机生活', W / 2, 790);
  ctx.fillText('som.top · 养生文化参考，不构成医疗诊断', W / 2, 830);

  // 小程序码
  var qrImg = new Image();
  qrImg.onload = function() {
    var qrSize = 130;
    ctx.drawImage(qrImg, W / 2 - qrSize / 2, 860, qrSize, qrSize);
    showSharePreview(canvas.toDataURL('image/png'));
  };
  qrImg.onerror = function() {
    showSharePreview(canvas.toDataURL('image/png'));
  };
  qrImg.src = '/public/qrcode.jpg';
}

function wrapCanvasText(ctx, text, x, y, maxWidth, lineHeight) {
  var line = '';
  for (var i = 0; i < text.length; i++) {
    var testLine = line + text[i];
    if (ctx.measureText(testLine).width > maxWidth && line) {
      ctx.fillText(line, x, y); line = text[i]; y += lineHeight;
    } else { line = testLine; }
  }
  ctx.fillText(line, x, y);
}

function wrapCanvasTextLeft(ctx, text, x, y, maxWidth, lineHeight) {
  var line = '';
  for (var i = 0; i < text.length; i++) {
    var testLine = line + text[i];
    if (ctx.measureText(testLine).width > maxWidth && line) {
      ctx.fillText(line, x, y); line = text[i]; y += lineHeight;
    } else { line = testLine; }
  }
  ctx.fillText(line, x, y);
}

function roundRectPath(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

// 测评结果分享按钮处理
function shareQuizResult() {
  var result = _healthTestState.result;
  var mode = _healthTestState.mode;
  if (result) generateTestShareImage(result, mode);
}

function shareScanResult() {
  var part = _healthTestState.scanPart || '舌苔';
  var scanText = _healthTestState.scanResult || '';
  // 扫描结果用通用分享图
  generateShareImage('📷 AI拍照扫描：' + part + '\n\n' + scanText.substring(0, 600));
}
