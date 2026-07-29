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
    pendingImage: '' // 待发送的图片临时路径
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value });
  },

  // 拍照/从相册选图（对应网页版 upload-btn）
  chooseImage() {
    if (this.data.sending) return;
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      sizeType: ['compressed'], // 压缩，减小base64体积
      camera: 'back',
      success: (res) => {
        const tempPath = res.tempFiles[0].tempFilePath;
        this.setData({ pendingImage: tempPath });
      },
      fail: (err) => {
        if (err.errMsg && err.errMsg.indexOf('cancel') === -1) {
          wx.showToast({ title: '选择图片失败', icon: 'none' });
        }
      }
    });
  },

  // 清除待发送图片（对应网页版 preview-remove）
  clearPendingImage() {
    this.setData({ pendingImage: '' });
  },

  // 点击预览大图
  previewPendingImage() {
    if (!this.data.pendingImage) return;
    wx.previewImage({ urls: [this.data.pendingImage] });
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
    const hasImage = !!this.data.pendingImage;
    if ((!message && !hasImage) || this.data.sending) return;

    // 显示用户消息（带图片）
    const userMsg = {
      id: 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
      type: 'user',
      text: message || (hasImage ? '📷 [舌苔照片]' : ''),
      image: hasImage ? this.data.pendingImage : ''
    };

    // 显示加载状态（对应 appendMessage('<div class="loading"></div>', 'assistant', true)）
    const loadingMsg = {
      id: 'msg-loading-' + Date.now(),
      type: 'assistant',
      text: '',
      loading: true
    };

    const imagePath = this.data.pendingImage;

    this.setData({
      messages: [...this.data.messages, userMsg, loadingMsg],
      inputValue: '',
      pendingImage: '',
      sending: true,
      // 先定位到用户消息（无动画），让用户看到自己发的内容
      scrollToId: userMsg.id
    });

    try {
      let data;
      if (hasImage) {
        // 图片辨证：转base64 → 调 /api/chat/vision
        const base64Uri = await this.imageToBase64(imagePath);
        data = await request('/api/chat/vision', {
          method: 'POST',
          data: {
            message: message || '请观察这张舌头照片，从中医角度分析舌色、舌苔、舌形，给出体质倾向和食养建议。',
            image_url: base64Uri,
            user_id: app.globalData.userId
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

      const replyText = data.reply || '';
      const products = data.products || [];
      const tizhi = data.tizhi || '';
      const zhengxing = data.zhengxing || '';
      const recommendations = data.recommendations || [];

      // 显示AI回复 + 辨证结果卡片
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
        favorited: false
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
          text: hasImage ? '抱歉，图片分析失败。请确保图片清晰、光线充足，或直接用文字描述身体状况。' : '抱歉，网络出现问题，请稍后重试。'
        });
      }
      this.setData({ messages: msgs, sending: false });
      console.error('发送消息失败:', err);
    }
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