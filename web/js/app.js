// SOM 松麦 - 前端逻辑

// API地址：同域部署时用相对路径，跨域时修改此处
const API_BASE = '';

// ========== 初始化 ==========

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();

    // 2026-09-29 小蕊补回：微信菜单路径路由（被 13bc7d81 备份覆盖时丢失）
    // 菜单跳转 som.top/products、/yangshenggu、/profile 时自动定位到对应 tab
    var _path = window.location.pathname;
    var _tabMap = {'/products': 'products', '/yangshenggu': 'yangshenggu', '/profile': 'profile'};
    if (_tabMap[_path]) {
        switchTab(_tabMap[_path]);
    }
    initChat();
    initHealthTest();
    initProductSearch();
    loadCategories();
    initProfile();
    loadJieqi();
    loadEyeExercise();
    loadTizhiGrid();
    loadYaoshiList();
    initScrollToTop();
});

// 2026-10-15 中华要求: 一键到顶按钮(右下角↑, 滚动过阈值才显示)
// 页面主滚动容器是 .app(100vh + overflow:hidden, 内部 .main overflow-y:auto), 不是 window。
// 之前监 window.scroll 永远不触发 → 按钮从不显示(中华反馈"没出来"的根因)。
function initScrollToTop() {
    var btn = document.getElementById('scroll-to-top');
    if (!btn) return;
    var THRESHOLD = 300; // 滚过 300px 才显示
    function getScroller() {
        // 主滚动容器: <main class="main">(flex 布局 100vh, 内部 overflow-y:auto)
        var main = document.querySelector('main.main') || document.querySelector('.main');
        return main || null;
    }
    function currentPos() {
        var sc = getScroller();
        if (sc) return sc.scrollTop;
        return window.pageYOffset || document.documentElement.scrollTop || 0;
    }
    function onScroll() {
        var pos = currentPos();
        if (pos > THRESHOLD) btn.classList.add('show');
        else btn.classList.remove('show');
    }
    var scroller = getScroller();
    if (scroller) {
        scroller.addEventListener('scroll', onScroll, { passive: true });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    // 切换 tab 时刷新显隐(有的 tab 内容长/短不一)
    var _origSwitchTab = switchTab;
    switchTab = function(targetTab) {
        _origSwitchTab(targetTab);
        setTimeout(onScroll, 80);
    };
    // 切 tab 后滚动容器 scrollTop 归零, 但要等渲染完再算
    document.addEventListener('click', function(e) {
        if (e.target && e.target.matches && e.target.matches('.nav-btn')) {
            setTimeout(onScroll, 120);
        }
    }, true);
    btn.addEventListener('click', function() {
        var sc = getScroller();
        if (sc) {
            sc.scrollTo({ top: 0, behavior: 'smooth' });
        } else {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });
    onScroll(); // 初始状态
}

// 2026-10-12 小蕊修(中华反馈"乱码还在"): 浏览器 localStorage 里残留的历史脏 som_auth_user
// (旧版回调页无 charset, 中文昵称被写坏), 页面加载时检测到乱码就修好回写, 一次清干净。
(function _cleanAuthUserMojibake() {
    try {
        var raw = localStorage.getItem('som_auth_user');
        if (!raw) return;
        var u = JSON.parse(raw);
        if (!u || !u.nickname || typeof u.nickname !== 'string') return;
        if (!/[\u00c0-\u00ff]/.test(u.nickname)) return;  // 正常中文不动
        var fixed = _fixMojibake(u.nickname);
        if (fixed !== u.nickname) {
            u.nickname = fixed;
            localStorage.setItem('som_auth_user', JSON.stringify(u));
        }
    } catch(e) {}
})();

// ========== 导航切换 ==========

function switchTab(targetTab) {
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    navBtns.forEach(btn => {
        if (btn.dataset.tab === targetTab) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    var tabEl = document.getElementById(targetTab + '-tab');
    if (tabEl) {
        tabEl.classList.add('active');
    }

    if (targetTab === 'health-test') {
        renderHealthTestPage();
    }

    // 2026-10-16 小蕊修(中华反馈「我的收藏还是没有出来」):
    // 每次进「我」页重新拉一次收藏区(后端双写已存库, 刷新即见),
    // 不依赖页面加载时的一次性 initProfile —— 用户会话中登录/收藏后, 切回「我」也能看到。
    if (targetTab === 'profile') {
        try { loadProfile(); } catch (e) { console.warn('loadProfile 出错', e); }
    }
}

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
            // 2026-10-19 根治(中华反馈"两个微信清缓存重登, 收藏列表/分享图还是不出来"):
            // 点导航按钮「我」进 profile tab 时必刷收藏区。原 window.switchTab 钩子只拦
            // URL 路由 switchTab('profile') 那条路, 手动点按钮走的是这里的 addEventListener,
            // 不经过 window.switchTab → 收藏列表接口(/api/favorites)从不发出。
            if (targetTab === 'profile') {
                setTimeout(function() {
                    var _sec = document.getElementById('my-favorites-section');
                    if (_sec && isLoggedIn()) {
                        _sec.style.display = '';
                        try { loadFavoritesCard(); } catch (e) { console.warn('[nav-click-fav] 出错', e); }
                    }
                }, 50);
            }
        });
    });
    
    // 2026-09-29 小蕊加：URL 路由支持（?tab=xxx 或 #xxx 进页自动切 tab）
    // 服务号菜单点「有机好物」「我」等跳转 som.top?tab=products 时自动定位到对应页
    try {
        let targetTab = null;
        const params = new URLSearchParams(window.location.search);
        if (params.get('tab')) targetTab = params.get('tab');
        if (!targetTab && window.location.hash.startsWith('#')) {
            const h = window.location.hash.substring(1);
            if (['chat','products','yangshenggu','health-test','profile'].includes(h)) targetTab = h;
        }
        if (targetTab) {
            const targetBtn = document.querySelector('.nav-btn[data-tab="' + targetTab + '"]');
            if (targetBtn) targetBtn.click();
            // 2026-10-19 根治: URL 路由(?tab=profile / #profile)进「我」页, click() 已触发
            // nav-click 钩子(带 50ms 延迟), 这里不再重复; 但 click() 找不到按钮时兜底一次。
            // 2026-10-19 根治: URL 路由(?tab=profile / #profile)进「我」页兜底刷收藏区(80ms 晚于 nav-click 的 50ms, loadFavoritesCard 幂等可重复调)
            if (targetTab === 'profile') {
                setTimeout(function() {
                    var _sec = document.getElementById('my-favorites-section');
                    if (_sec && isLoggedIn()) {
                        _sec.style.display = '';
                        try { loadFavoritesCard(); } catch (e) {}
                    }
                }, 80);
            }
        }
    } catch (e) { /* 静默失败，不影响默认聊天页 */ }
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
    // 2026-10-27 小蕊: 输入框随文字自动长高(微信式), 空/少字时保持小, 最多长到 5 行
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 160) + 'px';
    });
    
    // 图片上传/拍照（支持多张，连续拍）
    uploadBtn.addEventListener('click', () => {
        imageInput.value = ''; // 重置，确保取消后能再次拍照
        // 移除 capture 属性，让系统文件选择器支持多选
        imageInput.removeAttribute('capture');
        imageInput.setAttribute('multiple', 'multiple');
        imageInput.click();
    });
    imageInput.addEventListener('change', handleImageSelectWithConfirm); // 2026-10-13 小蕊: 先过本人确认
    
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

// ========== 2026-10-13 小蕊加(中华要求): 拍舌照前确认是本人拍摄 ==========
// 一人一户微信, 不做多人建档。新对话第一次拍弹确认, 本 session 连拍不再弹。
let _ownerConfirmedSession = null;  // 已确认本人的 session_id

// ========== 2026-10-13 小蕊加(中华要求): 拍照前量化人脸比对(方案B前端侧) ==========
// 本人确认后, 调后端 /api/face/check: 提取人脸特征向量, 比对当前用户已存档向量
// 返回 matched=true(本人) / matched=false(像别人) / no_record(未建档)
// 不存原图, 只存向量; 用户可在"我"里一键删除自己的存档
async function checkFaceMatch(firstImageDataUrl) {
    const userId = getUserId();
    if (!userId) return { matched: false, no_record: true };
    try {
        const resp = await fetch(`${API_BASE}/api/face/check`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, image: firstImageDataUrl })
        });
        return await resp.json();
    } catch (e) { return { matched: false, no_record: true, error: String(e) }; }
}

function confirmOwnerBeforeCapture() {
    const sid = getSessionId();
    if (_ownerConfirmedSession === sid) return true;  // 本 session 已确认过
    const ok = confirm('请确认：现在拍照的是本人（当前账户主人）\n\n一人一户，档案只记录在你自己的健康数据里。\n如果不是本人，请让对方用自己的账户登录。\n\n点【确定】= 是本人，继续分析；点【取消】= 不是本人，不分析。');
    if (ok) {
        _ownerConfirmedSession = sid;
        showToast('已确认本人拍摄 📷');
    } else {
        showToast('已取消（未拍摄）', 'warn');
    }
    return ok;
}

// 选图后统一入口: 先过本人确认, 再真正处理图片; 本 session 首次拍时顺带跑人脸量化(方案B)
let _faceCheckedSession = null;  // 2026-10-13 小蕊: 本 session 是否已跑过人脸比对(连拍不重复跑)
function handleImageSelectWithConfirm(e) {
    if (!confirmOwnerBeforeCapture()) {
        // 用户取消: 清空 input, 不加入 pendingImages
        e.target.value = '';
        return;
    }
    handleImageSelect(e);
    runFaceCheckOncePerSession(e);
}

// 2026-10-14 小蕊修(中华反馈: 前端调不到 face/ensure):
// 旧代码在图片 onload 异步完成前就取 pendingImages[0], 连拍/快拍时 pendingImages 可能还没装好 → 静默跳过。
// 改成: 等 300ms 让 handleImageSelect 的 img.onload 把 pendingImages 填满, 再取第一张。
async function runFaceCheckOncePerSession(e) {
    const sid = getSessionId();
    if (_faceCheckedSession === sid) return;  // 本 session 已成功存过, 连拍不重复
    const userId = getUserId();
    if (!userId) return;
    // 等图片异步 onload 进 pendingImages (handleImageSelect 是异步的)
    await new Promise(function(r){ setTimeout(r, 300); });
    if (_faceCheckedSession === sid) return;  // 等期间已被锁
    if (pendingImages.length === 0) return;    // 300ms 后仍没图, 这次跳过, 下次拍照再试
    const firstImg = pendingImages[0];
    try {
        const resp = await fetch(`${API_BASE}/api/face/ensure`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, image: firstImg, remember: true })
        });
        const data = await resp.json();
        // 2026-10-13 小蕊修: 只有 ensure 真正成功(库里有记录)才锁本 session;
        // 失败/没写库就【不锁】, 下次拍照再试 —— 避免一次静默失败后本 session 永远不再存脸
        const ensured = (data && data.ensure && data.ensure.success === true);
        const chk = (data && data.check) || {};
        if (chk.matched && chk.best_user_id && chk.best_user_id !== userId) {
            showToast('⚠️ 这张脸更像已建档的另一个账户, 请确认是本人拍摄', 'warn');
        }
        if (ensured) {
            _faceCheckedSession = sid;  // 存成功才锁
        }
    } catch (err) {
        // 失败不锁, 下次再试; 不阻断舌苔分析
    }
}

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
            if (textEl) textEl.innerHTML = '<div class="loading"></div><div style="color:#999;font-size:13px;margin-top:8px">正在分析图片，请稍候…可能需要30-120秒（整人照/多图会久一点）</div>';
        }
    }, 30000);
    
    try {
        let response;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 95000); // 2026-10-17 中华铁律: 辨证总耗时不超过90秒, 前端95s兜底, 后端80s总预算先返回
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
            // 2026-10-16 小蕊改(中华反馈「方案二三商品没输出」): 按方案分组渲染
            if (typeof appendGroupedProducts === 'function') {
                appendGroupedProducts(data, msgId);
            }
            appendFollowUpSuggestions(hasImage);
            appendMessageActions(msgId, replyText);
            // 2026-10-13 小蕊改: 后端 /api/chat/vision 现在统一提取体质并写 tizhi_records;
        // 前端兜底仍保留(浏览器缓存旧版时也能存), 兜底词表加全 9 型 + 辨证常见名
        var imgTizhi = '';
        var tizhiMatch = replyText.match(/(?:体质倾向|综合判断|体质|属于)[：:]\s*([\u4e00-\u9fa5、,，]+(?:质)[\u4e00-\u9fa5、,，]*)/);
        if (tizhiMatch) imgTizhi = tizhiMatch[1].split(/[、,，]/).slice(0, 3).join('、');
        if (!imgTizhi) {
            for (var ti of ['脾虚湿盛质','气虚质','阳虚质','阴虚质','痰湿质','湿热质','血瘀质','特禀质','平和质']) {
                if (replyText.indexOf(ti) >= 0) { imgTizhi += imgTizhi ? '、' : ''; imgTizhi += ti; }
            }
        }
        saveChatRecord('[图片辨证x' + imagesToSend.length + '] ' + message, replyText, imgTizhi);
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
            
            // 2026-10-16 小蕊改(中华反馈「方案二三商品没输出」): 按方案分组渲染
            if (typeof appendGroupedProducts === 'function') {
                appendGroupedProducts(data, chatMsgDiv);
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
                        this.innerHTML = '❤️ 已收藏';
                        this.classList.add('favorited');
                        // 2026-10-16 小蕊改(中华反馈「收藏商品与辨证内容没出来」):
                        // 原来只写 localStorage(换机/清缓存就丢), 现在上报后端存库,
                        // 「我」页收藏区(辨证内容)才查得到。localStorage 兜底保留。
                        var userMsg = document.querySelector('#chat-messages .message.user:last-of-type');
                        var umText = userMsg ? userMsg.querySelector('.message-text').textContent : '';
                        var prodArr = (data.products && data.products.length) ? data.products : [];
                        var favData = {
                            type: 'chat_with_products',
                            userMessage: umText,
                            assistantReply: replyText,
                            products: prodArr,
                            time: new Date().toISOString()
                        };
                        try {
                            var lsFavs = JSON.parse(localStorage.getItem('som_favorites') || '[]');
                            lsFavs.push(favData);
                            localStorage.setItem('som_favorites', JSON.stringify(lsFavs));
                        } catch (e) { /* localStorage 满/禁用也不影响上报 */ }
                        var uid = getUserId();
                        if (uid) {
                            fetch(API_BASE + '/api/favorites/content/add', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({
                                    user_id: uid,
                                    title: (prodArr.length ? ('🛒 ' + prodArr.length + '款好物 · ') : '辨证') + (replyText || '').replace(/\s+/g, ' ').slice(0, 40) + (replyText && replyText.length > 40 ? '…' : ''),
                                    content: replyText,
                                    user_message: umText,
                                    products: prodArr,
                                    source: 'chat'
                                })
                            }).then(function(r) { return r.json(); })
                              .then(function(j) { if (!j || j.success === false) console.warn('收藏内容上报失败', j); })
                              .catch(function(e) { console.warn('收藏内容上报网络错误', e); });
                        }
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
            this.innerHTML = '❤️ 已收藏';
            this.classList.add('favorited');
            const userMsg = document.querySelector('#chat-messages .message.user:last-of-type');
            const umText = userMsg ? userMsg.querySelector('.message-text').textContent : '';
            const favData = {
                type: 'chat',
                userMessage: umText,
                assistantReply: replyText,
                time: new Date().toISOString()
            };
            try {
                var lsFavs2 = JSON.parse(localStorage.getItem('som_favorites') || '[]');
                lsFavs2.push(favData);
                localStorage.setItem('som_favorites', JSON.stringify(lsFavs2));
            } catch (e) { /* 兜底保留, 不炸 */ }
            // 2026-10-16 小蕊改(中华反馈「收藏商品与辨证内容没出来」): 辨证内容收藏上报后端存库
            var uid2 = getUserId();
            if (uid2) {
                fetch(API_BASE + '/api/favorites/content/add', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: uid2,
                        title: '辨证 · ' + (replyText || '').replace(/\s+/g, ' ').slice(0, 40) + (replyText && replyText.length > 40 ? '…' : ''),
                        content: replyText,
                        user_message: umText,
                        products: [],
                        source: 'chat'
                    })
                }).then(function(r) { return r.json(); })
                  .then(function(j) { if (!j || j.success === false) console.warn('收藏内容上报失败', j); })
                  .catch(function(e) { console.warn('收藏内容上报网络错误', e); });
            }
        }
    };

    const shareBtn = document.createElement('button');
    shareBtn.className = 'msg-action-btn';
    shareBtn.innerHTML = '🖼️ 分享图';
    shareBtn.onclick = function() { generateShareImage(replyText); };

    // 2026-10-27 小蕊: 收藏/分享按钮前加「复制」按钮, 一键复制整段辨证内容
    const copyBtn = document.createElement('button');
    copyBtn.className = 'msg-action-btn';
    copyBtn.innerHTML = '📋 复制';
    copyBtn.onclick = function() {
        var self = this;
        function done() {
            self.innerHTML = '✅ 已复制';
            setTimeout(function() { self.innerHTML = '📋 复制'; }, 1500);
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(replyText || '').then(done, function() { legacyCopy(); });
        } else {
            legacyCopy();
        }
        function legacyCopy() {
            var ta = document.createElement('textarea');
            ta.value = replyText || '';
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.select();
            try { document.execCommand('copy'); done(); } catch (e) { alert('复制失败，请手动选择内容复制'); }
            document.body.removeChild(ta);
        }
    };

    bar.appendChild(copyBtn);
    bar.appendChild(favBtn);
    bar.appendChild(shareBtn);
    content.appendChild(bar);
}

