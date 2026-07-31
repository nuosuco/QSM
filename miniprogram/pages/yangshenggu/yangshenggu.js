// 养生谷：节气养生 + 护眼训练 + 九种体质 + 药食同源 + 分享 + 问小麦
const { request } = require('../../utils/api');

Page({
  data: {
    jieqi: null,
    eyeExercises: [],
    eyeTips: '',
    tizhiList: [],
    yaoshiList: [],
    loading: true
  },

  onLoad() {
    this.loadAll();
  },

  goTizhiTest() {
    wx.navigateTo({ url: '/pages/tizhi-test/tizhi-test' });
  },

  // M2: 问小麦入口（跳转聊天页，带养生知识提示）
  goAskXiaomai(e) {
    let hint = '我想了解养生知识，请根据我的体质推荐食疗方案';
    if (e && e.currentTarget && e.currentTarget.dataset) {
      const part = e.currentTarget.dataset.part;
      if (part) {
        hint = '我看到养生谷的' + part + '内容，想进一步了解，请给我食疗调理方案';
      }
    }
    wx.setStorageSync('som_tizhi_hint', hint);
    wx.switchTab({ url: '/pages/chat/chat' });
  },

  // M2: 分享养生知识给好友
  onShareAppMessage() {
    return {
      title: '🌿 中医养生 · 节气食疗 · 体质调理，尽在松麦SOM',
      path: '/pages/yangshenggu/yangshenggu'
    };
  },

  // M2: 分享养生谷海报图
  shareYangshengImage() {
    const query = wx.createSelectorQuery();
    query.select('#ygShareCanvas').fields({ node: true, size: true }).exec((res) => {
      if (!res || !res[0] || !res[0].node) {
        wx.showToast({ title: '生成中，请稍后', icon: 'none' });
        return;
      }
      const canvas = res[0].node;
      const ctx = canvas.getContext('2d');
      const dpr = wx.getWindowInfo().pixelRatio || 2;
      const W = 375, H = 400;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.scale(dpr, dpr);

      // 背景
      ctx.fillStyle = '#f0f7f0';
      ctx.fillRect(0, 0, W, H);

      // 顶部绿条
      ctx.fillStyle = '#4a9d6e';
      ctx.fillRect(0, 0, W, 8);

      // 标题
      ctx.fillStyle = '#2c3e50';
      ctx.font = 'bold 24px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('🌿 松麦养生谷', W / 2, 55);

      // 节气信息
      const jieqi = this.data.jieqi;
      if (jieqi) {
        ctx.fillStyle = '#4a9d6e';
        ctx.font = 'bold 18px sans-serif';
        ctx.fillText(`当前节气：${jieqi.jieqi}`, W / 2, 100);

        ctx.fillStyle = '#555';
        ctx.font = '14px sans-serif';
        this._wrapText(ctx, jieqi.yangsheng || jieqi.desc || '', W / 2, 135, W - 60, 20);
      } else {
        ctx.fillStyle = '#555';
        ctx.font = '14px sans-serif';
        ctx.fillText('节气养生 · 体质调理 · 药食同源', W / 2, 100);
      }

      // 功能列表
      const features = ['🔍 健康测评（AI拍照+答题）', '🌿 节气养生（当季食材）', '👁️ 护眼训练', '📋 九种体质调理', '🌱 药食同源知识库'];
      ctx.textAlign = 'left';
      ctx.fillStyle = '#333';
      ctx.font = '14px sans-serif';
      features.forEach((f, i) => {
        ctx.fillText(f, 50, 200 + i * 30);
      });

      // 底部引导
      ctx.textAlign = 'center';
      ctx.fillStyle = '#4a9d6e';
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText('扫码进入，免费测评 →', W / 2, 370);

      ctx.fillStyle = '#999';
      ctx.font = '11px sans-serif';
      ctx.fillText('松麦SOM · 中医养生 · 有机生活', W / 2, 392);

      // 导出并分享
      wx.canvasToTempFilePath({
        canvas,
        success: (tmpRes) => {
          wx.shareFileMessage({
            filePath: tmpRes.tempFilePath,
            fileName: 'yangshenggu.png',
            fail: (err) => {
              if (err.errMsg && err.errMsg.indexOf('cancel') === -1) {
                wx.showToast({ title: '分享失败', icon: 'none' });
              }
            }
          });
        },
        fail: () => wx.showToast({ title: '生成失败', icon: 'none' })
      });
    });
  },

  _wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    let line = '';
    for (let i = 0; i < text.length; i++) {
      const testLine = line + text[i];
      if (ctx.measureText(testLine).width > maxWidth && line) {
        ctx.fillText(line, x, y);
        line = text[i];
        y += lineHeight;
      } else {
        line = testLine;
      }
    }
    ctx.fillText(line, x, y);
  },

  loadAll() {
    this.setData({ loading: true });

    Promise.all([
      request('/api/jieqi/current').catch(() => null),
      request('/api/eye-exercise').catch(() => null),
      request('/api/knowledge/tizhi').catch(() => ({ items: [] })),
      request('/api/knowledge/yaoshi').catch(() => ({ items: [] }))
    ]).then(([jieqi, eye, tizhiData, yaoshiData]) => {
      this.setData({
        jieqi: jieqi,
        eyeExercises: (eye && eye.exercises) || [],
        eyeTips: (eye && eye.tips) || '',
        tizhiList: (tizhiData && tizhiData.items) || [],
        yaoshiList: (yaoshiData && yaoshiData.items) || [],
        loading: false
      });
    });
  }
});
