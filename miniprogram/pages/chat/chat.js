// 对应 app.js 中 initChat / sendMessage / appendMessage / escapeHtml / getSessionId
const { request } = require('../../utils/api');
const app = getApp();

Page({
  data: {
    messages: [],
    inputValue: '',
    sending: false,
    scrollToId: '',
    msgCounter: 0,
    pendingImage: '', // 兼容旧字段
    pendingImages: [] // 待发送的多张图片临时路径
  },

  onShow() {
    // 1. 从体质测评页跳过来时，自动发送测评结果给小麦
    const hint = wx.getStorageSync('som_tizhi_hint');
    if (hint) {
      wx.removeStorageSync('som_tizhi_hint');
      this.setData({ inputValue: hint });
      setTimeout(() => this.sendMessage(), 300);
      return;
    }

    // 2. 分享图扫码进入（scene=tizhi_qixu / symptom_tongfeng）
    const scene = app.globalData.pendingScene;
    if (scene) {
      app.globalData.pendingScene = '';
      const parts = scene.split('_');
      const mode = parts[0]; // tizhi / symptom
      const key = parts.slice(1).join('_'); // qixu / tongfeng 等
      const hint2 = mode === 'tizhi'
        ? `朋友分享了他的体质测评结果【${key}】，我也想测一下，请帮我分析`
        : `朋友分享了他的健康自测结果【${key}】，我也有类似症状，请帮我分析`;
      this.setData({ inputValue: hint2 });
      setTimeout(() => this.sendMessage(), 300);
      return;
    }

    // 3. 每次进入，如果没有对话记录，显示体质评测引导（不限新用户，每次刷新/打开都有）
    if (this.data.messages.length === 0) {
      const guideMsg = {
        id: 'msg-guide-' + Date.now(),
        type: 'assistant',
        text: '你好呀！我是小麦 🌾\n\n想知道自己是什么体质、该吃什么养生吗？\n\n📷 拍个照（舌苔/面色/皮肤/患处）\n📝 或做3分钟测评\n\n我帮你辨证，给你食疗方案！',
        showGuide: true
      };
      this.setData({ messages: [guideMsg] });
    }
  },

  // 下拉刷新：清空对话，回到引导首页（体质评测入口）
  onPullDownRefresh() {
    const guideMsg = {
      id: 'msg-guide-' + Date.now(),
      type: 'assistant',
      text: '你好呀！我是小麦 🌾\n\n想知道自己是什么体质、该吃什么养生吗？\n\n📷 拍个照（舌苔/面色/皮肤/患处）\n📝 或做3分钟测评\n\n我帮你辨证，给你食疗方案！',
      showGuide: true
    };
    this.setData({
      messages: [guideMsg],
      sending: false,
      inputValue: '',
      pendingImage: '',
      pendingImages: []
    });
    wx.showToast({ title: '已刷新', icon: 'success', duration: 1000 });
    wx.stopPullDownRefresh();
  },

  // 引导按钮：去测评
  goTizhiTest() {
    wx.navigateTo({ url: '/pages/tizhi-test/tizhi-test' });
  },

  // 引导按钮：拍照扫描
  goPhotoScan() {
    this.chooseImage();
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value });
  },

  // 拍照/从相册选图（支持多张，最多4张）
  chooseImage() {
    if (this.data.sending) return;
    const already = this.data.pendingImages.length;
    const remain = Math.max(1, 4 - already);
    wx.chooseMedia({
      count: remain,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      sizeType: ['compressed'], // 压缩，减小base64体积
      camera: 'back',
      success: (res) => {
        const paths = (res.tempFiles || []).map(f => f.tempFilePath);
        this.setData({
          pendingImages: [...this.data.pendingImages, ...paths].slice(0, 4),
          pendingImage: paths[0] || ''
        });
      },
      fail: (err) => {
        if (err.errMsg && err.errMsg.indexOf('cancel') === -1) {
          wx.showToast({ title: '选择图片失败', icon: 'none' });
        }
      }
    });
  },

  // 清除某张待发送图片
  removePendingImage(e) {
    const idx = e.currentTarget.dataset.idx;
    const arr = this.data.pendingImages.slice();
    arr.splice(idx, 1);
    this.setData({ pendingImages: arr, pendingImage: arr[0] || '' });
  },

  // 清除待发送图片（兼容旧版）
  clearPendingImage() {
    this.setData({ pendingImage: '', pendingImages: [] });
  },

  // 点击预览大图（支持多图滑动）
  previewPendingImage(e) {
    const urls = this.data.pendingImages;
    if (!urls.length) return;
    const current = e && e.currentTarget && e.currentTarget.dataset.src ? e.currentTarget.dataset.src : urls[0];
    wx.previewImage({ urls: urls, current: current });
  },

  // 点击消息中的图片预览
  previewMsgImage(e) {
    const src = e.currentTarget.dataset.src;
    if (!src) return;
    wx.previewImage({ urls: [src] });
  },

  // 把图片文件转成 base64 data URI
  imageToBase64(filePath) {
    return new Promise((resolve, reject) => {
      const fs = wx.getFileSystemManager();
      fs.readFile({
        filePath: filePath,
        encoding: 'base64',
        success: (res) => {
          // 根据扩展名判断MIME
          let mime = 'image/jpeg';
          const lower = filePath.toLowerCase();
          if (lower.endsWith('.png')) mime = 'image/png';
          else if (lower.endsWith('.gif')) mime = 'image/gif';
          else if (lower.endsWith('.webp')) mime = 'image/webp';
          resolve('data:' + mime + ';base64,' + res.data);
        },
        fail: reject
      });
    });
  },

  // 对应 sendMessage()
  async sendMessage() {
    const message = this.data.inputValue.trim();
    const imagePaths = this.data.pendingImages.slice();
    const hasImage = imagePaths.length > 0;
    if ((!message && !hasImage) || this.data.sending) return;

    // 显示用户消息（带多张图片）
    const userMsg = {
      id: 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
      type: 'user',
      text: message || (hasImage ? '📷 [' + imagePaths.length + '张照片]' : ''),
      images: imagePaths,
      image: imagePaths[0] || ''
    };

    // 显示加载状态（对应 appendMessage('<div class="loading"></div>', 'assistant', true)）
    const loadingMsg = {
      id: 'msg-loading-' + Date.now(),
      type: 'assistant',
      text: '',
      loading: true
    };

    this.setData({
      messages: [...this.data.messages, userMsg, loadingMsg],
      inputValue: '',
      pendingImage: '',
      pendingImages: [],
      sending: true,
      // 先定位到用户消息（无动画），让用户看到自己发的内容
      scrollToId: userMsg.id
    });

    try {
      let data;
      if (hasImage) {
        // 多图辨证：全部转base64 → 调 /api/chat/vision（images数组）
        const base64List = await Promise.all(imagePaths.map(p => this.imageToBase64(p)));
        data = await request('/api/chat/vision', {
          method: 'POST',
          timeout: 90000, // vision 分析慢：LLM 45s + 商品搜索 10s + 余量
          data: {
            message: message || (base64List.length > 1
              ? '请综合观察这' + base64List.length + '张照片（舌苔/面色/皮肤/患处），多维度交叉分析，给出综合辨证和食疗建议。'
              : '请观察这张照片，从中医角度分析舌色、舌苔、舌形或面色、皮肤，给出体质倾向和食养建议。'),
            images: base64List,
            image_url: base64List[0],
            user_id: app.globalData.userId,
            session_id: app.globalData.sessionId
          }
        });
      } else {
        // 普通对话：调 /api/chat
        data = await request('/api/chat', {
          method: 'POST',
          data: {
            message: message,
            session_id: app.globalData.sessionId,
            user_id: app.globalData.userId
          }
        });
      }

      // 移除加载状态（对应 document.getElementById(loadingId).remove()）
      let msgs = this.data.messages.filter(m => !m.loading);

      // 后端返回 success:false（如 LLM 全部失败），视为失败，显示重试按钮
      if (data && data.success === false) {
        msgs.push({
          id: 'msg-err-' + Date.now(),
          type: 'assistant',
          text: data.reply || (hasImage ? '抱歉，图片分析失败。请确保图片清晰、光线充足，或直接用文字描述身体状况。' : '抱歉，服务暂时不可用，请稍后重试。'),
          showRetry: true,
          retryMessage: message,
          retryImages: imagePaths
        });
        this.setData({ messages: msgs, sending: false });
        return;
      }

      const replyText = data.reply || '';
      const products = data.products || [];
      const tizhi = data.tizhi || '';
      const zhengxing = data.zhengxing || '';
      const recommendations = data.recommendations || [];

      // 判断是否显示引导提问（统一一套，无论是否拍过照）
      const showFollowup = true;
      const followupChips = [
        '📷 再拍一张其他部位（面色/皮肤/患处）',
        '📝 帮我再做个3分钟体质评测',
        '🌾 给我推荐药膳食疗方案'
      ];

      // 显示AI回复 + 辨证结果卡片 + 引导提问 + 商品推荐
      const assistantMsg = {
        id: 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
        type: 'assistant',
        text: replyText,
        tizhi: tizhi,
        zhengxing: zhengxing,
        recommendations: recommendations,
        hasBianzheng: !!(tizhi || zhengxing),
        products: products,
        showFav: products.length > 0 || recommendations.length > 0,
        favorited: false,
        showFollowup: showFollowup,
        followupChips: followupChips,
        hasImage: hasImage
      };

      msgs.push(assistantMsg);

      this.setData({
        messages: msgs,
        sending: false,
        // 定位到用户消息（无动画）：看到自己输入+小麦回答，下滑看商品
        scrollToId: userMsg.id
      });

      // 保存对话记录（对应 saveChatRecord）
      try {
        this.saveChatRecord(message || '[图片辨证]', replyText, data.tizhi || '');
      } catch (e) {
        console.error('保存对话记录失败:', e);
      }

    } catch (err) {
      // 对应 catch 中的错误处理（只在请求真正失败时显示）
      let msgs = this.data.messages.filter(m => !m.loading);
      // 如果已经有AI回复了（说明请求成功但后续处理出错），不再追加错误消息
      const hasReply = msgs.some(m => m.type === 'assistant' && m.text && !m.loading);
      if (!hasReply) {
        msgs.push({
          id: 'msg-err-' + Date.now(),
          type: 'assistant',
          text: hasImage ? '抱歉，图片分析失败。请确保图片清晰、光线充足，或直接用文字描述身体状况。' : '抱歉，网络出现问题，请稍后重试。',
          showRetry: true,
          retryMessage: message,
          retryImages: imagePaths
        });
      }
      this.setData({ messages: msgs, sending: false });
      console.error('发送消息失败:', err);
    }
  },

  // 重试按钮（对应网页版 retryBtn.onclick）
  onRetry(e) {
    const idx = e.currentTarget.dataset.idx;
    const msg = this.data.messages[idx];
    if (!msg || !msg.showRetry) return;

    // 移除错误消息
    const msgs = this.data.messages.filter((m, i) => i !== idx);
    this.setData({
      messages: msgs,
      inputValue: msg.retryMessage || '',
      pendingImages: msg.retryImages || [],
      pendingImage: (msg.retryImages && msg.retryImages[0]) || ''
    });

    // 重新发送
    setTimeout(() => this.sendMessage(), 200);
  },

  // 对应 toggleChatFav（收藏对话+推荐商品）
  toggleChatFav(e) {
    const idx = e.currentTarget.dataset.idx;
    const msg = this.data.messages[idx];
    if (!msg) return;

    const isFav = msg.favorited;
    const key = 'messages[' + idx + '].favorited';

    if (isFav) {
      this.setData({ [key]: false });
    } else {
      this.setData({ [key]: true });
      // 收藏内容：用户问题+小麦回答+推荐商品（对应网页版 favData）
      const favData = {
        type: 'chat_with_products',
        userMessage: '',
        assistantReply: msg.text,
        products: msg.products,
        time: new Date().toISOString()
      };
      // 找最近的用户消息
      for (let i = idx - 1; i >= 0; i--) {
        if (this.data.messages[i].type === 'user') {
          favData.userMessage = this.data.messages[i].text;
          break;
        }
      }
      let favs = wx.getStorageSync('som_favorites') || [];
      favs.push(favData);
      wx.setStorageSync('som_favorites', favs);
    }
  },

  // 分享图（对应网页版 generateShareImage）
  onShareChatImage(e) {
    const idx = e.currentTarget.dataset.idx;
    const msg = this.data.messages[idx];
    if (!msg || !msg.text) return;

    wx.showLoading({ title: '生成分享图...' });

    const query = wx.createSelectorQuery();
    query.select('#chatShareCanvas').fields({ node: true, size: true }).exec((res) => {
      if (!res || !res[0] || !res[0].node) {
        wx.hideLoading();
        wx.showToast({ title: '生成失败', icon: 'none' });
        return;
      }
      const canvas = res[0].node;
      const ctx = canvas.getContext('2d');
      const dpr = wx.getWindowInfo().pixelRatio || 2;
      const W = 375;

      // 先算文字换行，确定高度
      const fontSize = 14, lineHeight = 22, padding = 30;
      const maxTextW = W - padding * 2;
      ctx.font = fontSize + 'px sans-serif';
      const rawLines = String(msg.text).split('\n');
      let lines = [];
      rawLines.forEach(raw => {
        let line = '';
        for (let i = 0; i < raw.length; i++) {
          const testLine = line + raw[i];
          if (ctx.measureText(testLine).width > maxTextW && line) {
            lines.push(line);
            line = raw[i];
          } else {
            line = testLine;
          }
        }
        lines.push(line);
      });
      // 最多显示30行，超出截断
      if (lines.length > 30) {
        lines = lines.slice(0, 30);
        lines.push('……（内容较长，扫码问小麦获取完整分析）');
      }

      const textH = lines.length * lineHeight;
      const H = 120 + textH + 170; // 头部 + 文字 + 底部（含免责声明+小程序码）

      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.scale(dpr, dpr);

      // 背景
      ctx.fillStyle = '#f0f7f0';
      ctx.fillRect(0, 0, W, H);

      // 顶部绿色条
      ctx.fillStyle = '#4a9d6e';
      ctx.fillRect(0, 0, W, 6);

      // 标题
      ctx.fillStyle = '#2c3e50';
      ctx.font = 'bold 18px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('🌿 小麦SOM · 中医养生分析', W / 2, 40);

      // 分割线
      ctx.strokeStyle = '#d4e8d4';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(padding, 55);
      ctx.lineTo(W - padding, 55);
      ctx.stroke();

      // 正文
      ctx.fillStyle = '#333';
      ctx.font = fontSize + 'px sans-serif';
      ctx.textAlign = 'left';
      let y = 80;
      lines.forEach(line => {
        ctx.fillText(line, padding, y);
        y += lineHeight;
      });

      // 底部引导
      ctx.textAlign = 'center';
      ctx.fillStyle = '#4a9d6e';
      ctx.font = 'bold 13px sans-serif';
      ctx.fillText('扫码问小麦，获取你的养生方案 →', W / 2, H - 130);

      ctx.fillStyle = '#999';
      ctx.font = '11px sans-serif';
      ctx.fillText('松麦SOM · 中医养生 · 有机生活', W / 2, H - 108);

      ctx.fillStyle = '#bbb';
      ctx.font = '10px sans-serif';
      ctx.fillText('som.top 养生文化参考 不构成医疗诊断', W / 2, H - 90);

      // 小程序码
      const qrImg = canvas.createImage();
      qrImg.src = '/images/qrcode.jpg';
      qrImg.onload = () => {
        const qrSize = 70;
        ctx.drawImage(qrImg, W / 2 - qrSize / 2, H - 80, qrSize, qrSize);

        this._shareCanvas = canvas;
        wx.hideLoading();

        // 弹出操作菜单
        wx.showActionSheet({
          itemList: ['💾 保存到相册', '📤 分享给朋友'],
          success: (res) => {
            if (res.tapIndex === 0) this._saveShareImage();
            else if (res.tapIndex === 1) this._shareToFriend();
          }
        });
      };
      qrImg.onerror = () => {
        // 二维码加载失败也要能继续
        this._shareCanvas = canvas;
        wx.hideLoading();
        wx.showActionSheet({
          itemList: ['💾 保存到相册', '📤 分享给朋友'],
          success: (res) => {
            if (res.tapIndex === 0) this._saveShareImage();
            else if (res.tapIndex === 1) this._shareToFriend();
          }
        });
      };
    });
  },

  _saveShareImage() {
    if (!this._shareCanvas) return;
    wx.canvasToTempFilePath({
      canvas: this._shareCanvas,
      success: (res) => {
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: () => wx.showToast({ title: '已保存到相册', icon: 'success' }),
          fail: () => wx.showToast({ title: '保存失败，请检查相册权限', icon: 'none' })
        });
      },
      fail: () => wx.showToast({ title: '生成失败', icon: 'none' })
    });
  },

  _shareToFriend() {
    if (!this._shareCanvas) return;
    wx.canvasToTempFilePath({
      canvas: this._shareCanvas,
      success: (res) => {
        wx.shareFileMessage({
          filePath: res.tempFilePath,
          fileName: 'som-analysis.png',
          success: () => {},
          fail: (err) => {
            if (err.errMsg && err.errMsg.indexOf('cancel') === -1) {
              wx.showToast({ title: '小程序未认证，暂不支持分享', icon: 'none' });
            }
          }
        });
      },
      fail: () => wx.showToast({ title: '生成失败', icon: 'none' })
    });
  },

  // 引导提问点击处理
  onFollowupChip(e) {
    const chip = e.currentTarget.dataset.chip;
    if (!chip) return;

    // 拍照类：直接唤起图片选择
    if (chip.indexOf('📷') === 0) {
      this.chooseImage();
      return;
    }
    // 测评类：跳体质测评页
    if (chip.indexOf('体质测评') >= 0) {
      wx.navigateTo({ url: '/pages/tizhi-test/tizhi-test' });
      return;
    }
    // 其他：填入输入框并发送
    this.setData({ inputValue: chip.replace(/^[\u{1F300}-\u{1FAFF}\u2600-\u27BF]\s*/u, '') });
    this.sendMessage();
  },

  // 对应 openProduct → showProductDetail
  openProductDetail(e) {
    const { msgIdx, prodIdx } = e.currentTarget.dataset;
    const msg = this.data.messages[msgIdx];
    if (!msg || !msg.products) return;
    const product = msg.products[prodIdx];
    if (!product) return;
    getApp().globalData.currentProduct = product;
    wx.navigateTo({ url: '/pages/product-detail/product-detail' });
  },

  // 图片加载失败（对应 onerror）
  onImgError(e) {
    // 小程序 image 组件不支持 onerror 替换，用默认占位
  },

  // 对应 saveChatRecord
  saveChatRecord(message, reply, tizhi) {
    const userId = app.globalData.userId;
    const key = 'som_user_data_' + userId;
    let data = wx.getStorageSync(key) || {};
    if (!data.name) data.name = '养生用户';
    if (!data.tizhi) data.tizhi = '未检测';
    if (!data.points) data.points = 0;
    if (!data.chats) data.chats = [];
    if (!data.checkins) data.checkins = [];
    if (!data.productBrowses) data.productBrowses = 0;
    if (!data.tizhiRecords) data.tizhiRecords = [];

    data.chats.push({
      date: new Date().toISOString(),
      message: message.substring(0, 100),
      tizhi: tizhi || ''
    });

    if (tizhi && tizhi !== '未检测') {
      data.tizhiRecords.push({
        date: new Date().toISOString().split('T')[0],
        tizhi: tizhi,
        desc: message.substring(0, 50)
      });
      data.tizhi = tizhi;
      // 同步体质记录到后端
      this.saveTizhiToBackend(tizhi, message);
    }

    wx.setStorageSync(key, data);
  },

  // 同步体质评测结果到后端
  saveTizhiToBackend(tizhi, symptoms) {
    request('/api/tizhi/save', {
      method: 'POST',
      data: {
        user_id: app.globalData.userId,
        tizhi: tizhi,
        symptoms: (symptoms || '').substring(0, 200),
        source: 'miniprogram_chat'
      }
    }).catch(err => {
      console.error('体质记录同步失败:', err);
    });
  }
});