// ========== 我的收藏列表页 (2026-10-15 中华要求: 收藏的商品要随时能打开) ==========
// 入口: 「我」页用户卡片里的「♥ 我的收藏」按钮
// 数据: 服务器 product_favorites 表(随登录同步, 换设备也能看到)
// 打开: 每条收藏可点详情(多图轮播弹窗, 复用 openProductDetailModal) + 取消收藏
function openMyFavorites() {
    var userId = getUserId();
    if (!userId || userId === 'anonymous') {
        alert('请先在「我」页登录后再查看收藏');
        switchTab('profile');
        return;
    }
    // 移除旧弹窗
    var old = document.getElementById('favorites-modal');
    if (old) old.remove();

    var modal = document.createElement('div');
    modal.id = 'favorites-modal';
    modal.className = 'detail-overlay show';
    modal.style.zIndex = '9998';
    modal.innerHTML =
        '<div class="favorites-panel" onclick="event.stopPropagation()">' +
            '<div class="favorites-header">' +
                '<span><span style="color:#e8433d;font-size:1.1em;">♥</span> 我的收藏</span> +'
                '<button class="favorites-close" onclick="document.getElementById(\'favorites-modal\').remove()">✕</button>' +
            '</div>' +
            '<div class="favorites-list" id="favorites-list"><div class="favorites-loading">加载中...</div></div>' +
        '</div>';
    modal.onclick = function(e) { if (e.target === modal) modal.remove(); };
    document.body.appendChild(modal);

    fetch(API_BASE + '/api/favorites?user_id=' + encodeURIComponent(userId) + '&limit=100')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var list = document.getElementById('favorites-list');
            if (!list) return;
            var favs = data.favorites || [];
            if (!favs.length) {
                list.innerHTML = '<div class="favorites-empty">还没有收藏的商品<br><small>在商品详情的「♡ 收藏」点一下，下次就能在这里找到</small></div>';
                return;
            }
            var html = '';
            for (var i = 0; i < favs.length; i++) {
                var f = favs[i];
                var esc = function(s) { var d = document.createElement('div'); d.textContent = s == null ? '' : String(s); return d.innerHTML; };
                html +=
                    '<div class="fav-item">' +
                        '<img class="fav-image" src="' + esc(f.image || '') + '" onerror="this.style.visibility=\'hidden\'" alt="">' +
                        '<div class="fav-info">' +
                            '<div class="fav-title">' + esc(f.title || '未命名商品') + '</div>' +
                            '<div class="fav-price">¥' + esc(f.price || '0') + '</div>' +
                            '<div class="fav-shop">' + esc(f.shop_name || f.platform || '') + ' · ' + esc(f.created_at || '') + '</div>' +
                            '<div class="fav-actions">' +
                                '<button class="fav-btn fav-view" data-idx="' + i + '">查看</button>' +
                                '<button class="fav-btn fav-remove" data-item="' + esc(f.item_id) + '">取消收藏</button>' +
                            '</div>' +
                        '</div>' +
                    '</div>';
            }
            list.innerHTML = html;
            list.dataset.favs = JSON.stringify(favs);
            list.querySelectorAll('.fav-view').forEach(function(b) {
                b.onclick = function() {
                    var idx = parseInt(b.dataset.idx, 10);
                    var items = JSON.parse(list.dataset.favs || '[]');
                    var f = items[idx];
                    if (!f) return;
                    // 复用商品详情弹窗(多图轮播): 传完整 product 结构, images 走搜索接口回查
                    var fakeProduct = {
                        item_id: f.item_id,
                        title: f.title,
                        price: f.price,
                        image: f.image,
                        url: f.url,
                        app_url: (f.url || '').replace('https://', 'taobao://', 1),
                        platform: f.platform || 'taobao',
                        shop_name: f.shop_name,
                        images: []
                    };
                    // 收藏只有单张主图, 用收藏时的关键词(title)回查搜索接口补多图, 查不到就只展示主图
                    var _fillAndOpen = function() { showProductDetail(fakeProduct); };
                    var _kw = f.title || '';
                    if (f.item_id && _kw) {
                        fetch(API_BASE + '/api/products/search?keyword=' + encodeURIComponent(_kw) + '&platform=' + encodeURIComponent(f.platform || 'taobao') + '&limit=50')
                            .then(function(r) { return r.json(); })
                            .then(function(data) {
                                var found = null;
                                (data.items || []).forEach(function(p) {
                                    if (!found && String(p.item_id) === String(f.item_id)) found = p;
                                });
                                if (found) {
                                    // 2026-10-19 中华反馈"详情缺第一张": 首图 f.image 永远保留,
                                    // 再拼回查到的全部图, showProductDetail 首图豁免去重统一处理
                                    fakeProduct.images = (f.image ? [f.image] : []).concat(found.images || []);
                                    if (!fakeProduct.url && found.url) fakeProduct.url = found.url;
                                    if (!fakeProduct.app_url && found.app_url) fakeProduct.app_url = found.app_url;
                                }
                                _fillAndOpen();
                            })
                            .catch(_fillAndOpen);
                    } else {
                        _fillAndOpen();
                    }
                    var favModal = document.getElementById('favorites-modal');
                    if (favModal) favModal.remove();
                };
            });
            list.querySelectorAll('.fav-remove').forEach(function(b) {
                b.onclick = function() {
                    var item = b.dataset.item;
                    fetch(API_BASE + '/api/favorites/remove', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ user_id: userId, item_id: item })
                    }).then(function() {
                        b.closest('.fav-item').remove();
                        var empty = document.getElementById('favorites-empty');
                        var rest = list.querySelectorAll('.fav-item');
                        if (!rest.length) {
                            list.innerHTML = '<div class="favorites-empty">收藏都取消啦</div>';
                        }
                        refreshFavCount();
                    }).catch(function() { alert('取消失败, 请重试'); });
                };
            });
        })
        .catch(function() {
            var list = document.getElementById('favorites-list');
            if (list) list.innerHTML = '<div class="favorites-empty">加载失败, 请重试</div>';
        });
}

// 收藏入口上的数量角标: 登录后拉一次 (2026-10-15 改为读混排接口, 商品+辨证内容都算)
function refreshFavCount() {
    var userId = getUserId();
    var label = document.getElementById('fav-count-label');
    if (!userId || userId === 'anonymous' || !label) {
        if (label) label.textContent = '';
        return;
    }
    fetch(API_BASE + '/api/favorites/mixed?user_id=' + encodeURIComponent(userId) + '&page=1')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var n = data.total || 0;
            label.textContent = n ? '（共 ' + n + ' 件）' : '（共 0 件）';
        })
        .catch(function() {});
}

// ========== 2026-10-15 中华要求: 「我」页收藏 = 上下两个分类区(小麦辨证 / 有机商品), 不混编, 各自独立10条/页 ========== //
// 辨证内容区: fav-group-content + fav-content-list + fav-more-content (走 /api/favorites/content 独立分页)
// 商品区: fav-group-product + fav-product-list + fav-more-product (走 /api/favorites 独立分页)
// 每区「加载更多」只翻该区下一页, 互不影响; 某区 0 条时隐藏整区
var _favContentPage = 1, _favProductPage = 1;
// 2026-10-19 中华反馈「辨证内容与商品都加载非常慢」: 收藏接口加会话内 5s 缓存,
// 同一 user+page+size 短时间内重复进「我」页直接复用, 不再重复发 fetch。
var _favCache = {};
function _favCacheGet(key) {
    var c = _favCache[key];
    if (c && (Date.now() - c.t) < 5000) return c.data;
    return null;
}
function _favCacheSet(key, data) { _favCache[key] = { t: Date.now(), data: data }; }


var _favContentTotal = 0, _favProductTotal = 0;
// 2026-10-19 收藏 60s 会话缓存: 同 user 短时间内反复进「我」不重发请求
var _favLastLoadUser = null, _favLastLoadT = 0, _favLastLoaded = false;
// 2026-10-19 空提示根治: 两区各自标记"已加载完"(true/false), 都加载完且都为空才显示空提示
var _favContentDone = false, _favProductDone = false;
function _favMaybeShowEmpty() {
    if (!(_favContentDone && _favProductDone)) return;
    var hasAny = document.querySelectorAll('#fav-content-list .fav-card, #fav-product-list .fav-card').length;
    var emptyHint = document.getElementById('fav-empty-hint');
    var sec = document.getElementById('my-favorites-section');
    if (!hasAny && !emptyHint && sec) {
        emptyHint = document.createElement('p');
        emptyHint.id = 'fav-empty-hint';
        emptyHint.className = 'empty-hint';
        emptyHint.style.cssText = 'padding:10px 0;color:#999;font-size:13px;text-align:center;';
        sec.appendChild(emptyHint);
        emptyHint.textContent = '还没有收藏哦～在商品卡片或小麦回复上点「♡ 收藏」，这里就会显示';
    } else if (hasAny && emptyHint) {
        emptyHint.remove();
    }
}
var _favProductItems = []; // 已渲染商品(供「查看」回查多图/链接)

function favEsc(v) { var d = document.createElement('div'); d.textContent = v == null ? '' : String(v); return d.innerHTML; }

function loadFavoritesCard() {
    var userId = getUserId();
    // 2026-10-19 根治: 已登录但 userId 还是旧匿名号(user_ 开头非 u_)时, 强制切到正式账号再查,
    // 这是清缓存+微信登录后收藏区空、分享图出不来的根因: 数据在 u_ 账号, 查询却拿 user_ 匿名号, 查个空。
    if (isLoggedIn() && userId && userId.indexOf('u_') !== 0) {
        try { var _au = JSON.parse(localStorage.getItem('som_auth_user') || '{}');
            if (_au && _au.user_id && _au.user_id.indexOf('u_') === 0) userId = _au.user_id; } catch (e) {}
    }
    var section = document.getElementById('my-favorites-section');
    var gC = document.getElementById('fav-group-content');
    var gP = document.getElementById('fav-group-product');
    if (!section || !gC || !gP) {
        // 2026-10-17 小蕊诊断: DOM 缺收藏区节点(旧版 HTML 缓存)时打日志, 方便定位
        console.warn('[favorites] loadFavoritesCard: DOM 缺节点 section=' + !!section, 'gC=' + !!gC, 'gP=' + !!gP);
        return;
    }
    if (!userId || userId === 'anonymous') {
        section.style.display = 'none';
        return;
    }
    section.style.display = '';
    // 2026-10-19 中华反馈「每次回到我, 我的收藏数据都加载一次, 加载太慢」:
    // 60s 会话缓存: 短时间内反复进「我」页直接复用已加载数据, 不重发请求;
    // 只有首次进或超过 60s(可能删除/新增了)才真请求。
    // 2026-10-19 根治(日志实锤): 微信服务号菜单点进 ?tab=profile 是整页重载,
    // 内存 60s 缓存全部清零 → 每次进页都真发请求。改 localStorage 持久缓存:
    // 60s 内反复进「我」页直接跳过网络请求(秒开), 新增/删除收藏时清标记强制刷新。
    var _now = Date.now();
    try {
        var _lsMeta = JSON.parse(localStorage.getItem('som_fav_load') || 'null');
    } catch (e) {}
    // 2026-10-19 中华反馈「每次回到我都加载一次、还挂着空提示」根治:
    // 关键区分两种「回到我」:
    //  A) 同一次页面会话内反复切 tab(不重载): 内存 _favCache 有数据, 直接秒开不发请求
    //  B) 微信服务号菜单整页重载(?tab=profile 全新 URL): 内存 _favCache 已清零,
    //     必须重新拉数据(接口 0.006s, 很快), 拉完就地渲染, 杜绝空白/误显空提示。
    //  所以: 内存缓存命中(同会话切 tab)→ 秒开不请求; 否则(整页重载)→ 重新拉。
    var _memFresh = (_favLastLoadUser === userId && (_now - _favLastLoadT) < 600000 && _favLastLoaded);
    if (_memFresh) {
        // 同一会话内反复进「我」页: 内存缓存秒开, 不发网络请求, 顺手清残留空提示
        section.style.display = '';
        var _eh0 = document.getElementById('fav-empty-hint');
        if (_eh0 && document.querySelectorAll('#fav-content-list .fav-card, #fav-product-list .fav-card').length) _eh0.remove();
        var _c0 = _favCacheGet('c|' + userId + '|' + _favContentPage);
        var _p0 = _favCacheGet('p|' + userId + '|' + _favProductPage);
        if (_c0) _favRenderContent(userId, _c0, document.getElementById('fav-content-list'), document.getElementById('fav-group-content'));
        if (_p0) _favRenderProduct(_p0, document.getElementById('fav-product-list'), document.getElementById('fav-group-product'));
        _favContentDone = true; _favProductDone = true; _favMaybeShowEmpty();
        return;
    }
    // 整页重载后首次进「我」: 重新拉数据(快), 标记防并发重复请求
    _favLastLoadUser = userId; _favLastLoadT = _now;
    try { localStorage.setItem('som_fav_load', JSON.stringify({ u: userId, t: _now })); } catch (e) {}
    _favContentDone = false; _favProductDone = false;
    // 防抖: 整页重载可能触发多次 loadFavoritesCard(nav-click + url-route + fav-tab-hook),
    // 300ms 内重复调用直接忽略, 避免同一接口并发打 3 份
    if (loadFavoritesCard._inflight && _now - loadFavoritesCard._inflightT < 300) return;
    loadFavoritesCard._inflight = true; loadFavoritesCard._inflightT = _now;
    fetchFavoritesContent(false);
    fetchFavoritesProduct(false);
    setTimeout(refreshFavCount, 100);
    // 2026-10-17 小蕊修(中华反馈「我的收藏没出现商品与辨证内容」): 两区都加载完仍是空时,
    // 给一条明确的空状态提示, 不再整区消失看不出有没有数据
    // 2026-10-19 中华反馈「加载完数据后, 下面还挂着『还没有收藏哦』空提示」:
    // 原来 1.5s 兜底查不到 .fav-card 就显示空提示, 但接口可能还没返回(加载中)→ 误显示。
    // 根治: 不在 loadFavoritesCard 里定时误判; 改由两个 fetch 的 .then(数据到手)后
    // 调 _favMaybeShowEmpty(两区都返回且确实为空)才显示, 任一区有数据就移除空提示。
}

