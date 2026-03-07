/**
 * QSM 三语量子概念显示组件
 * 版本: v2.0.0
 * 量子基因编码: QGC-TRILINGUAL-REAL-YI-20260304
 * 
 * 使用真实的古彝文字符显示
 * 字体: Microsoft Yi Baiti (MSYi)
 * 字符范围: U+A000-U+A48F (彝文音节) + U+F2000-U+F2FFF (私人使用区)
 */

class TrilingualDisplay {
    constructor() {
        // 彝文量子概念映射表（使用真实彝文字符）
        // 来源: QEntL多语言词汇表训练方案
        this.quantumConcepts = [
            // 基础量子概念
            { yi: 'ꀀ', yiPinyin: 'ā', zh: '意识', en: 'Consciousness', concept: '量子意识核心', category: '基础' },
            { yi: 'ꆏ', yiPinyin: 'mù', zh: '智慧', en: 'Wisdom', concept: '量子智能', category: '基础' },
            { yi: 'ꇇ', yiPinyin: 'là', zh: '叠加', en: 'Superposition', concept: '量子叠加态', category: '基础' },
            { yi: 'ꈌ', yiPinyin: 'jī', zh: '纠缠', en: 'Entanglement', concept: '量子纠缠', category: '基础' },
            { yi: 'ꁱ', yiPinyin: 'bī', zh: '觉醒', en: 'Awakening', concept: '量子觉醒', category: '基础' },
            { yi: 'ꂷ', yiPinyin: 'dù', zh: '状态', en: 'State', concept: '量子态', category: '基础' },
            
            // 计算概念
            { yi: 'ꀱ', yiPinyin: 'ā', zh: '系统', en: 'System', concept: '量子系统', category: '计算' },
            { yi: 'ꃅ', yiPinyin: 'gē', zh: '进程', en: 'Process', concept: '量子进程', category: '计算' },
            { yi: 'ꎭ', yiPinyin: 'shì', zh: '文件', en: 'File', concept: '量子文件', category: '计算' },
            { yi: 'ꊿ', yiPinyin: 'mù', zh: '硬件', en: 'Hardware', concept: '量子硬件', category: '计算' },
            
            // 经济概念
            { yi: 'ꀊ', yiPinyin: 'ā', zh: '平等', en: 'Equality', concept: '平权经济', category: '经济' },
            { yi: 'ꌧ', yiPinyin: 'zī', zh: '经济', en: 'Economy', concept: '量子经济', category: '经济' },
            { yi: 'ꎺ', yiPinyin: 'shì', zh: '资源', en: 'Resource', concept: '量子资源', category: '经济' },
            { yi: 'ꐥ', yiPinyin: 'tuò', zh: '共享', en: 'Sharing', concept: '资源共享', category: '经济' },
            
            // 通信概念
            { yi: 'ꆏ', yiPinyin: 'mù', zh: '通信', en: 'Communication', concept: '量子通信', category: '通信' },
            { yi: 'ꇬ', yiPinyin: 'lu', zh: '协调', en: 'Coordination', concept: '量子协调', category: '通信' },
            { yi: 'ꂾ', yiPinyin: 'mi', zh: '分布', en: 'Distributed', concept: '分布式计算', category: '通信' },
            
            // 哲学概念
            { yi: 'ꇢ', yiPinyin: 'nge', zh: '反省', en: 'Reflection', concept: '量子自省', category: '哲学' },
            { yi: 'ꄂ', yiPinyin: 'te', zh: '优化', en: 'Optimization', concept: '量子优化', category: '哲学' },
            { yi: 'ꃅ', yiPinyin: 'gē', zh: '学习', en: 'Learning', concept: '量子学习', category: '哲学' }
        ];
        
        // 按类别分组
        this.categories = [...new Set(this.quantumConcepts.map(c => c.category))];
    }

