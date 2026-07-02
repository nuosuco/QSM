/**
 * QEntL Web操作系统 - 三语国际化模块
 * 支持中文、英文、滇川黔贵通用彝文
 */

const i18n = {
    // 当前语言
    currentLang: 'zh',
    
    // 语言配置
    languages: {
        zh: { name: '中文', font: 'Microsoft YaHei' },
        en: { name: 'English', font: 'Segoe UI' },
        yi: { name: 'ꆈꌠ', font: 'LSTY-Yi-Black' }
    },
    
    // 翻译表
    translations: {
        // 系统界面
        'system.name': { zh: 'QEntL量子操作系统', en: 'QEntL Quantum OS', yi: 'QEntLꀱꏦꃅꊿ' },
        'system.desktop': { zh: '桌面', en: 'Desktop', yi: 'ꀀꀋ' },
        'system.running': { zh: '量子态运行中', en: 'Quantum Active', yi: 'ꇇꃀꈌꐥꁱꄂ' },
        
        // 应用名称
        'app.qvm': { zh: '量子虚拟机', en: 'Quantum VM', yi: 'ꇇꃀꈌꐥ' },
        'app.compiler': { zh: '编译器', en: 'Compiler', yi: 'ꃅꊿꄂ' },
        'app.files': { zh: '文件管理', en: 'Files', yi: 'ꎭꂷ' },
        'app.settings': { zh: '设置', en: 'Settings', yi: 'ꀀꀋ' },
        'app.store': { zh: '应用商店', en: 'App Store', yi: 'ꐥꌊ' },
        'app.help': { zh: '帮助', en: 'Help', yi: 'ꆏꌠ' },
        'app.terminal': { zh: '终端', en: 'Terminal', yi: 'ꁱꄂ' },
        'app.social': { zh: '社交网络', en: 'Social', yi: 'ꈌꄂ' },
        
        // 操作
        'action.open': { zh: '打开', en: 'Open', yi: 'ꀀꀋ' },
        'action.close': { zh: '关闭', en: 'Close', yi: 'ꁉꇁ' },
        'action.save': { zh: '保存', en: 'Save', yi: 'ꁦꎆ' },
        'action.cancel': { zh: '取消', en: 'Cancel', yi: 'ꁉꇁ' },
        'action.search': { zh: '搜索', en: 'Search', yi: 'ꀊꁁ' },
        
        // 状态
        'status.ready': { zh: '准备就绪', en: 'Ready', yi: 'ꀀꌠ' },
        'status.loading': { zh: '加载中...', en: 'Loading...', yi: 'ꀊꁁ...' },
        'status.success': { zh: '成功', en: 'Success', yi: 'ꁱꄂ' },
        'status.error': { zh: '错误', en: 'Error', yi: 'ꁉꇁ' },
        
        // 量子概念
        'quantum.superposition': { zh: '量子叠加态', en: 'Quantum Superposition', yi: 'ꇇꃀꈌꐥ' },
        'quantum.entanglement': { zh: '量子纠缠', en: 'Quantum Entanglement', yi: 'ꈌꐥ' },
        'quantum.coherence': { zh: '量子相干', en: 'Quantum Coherence', yi: 'ꇇꃀ' },
        'quantum.state': { zh: '量子态', en: 'Quantum State', yi: 'ꂷꌠ' },
        
        // 彝文量子核心概念
        'yi.heart': { zh: '心', en: 'Heart', yi: 'ꀀꌠ' },
        'yi.universe': { zh: '乾坤', en: 'Universe', yi: 'ꑌꑌ' },
        'yi.fire': { zh: '火', en: 'Fire', yi: 'ꆏ' },
        'yi.sky': { zh: '天', en: 'Sky', yi: 'ꑌ' },
        'yi.king': { zh: '王', en: 'King', yi: 'ꑌ' },
        'yi.choice': { zh: '选择', en: 'Choice', yi: 'ꑌ' },
        'yi.connect': { zh: '连接', en: 'Connect', yi: 'ꆏ' },
        'yi.gather': { zh: '聚集', en: 'Gather', yi: 'ꆏ' }
    },
    
    // 获取翻译
    t(key) {
        const trans = this.translations[key];
        if (!trans) return key;
        return trans[this.currentLang] || trans.zh || key;
    },
    
    // 切换语言
    setLang(lang) {
        if (this.languages[lang]) {
            this.currentLang = lang;
            this.updateAllText();
            document.documentElement.lang = lang;
            return true;
        }
        return false;
    },
    
    // 更新所有文本
    updateAllText() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.dataset.i18n;
            el.textContent = this.t(key);
        });
        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            const key = el.dataset.i18nPlaceholder;
            el.placeholder = this.t(key);
        });
        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            const key = el.dataset.i18nTitle;
            el.title = this.t(key);
        });
    },
    
    // 获取所有语言列表
    getLanguages() {
        return Object.entries(this.languages).map(([code, info]) => ({
            code,
            name: info.name,
            font: info.font
        }));
    }
};

// 导出
window.i18n = i18n;