// ---- 辨证内容区(独立分页) ----
function fetchFavoritesContent(append, keepPage) {
    var userId = getUserId();
    var list = document.getElementById('fav-content-list');
    var group = document.getElementById('fav-group-content');
    if (!list || !group) return;
    // 2026-10-19 缓存: 翻页/刷新场景(append 或 keepPage)查 5s 缓存, 命中直接渲染不发请求
    var _cKey = 'c|' + userId + '|' + _favContentPage;
    var _cached = _favCacheGet(_cKey);
    // 2026-10-19 中华反馈「下一页点击没反应」: 缓存命中早退时把 append/keepPage 透传,
    // 否则翻页器不重绑/不滚回组顶, 列表点了没反应
    if (_cached) { _favRenderContent(userId, _cached, list, group, append, keepPage); return; }
    if (!append && !keepPage) {
        // 首次进收藏区: 清空占位
        _favContentPage = 1;
        list.innerHTML = '<p class="empty-hint">加载中…</p>';
        var pgC0 = document.getElementById('fav-content-pager'); if (pgC0) pgC0.style.display = 'none';
    }
    // 2026-10-19 中华反馈「点下一页先跑到底部再弹回, 头晕浪费时间」:
    // 翻页(keepPage)时不清空旧列表, 等新数据到位一次性整页替换, 杜绝『列表塌掉→整页变短→视觉跑到底→再弹回』。
    // 只在渲染完成时滚回辨证组顶, 且瞬间定位(auto), 不滑动画。
    fetch(API_BASE + '/api/favorites/content?user_id=' + encodeURIComponent(userId) + '&page=' + _favContentPage + '&page_size=5')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            _favCacheSet(_cKey, data);
            _favLastLoaded = true; _favLastLoadUser = userId; _favLastLoadT = Date.now();
            _favContentDone = true; _favMaybeShowEmpty();
            _favRenderContent(userId, data, list, group, append, keepPage);
        })
        .catch(function(e) {
            console.warn('[favorites] 内容收藏加载失败', e);
            if (!append) list.innerHTML = '<p class="empty-hint">加载失败，请刷新重试</p>';
        });
}
function _favRenderContent(userId, data, list, group, append, keepPage) {
    if (false) { // 旧的 catch 分支占位, 实际逻辑在 fetch 回调里
    }
    var _inner = function() {
            var items = data.items || [];
            _favContentTotal = data.total || 0;
            if (!append && !items.length && _favContentPage === 1) {
                group.style.display = 'none';
                var pgC = document.getElementById('fav-content-pager'); if (pgC) pgC.style.display = 'none';
                _favContentTotal = 0;
                return;
            }
            group.style.display = '';
            var html = '';
            items.forEach(function(it) {
                var preview = String(it.content || '').slice(0, 40);
                html +=
                    '<div class="fav-card fav-card-content" data-cid="' + favEsc(it.id) + '">' +
                        '<div class="fav-card-badge">🌿 小麦辨证</div>' +
                        '<div class="fav-card-body">' +
                            '<div class="fav-card-title">' + (favEsc(it.title || '') || '养生辨证分析') + '</div>' +
                            '<div class="fav-card-meta">' + favEsc((it.created_at || '').slice(0, 10)) + '</div>' +
                            '<div class="fav-card-preview">' + favEsc(preview) + '…</div>' +
                        '</div>' +
                        '<div class="fav-card-actions">' +
                            '<button class="fav-card-btn" data-act="toggle">展开</button>' +
                            '<button class="fav-card-btn" data-act="share">🖼️ 分享图</button>' +
                            '<button class="fav-card-btn fav-card-remove" data-act="rm-c" data-id="' + favEsc(it.id) + '">删除</button>' +
                        '</div>' +
                        '<div class="fav-card-detail fav-card-detail-md" style="display:none;">' + mdToHtml(String(it.content || '')) + '</div>' +
                    '</div>';
            });
            // 2026-10-19 中华要求「学体质记录那种翻页器, 辨证与商品各自独立」:
            // 上一页 / 第X页共Y页 / 下一页, 5 条/页, 整页替换(不追加)
            list.innerHTML = html;
            var totalPagesC = data.total_pages || 1;
            if (_favContentPage > totalPagesC) _favContentPage = Math.max(1, totalPagesC);
            renderFavPager('fav-content-pager', _favContentPage, totalPagesC, function(d) {
                _favContentPage += d;
                fetchFavoritesContent(false, true);
            });
            bindFavContentEvents(list);
            // 2026-10-19 中华反馈「小麦辨证点下一页跑到有机商品末尾」:
            // 辨证组在商品区上方, 翻页后列表变长, 视口可能停在商品区。
            // 翻页(keepPage)后滚回辨证组顶部, 让用户看到辨证内容。
            if (keepPage) {
                // 瞬间定位到组顶(不滑动画, 且只在组不在视口内才滚, 避免多余跳变)
                requestAnimationFrame(function() {
                    var top = group.getBoundingClientRect().top;
                    if (top < 0 || top > 200) group.scrollIntoView({ behavior: 'auto', block: 'start' });
                });
            }
    };
    _inner();
}

// ---- 商品区(独立分页) ----
function fetchFavoritesProduct(append, keepPage) {
    var userId = getUserId();
    var list = document.getElementById('fav-product-list');
    var group = document.getElementById('fav-group-product');
    if (!list || !group) return;
    // 2026-10-19 缓存: 同一 user+page 5s 内重复进「我」页直接复用, 不再重发请求(加载慢)
    var _pKey = 'p|' + userId + '|' + _favProductPage;
    var _pCached = _favCacheGet(_pKey);
    // 2026-10-19 同上: 翻页缓存命中早退, 透传 append/keepPage 保证翻页器重绑+滚回
    if (_pCached) { _favRenderProduct(_pCached, list, group, append, keepPage); return; }
    if (!append && !keepPage) {
        _favProductPage = 1;
        _favProductItems = [];
        list.innerHTML = '<p class="empty-hint">加载中…</p>';
        var pgP0 = document.getElementById('fav-product-pager'); if (pgP0) pgP0.style.display = 'none';
    }
    // 2026-10-19 翻页不清空旧列表, 数据到位整页替换, 杜绝先塌底再弹回(头晕)
    fetch(API_BASE + '/api/favorites?user_id=' + encodeURIComponent(userId) + '&page=' + _favProductPage + '&page_size=5')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            _favCacheSet(_pKey, data);
            _favLastLoaded = true; _favLastLoadUser = userId; _favLastLoadT = Date.now();
            _favProductDone = true; _favMaybeShowEmpty();
            _favRenderProduct(data, list, group, append, keepPage);
        });
}
function _favRenderProduct(data, list, group, append, keepPage) {
    var _pInner = function() {
            var items = data.favorites || data.items || [];
            var total = (typeof data.total !== 'undefined') ? data.total : items.length;
            var totalPages = (typeof data.total_pages !== 'undefined') ? data.total_pages : 1;
            _favProductTotal = total;
            var hasMore = _favProductPage < totalPages;
            if (!append && !items.length && _favProductPage === 1) {
                group.style.display = 'none';
                var pgP = document.getElementById('fav-product-pager'); if (pgP) pgP.style.display = 'none';
                _favProductTotal = 0;
                return;
            }
            group.style.display = '';
            var html = '';
            items.forEach(function(it) {
                var iid = it.item_id || it.id;
                // 2026-10-16 小蕊修: image 字段历史脏数据(整串多图+转义引号)兜底取第一个URL
                var _favImg = String(it.image || '').trim();
                if (_favImg.indexOf('",') >= 0 || _favImg.indexOf('", ') >= 0) {
                    _favImg = _favImg.split('",')[0].trim().replace(/^[\u0022]+/, '');
                }
                if (_favImg.indexOf('http') !== 0) _favImg = '';
                // 2026-10-19 多图: 解析收藏行 images 列(JSON 数组串或数组), 点「查看」全轮播
                var _favImages = [];
                try {
                    var _rawImgs = it.images;
                    if (typeof _rawImgs === 'string' && _rawImgs) {
                        var _parsed = JSON.parse(_rawImgs);
                        if (Array.isArray(_parsed)) _favImages = _parsed;
                    } else if (Array.isArray(_rawImgs)) {
                        _favImages = _rawImgs;
                    }
                } catch (e) { /* 脏串兜底: 不炸, 回退回查补全 */ }
                _favImages = _favImages.filter(function(u){ return typeof u === 'string' && u.indexOf('http') === 0; });
                if (_favImages.length) it._images = _favImages;
                html +=
                    '<div class="fav-card fav-card-product">' +
                        '<img class="fav-card-img" src="' + favEsc(_favImg) + '" onerror="this.style.visibility=\'hidden\'" alt="">' +
                        '<div class="fav-card-body">' +
                            '<div class="fav-card-title">' + favEsc(it.title || '未命名商品') + '</div>' +
                            '<div class="fav-card-meta">¥' + favEsc(it.price || '0') + ' · ' + favEsc(it.shop_name || it.platform || '') + '</div>' +
                        '</div>' +
                        '<div class="fav-card-actions">' +
                            '<button class="fav-card-btn" data-act="view" data-id="' + favEsc(iid) + '">查看</button>' +
                            '<button class="fav-card-btn fav-card-remove" data-act="rm-p" data-id="' + favEsc(iid) + '">取消</button>' +
                        '</div>' +
                    '</div>';
            });
            // 2026-10-19 中华要求「学体质记录那种翻页器, 辨证与商品各自独立」: 整页替换
            list.innerHTML = html;
            _favProductItems = items;
            if (_favProductPage > totalPages) _favProductPage = Math.max(1, totalPages);
            renderFavPager('fav-product-pager', _favProductPage, totalPages, function(d) {
                _favProductPage += d;
                fetchFavoritesProduct(false, true);
            });
            bindFavProductEvents(list);
            // 商品区翻页后滚回商品组顶部
            if (keepPage) {
                requestAnimationFrame(function() {
                    var top = group.getBoundingClientRect().top;
                    if (top < 0 || top > 200) group.scrollIntoView({ behavior: 'auto', block: 'start' });
                });
            }
    };
    _pInner();
}

// 辨证内容卡片交互: 展开/分享图/删除
function bindFavContentEvents(list) {
    var userId = getUserId();
    list.querySelectorAll('[data-act="toggle"]').forEach(function(b) {
        b.onclick = function() {
            var card = b.closest('.fav-card-content');
            var detail = card.querySelector('.fav-card-detail');
            var open = detail.style.display !== 'none';
            detail.style.display = open ? 'none' : 'block';
            b.textContent = open ? '展开' : '收起';
        };
    });
    list.querySelectorAll('[data-act="share"]').forEach(function(b) {
        b.onclick = function() {
            var card = b.closest('.fav-card-content');
            var detail = card.querySelector('.fav-card-detail');
            // 2026-10-19 中华反馈「分享图内容与图片都没有」: detail 现在是 mdToHtml 渲染的
            // (h1/h2/li/table/strong), detail.textContent 会把标签文字连成一片、丢掉段落/表格结构。
            // 传 detail.innerHTML(服务端 _clean_text 会剥 HTML 标签+剥 markdown 符号+压缩空白+限量, 能消化 HTML 残留标签)
            // 2026-10-20 中华反馈「分享图排版全混乱」: textContent 把所有段落/表格压成一坨, 改回 innerHTML 服务端才能保段落结构
            var _raw = detail ? (detail.innerHTML || detail.textContent || '') : (b.closest('.fav-card').querySelector('.fav-card-title').textContent || '');
            generateShareImage(_raw);
        };
    });
    list.querySelectorAll('[data-act="rm-c"]').forEach(function(b) {
        b.onclick = function() {
            fetch(API_BASE + '/api/favorites/content?user_id=' + encodeURIComponent(userId) + '&id=' + encodeURIComponent(b.dataset.id), { method: 'DELETE' })
                .then(function() {
                    try { localStorage.removeItem('som_fav_load'); } catch (e) {}
                    var card = b.closest('.fav-card'); if (card) card.remove();
                    _favContentTotal = Math.max(0, _favContentTotal - 1);
                    var gl = document.getElementById('fav-content-list');
                    if (gl && !gl.querySelectorAll('.fav-card').length) document.getElementById('fav-group-content').style.display = 'none';
                    refreshFavCount();
                }).catch(function() { alert('删除失败, 请重试'); });
        };
    });
}

// 商品卡片交互: 查看(多图轮播回查)/取消
function bindFavProductEvents(list) {
    var userId = getUserId();
    list.querySelectorAll('[data-act="view"]').forEach(function(b) {
        b.onclick = function() {
            var item = _favProductItems.filter(function(x){ return String(x.item_id || x.id) === b.dataset.id; })[0];
            if (!item) return;
            var iid = item.item_id || item.id;
            // 2026-10-19 小蕊修(中华反馈"收藏商品详情没图"): 老收藏 images 列为空,
            // 点「查看」回查搜索接口也匹配不到(商品下架/关键词漂移) → 弹窗图空白。
            // 修: fakeProduct.images 至少包含首图 item.image(收藏时存的单张),
            // 保证弹窗轮播永远有 ≥1 张图; 收藏行自带多图则优先全量。
            var fakeProduct = {
                item_id: iid, title: item.title, price: item.price,
                image: item.image, url: item.url,
                app_url: String(item.url || '').replace('https://', 'taobao://', 1),
                platform: item.platform || 'taobao', shop_name: item.shop_name,
                images: (item._images && item._images.length ? item._images : []).concat(item.image || []).filter(Boolean)
            };
            // 老收藏(无自带多图)时, 回查搜索接口补全; 首图已兜底所以即使回查失败弹窗也有图
            var _open = function() { showProductDetail(fakeProduct); };
            if (fakeProduct.images.length > 1) {
                // 收藏行已有多图, 直接开弹窗(快, 不依赖搜索接口)
                _open();
            } else if (iid && (item.title || '')) {
                fetch(API_BASE + '/api/products/search?keyword=' + encodeURIComponent(item.title) + '&platform=' + encodeURIComponent(item.platform || 'taobao') + '&limit=50')
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        var found = null;
                        (data.items || []).forEach(function(p) { if (!found && String(p.item_id) === String(iid)) found = p; });
                        if (found) {
                            // 2026-10-19 中华反馈"详情缺第一张": 保留首图 item.image,
                            // 再拼回查到的全部图, 交给 showProductDetail 的"首图豁免去重"统一处理
                            var _base = item._images && item._images.length ? item._images.slice() : (item.image ? [item.image] : []);
                            var _all = _base.concat(found.images || []);
                            fakeProduct.images = _all.length ? _all : (item.image ? [item.image] : []);
                            if (found.app_url) fakeProduct.app_url = found.app_url;
                        }
                        _open();
                    })
                    .catch(_open);
            } else { _open(); }
        };
    });
    list.querySelectorAll('[data-act="rm-p"]').forEach(function(b) {
        b.onclick = function() {
            fetch(API_BASE + '/api/favorites/remove', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, item_id: b.dataset.id })
            }).then(function() {
                try { localStorage.removeItem('som_fav_load'); } catch (e) {}
                var card = b.closest('.fav-card'); if (card) card.remove();
                _favProductTotal = Math.max(0, _favProductTotal - 1);
                _favProductItems = _favProductItems.filter(function(x){ return String(x.item_id || x.id) !== b.dataset.id; });
                var gl = document.getElementById('fav-product-list');
                if (gl && !gl.querySelectorAll('.fav-card').length) document.getElementById('fav-group-product').style.display = 'none';
                refreshFavCount();
            }).catch(function() { alert('取消失败, 请重试'); });
        };
    });
}

// 各区「加载更多」独立翻页
// 2026-10-19 中华要求「5 条/页 + 下一页(替换, 不是加载更多追加)」: 点「下一页」翻到下一页, 替换当前列表

