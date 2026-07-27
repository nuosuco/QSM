// 对应 app.js 中 initChat / sendMessage / appendMessage / escapeHtml / getSessionId
const { request } = require('../../utils/api');
const app = getApp();

Page({
  data: {
    messages: [],
    inputValue: '',
    sending: false,
    scrollToId: '',
    msgCounter: 0
  },

  onInput(e) {
    this.setData({ inputValue: e.detail.value });
  },

  // 对应 sendMessage()
  sendMessage() {
    const message = this.data.inputValue.trim();
    if (!message || this.data.sending) return;

    // 显示用户消息（对应 appendMessage(message, 'user')）
    const userMsg = {
      id: 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
      type: 'user',
      text: message
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
      sending: true,
      scrollToId: 'msg-' + loadingMsg.id
    });

    // 调用 /api/chat（对应 fetch(`${API_BASE}/api/chat`, ...)）
    request('/api/chat', {
      method: 'POST',
      data: {
        message: message,
        session_id: app.globalData.sessionId
      }
    }).then(data => {
      // 移除加载状态（对应 document.getElementById(loadingId).remove()）
      let msgs = this.data.messages.filter(m => !m.loading);

      const replyText = data.reply || '';
      const products = data.products || [];

      // 显示AI回复（对应 appendMessage(replyText, 'assistant')）
      const assistantMsg = {
        id: 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9),
        type: 'assistant',
        text: replyText,
        products: products,
        showFav: products.length > 0,
        favorited: false
      };

      msgs.push(assistantMsg);

      this.setData({
        messages: msgs,
        sending: false,
        scrollToId: 'msg-' + assistantMsg.id
      });

      // 保存对话记录（对应 saveChatRecord）
      try {
        this.saveChatRecord(message, replyText, data.tizhi || '');
      } catch (e) {
        console.error('保存对话记录失败:', e);
      }

    }).catch(err => {
      // 对应 catch 中的错误处理（只在请求真正失败时显示）
      let msgs = this.data.messages.filter(m => !m.loading);
      // 如果已经有AI回复了（说明请求成功但后续处理出错），不再追加错误消息
      const hasReply = msgs.some(m => m.type === 'assistant' && m.text && !m.loading);
      if (!hasReply) {
        msgs.push({
          id: 'msg-err-' + Date.now(),
          type: 'assistant',
          text: '抱歉，网络出现问题，请稍后重试。'
        });
      }
      this.setData({ messages: msgs, sending: false });
      console.error('发送消息失败:', err);
    });
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
    }

    wx.setStorageSync(key, data);
  }
});