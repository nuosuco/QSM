// SOM 松麦 - 小程序全局
App({
  globalData: {
    baseUrl: 'https://som.top',
    userId: '',
    sessionId: ''
  },
  onLaunch(options) {
    // 获取/生成用户ID（对应网页版 getUserId）
    let uid = wx.getStorageSync('som_user_id');
    if (!uid) {
      uid = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      wx.setStorageSync('som_user_id', uid);
    }
    this.globalData.userId = uid;

    // 获取/生成会话ID（对应网页版 getSessionId）
    let sid = wx.getStorageSync('som_session_id');
    if (!sid) {
      sid = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
      wx.setStorageSync('som_session_id', sid);
    }
    this.globalData.sessionId = sid;

    // 处理分享图小程序码扫码进入（scene=tizhi_qixu 等）
    if (options && options.scene) {
      const scene = decodeURIComponent(options.scene);
      // scene格式: tizhi_qixu / symptom_tongfeng 等
      if (scene.startsWith('tizhi_') || scene.startsWith('symptom_')) {
        this.globalData.pendingScene = scene;
      }
    }
  }
})