// 2026-10-19 中华要求: 收藏分页学「体质记录」那种翻页器(上一页/第X页共Y页/下一页), 辨证与商品各自独立
function renderFavPager(pagerId, page, totalPages, onNav) {
    var pager = document.getElementById(pagerId);
    if (!pager) return;
    totalPages = Math.max(1, totalPages | 0);
    if (page > totalPages) page = totalPages;
    if (totalPages <= 1) {
        // 只有一页, 隐藏整个翻页器(不显示按钮)
        pager.style.display = 'none';
        pager.innerHTML = '';
        return;
    }
    var html = '';
    html += '<button class="fav-pager-btn" ' + (page <= 1 ? 'disabled' : '') + ' data-d="-1">上一页</button>';
    html += '<span class="fav-pager-info">第 ' + page + ' / ' + totalPages + ' 页</span>';
    html += '<button class="fav-pager-btn" ' + (page >= totalPages ? 'disabled' : '') + ' data-d="1">下一页</button>';
    pager.style.display = '';
    pager.innerHTML = html;
    Array.prototype.forEach.call(pager.querySelectorAll('.fav-pager-btn'), function(b) {
        b.onclick = function() {
            if (b.disabled) return;
            onNav(parseInt(b.dataset.d, 10));
        };
    });
}

(function hookFavMore() {
    document.addEventListener('DOMContentLoaded', function() {
        var mc = document.getElementById('fav-more-content');
        var mp = document.getElementById('fav-more-product');
        if (mc) mc.onclick = function() { _favContentPage += 1; fetchFavoritesContent(false); };
        if (mp) mp.onclick = function() { _favProductPage += 1; fetchFavoritesProduct(false); };
    });
})();

// 2026-10-16 小蕊删: 原 hookFavoritesCard 把 loadFavoritesCard 挂到 window.updateProfileCard,
// 但 updateProfileCard 全项目从未定义/调用, hook 永远不触发 → 收藏区不出现。
// 已改由 loadProfile() 直接调用(见 loadProfile 末尾)。

// 2026-10-19 小蕊修: 原 edit 失误把整段收藏系统嵌进 appendMessageActions 函数体内 →
// loadFavoritesCard 等 8 个函数不在全局作用域, loadProfile/switchTab/nav-click 调用全部
// ReferenceError, 收藏区永远不出现、不发起 fetch。已把收藏函数提回顶层, appendMessageActions
// 还原为纯按钮追加逻辑。

// 2026-10-16 小蕊重写(中华反馈「微信里不能分享」):
// 原实现用 canvas 画分享图, 但微信 WebView 里只要画过跨域图(淘宝/天猫商品图)
// canvas 就被污染, toDataURL() 直接抛 SecurityError → 分享图弹不出来, 微信里点不动。
// 改服务端渲染: POST 文本到 /api/share/content-image, 后端 Pillow 出 PNG 回传,
// 前端只回显, 永远绕开跨域。普通浏览器也走同一通道, 模板与原来一致。
function generateShareImage(text) {
    showShareLoading();
    // 2026-10-17 修(中华反馈「图片分享生成太慢, 一直默默加载卡住」):
    // 原来 loading 遮罩只有「正在生成分享图…」一句, 没超时兜底、没进度感知,
    // 后端 Pillow 渲染大图/拉商品图偶尔要 3~6s, 微信里用户就以为卡死。现在:
    // (1) 45s 强制兜底: 超时自动关遮罩+提示; (2) 文案写明大概要多久。
    var _shareTimer = setTimeout(function() {
        removeShareLoading();
        alert('分享图生成超时了(超过45秒), 请重试; 也可以长按商品图片直接保存');
    }, 45000);
    fetch(API_BASE + '/api/share/content-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: String(text == null ? '' : text) })
    })
        .then(function(r) {
            if (!r.ok) throw new Error('render failed');
            // 2026-10-16 小蕊改(中华反馈「分享图不能用微信分享」):
            // 后端 X-Share-Url 返回 http 直链, <img src> 指向 http URL——
            // 微信 WebView 里 http 图片才能长按保存, data URL 长按不出保存菜单。
            var shareUrl = r.headers.get('X-Share-Url');
            if (shareUrl) {
                showSharePreview(API_BASE + shareUrl);
                // 2026-10-17 小蕊修: 必须返回字符串! 原来 return undefined 会掉进下面
                // FileReader.readAsDataURL(undefined) 抛 TypeError → 误报「生成失败」
                return API_BASE + shareUrl;
            }
            return r.blob();
        })
        .then(function(blobOrUrl) {
            if (typeof blobOrUrl === 'string') return; // 已走 http 直链
            var reader = new FileReader();
            reader.onloadend = function() { showSharePreview(reader.result); };
            reader.readAsDataURL(blobOrUrl);
        })
        .catch(function(e) {
            console.error('辨证分享图生成失败:', e);
            alert('分享图生成失败: ' + (e && e.message ? e.message : '未知错误') + ', 请重试');
        })
        .then(function() {
            clearTimeout(_shareTimer); generateProductShareImage._inflight = false;
            removeShareLoading();
        });
}

// 商品分享图(2026-10-16 中华要求 v2: 同辨证模板, 正文换成全部商品图(最多4张)+商品名, 加淘宝二维码, 底部留松麦服务号码, 不放价格)
// product = { title, price, shop_name, image, images[], url, item_id, platform, app_url }
function generateProductShareImage(product) {
    // 2026-10-20 中华反馈「商品分享图生成失败」: 连点/多商品同时点 → 并发请求互相挤, 微信里
    // 一个没回来就再发一个, 容易 499 中断 + 失败弹窗乱飞。加进行中锁, 已有请求在飞就忽略点击。
    if (generateProductShareImage._inflight) { alert('分享图正在生成中, 请稍候'); return; }
    generateProductShareImage._inflight = true;
    var p = product || {};
    var buyUrl = p.url || p.app_url || '';
    if (!buyUrl || buyUrl === '#') buyUrl = 'https://item.taobao.com/item.htm?id=' + (p.item_id || '');
    // 收集全部商品图: image + images[] 去重, 最多4张(服务端再保险一次)
    var all = [];
    if (p.image) all.push(p.image);
    (p.images || []).forEach(function(u) { if (u && all.indexOf(u) < 0) all.push(u); });
    if (all.length > 5) all = all.slice(0, 5); // 2026-10-20 中华要求: 5张全出(竖排看得清), 上限从4改5
    showShareLoading();
    // 2026-10-17 修(同 generateShareImage): 加 45s 超时兜底 + 进度文案,
    // 避免微信里遮罩默默转圈被当成卡死
    var _shareTimer = setTimeout(function() {
        removeShareLoading();
        alert('分享图生成超时了(超过45秒), 请重试; 也可以长按商品图片直接保存');
    }, 45000);
    fetch(API_BASE + '/api/share/product-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title: p.title || '', price: String(p.price == null ? '' : p.price),
            shop: p.shop_name || '', image: p.image || '',
            images: all, buy_url: buyUrl
        })
    })
        .then(function(r) {
            if (!r.ok) throw new Error('render failed');
            // 同 generateShareImage: 优先 http 直链(X-Share-Url), 微信内长按保存才可靠
            var shareUrl = r.headers.get('X-Share-Url');
            if (shareUrl) {
                showSharePreview(API_BASE + shareUrl);
                // 2026-10-17 小蕊修: 必须返回字符串, 否则掉进 FileReader(undefined) 误报失败
                return API_BASE + shareUrl;
            }
            return r.blob();
        })
        .then(function(blobOrUrl) {
            if (typeof blobOrUrl === 'string') return;
            var reader = new FileReader();
            reader.onloadend = function() { showSharePreview(reader.result); };
            reader.readAsDataURL(blobOrUrl);
        })
        .catch(function(e) {
            console.error('商品分享图生成失败:', e);
            alert('商品分享图生成失败：' + (e && e.message ? e.message : '未知错误') + '。请重试，或长按商品卡片图片直接保存。');
        })
        .then(function() {
            clearTimeout(_shareTimer);
            removeShareLoading();
            generateProductShareImage._inflight = false;
        });
}

function showShareLoading() {
    // 2026-10-19 小蕊修: 原来 loading 和 preview 抢同一个 share-preview-mask,
    // 导致"正在生成"遮罩和弹窗互相覆盖。现在 loading 独立 id/class。
    var old = document.getElementById('share-loading-mask');
    if (old) old.remove();
    var mask = document.createElement('div');
    mask.id = 'share-loading-mask';
    mask.className = 'share-preview-mask';
    // 2026-10-17 修: 原来只一句「正在生成分享图…」, 用户不知道要等多久以为卡死。
    // 改成: 标题 + 时长说明 + 动画圆点, 让用户知道在干活、正常要多久。
    mask.innerHTML =
        '<div class="share-preview-box">' +
            '<p style="padding:20px 10px 6px;color:#3a7d5c;font-size:15px;font-weight:600;">⏳ 正在生成分享图</p>' +
            '<p style="padding:0 10px 14px;color:#888;font-size:12px;">一般 3~6 秒就好, 最多约 30 秒; 超过 45 秒会自动提示重试</p>' +
            '<div style="display:flex;gap:8px;justify-content:center;padding-bottom:10px;">' +
                '<span style="width:10px;height:10px;border-radius:50%;background:#7bc49f;animation:shareDot 1s infinite 0s;"></span>' +
                '<span style="width:10px;height:10px;border-radius:50%;background:#7bc49f;animation:shareDot 1s infinite .2s;"></span>' +
                '<span style="width:10px;height:10px;border-radius:50%;background:#7bc49f;animation:shareDot 1s infinite .4s;"></span>' +
            '</div>' +
        '</div>';
    // 动画 keyframes(只在分享 loading 期间用到, 动态注入不重复)
    if (!document.getElementById('share-dot-style')) {
        var st = document.createElement('style');
        st.id = 'share-dot-style';
        st.textContent = '@keyframes shareDot{0%,80%,100%{transform:scale(.6);opacity:.4}40%{transform:scale(1.15);opacity:1}}';
        document.head.appendChild(st);
    }
    document.body.appendChild(mask);
}

function removeShareLoading() {
    // 2026-10-19 小蕊修: 原来这里删的是 share-preview-mask, 和弹窗共用一个 id,
    // 结果"正在生成"遮罩删掉的瞬间, 已渲染的分享图弹窗也被一起删了 → 中华看到
    // "等了一会儿什么都没有"。现在只删独立的 loading 遮罩。
    var m = document.getElementById('share-loading-mask');
    if (m) m.remove();
}

function showSharePreview(imgSrc) {
    // 2026-10-16 小蕊改(中华反馈「分享图不能用微信分享」):
    // 微信 WebView 不支持 Web Share API, 长按保存 http 图片后手动发微信是唯一可靠路径。
    // 微信内: 隐藏"分享给朋友"按钮, 把长按保存提示放大加粗; 非微信: 保留原生分享。
    var isWx = /MicroMessenger/i.test(navigator.userAgent);
    var nativeBtn = isWx
        ? ''
        : '<button class="share-native-btn" onclick="nativeShareImage()">📤 分享给朋友</button>';
    var tipText = isWx
        ? '长按上面图片 → 选择「保存图片」→ 回到微信聊天里发给朋友 💚'
        : '长按图片保存，或点击下方按钮分享 💚';
    let mask = document.getElementById('share-preview-mask');
    if (mask) mask.remove();
    mask = document.createElement('div');
    mask.id = 'share-preview-mask';
    mask.className = 'share-preview-mask';
    mask.innerHTML =
        '<div class="share-preview-box">' +
          '<div class="share-preview-loading" id="share-preview-loading">🖼️ 分享图生成中…</div>' +
          '<img src="' + imgSrc + '" alt="分享图" style="display:none;' + (isWx ? 'border:2px dashed #07c160; padding:2px;' : '') + '">' +
          '<div class="share-preview-tip" style="' + (isWx ? 'font-size:14px; color:#07c160; font-weight:700;' : '') + '">' + tipText + '</div>' +
          '<div class="share-preview-btns">' +
            nativeBtn +
            '<a class="share-dl-btn" href="' + imgSrc + '" download="xiaomai-share.png">⬇️ 保存图片</a>' +
            '<button class="share-close-btn" onclick="document.getElementById(\'share-preview-mask\').remove()">关闭</button>' +
          '</div>' +
        '</div>';
    mask.addEventListener('click', (e) => { if (e.target === mask) mask.remove(); });
    document.body.appendChild(mask);
    // 2026-10-19 中华反馈「分享图弹窗弹出但内容没加载完」:
    // img 显示前先转圈, onload 后再显图, 避免"弹窗空了没图"
    // 2026-10-19 中华反馈「分享图一直在生成中」: 微信 WebView 里 <img> 的 onload 经常不触发
    // (http 直链 + 微信缓存策略), loading 态永远不关。改用 new Image() 预加载,
    // onload/onerror 明确回调 + 8s 轮询兜底 + 最终强制显图, 保证 loading 一定被关。
    var _ld0 = document.getElementById('share-preview-loading');
    var _done = false;
    var _reveal = function() {
        if (_done) return; _done = true;
        if (_ld0) _ld0.style.display = 'none';
        var _img = mask.querySelector('img');
        if (_img) _img.style.display = '';
    };
    var _fail = function() {
        if (_done) return; _done = true;
        if (_ld0) { _ld0.textContent = '🖼️ 分享图加载失败, 请关闭重试'; _ld0.style.display = ''; }
    };
    var _probe = new Image();
    _probe.onload = _reveal;
    _probe.onerror = _fail;
    _probe.src = imgSrc;
    // 8s 轮询兜底: 微信里 onload 没触发但图其实已缓存, 直接显
    var _pollCount = 0;
    var _poll = setInterval(function() {
        _pollCount++;
        if (_done || _pollCount > 8) { clearInterval(_poll); if (!_done) _reveal(); return; }
        // 探测图片是否已可显示(width>0 = 已加载)
        try { if (_probe.width > 0) { clearInterval(_poll); _reveal(); } } catch (e) {}
    }, 1000);
    // 10s 硬兜底: 无论如何关 loading(显图或提示), 不卡死
    setTimeout(function() { if (!_done) { clearInterval(_poll); _reveal(); } }, 10000);
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
    // 2026-10-16 小蕊修(中华反馈「表格输出框太窄就乱了」):
    // 小麦回复是 markdown(### 表格 | 加粗 * 列表 -), 原 escapeHtml 直接进气泡,
    // pre-line 下 | 符号原样显示 → 乱。现在助手气泡走 mdToHtml(表格转卡片化、加粗/列表/小标题美化),
    // 用户消息(输入内容)仍走 escapeHtml, 不受影响。
    let bodyHtml;
    if (isHtml) {
        bodyHtml = text;
    } else if (type === 'assistant' && typeof mdToHtml === 'function') {
        bodyHtml = mdToHtml(text);
    } else {
        bodyHtml = escapeHtml(text);
    }
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-text${type === 'assistant' ? ' md-text' : ''}">${bodyHtml}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    if (autoScroll) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    return messageId;
}