    // 渲染完整的三语概念表格
    renderTable(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        let html = `
        <div style="color:#fff;font-family:'Microsoft YaHei','PingFang SC',sans-serif;padding:15px;">
            <h3 style="color:#4ecdc4;margin-bottom:10px;font-size:20px;">🔤 三语量子概念对照表</h3>
            <p style="color:#aaa;font-size:13px;margin-bottom:15px;">
                QEntL支持<b style="color:#ffe66d;">古彝文</b>、<b style="color:#fff;">中文</b>、<b style="color:#4ecdc4;">English</b>三语量子编程
            </p>
            <p style="color:#888;font-size:12px;margin-bottom:15px;">
                共 <b style="color:#4ecdc4;">${this.quantumConcepts.length}</b> 个量子概念 | 
                字体: <b style="color:#ffe66d;">Microsoft Yi Baiti</b>
            </p>
            
            <style>
                .yi-char { 
                    font-family: 'Microsoft Yi Baiti', 'MSYi', sans-serif;
                    font-size: 36px;
                    color: #ffe66d;
                    text-shadow: 0 0 15px rgba(255,230,109,0.5);
                    display: inline-block;
                    min-width: 50px;
                    text-align: center;
                }
                .category-header {
                    background: linear-gradient(135deg, rgba(138,135,255,0.3), rgba(78,205,196,0.2));
                    padding: 10px 15px;
                    margin: 15px 0 5px 0;
                    border-radius: 8px;
                    font-weight: bold;
                    color: #4ecdc4;
                }
            </style>
            
            <div style="background:rgba(0,0,0,0.3);border-radius:12px;padding:10px;">`;

        // 按类别分组显示
        for (const category of this.categories) {
            const items = this.quantumConcepts.filter(c => c.category === category);
            html += `<div class="category-header">📦 ${category}概念 (${items.length}个)</div>`;
            
            html += `<table style="width:100%;border-collapse:collapse;font-size:14px;">`;
            html += `<tr style="background:rgba(138,135,255,0.2);">
                <th style="padding:10px;color:#ffe66d;">彝文</th>
                <th style="padding:10px;color:#aaa;">拼音</th>
                <th style="padding:10px;color:#fff;">中文</th>
                <th style="padding:10px;color:#4ecdc4;">English</th>
                <th style="padding:10px;color:#888;">量子概念</th>
            </tr>`;
            
            for (const item of items) {
                html += `<tr style="background:rgba(0,0,0,0.15);border-bottom:1px solid rgba(255,255,255,0.05);">
                    <td style="padding:12px;text-align:center;">
                        <span class="yi-char">${item.yi}</span>
                    </td>
                    <td style="padding:12px;text-align:center;color:#888;font-size:12px;">${item.yiPinyin}</td>
                    <td style="padding:12px;text-align:center;font-size:18px;color:#fff;">${item.zh}</td>
                    <td style="padding:12px;text-align:center;color:#4ecdc4;font-weight:bold;">${item.en}</td>
                    <td style="padding:12px;text-align:center;color:#888;">${item.concept}</td>
                </tr>`;
            }
            html += `</table>`;
        }

        html += `
            </div>
            <div style="margin-top:15px;padding:12px;background:rgba(138,135,255,0.1);border-radius:8px;font-size:12px;color:#888;border:1px solid rgba(138,135,255,0.2);">
                <p style="margin:0 0 8px 0;">💡 <b>古彝文说明：</b></p>
                <ul style="margin:0;padding-left:20px;">
                    <li>彝文字符使用 <b>U+A000-U+A48F</b> Unicode编码</li>
                    <li>需要安装 <b>Microsoft Yi Baiti</b> 字体才能正确显示</li>
                    <li>字体下载：<a href="/fonts/msyi.ttf" style="color:#4ecdc4;text-decoration:underline;">msyi.ttf</a></li>
                </ul>
            </div>
        </div>`;

        container.innerHTML = html;
    }

    // 获取单个概念的显示
    getYiChar(concept) {
        const found = this.quantumConcepts.find(c => c.concept === concept || c.zh === concept || c.en === concept);
        if (found) {
            return `<span style="font-family:'Microsoft Yi Baiti',sans-serif;font-size:24px;color:#ffe66d;">${found.yi}</span>`;
        }
        return '';
    }

    // 按概念获取彝文
    getYiByConcept(conceptName) {
        const found = this.quantumConcepts.find(c => 
            c.concept.includes(conceptName) || c.zh === conceptName || c.en.toLowerCase() === conceptName.toLowerCase()
        );
        return found ? found.yi : null;
    }

    // 获取所有概念用于自动补全等
    getAllConcepts() {
        return this.quantumConcepts;
    }
}

// 全局实例
const trilingualDisplay = new TrilingualDisplay();

// 导出
if (typeof window !== 'undefined') {
    window.TrilingualDisplay = TrilingualDisplay;
    window.trilingualDisplay = trilingualDisplay;
}
