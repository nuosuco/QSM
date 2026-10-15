// 2026-10-12 小蕊加(中华反馈): 弹窗在微信WebView点不出, 加全局错误捕获帮定位
// 捕获未处理的异常, 显示在页面底部红条, 同时存 localStorage 便于排查
(function() {
    if (window.__somErrorTrapInstalled) return;
    window.__somErrorTrapInstalled = true;

    var errors = [];

    function _recordError(kind, msg) {
        errors.unshift({ kind: kind, msg: msg.slice(0, 200), t: new Date().toISOString() });
        errors.length = Math.min(errors.length, 20);
        try { localStorage.setItem('som_last_errors', JSON.stringify(errors)); } catch (e) {}
        _showErrorBanner();
    }

    window.addEventListener('error', function(e) {
        var desc = (e.message || 'unknown') + ' @line:' + (e.lineno || '?') + ',col:' + (e.colno || '?');
        _recordError('error', desc);
    });
    window.addEventListener('unhandledrejection', function(e) {
        var d = e.reason;
        _recordError('promise', d && d.message ? d.message : String(d));
    });

    function _showErrorBanner() {
        var div = document.getElementById('som-error-banner');
        if (!div) {
            div = document.createElement('div');
            div.id = 'som-error-banner';
            div.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#d9534f;color:#fff;' +
                'padding:10px 12px;font-size:12px;z-index:99999;max-height:50%;overflow:auto;white-space:pre-wrap;';
            document.body.appendChild(div);
        }
        var lines = ['⚠ 本次会话检测到 ' + errors.length + ' 个 JS 错误 (最近5条, 关闭页面即清空):'];
        errors.slice(0, 5).forEach(function(x, i) {
            lines.push((i + 1) + '. [' + x.kind + '] ' + x.msg);
        });
        div.textContent = lines.join('\n');
        div.onclick = function() { div.remove(); };
    }
})();