// 2026-10-16 小蕊加: 轻量 markdown → HTML(表格/加粗/小标题/列表/分隔线), 无外部依赖,
// 兼容老浏览器; 先整体转义再渲染标记, 防 XSS。表格转「响应式卡片表」: 表头深色,
// 窄屏(手机)自动变竖排卡片(每行一格), 解决「框太窄表格乱」问题。
function mdToHtml(text) {
    var s = String(text == null ? '' : text);
    // 1) 整体转义
    var esc = escapeHtml(s);
    // 2) 表格: 匹配连续的 | 行(含表头分隔行 |---|---|)
    esc = esc.replace(/(^|\n)((?:\|.*\|\n?)+)/g, function(all, lead, block) {
        var rows = block.trim().split('\n').filter(function(l) { return l.trim() !== ''; });
        if (rows.length < 2) return all;
        var tableRows = rows.map(function(l) {
            return l.trim().replace(/^\|/, '').replace(/\|$/, '').split('\|').map(function(c) { return c.trim(); });
        }).filter(function(cells) {
            // 表头分隔行(---)跳过
            return !cells.every(function(c) { return /^:?-+:?$/.test(c.replace(/[^-]/g, '')) && /^[-: ]+$/.test(c.replace(/\|/g, '')); });
        }).filter(function(cells) {
            return !(cells.length === 1 && /^:?-+:?$/.test(cells[0]));
        });
        if (tableRows.length < 2) return all;
        var head = tableRows[0];
        var html = '<div class="md-table-wrap"><table class="md-table"><thead><tr>';
        head.forEach(function(c) { html += '<th>' + c + '</th>'; });
        html += '</tr></thead><tbody>';
        tableRows.slice(1).forEach(function(cells) {
            html += '<tr>';
            for (var i = 0; i < head.length; i++) html += '<td>' + (cells[i] || '') + '</td>';
            html += '</tr>';
        });
        html += '</tbody></table></div>';
        return lead + html;
    });
    // 3) 小标题 ###/##/# → <div class="md-h3">等(保留层级感, 手机端不爆炸)
    esc = esc.replace(/^#{1,3}\s+(.+)$/gm, '<div class="md-h3">$1</div>');
    // 4) 加粗 **xxx** → <strong>(转义后 \*\* 仍匹配)
    esc = esc.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // 5) 斜体 _xxx_ → <em>(仅 ASCII 单词边界, 中文下划线不转, 避免误伤)
    esc = esc.replace(/(^|[^\w_])_([A-Za-z0-9]+)_(?=$|[^\w])/g, '$1<em>$2</em>');
    // 6) 列表行 "- xxx" / "· xxx" / "• xxx" / "1. xxx" → <li>, 收尾时自动补 <ul>/</ul>
    esc = esc.replace(/(^|\n)(\s*)([-·•*]|\d+[.、])\s+/g, function(all, lead, sp, marker) {
        if (/\d/.test(marker)) return lead + '<li class="md-ol">';
        return lead + '<li class="md-ul">';
    });
    // 7) 分隔线 --- 单独一行 → hr
    esc = esc.replace(/^\n\s*(?:---|\*\*\*)\s*\n/g, '\n<hr class="md-hr">\n');
    // 8) 剩余换行 → 保持(气泡 CSS pre-line 处理); 自动补 <ul>/</ul> 包 li
    esc = esc.split('\n').map(function(l) {
        var isLi = /^\s*<li/.test(l);
        var nextIsLi = false;
        return l;
    }).join('\n');
    // 简单补全: 在 <li 行组前补 <ul class="md-ul">, 组后补 </ul>
    var lines8 = esc.split('\n');
    var out8 = [];
    var inUl = false;
    for (var i8 = 0; i8 < lines8.length; i8++) {
        var l8 = lines8[i8];
        var isLi8 = /^\s*<li/.test(l8);
        var isUlOpen = /^\s*<ul/.test(l8);
        var isUlClose = /^\s*<\/ul/.test(l8);
        if (isLi8 && !inUl) { out8.push('<ul class="md-ul">'); inUl = true; }
        if (!isLi8 && !isUlOpen && inUl) { out8.push('</ul>'); inUl = false; }
        out8.push(l8);
    }
    if (inUl) out8.push('</ul>');
    esc = out8.join('\n');
    return esc;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    // 2026-10-15 小蕊修: div.innerHTML 只转义 & < > "，不转义单引号;
    // 但内联 onclick 的属性值用单引号包 JS 字符串, 标题含 ' 会炸整页 JS(SyntaxError)。
    // 追加单引号 → &#39;, 反斜杠原样保留即可(JS 字符串内 \\ 与 \ 等价转义)。
    return div.innerHTML.replace(/'/g, '&#39;');
}
// 2026-10-15 小蕊加: 内联事件处理器(onclick 单引号串)专用转义, 比 escapeHtml 更严格
function escapeJsAttr(text) {
    return String(text == null ? '' : text)
        .replace(/&/g, '&amp;')
        .replace(/'/g, '&#39;')
        .replace(/"/g, '&quot;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
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
                // 空结果友好提示
                const emptyMsg = document.createElement('div');
                emptyMsg.className = 'products-list';
                emptyMsg.innerHTML = '<div style="text-align:center;padding:40px 20px;color:#999;font-size:14px;line-height:1.8"><div style="font-size:40px;margin-bottom:12px">📦</div>没找到「' + currentKeyword + '」相关商品<br>数据源同步中，稍后再试，或换个关键词看看</div>';
                productsList.innerHTML = '';
                productsList.appendChild(emptyMsg);
                return;
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


// 2026-10-16 小蕊加(中华反馈「方案二三商品没输出」): 商品卡片按 方案一/二/三 分组渲染。
// product.plan = '方案一'/'方案二'/'方案三'/''(通用); 无 plan 字段的老数据全归「推荐好物」。
// 返回已 append 到 chatContainer 的容器 div。
function appendGroupedProducts(data, chatMsgId) {
    var chatContainer = document.getElementById('chat-messages');
    var products = (data && data.products) || [];
    if (!products.length) return;
    var afterEl = chatMsgId ? document.getElementById(chatMsgId) : null;

    function makeCard(product) {
        _productIndex++;
        _productCache[_productIndex] = product;
        var card = document.createElement('div');
        card.className = 'product-card';
        card.setAttribute('data-product-idx', _productIndex);
        card.innerHTML = `
            <img class="product-image" src="${escapeHtml(product.image)}" alt="${escapeHtml(product.title)}" onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23f5f7f6%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 fill=%22%237bc49f%22 font-size=%2220%22>暂无图片</text></svg>'">
            <div class="product-info">
                <div class="product-title">${escapeHtml(product.title)}</div>
                <div class="product-price">¥${product.price}</div>
                <div class="product-shop">${escapeHtml(product.shop_name || '')} · ${product.platform === 'taobao' ? '淘宝' : '京东'}</div>
            </div>
            <button class="product-card-share" data-share-idx="${_productIndex}" title="生成商品分享图（商品图+淘宝二维码）" aria-label="分享该商品">📤 分享图</button>
        `;
        return card;
    }

    // 按 plan 分组(保持首次出现顺序); 空 plan → 通用组
    var groups = {};
    var order = [];
    products.forEach(function(p) {
        var g = (p.plan || '推荐好物');
        if (!groups[g]) { groups[g] = []; order.push(g); }
        groups[g].push(p);
    });

    var hasPlan = order.some(function(g) { return g !== '推荐好物'; });
    var wrapper = document.createElement('div');
    wrapper.className = 'chat-products';

    if (hasPlan) {
        // 有方案分组: 每个方案一个小区块, 区块内小卡横排/网格
        order.forEach(function(g) {
            var sec = document.createElement('div');
            sec.className = 'plan-group';
            sec.innerHTML = '<div class="plan-group-title">🌿 ' + escapeHtml(g) + ' 食材</div>';
            var grid = document.createElement('div');
            grid.className = 'products-grid plan-group-grid';
            groups[g].forEach(function(p) { grid.appendChild(makeCard(p)); });
            sec.appendChild(grid);
            wrapper.appendChild(sec);
        });
    } else {
        wrapper.innerHTML = '<div class="chat-products-title">🛒 为你推荐以下有机好物：</div>';
        var grid = document.createElement('div');
        grid.className = 'products-grid chat-products-grid';
        products.forEach(function(p) { grid.appendChild(makeCard(p)); });
        wrapper.appendChild(grid);
    }

    if (afterEl) afterEl.after(wrapper);
    else chatContainer.appendChild(wrapper);
    return wrapper;
}

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
            <button class="product-card-share" data-share-idx="${_productIndex}" title="生成商品分享图（商品图+淘宝二维码）" aria-label="分享该商品">📤 分享图</button>
        </div>
        `;
    }).join('');
    
    if (append) {
        productsGrid.insertAdjacentHTML('beforeend', productHtml);
    } else {
        productsGrid.innerHTML = productHtml;
    }
}

// 事件委托：商品卡片点击 / 分享按钮(2026-10-16 中华要求: 商品也要能生成分享图, 商品图+淘宝二维码)
document.addEventListener('click', (e) => {
    // 卡片上的「📤 分享图」按钮: 先拦下来, 不触发详情弹窗
    var shareBtn = e.target.closest('.product-card-share');
    if (shareBtn) {
        e.stopPropagation();
        var sidx = parseInt(shareBtn.dataset.shareIdx, 10);
        var sp = _productCache[sidx];
        if (sp) generateProductShareImage(sp);
        return;
    }
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

function openProduct(webUrl, platform, itemId, appUrl) {
    if (!webUrl) return;
    
    // 判断是否在微信内
    var isWeixin = /MicroMessenger/i.test(navigator.userAgent);
    // 判断是否手机浏览器
    var isMobile = /Android|iPhone|iPad|iPod|webOS|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (platform === 'taobao' || !platform) {
        if (isWeixin) {
            // 微信内（服务号/小程序）：走淘口令方案
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
        } else if (isMobile) {
            // 2026-10-12 小蕊改(中华要求:手机浏览器点购买要干脆唤起淘宝APP, 不要绕H5)
            // 直接跳 app_url(taobao:// 协议), 淘宝APP 已装就立刻唤起并落到商品页; 没装则走淘宝H5兜底。
            var target = appUrl || '';
            if (!target || target === '#') {
                var u = webUrl.indexOf('//') === 0 ? 'https:' + webUrl : webUrl;
                target = u.replace(/^https:\/\//, 'taobao://');
            }
            window.location.href = target;
        } else {
            // 电脑端：直接跳转淘宝推广链接（click_url），淘宝会识别并跳转到商品页/引导下载APP
            // 2026-10-12 小蕊修复(中华报:电脑端"宝贝不存在")：之前误改为 item.taobao.com/item.htm?id=<淘口令>
            // 但 item_id 是淘宝联盟淘口令编码而非数字商品ID，导致淘宝报不存在；现恢复为以前的 window.open(webUrl)
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
    hint.innerHTML = '<span class="qr-hint-icon">📱</span> 打开手机淘宝APP，点"扫一扫"即可购买';
    modal.appendChild(hint);
    
    var container = document.createElement('div');
    container.id = 'qr-code-container';
    container.className = 'qr-code-container';
    modal.appendChild(container);
    
    var titleDiv = document.createElement('div');
    titleDiv.className = 'qr-title';
    titleDiv.textContent = title || '';
    modal.appendChild(titleDiv);
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // 生成二维码 - 先尝试 canvas（正常浏览器），失败则用纯 table（微信服务号）
    setTimeout(function() {
        var c = document.getElementById('qr-code-container');
        if (!c) return;
        c.innerHTML = '';
        try {
            if (typeof QRCode === 'undefined') {
                c.innerHTML = '<p style="color:#e85d2c;padding:40px;text-align:center;font-size:14px;">📱 二维码加载失败，请点击下方「复制链接」<br>然后在手机淘宝中粘贴打开</p>';
                return;
            }

            // 第一步：先用正常方式生成二维码
            var qr = new QRCode(c, {
                text: url,
                width: 200,
                height: 200,
                colorDark: '#000000',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.L
            });

            // 检查是否有 canvas
            var qrCanvas = c.querySelector('canvas');
            if (qrCanvas) {
                try {
                    var dataUrl = qrCanvas.toDataURL('image/png');
                    if (dataUrl && dataUrl.length > 100) {
                        // canvas 可用，正常浏览器，生成 img 并加保存按钮
                        c.innerHTML = '';
                        var img = document.createElement('img');
                        img.src = dataUrl;
                        img.alt = '二维码';
                        img.style.width = '200px';
                        img.style.height = '200px';
                        img.style.display = 'block';
                        img.style.margin = '0 auto';
                        c.appendChild(img);
                        var saveBtn = document.createElement('a');
                        saveBtn.href = dataUrl;
                        saveBtn.download = 'qrcode.png';
                        saveBtn.textContent = '⬇️ 保存二维码';
                        saveBtn.style.cssText = 'display:block;margin-top:10px;color:#4a9d6e;font-size:14px;text-decoration:none;font-weight:600;text-align:center;';
                        saveBtn.onclick = function(e) {
                            var link = document.createElement('a');
                            link.href = dataUrl;
                            link.download = 'qrcode.png';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        };
                        c.appendChild(saveBtn);
                        return;
                    }
                } catch(e1) {
                    // toDataURL 失败（微信内），继续 fallback
                }
            }

            // 第二步：canvas 不可用，清空容器，用纯 table 渲染
            c.innerHTML = '';
            var qrMatrix = qr._oQRCode;
            if (!qrMatrix) {
                c.innerHTML = '<p style="color:#e85d2c;padding:40px;text-align:center;font-size:14px;">📱 二维码生成失败，请点击下方「复制链接」<br>然后在手机淘宝中粘贴打开</p>';
                return;
            }
            var moduleCount = qrMatrix.getModuleCount();
            var cellSize = Math.floor(200 / moduleCount);

            var html = '<table style="border:0;border-collapse:collapse;margin:0 auto;">';
            for (var row = 0; row < moduleCount; row++) {
                html += '<tr>';
                for (var col = 0; col < moduleCount; col++) {
                    var dark = qrMatrix.isDark(row, col);
                    html += '<td style="border:0;padding:0;width:' + cellSize + 'px;height:' + cellSize + 'px;background-color:' + (dark ? '#000000' : '#ffffff') + ';"></td>';
                }
                html += '</tr>';
            }
            html += '</table>';
            c.innerHTML = html;

            // 保存按钮
            var saveBtn = document.createElement('a');
            saveBtn.textContent = '⬇️ 保存二维码';
            saveBtn.style.cssText = 'display:block;margin-top:10px;color:#4a9d6e;font-size:14px;text-decoration:none;font-weight:600;text-align:center;';
            saveBtn.onclick = function() {
                copyToClipboard(url, '二维码链接已复制');
            };
            c.appendChild(saveBtn);
        } catch(e) {
            c.innerHTML = '<p style="color:#e85d2c;padding:40px;text-align:center;font-size:14px;">📱 二维码生成失败，请点击下方「复制链接」<br>然后在手机淘宝中粘贴打开</p>';
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
    // 2026-10-17/18 小蕊修: 主图常常就是 images[0], 淘宝图床还存在同图不同URL(尺寸后缀不同),
    // 轮播出现"看起来重复"的两张 → 双重去重: URL 精确去重 + 图床指纹去重(去掉尺寸后缀/查询串比较)
    var _seenImgs = {};
    var _seenFp = {};
    var _fp = function(u) {
        // 取图床指纹: 去掉 ?查询串 与尺寸后缀(如 _60x60.jpg / !!6000000000976-0-... 图床规格标记)
        var s = String(u || '').split('?')[0];
        s = s.replace(/_\d+x\d+\.(jpg|jpeg|png|webp)$/i, '.jpg');
        s = s.replace(/\!\!/g, '');
        return s;
    };
    var _deduped = [];
    for (var _ai = 0; _ai < allImgs.length; _ai++) {
        var _u = allImgs[_ai], _f = _fp(_u);
        // 2026-10-19 小蕊修(中华反馈"详情弹窗第一张没放进去, 只有4张"):
        // 首图(_ai===0, 即 product.image)永远保留, 不参与指纹去重——
        // 淘宝首图常和 images[0] 是同图不同尺寸后缀(_600x600 vs _800x800),
        // 原去重把首图吞了导致详情少一张。只去重"非首图之间"的真重复。
        if (_ai > 0 && (_seenImgs[_u] || _seenFp[_f])) continue;
        _seenImgs[_u] = 1; _seenFp[_f] = 1;
        _deduped.push(_u);
    }
    allImgs.length = 0; allImgs.push.apply(allImgs, _deduped);
    var currentImgIdx = 0;

    overlay.innerHTML = `
        <button class="detail-close" onclick="closeProductDetail()">✕</button>
        <div class="detail-modal detail-modal-full">
            <div class="detail-img-wrap">
                <button class="detail-arrow detail-arrow-left" data-arrow="prev">‹</button>
                <img id="detail-main-img" src="${escapeHtml(imgSrc)}" alt="${escapeHtml(product.title || '')}" onclick="location.href='${escapeHtml(imgSrc)}'" style="cursor:pointer" onerror="this.parentElement.innerHTML+='<div class=\'detail-no-img\'>暂无图片</div>'">
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
                    <button class="detail-buy" onclick="openProduct('${escapeJsAttr(product.url || '#')}', '${escapeJsAttr(product.platform)}', '${escapeJsAttr(itemId)}', '${escapeJsAttr(product.app_url || '#')}')">点击购买</button>
                    <button class="detail-qr-btn" onclick="(function(){var u='${escapeJsAttr(product.url || '#')}'; if(!u||u==='#'){u='https://item.taobao.com/item.htm?id=${escapeJsAttr(itemId)}';} showQRCode(u, '${escapeJsAttr(product.title || '')}');})()" title="手机扫码购买">📱 用手机淘宝APP扫描购买</button>
                </div>
                <div class="detail-actions detail-actions-sub">
                    <button class="detail-fav" id="detail-fav-btn" data-item-id="${escapeHtml(itemId)}">♡ 收藏</button>
                    <button class="detail-fav detail-share" id="detail-share-btn" title="生成商品分享图（全部商品图+淘宝二维码）">📤 分享图</button>
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
                    <button class="detail-detail-btn" onclick="openProduct('${escapeJsAttr(detailUrl || '#')}', '${escapeJsAttr(product.platform)}', '${escapeJsAttr(itemId)}', '${escapeJsAttr(product.app_url || '#')}')">点击购买</button>
                    <button class="detail-detail-qr-btn" onclick="(function(){var u='${escapeJsAttr(detailUrl || '#')}'; if(!u||u==='#'){u='https://item.taobao.com/item.htm?id=${escapeJsAttr(itemId)}';} showQRCode(u, '${escapeJsAttr(product.title || '')}');})()" title="手机扫码购买">📱 用手机淘宝APP扫描购买</button>
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
        // 2026-10-17 小蕊修: 点缩略图时 e.target 常是内层 <img>(没有 data-thumb-idx),
        // 原来取不到 idx 就什么都不发生, 用户以为点了没反应; 改用 closest 找带属性的祖先
        var arrowEl = e.target.closest ? e.target.closest('[data-arrow]') : null;
        if (arrowEl) {
            var arrow = arrowEl.getAttribute('data-arrow');
            if (arrow === 'prev') { switchImg(currentImgIdx - 1); e.stopPropagation(); }
            else if (arrow === 'next') { switchImg(currentImgIdx + 1); e.stopPropagation(); }
            return;
        }
        var thumbEl = e.target.closest ? e.target.closest('[data-thumb-idx]') : null;
        if (thumbEl) { switchImg(parseInt(thumbEl.getAttribute('data-thumb-idx')) || 0); e.stopPropagation(); }
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
                    favBtn.textContent = '❤️ 已收藏';
                    favBtn.classList.add('favorited');
                }
            })
            .catch(() => {});
    }

    // 2026-10-16 小蕊修: 分享按钮原内联 onclick 里嵌 JSON.stringify(allImgs)(双引号炸 HTML 属性)
    // 且 allImgs 是闭包变量根本不在内联作用域里 → 一点就 ReferenceError, 错误越攒越多。
    // 改闭包直接绑定, 数据走变量不走内联字符串。
    // 2026-10-19 小蕊修(中华反馈"商品收藏点不动, 底部红色JS错误"): 原收藏按钮内联 onclick 里嵌
    // JSON.stringify(allImgs)(双引号炸 HTML 属性) → 解析报错。改闭包直接绑定, 与分享按钮同套路。
    const favBtn = document.getElementById('detail-fav-btn');
    if (favBtn) {
        favBtn.addEventListener('click', function(ev) {
            ev.stopPropagation();
            toggleFavorite(favBtn, itemId, product.title || '', String(product.price == null ? '' : product.price), imgSrc, detailUrl, product.platform || 'taobao', product.shop_name || '', allImgs);
        });
    }

    const shareBtn = document.getElementById('detail-share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', function(ev) {
            ev.stopPropagation();
            var shareProduct = {
                title: product.title || '',
                price: String(product.price == null ? '' : product.price),
                shop_name: product.shop_name || '',
                image: imgSrc,
                images: allImgs,
                url: detailUrl,
                app_url: product.app_url || '',
                item_id: itemId,
                platform: product.platform || 'taobao'
            };
            generateProductShareImage(shareProduct);
        });
    }

    saveProductBrowse(product.title || '', 1);
}

