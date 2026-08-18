// QEntL 字形识别模块
// 调用glyph_api.py提供的REST API

const GLYPH_API = 'http://localhost:8765';

class GlyphRecognizer {
    constructor() {
        this.weights = null;
        this.glyphs = null;
    }
    
    async init() {
        try {
            const [glyphsResp, weightsResp] = await Promise.all([
                fetch(`${GLYPH_API}/glyphs/`),
                fetch(`${GLYPH_API}/weights/1`)
            ]);
            
            this.glyphs = await glyphsResp.json();
            this.weights = await weightsResp.json();
            
            console.log('QEntL 字形识别器初始化成功');
            console.log(`  字形数: ${this.glyphs.length}`);
            console.log(`  权重数: ${this.weights.weights.length}`);
            
            return true;
        } catch (e) {
            console.error('QEntL 初始化失败:', e);
            return false;
        }
    }
    
    // 前向传播
    forward(pixels) {
        const w = this.weights.weights;
        const logits = [];
        
        for (let j = 0; j < 16; j++) {
            let sum = 0;
            for (let i = 0; i < 64; i++) {
                sum += w[j * 64 + i] * pixels[i];
            }
            logits.push(sum);
        }
        
        // argmax
        let maxIdx = 0;
        let maxVal = logits[0];
        for (let i = 1; i < 16; i++) {
            if (logits[i] > maxVal) {
                maxVal = logits[i];
                maxIdx = i;
            }
        }
        
        return {
            prediction: maxIdx,
            logits: logits,
            confidence: maxVal / logits.reduce((a, b) => a + Math.abs(b), 0)
        };
    }
    
    // 预测字形
    async predict(pixels) {
        if (!this.weights) {
            await this.init();
        }
        return this.forward(pixels);
    }
    
    // 获取所有字形
    getGlyphs() {
        return this.glyphs || [];
    }
}

// 全局实例
window.glyphRecognizer = new GlyphRecognizer();