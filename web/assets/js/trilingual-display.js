/**
 * QSM 三语量子概念显示组件 - v6.0.0
 * 滇川黔贵通用彝文（私人使用区编码）
 */

class TrilingualDisplay {
 constructor() {
 this.quantumConcepts = [
 { yi: '󲜷', zh: '心', en: 'Heart', concept: '量子意识核心', category: '基础' },
 { yi: '󲞭', zh: '天', en: 'Sky', concept: '量子宇宙', category: '基础' },
 { yi: '󲞮', zh: '火', en: 'Fire', concept: '量子能量', category: '基础' },
 { yi: '󲞰', zh: '王', en: 'King', concept: '量子核心', category: '基础' },
 { yi: '󲥝', zh: '纠缠', en: 'Entanglement', concept: '量子纠缠', category: '基础' },
 { yi: '󲜧', zh: '膨胀', en: 'Expansion', concept: '量子叠加', category: '基础' },
 { yi: '󲜙', zh: '分开', en: 'Separate', concept: '量子分解', category: '计算' },
 { yi: '󲜫', zh: '爆', en: 'Explode', concept: '量子计算', category: '计算' },
 { yi: '󲢙', zh: '和平', en: 'Peace', concept: '量子平衡', category: '计算' },
 { yi: '󲜔', zh: '便宜', en: 'Cheap', concept: '平权经济', category: '经济' },
 { yi: '󲜪', zh: '翻', en: 'Flip', concept: '量子交换', category: '经济' },
 { yi: '󲜢', zh: '飘', en: 'Float', concept: '量子传输', category: '通信' },
 { yi: '󲟘', zh: '觉', en: 'Awake', concept: '量子觉醒', category: '哲学' },
 { yi: '󲢩', zh: '醒', en: 'Wake', concept: '量子开悟', category: '哲学' },
 ];
 this.categories = [...new Set(this.quantumConcepts.map(c => c.category))];
 }
 
 renderTable(containerId) {
 const container = document.getElementById(containerId);
 if (!container) return;
 
 let html = `<div style="color:#fff;padding:15px;">
<h3 style="color:#4ecdc4;font-size:20px;margin-bottom:15px;">🔤 三语量子概念对照表</h3>
<style>.yi-char{font-family:"YiTongyong",sans-serif;font-size:48px;color:#ffe66d;text-shadow:0 0 15px rgba(255,230,109,0.5);}</style>
<div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:10px;">`;
 
 for (const cat of this.categories) {
 const items = this.quantumConcepts.filter(c => c.category === cat);
 html += `<div style="background:linear-gradient(135deg,rgba(138,135,255,0.3),rgba(78,205,196,0.2));padding:10px;margin:10px 0;border-radius:8px;color:#4ecdc4;font-weight:bold;">📦 ${cat}概念</div>
<table style="width:100%;border-collapse:collapse;"><tr style="background:rgba(138,135,255,0.2);"><th style="padding:10px;color:#ffe66d;">彝文</th><th style="padding:10px;color:#fff;">中文</th><th style="padding:10px;color:#4ecdc4;">English</th><th style="padding:10px;color:#888;">概念</th></tr>`;
 for (const item of items) {
 html += `<tr style="background:rgba(0,0,0,0.1);">
<td style="padding:10px;text-align:center;"><span class="yi-char">${item.yi}</span></td>
<td style="padding:10px;text-align:center;color:#fff;font-size:18px;">${item.zh}</td>
<td style="padding:10px;text-align:center;color:#4ecdc4;">${item.en}</td>
<td style="padding:10px;text-align:center;color:#888;">${item.concept}</td></tr>`;
 }
 html += `</table>`;
 }
 
 html += `</div>
<div style="margin-top:15px;padding:12px;background:rgba(138,135,255,0.1);border-radius:8px;font-size:13px;color:#888;">
<p style="margin:0 0 10px 0;color:#fff;">💡 <b>滇川黔贵通用彝文说明：</b></p>
<ul style="margin:0;padding-left:20px;line-height:1.8;">
<li>编码：私人使用区 (U+F2000-U+F2FFF)</li>
<li>字体：<b style="color:#ffe66d;">零碎通用彝文（黑）</b></li>
<li>浏览器会自动加载字体</li>
<li>如不能显示，<a href="/font-installer.html" style="color:#4ecdc4;text-decoration:underline;">点击安装字体</a></li>
</ul>
</div></div>`;
 
 container.innerHTML = html;
 }
 
 getAllConcepts() { return this.quantumConcepts; }
}

const trilingualDisplay = new TrilingualDisplay();
if (typeof window !== 'undefined') {
 window.TrilingualDisplay = TrilingualDisplay;
 window.trilingualDisplay = trilingualDisplay;
}