function closeProductDetail() {
    const existing = document.querySelector('.detail-overlay');
    if (existing) existing.remove();
    document.body.style.overflow = '';
}

// ========== 收藏功能 ==========

globalThis.toggleFavorite = function(btn, itemId, title, price, image, url, platform, shopName, images) {
    if (!itemId) return;
    var userId = getUserId();
    var isFav = btn.classList.contains('favorited');
    var _imgList = Array.isArray(images) ? images.filter(function(u){ return u && u.indexOf('http') === 0; }) : [];
    
    if (isFav) {
        fetch(API_BASE + '/api/favorites/remove', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user_id: userId, item_id: itemId})
        }).then(function() {
            try { localStorage.removeItem('som_fav_load'); } catch (e) {}
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
                shop_name: shopName || '',
                images: _imgList
            })
        }).then(function() {
            try { localStorage.removeItem('som_fav_load'); } catch (e) {}
            btn.classList.add('favorited');
            btn.textContent = '❤️ 已收藏';
        }).catch(function() {});
    }
};

// ========== 统一认证（全球手机号 + 邮箱） ==========

let _codeCooldown = 0;

function switchLoginChannel(channel) {
    document.querySelectorAll('.login-tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`.login-tab[data-channel="${channel}"]`).classList.add('active');
    document.getElementById('login-form-sms').style.display = channel === 'sms' ? 'flex' : 'none';
    document.getElementById('login-form-wechat').style.display = channel === 'wechat' ? 'flex' : 'none';
    document.getElementById('login-form-password').style.display = channel === 'password' ? 'flex' : 'none';
    document.getElementById('login-form-email').style.display = channel === 'email' ? 'flex' : 'none';
    hideLoginError();
}

// 密码登录
async function doPasswordLogin() {
    hideLoginError();
    const account = document.getElementById('password-account').value.trim();
    const password = document.getElementById('password-input').value;
    
    if (!account) { showLoginError('请输入账号'); return; }
    if (!password) { showLoginError('请输入密码'); return; }
    
    try {
        // 2026-10-12 中华: 四账户统一, 把匿名uid带过去, 后端合并匿名数据
        let anonUid = '';
        try { anonUid = localStorage.getItem('som_user_id') || ''; } catch(e) {}
        const resp = await fetch(`${API_BASE}/api/auth/login/password`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ account, password, anonymous_user_id: anonUid })
        });
        const data = await resp.json();
        if (data.success) {
            localStorage.setItem('som_auth_token', data.token);
            localStorage.setItem('som_auth_user', JSON.stringify(data.user));
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

// 账号绑定弹窗
var _emailCodeCooldown = 0;
function showBindAccountModal(type) {
    try {
    document.getElementById('bind-account-modal').style.display = 'flex';
    document.getElementById('bind-account-input').value = '';
    var _codeEl = document.getElementById('bind-email-code');
    if (_codeEl) _codeEl.value = '';
    var _btn = document.getElementById('send-bind-email-code-btn');
    if (_btn) _btn.textContent = '发送验证码';
    } catch(e) { alert('弹窗打开失败: ' + e.message + '。请下拉刷新页面后重试'); }
}
async function sendBindEmailCode() {
    const email = document.getElementById('bind-account-input').value.trim();
    if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { alert('请输入有效邮箱'); return; }
    const btn = document.getElementById('send-bind-email-code-btn');
    btn.disabled = true;
    try {
        const resp = await fetch(`${API_BASE}/api/auth/send-code`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ target: email, channel: 'email' })
        });
        const data = await resp.json();
        if (data.success) {
            showToast(data.message || '验证码已发送至邮箱');
            _emailCodeCooldown = 60;
            const t = setInterval(function() {
                _emailCodeCooldown--;
                if (_emailCodeCooldown <= 0) { clearInterval(t); btn.disabled = false; btn.textContent = '发送验证码'; }
                else btn.textContent = _emailCodeCooldown + 's';
            }, 1000);
            btn.textContent = '60s';
        } else {
            alert(data.error || data.detail || '发送失败');
            btn.disabled = false;
        }
    } catch(e) {
        alert('网络错误');
        btn.disabled = false;
    }
}
function hideBindAccountModal() {
    document.getElementById('bind-account-modal').style.display = 'none';
}

async function doBindAccount() {
    const account = document.getElementById('bind-account-input').value.trim();
    if (!account) { alert('请输入邮箱'); return; }
    const code = (document.getElementById('bind-email-code') || {}).value ? document.getElementById('bind-email-code').value.trim() : '';
    const userId = getUserId();
    try {
        const resp = await fetch(`${API_BASE}/api/auth/bind-account`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, account, account_type: 'email', code })
        });
        const data = await resp.json();
        if (data.success) {
            hideBindAccountModal();
            showToast('邮箱绑定成功！');
            loadUserAccount();
        } else {
            alert(data.error || data.detail || '绑定失败');
        }
    } catch (e) {
        alert('网络错误');
    }
}

// ========== 2026-10-12 小蕊加: 手机号绑定(中华要求: 账号绑定手机号, 发验证码) ==========
var _phoneCodeCooldown = 0;
var _smsUnconfigured = false;  // 短信通道未开通时免验证直接绑(临时)
function showBindPhoneModal() {
    try {
    document.getElementById('bind-phone-modal').style.display = 'flex';
    document.getElementById('bind-phone-input').value = '';
    document.getElementById('bind-phone-code').value = '';
    } catch(e) { alert('弹窗打开失败: ' + e.message + '。请下拉刷新页面后重试'); }
}
function hideBindPhoneModal() {
    document.getElementById('bind-phone-modal').style.display = 'none';
}
async function sendBindPhoneCode() {
    const phone = document.getElementById('bind-phone-input').value.trim();
    if (!/^1\d{10}$/.test(phone)) { alert('请输入11位手机号'); return; }
    const btn = document.getElementById('send-phone-code-btn');
    btn.disabled = true;
    try {
        const resp = await fetch(`${API_BASE}/api/auth/send-code`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ target: phone, channel: 'sms' })
        });
        const data = await resp.json();
        if (data.success) {
            showToast(data.message || '验证码已发送');
            _phoneCodeCooldown = 60;
            const t = setInterval(function() {
                _phoneCodeCooldown--;
                btn.textContent = _phoneCodeCooldown + 's';
                if (_phoneCodeCooldown <= 0) {
                    clearInterval(t);
                    btn.disabled = false;
                    btn.textContent = '发送验证码';
                }
            }, 1000);
        } else if ((data.error || '').indexOf('短信服务未配置') >= 0) {
            // 2026-10-12: 短信还没开通, 降级为免验证直接绑定(临时方案, 短信通了恢复验证)
            showToast('短信通道开通中, 本次直接绑定(免验证码)');
            document.getElementById('bind-phone-code').value = '';
            _smsUnconfigured = true;
            btn.disabled = false;
        } else {
            alert(data.detail || data.error || '发送失败');
            btn.disabled = false;
        }
    } catch(e) {
        alert('网络错误');
        btn.disabled = false;
    }
}
async function doBindPhone() {
    const phone = document.getElementById('bind-phone-input').value.trim();
    let code = document.getElementById('bind-phone-code').value.trim();
    if (!/^1\d{10}$/.test(phone)) { alert('请输入11位手机号'); return; }
    if (_smsUnconfigured) { code = 'DIRECT'; }  // 免验证模式
    else if (!code) { alert('请输入验证码'); return; }
    const userId = getUserId();
    try {
        const resp = await fetch(`${API_BASE}/api/auth/bind-phone`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, phone: phone, code: code })
        });
        const data = await resp.json();
        if (data.success) {
            hideBindPhoneModal();
            showToast('手机号绑定成功！');
            loadUserAccount();
        } else {
            alert(data.error || '绑定失败');
        }
    } catch(e) { alert('网络错误'); }
}
async function doUnbindPhone() {
    if (!confirm('解绑手机号后, 该手机号可绑到其他账号, 确定?')) return;
    const userId = getUserId();
    try {
        const resp = await fetch(`${API_BASE}/api/auth/unbind-account`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, account_type: 'phone' })
        });
        const data = await resp.json();
        if (data.success) { showToast('已解绑'); loadUserAccount(); }
        else alert(data.error || '解绑失败');
    } catch(e) { alert('网络错误'); }
}
async function doUnbindAccount() {
    if (!confirm('解绑邮箱账号后, 该邮箱可被其他人注册绑定, 确定?')) return;
    const userId = getUserId();
    try {
        const resp = await fetch(`${API_BASE}/api/auth/unbind-account`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, account_type: 'email' })
        });
        const data = await resp.json();
        if (data.success) { showToast('已解绑'); loadUserAccount(); }
        else alert(data.error || '解绑失败');
    } catch(e) { alert('网络错误'); }
}

function showBindPasswordModal() {
    try {
    document.getElementById('bind-password-modal').style.display = 'flex';
    document.getElementById('bind-password-input').value = '';
    document.getElementById('bind-password-confirm').value = '';
    } catch(e) { alert('弹窗打开失败: ' + e.message + '。请下拉刷新页面后重试'); }
}
function hideBindPasswordModal() {
    document.getElementById('bind-password-modal').style.display = 'none';
}

async function doBindPassword() {
    const password = document.getElementById('bind-password-input').value;
    const confirm = document.getElementById('bind-password-confirm').value;
    if (!password) { alert('请输入密码'); return; }
    if (password.length < 6) { alert('密码至少6位'); return; }
    if (password !== confirm) { alert('两次密码不一致'); return; }
    const userId = getUserId();
    try {
        const resp = await fetch(`${API_BASE}/api/auth/bind-password`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, password })
        });
        const data = await resp.json();
        if (data.success) {
            hideBindPasswordModal();
            showToast('密码设置成功！');
            loadUserAccount();
        } else {
            alert(data.error || data.detail || '设置失败');
        }
    } catch (e) {
        alert('网络错误');
    }
}

async function loadUserAccount() {
    const userId = getUserId();
    const token = localStorage.getItem('som_auth_token');
    if (!token) return;
    try {
        const resp = await fetch(`${API_BASE}/api/user/profile?user_id=${userId}`);
        const data = await resp.json();
        if (data.success && data.user) {
            const user = data.user;
            var emailEl = document.getElementById('binding-email');
            emailEl.textContent = user.email || '未绑定';  // 2026-10-15 中华反馈: 绑定页显示邮箱(email列), 不再显示账号名(account列)
            var unbindEmailBtn = document.getElementById('unbind-email-btn');
            if (unbindEmailBtn) unbindEmailBtn.style.display = user.email ? 'inline-block' : 'none';
            var phoneEl = document.getElementById('binding-phone');
            var unbindPhoneBtn = document.getElementById('unbind-phone-btn');
            if (user.phone) { phoneEl.textContent = user.phone; if (unbindPhoneBtn) unbindPhoneBtn.style.display = 'inline-block'; }
            else if (phoneEl) { phoneEl.textContent = '未绑定'; if (unbindPhoneBtn) unbindPhoneBtn.style.display = 'none'; }
            var pwEl = document.getElementById('binding-password');
            if (pwEl) pwEl.textContent = (user.password_set || user.password_hash) ? '已设置' : '未设置';
            // 2026-10-12 小蕊: 微信绑定状态
            const wechatEl = document.getElementById('binding-wechat');
            if (wechatEl) wechatEl.textContent = user.wechat_openid ? '已绑定' : '未绑定';
            // 积分同步(后端 users.points)
            if (user.points !== undefined) document.getElementById('profile-points').textContent = '积分：' + (user.points || 0);
            // 头像/昵称 跟随微信(用户可自行修改)
            refreshProfileAvatarName(user);
        }
    } catch (e) {}
}

// 2026-10-12 小蕊加: 头像/昵称 显示(微信登录默认取微信侧, 用户改过的优先)
// 2026-10-12 小蕊修(中华反馈): 微信昵称乱码兜底
// 现象: 微信 sns/userinfo 返回的 UTF-8 昵称被按 latin-1 逐字节解出后存进库
//       (例 "用音乐说世界" -> "ç\x94\x8é\x9f\xb..."), 或历史脏数据。
// 修法: 仅当原文确实含 latin-1 扩展区字符(ç è é 等 U+00C0-U+00FF)才尝试
//       unescape(encodeURIComponent(s)) 还原; 还原结果须全为 CJK/常规字符才采用,
//       避免把正常中文二次"修复"成乱码。
function _fixMojibake(s) {
    if (!s || typeof s !== 'string') return s;
    var hasLatinExt = /[\u00c0-\u00ff]/.test(s);
    if (!hasLatinExt) return s;  // 正常中文/英文, 不动
    try {
        var fixed = unescape(encodeURIComponent(s));
        // 修好后应基本全是 CJK / 常规可读字符; 若仍混入 latin-1 伪字符则失败
        var stillBroken = /[\u00c0-\u00ff]/.test(fixed);
        if (stillBroken) return s;
        return fixed;
    } catch(e) { return s; }
}
function refreshProfileAvatarName(user) {
    const avatarEl = document.getElementById('profile-avatar');
    const nameEl = document.getElementById('profile-name');
    if (!user) return;
    var nick = _fixMojibake(user.nickname || '');
    if (nameEl) nameEl.textContent = nick || '养生用户';
    if (avatarEl) {
        if (user.avatar) {
            // 2026-10-12 小蕊修(中华反馈): 微信头像没变圆 - img 的 border-radius 写死 8px 覆盖了容器的圆形
            avatarEl.innerHTML = '<img src="' + user.avatar + '" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" alt="头像">';
        } else {
            avatarEl.textContent = '松';
        }
    }
}

// 注册弹窗
function showRegisterModal() {
    document.getElementById('register-modal').style.display = 'flex';
}
function hideRegisterModal() {
    document.getElementById('register-modal').style.display = 'none';
    document.getElementById('register-account').value = '';
    document.getElementById('register-nickname').value = '';
    document.getElementById('register-password').value = '';
    document.getElementById('register-confirm-password').value = '';
}

async function registerAccount() {
    const account = document.getElementById('register-account').value.trim();
    const nickname = document.getElementById('register-nickname').value.trim();
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    
    if (!account) { alert('请输入账号'); return; }
    if (!password) { alert('请输入密码'); return; }
    if (password.length < 6) { alert('密码至少6位'); return; }
    if (password !== confirmPassword) { alert('两次密码不一致'); return; }
    
    try {
        const resp = await fetch(`${API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ account, password, nickname: nickname || account })
        });
        const data = await resp.json();
        if (data.success) {
            hideRegisterModal();
            alert('注册成功！请登录');
            showLoginError = () => {}; // 屏蔽错误
        } else {
            alert(data.error || '注册失败');
        }
    } catch (e) {
        alert('网络错误，请重试');
    }
}

// 忘记密码
function showForgotPassword() {
    document.getElementById('forgot-password-modal').style.display = 'flex';
}

function hideForgotPassword() {
    document.getElementById('forgot-password-modal').style.display = 'none';
}

async function sendForgotPassword() {
    const account = document.getElementById('forgot-account').value.trim();
    if (!account) { alert('请输入账号'); return; }
    
    try {
        const resp = await fetch(`${API_BASE}/api/auth/forgot-password`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ account, base_url: window.location.origin })
        });
        const data = await resp.json();
        if (data.success) {
            alert('重置链接已发送，请检查邮箱');
            hideForgotPassword();
        } else {
            alert(data.error || '发送失败');
        }
    } catch (e) {
        alert('网络错误');
    }
}

// 微信服务号登录
function wechatLogin() {
    // 微信服务号OAuth2.0授权 (2026-10-12 小蕊接通: 原为 YOUR_APPID 占位符, 导致服务号登录一直失败)
    // 2026-10-12 中华升级(服务号域名备案通过, 现在OAuth可直接通):
    // - state 里带 anon=<当前匿名uid>, 回调时后端一次性合并匿名数据(四账户统一)
    // - 授权成功后回调跳 '/?tab=profile'(个人中心), 不再跳首页
    var redirectUrl = encodeURIComponent(window.location.origin + '/wechat-callback');
    var appId = 'wx82287ef5c8de2fd2';
    var anonUid = '';
    try { anonUid = localStorage.getItem('som_user_id') || ''; } catch(e) {}
    var state = 'som_wechat_login' + (anonUid ? ':anon=' + encodeURIComponent(anonUid) : '');
    
    // 跳转到微信授权页 (snsapi_userinfo 拿昵称头像; 服务号域名已备案, 授权页可直接显示)
    var authUrl = 'https://open.weixin.qq.com/connect/oauth2/authorize' +
        '?appid=' + appId +
        '&redirect_uri=' + redirectUrl +
        '&response_type=code' +
        '&scope=snsapi_userinfo' +
        '&state=' + encodeURIComponent(state) +
        '#wechat_redirect';
    
    window.location.href = authUrl;
}

// 2026-10-12 小蕊加: 微信登录后自动补匿名合并(账户四统一: 微信/账密/邮箱/匿名)
// wechat-callback 返回的登录态写入 localStorage 后, 把旧匿名 user_id 数据迁到统一账号
function mergeAnonymousToWechat() {
    try {
        var userId = localStorage.getItem('som_user_id');
        if (!userId) return;
        // 匿名 user 的 user_id 形如 user_xxx_ 开头, 正式账号 u_xxx
        if (userId.indexOf('u_') !== 0) return;
        // 找 localStorage 里旧匿名数据键 som_user_data_user_...
        var anonDataKey = null;
        for (var i = 0; i < localStorage.length; i++) {
            var k = localStorage.key(i);
            if (k && k.indexOf('som_user_data_user_') === 0) { anonDataKey = k; break; }
        }
        if (anonDataKey && anonDataKey !== ('som_user_data_' + userId)) {
            var anonId = anonDataKey.replace('som_user_data_', '');
            if (anonId !== userId) {
                fetch(API_BASE + '/api/auth/bind-anon', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ user_id: userId, anonymous_user_id: anonId })
                }).catch(function(){});
            }
        }
    } catch(e) {}
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

// 2026-10-12 小蕊加: 修改头像/昵称 弹窗(中华要求: 头像与用户名都可以自己修改)
function showEditProfileModal() {
    var modal = document.getElementById('edit-profile-modal');
    if (!modal) { alert('请刷新页面后再试'); return; }
    _editAvatarDataUrl = null;
    var fileInput = document.getElementById('edit-avatar-file');
    if (fileInput) fileInput.value = '';
    try {
        var user = JSON.parse(localStorage.getItem('som_auth_user') || '{}');
        var nick = _fixMojibake(user.nickname || '');
        document.getElementById('edit-avatar-url').value = user.avatar || '';
        document.getElementById('edit-nickname').value = nick || '';
        var prev = document.getElementById('edit-avatar-preview');
        if (prev) {
            if (user.avatar) { prev.src = user.avatar; prev.style.display = 'block'; }
            else { prev.style.display = 'none'; }
        }
    } catch(e) {}
    modal.style.display = 'flex';
}
function hideEditProfileModal() {
    var m = document.getElementById('edit-profile-modal');
    if (m) m.style.display = 'none';
}
// 2026-10-12 小蕊加(中华要求): 头像支持点击上传本地图片(转128x128 JPEG dataURL存库, 压缩到最小), 不依赖外链
var _editAvatarDataUrl = null;
function onEditAvatarFile(input) {
    var f = input.files && input.files[0];
    if (!f) return;
    if (f.size > 8*1024*1024) { alert('图片太大, 请选 8MB 以内的'); return; }
    var reader = new FileReader();
    reader.onload = function(e) {
        var img = new Image();
        img.onload = function() {
            var canvas = document.createElement('canvas');
            var size = 128;
            canvas.width = size; canvas.height = size;
            var ctx = canvas.getContext('2d');
            var min = Math.min(img.width, img.height);
            var sx = (img.width - min)/2, sy = (img.height - min)/2;
            ctx.drawImage(img, sx, sy, min, min, 0, 0, size, size);
            _editAvatarDataUrl = canvas.toDataURL('image/jpeg', 0.85);
            var prev = document.getElementById('edit-avatar-preview');
            if (prev) { prev.src = _editAvatarDataUrl; prev.style.display = 'block'; }
            var urlInput = document.getElementById('edit-avatar-url');
            if (urlInput) urlInput.placeholder = '已选图片(128x128), 保存时优先用它';
            showToast('图片已选, 点保存生效');
        };
        img.onerror = function() { alert('图片读取失败, 换个图试试'); };
        img.src = e.target.result;
    };
    reader.readAsDataURL(f);
}
async function doEditProfile() {
    var userId = getUserId();
    var token = localStorage.getItem('som_auth_token');
    if (!token) { alert('请先登录'); return; }
    var nickname = document.getElementById('edit-nickname').value.trim() || undefined;
    var avatar = _editAvatarDataUrl || document.getElementById('edit-avatar-url').value.trim() || '';
    try {
        var resp = await fetch(`${API_BASE}/api/user/profile/update`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId, nickname: nickname, avatar: avatar })
        });
        var data = await resp.json();
        if (data.success) {
            // 更新本地登录态
            var user = JSON.parse(localStorage.getItem('som_auth_user') || '{}');
            if (data.user) user = Object.assign(user, data.user);
            localStorage.setItem('som_auth_user', JSON.stringify(user));
            refreshProfileAvatarName(user);
            hideEditProfileModal();
            showToast('已保存');
            loadUserAccount();
        } else {
            alert(data.error || '修改失败');
        }
    } catch(e) {
        alert('网络错误, 请重试');
    }
}

// ========== 2026-10-12 小蕊加: 每日签到(中华要求: 让用户能签到) ==========
async function doCheckin() {
    var userId = getUserId();  // 匿名uid也行, 后端 checkin_records 按 user_id 存
    var btn = document.getElementById('checkin-btn');
    if (btn) { btn.disabled = true; btn.textContent = '签到中…'; }
    try {
        var resp = await fetch(`${API_BASE}/api/checkin/do`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ user_id: userId })
        });
        var data = await resp.json();
        if (data.success) {
            // 本地积分累加(与后端保持一致)
            var data2 = getUserData();
            data2.points = (data.total_points || 0);
            saveUserData(data2);
            loadCheckinStatus();
            loadProfile();
            loadUserAccount();
            showToast(data.message || '签到成功！');
            if (btn) { btn.textContent = '✅ 今天已签到'; }
        } else {
            showToast(data.message || '签到失败');
            if (btn) { btn.disabled = false; btn.textContent = '立即签到'; }
            loadCheckinStatus();
        }
    } catch(e) {
        alert('网络错误, 请重试');
        if (btn) { btn.disabled = false; btn.textContent = '立即签到'; }
    }
}

// 签到状态刷新(显示连续天数 + 按钮状态)
async function loadCheckinStatus() {
    var userId = getUserId();
    var btn = document.getElementById('checkin-btn');
    var streakEl = document.getElementById('checkin-streak');
    var section = document.getElementById('checkin-section');
    if (!userId || !btn) return;
    try {
        var resp = await fetch(`${API_BASE}/api/checkin/status?user_id=${encodeURIComponent(userId)}`);
        var data = await resp.json();
        if (data.checked_in_today) {
            btn.disabled = true;
            btn.textContent = '✅ 今天已签到';
        } else {
            btn.disabled = false;
            btn.textContent = '立即签到';
        }
        if (streakEl) streakEl.textContent = '连续 ' + (data.streak || 0) + ' 天 · 总积分 ' + (data.total_points || 0);
        // 同步用户卡片的"签到"行
        var pc = document.getElementById('profile-checkin');
        if (pc) pc.textContent = data.checked_in_today ? '✅ 今天已签到' : '签到：今天未签到';
    } catch(e) {}
}

// 显示签到区 + 初始化
function showCheckinSection() {
    var section = document.getElementById('checkin-section');
    if (section) section.style.display = 'block';  // 2026-10-12 中华要求: 签到对所有用户开放, 不只登录用户
}

// 页面加载/登录成功后调用
function initCheckin() {
    showCheckinSection();
    loadCheckinStatus();
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
        // 显示昵称/头像(微信登录默认取微信侧, 可修改)
        try {
            const user = JSON.parse(localStorage.getItem('som_auth_user') || '{}');
            refreshProfileAvatarName(user);
        } catch(e) {}
        // 显示绑定状态 + 签到区
        loadUserAccount();
        initCheckin();
        // 匿名→统一 数据合并(四统一)
        try { mergeAnonymousToWechat(); } catch(e) {}
    } else {
        loginSection.style.display = 'block';
        profileCard.style.display = 'none';
        var cs = document.getElementById('checkin-section');
        if (cs) cs.style.display = 'none';
    }
}

// ========== 个人中心 ==========

function initProfile() {
    updateLoginUI();
    loadProfile();
    loadUserAccount();
    // 2026-10-12 小蕊: 已登录(微信登录过)时, 补一次匿名数据合并(四统一)
    if (isLoggedIn()) {
        try { mergeAnonymousToWechat(); } catch(e) {}
    }
}

function getUserId() {
    // 2026-10-19 根治(中华反馈"收藏商品与辨证内容收藏没出来/分享图不出来"): 登录态优先。
    // 旧实现只读 som_user_id: 清缓存→微信登录 bind-anon 把 som_user_id 改成 u_xxx 后,
    // 但页面内旧渲染/定时器仍可能拿旧匿名 user_xxx 去查收藏/分享, 查的是空匿名号→显示不出。
    // 现: 只要已登录(som_auth_user 在), 一律返回正式账号 u_xxx; 未登录才回退 som_user_id/生成匿名号。
    var _authUser = '';
    try { _authUser = JSON.parse(localStorage.getItem('som_auth_user') || '{}'); } catch (e) {}
    if (_authUser && _authUser.user_id && _authUser.user_id.indexOf('u_') === 0) {
        // 顺带把 som_user_id 同步回正式账号, 保证所有调用点口径一致
        try { localStorage.setItem('som_user_id', _authUser.user_id); } catch (e) {}
        return _authUser.user_id;
    }
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
    
    // 2026-10-13 小蕊修(中华反馈): 对话次数原来读本地数组(清缓存后归零), 改读后端 chat_history
    loadChatStats();
    document.getElementById('stat-chats').textContent = (data.chats || []).length; // 先显示本地, 后端返回后覆盖
    // 2026-10-13 小蕊修(中华反馈): 签到天数原来读本地数组(永远0), 改读后端 checkin_records
    loadCheckinStats();
    document.getElementById('stat-products').textContent = data.productBrowses || 0;
    
    // 优先从后端加载体质记录，失败则用本地
    loadTizhiRecordsFromBackend().catch(() => loadTizhiRecords(data));
    // 2026-10-14 健康画像多维时间线(中华要求): 登录后拉后端 /api/health/portrait
    loadHealthPortrait();

    // 2026-10-16 小蕊修(中华反馈「收藏没有出现」):
    // 原实现把 loadFavoritesCard 挂在 window.updateProfileCard 上, 但 updateProfileCard
    // 全项目从未被定义/调用(旧版是 openMyFavorites 弹窗式收藏), 导致收藏区永远
    // display:none 不出现, 清微信缓存也没用(不是缓存问题, 是代码没被调用)。
    // 改直接挂 loadProfile —— 登录/注册/签到后都会走这里, 进「我」页即加载收藏。
    var _favSec = document.getElementById('my-favorites-section');
    if (_favSec) {
        if (isLoggedIn()) { _favSec.style.display = '';
            try { loadFavoritesCard(); } catch (e) { console.warn('loadFavoritesCard 出错', e); } }
        else { _favSec.style.display = 'none'; }
    }
}

// 2026-10-17 小蕊修(中华反馈「清完缓存收藏还是不出来」):
// loadProfile 只在「登录后」才设 _favSec 的 display, 但用户进「我」页的时机可能是:
// 1) 已登录直接切到 profile tab → loadProfile 没重跑 → _favSec 保持初始 display:none
// 2) loadProfile 跑了但 my-favorites-section 节点当时还没渲染完(时序问题)
// 修法: switchTab('profile') 每次进「我」页都强制触发一次 loadFavoritesCard,
// 并先确保节点可见。loadFavoritesCard 内部会去 fetch 后端, 有数据才渲染, 没数据就隐藏。
if (!window.__favTabHookInstalled) {
    window.__favTabHookInstalled = true;
    var _origSwitchTab = window.switchTab;
    if (typeof _origSwitchTab === 'function') {
        window.switchTab = function(tabName) {
            var _ret = _origSwitchTab(tabName);
            if (tabName === 'profile') {
                // 延迟一拍, 等 tab 切换后的 DOM 就绪
                setTimeout(function() {
                    var _sec = document.getElementById('my-favorites-section');
                    if (!_sec) return;
                    if (isLoggedIn()) {
                        _sec.style.display = '';
                        try { loadFavoritesCard(); } catch (e) { console.warn('[fav-tab-hook] loadFavoritesCard 出错', e); }
                    } else {
                        _sec.style.display = 'none';
                    }
                }, 50);
            }
            return _ret;
        };
    }
}

// ========== 2026-10-14 健康画像(多维时间画像) ==========
// 脸/舌苔/面色/患处的照片视觉特征 + 小麦辨证, 随时间积累, 用户一看趋势就掌握自己的健康
async function loadHealthPortrait() {
    const section = document.getElementById('health-portrait-section');
    const box = document.getElementById('health-portrait');
    if (!section || !box) return;
    if (!isLoggedIn()) { section.style.display = 'none'; return; }
    const userId = getUserId();
    if (!userId) { section.style.display = 'none'; return; }
    _portraitPage = 1; await fetchPortraitPage();
}

// 2026-10-14 小蕊修(中华要求: 卡片底部应该是翻页, 不是加载更多/向下滑动)
// 健康画像真翻页器: 上一页 / 第X页共Y页 / 下一页, 每页 10 条
// 口径与体质记录统一: 不传 days = 全量, 两张卡片条数一致
const PORTRAIT_PAGE_SIZE = 10;
let _portraitPage = 1;
let _portraitTotal = 0;
let _portraitCache = { total: 0, face: {}, dist: {}, trend: {}, registered_days: null };

async function fetchPortraitPage() {
    const section = document.getElementById('health-portrait-section');
    const box = document.getElementById('health-portrait');
    if (!section || !box) return;
    const userId = getUserId();
    const offset = (_portraitPage - 1) * PORTRAIT_PAGE_SIZE;
    const isFirst = _portraitPage === 1;
    let result;
    try {
        const resp = await fetch(`${API_BASE}/api/health/portrait?user_id=${encodeURIComponent(userId)}&offset=${offset}`);
        result = await resp.json();
    } catch (e) { console.warn('health portrait 拉取失败', e); section.style.display = 'none'; return; }
    const p = result && result.portrait;
    if (!p || !p.timeline || p.timeline.length === 0) {
        if (isFirst) section.style.display = 'none';
        return;
    }
    section.style.display = 'block';
    _portraitTotal = result.total || 0;
    const totalPages = Math.max(1, Math.ceil(_portraitTotal / PORTRAIT_PAGE_SIZE));
    if (_portraitPage > totalPages) _portraitPage = 1;
    // 缓存汇总数据(第 1 页拉取时保存, 后续翻页复用)
    if (isFirst) {
        _portraitCache = { total: result.total || 0, face: p.face || {}, dist: p.tizhi_distribution || {}, trend: p.trend || {}, registered_days: p.registered_days };
    }
    // 重建整卡(翻页不累积, 每页独立渲染)
    const d = _portraitCache.trend || {}, face = _portraitCache.face || {}, dist = _portraitCache.dist || {};
    const distStr = Object.keys(dist).map(k => `${k}×${dist[k]}`).join('、') || '暂无';
    let html = '';
    // ① 汇总条
    html += '<div style="font-size:13px;color:#555;line-height:1.9;">';
    html += `<div>📊 累计辨证 <b>${_portraitTotal}</b> 次 · 体质分布: ${escapeHtml(distStr)}</div>`;
    if (face.vector_count) {
        html += `<div>🧬 人脸向量组已学 <b>${face.vector_count}</b> 张(认得你变老/换角度/换光线)</div>`;
    }
    if (d.first_tizhi && d.last_tizhi) {
        const changed = d.changed ? ' <span style="color:#fa5151;">↺ 体质发生了变化</span>' : ' <span style="color:#07c160;">✔ 体质保持稳定</span>';
        html += `<div>📈 趋势: ${escapeHtml(d.first_tizhi)}(${escapeHtml((d.first_date||'').slice(0,10))}) → ${escapeHtml(d.last_tizhi)}(${escapeHtml((d.last_date||'').slice(0,10))})${changed}</div>`;
    }
    if (_portraitCache.registered_days != null) html += `<div>⏳ 健康大数据已积累 ${_portraitCache.registered_days} 天</div>`;
    html += '</div>';
    // ② 时间线(本页 10 条, 新→旧)
    html += '<div id="health-portrait-timeline" style="margin-top:8px;border-top:1px solid #f0f0f0;padding-top:8px;font-size:12px;color:#666;"></div>';
    box.innerHTML = html;
    const tlBox = document.getElementById('health-portrait-timeline');
    // 2026-10-15 小蕊修: 后端已改倒序(最新在前), 前端不再 reverse, 避免双重反转
    const tl = p.timeline || [];
    let pageHtml = '';
    for (let i = 0; i < tl.length; i++) {
        const t = tl[i];
        const date = escapeHtml((t.date || '').slice(0, 16));
        const tag = t.has_photo ? '📷' : '💬';
        let delta = '';
        if (t.has_photo) {
            // 2026-10-15 中华指出: 最新一条是"待比较者", 历史均值是基准, 应显示最新相对历史的变化
            if (t.visual_delta == null) {
                // 只有一张有照片记录(无历史可比) 或 计算异常
                delta = '<span style="color:#888;">(首张记录)</span>';
            } else {
                const sim = t.visual_delta;
                delta = sim < 0.25 ? '<span style="color:#07c160;">(照片变化小)</span>'
                       : sim < 0.6 ? '<span style="color:#faad14;">(照片有变化)</span>'
                       : '<span style="color:#fa5151;">(照片变化大)</span>';
            }
        }
        pageHtml += `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dashed #f5f5f5;">`;
        pageHtml += `<span>${tag} ${date}</span><span><b>${escapeHtml(t.tizhi || '未知')}</b>${delta}</span></div>`;
    }
    // ③ 翻页器(上一页 / 第X页共Y页 / 下一页)
    pageHtml += '<div style="display:flex;justify-content:center;align-items:center;gap:12px;padding:12px 0;">';
    pageHtml += `  <button id="portrait-prev" style="background:#07c160;color:#fff;border:none;border-radius:16px;padding:6px 18px;font-size:13px;cursor:pointer;${_portraitPage <= 1 ? 'opacity:0.35;cursor:default;' : ''}">上一页</button>`;
    pageHtml += `  <span style="font-size:12px;color:#666;">第 ${_portraitPage} / ${totalPages} 页 · 共 ${_portraitTotal} 条</span>`;
    pageHtml += `  <button id="portrait-next" style="background:#07c160;color:#fff;border:none;border-radius:16px;padding:6px 18px;font-size:13px;cursor:pointer;${_portraitPage >= totalPages ? 'opacity:0.35;cursor:default;' : ''}">下一页</button>`;
    pageHtml += '</div>';
    tlBox.innerHTML = pageHtml;
    const prevBtn = document.getElementById('portrait-prev');
    const nextBtn = document.getElementById('portrait-next');
    if (prevBtn && _portraitPage > 1) prevBtn.addEventListener('click', async () => { _portraitPage--; await fetchPortraitPage(); });
    if (nextBtn && _portraitPage < totalPages) nextBtn.addEventListener('click', async () => { _portraitPage++; await fetchPortraitPage(); });
}

// 从后端加载体质记录
// 2026-10-13 小蕊加: 从后端拉签到总天数, 修"连续签到2次但我的数据显示0"
// 2026-10-13 小蕊加: 从后端拉对话次数, 修"清缓存后我的数据对话次数归零"
async function loadChatStats() {
    const userId = getUserId();
    const el = document.getElementById('stat-chats');
    if (!el || !userId) return;
    try {
        // 2026-10-13 中华规则: 小麦辨证一次=一次对话=一条健康数据, 一一对应
        // 对话次数 = 该用户 tizhi_records 总条数(不再按 session 去重, 不再用 chat_history limit=1)
        const resp = await fetch(`${API_BASE}/api/tizhi/records?user_id=${encodeURIComponent(userId)}&limit=9999`);
        const data = await resp.json();
        el.textContent = String((data.records || []).length);
    } catch (e) {}
}

async function loadCheckinStats() {
    const userId = getUserId();
    const el = document.getElementById('stat-checkins');
    if (!el || !userId) return;
    try {
        // 后端 /api/checkin/status 返回 total_points(每次+10), 用 total_points/10 得到总签到天数
        const resp = await fetch(`${API_BASE}/api/checkin/status?user_id=${encodeURIComponent(userId)}`);
        const data = await resp.json();
        const totalDays = Math.round((data.total_points || 0) / 10);
        el.textContent = String(totalDays);
        // 顺带刷新"连续X天"显示
        var streakEl = document.getElementById('checkin-streak');
        if (streakEl) streakEl.textContent = '连续 ' + (data.streak || 0) + ' 天 · 总积分 ' + (data.total_points || 0);
        var pc = document.getElementById('profile-checkin');
        if (pc) pc.textContent = data.checked_in_today ? '✅ 今天已签到' : '签到：今天未签到';
    } catch (e) {}
}

// 2026-10-13 小蕊重写(中华反馈"展开不能展开"): 每条记录自带详情 div, 点展开直接 toggle 相邻 div
// 不再依赖 event delegation + 全局 _tizhiFullTexts 数组, 彻底排除"绑定失败/数组为空"两类根因
function initTizhiToggle() {
    document.querySelectorAll('.tizhi-toggle-btn').forEach(function(btn) {
        if (btn._bound) return;  // 防重复绑定
        btn._bound = true;
        btn.addEventListener('click', function() {
            // 详情 div 是按钮的最近同级兄弟(渲染顺序: 按钮后紧跟 detail)
            let detail = btn.parentElement.parentElement.querySelector(':scope > .tizhi-detail-block');
            if (!detail) {
                // 兜底: 在按钮所在 history-item 里找/建
                const item = btn.closest('.history-item');
                if (!item) return;
                detail = document.createElement('div');
                detail.className = 'tizhi-detail-block';
                detail.style.cssText = 'display:none;margin:8px 0 4px;padding:10px;background:#f9f9f9;border-radius:8px;font-size:13px;color:#666;white-space:pre-wrap;line-height:1.6;';
                item.appendChild(detail);
            }
            if (btn.textContent.trim() === '展开' || detail.style.display === 'none') {
                detail.style.display = 'block';
                btn.textContent = '收起';
            } else {
                detail.style.display = 'none';
                btn.textContent = '展开';
            }
        });
    });
}

// 2026-10-14 小蕊修(中华要求: 卡片底部应该是翻页, 不是加载更多/向下滑动)
// 体质记录真翻页器: 上一页 / 第X页共Y页 / 下一页, 每页 10 条
let _tizhiPage = 1;
const TIZHI_PAGE_SIZE = 10;
let _tizhiTotal = 0;

async function loadTizhiRecordsFromBackend() {
    _tizhiPage = 1;
    await fetchTizhiPage();
}

async function fetchTizhiPage() {
    const offset = (_tizhiPage - 1) * TIZHI_PAGE_SIZE;
    const resp = await fetch(`${API_BASE}/api/tizhi/records?user_id=${encodeURIComponent(getUserId())}&limit=${TIZHI_PAGE_SIZE}&offset=${offset}`);
    const result = await resp.json();
    const history = document.getElementById('profile-history');
    if (!history) return;

    const records = (result.records || []);
    _tizhiTotal = result.total || 0;
    const totalPages = Math.max(1, Math.ceil(_tizhiTotal / TIZHI_PAGE_SIZE));
    if (_tizhiPage > totalPages) _tizhiPage = 1;

    if (records.length === 0 && _tizhiTotal === 0) {
        history.innerHTML = '<p class="empty-hint">暂无体质记录，快去和小麦SOM对话吧</p>';
        return;
    }

    let html = '';
    for (let i = 0; i < records.length; i++) {
        const r = records[i];
        const full = (r.advice ? r.advice : (r.symptoms || ''));
        html += '<div class="history-item" style="display:block;padding:8px;border-bottom:1px solid #f0f0f0;">';
        html += '  <div style="display:flex;justify-content:space-between;align-items:center;">';
        html += '    <div><span class="history-date">' + escapeHtml((r.created_at || '').slice(0, 10)) + '</span> ';
        html += '    <span class="history-tizhi">' + escapeHtml(r.tizhi || '') + '</span></div>';
        html += '    <button class="tizhi-toggle-btn" style="background:none;border:none;color:#07c160;font-size:12px;cursor:pointer;white-space:nowrap;">展开</button>';
        html += '  </div>';
        html += '  <div class="tizhi-detail-block" style="display:none;margin:8px 0 4px;padding:10px;background:#f9f9f9;border-radius:8px;font-size:13px;color:#666;white-space:pre-wrap;line-height:1.6;">' + escapeHtml(full) + '</div>';
        html += '</div>';
    }
    // 翻页器(上一页 / 第X页共Y页 / 下一页)
    html += '<div style="display:flex;justify-content:center;align-items:center;gap:12px;padding:12px 0;">';
    html += `  <button id="tizhi-prev" style="background:#07c160;color:#fff;border:none;border-radius:16px;padding:6px 18px;font-size:13px;cursor:pointer;${_tizhiPage <= 1 ? 'opacity:0.35;cursor:default;' : ''}">上一页</button>`;
    html += `  <span style="font-size:12px;color:#666;">第 ${_tizhiPage} / ${totalPages} 页 · 共 ${_tizhiTotal} 条</span>`;
    html += `  <button id="tizhi-next" style="background:#07c160;color:#fff;border:none;border-radius:16px;padding:6px 18px;font-size:13px;cursor:pointer;${_tizhiPage >= totalPages ? 'opacity:0.35;cursor:default;' : ''}">下一页</button>`;
    html += '</div>';
    history.innerHTML = html;
    initTizhiToggle();
    const prevBtn = document.getElementById('tizhi-prev');
    const nextBtn = document.getElementById('tizhi-next');
    if (prevBtn && _tizhiPage > 1) prevBtn.addEventListener('click', async () => { _tizhiPage--; await fetchTizhiPage(); });
    if (nextBtn && _tizhiPage < totalPages) nextBtn.addEventListener('click', async () => { _tizhiPage++; await fetchTizhiPage(); });
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
        // 2026-10-13 中华规则: 小麦辨证一次=一次对话=一条记录, 一一对应
        // 所以【不按 session 覆盖】, 每次辨证都新增一条(同 session 多次辨证=多条)
        data.tizhiRecords.push({
            date: new Date().toISOString().split('T')[0],
            tizhi: tizhi,
            desc: message.substring(0, 50),
            session_id: getSessionId()
        });
        data.tizhi = tizhi;
        // 2026-10-13 小蕊改(中华规则): 后端 /api/chat 和 /api/chat/vision 已自动存 tizhi_records,
        // 前端不再调 /api/tizhi/save, 避免一次辨证存两条(破坏 1:1 对应)
        // 本地 data.tizhiRecords 仍记录(离线兜底), 但不重复推后端
    }
    
    saveUserData(data);
}

// 同步体质评测结果到后端
// 2026-10-13 小蕊改(中华反馈): 传 session_id, 同一次对话只存一条体质记录
async function saveTizhiToBackend(tizhi, symptoms) {
    try {
        // 2026-10-12 中华要求: 健康大数据压缩到最小存储
        // 只存: 体质类型 + 症状关键词(截断80字) + 来源 + 时间。不存完整对话、不存原文。
        await fetch(`${API_BASE}/api/tizhi/save`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: getUserId(),
                tizhi: tizhi,
                symptoms: (symptoms || '').substring(0, 80),
                source: 'web_chat',
                session_id: getSessionId()
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
