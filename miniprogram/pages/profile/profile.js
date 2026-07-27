// 对应 app.js 中 initProfile / loadProfile / getUserId / getUserData / loadTizhiRecords
const app = getApp();

Page({
  data: {
    userData: {
      name: '养生用户',
      tizhi: '未检测',
      points: 0
    },
    checkedInToday: false,
    tizhiRecords: [],
    stats: {
      chats: 0,
      checkins: 0,
      products: 0
    }
  },

  onShow() {
    // 每次显示时刷新（对应 loadProfile）
    this.loadProfile();
  },

  // 对应 getUserId()
  getUserId() {
    return app.globalData.userId;
  },

  // 对应 getUserData()
  getUserData() {
    const key = 'som_user_data_' + this.getUserId();
    let data = wx.getStorageSync(key) || {};
    if (!data.name) data.name = '养生用户';
    if (!data.tizhi) data.tizhi = '未检测';
    if (!data.points) data.points = 0;
    if (!data.chats) data.chats = [];
    if (!data.checkins) data.checkins = [];
    if (!data.productBrowses) data.productBrowses = 0;
    if (!data.tizhiRecords) data.tizhiRecords = [];
    return data;
  },

  // 对应 loadProfile()
  loadProfile() {
    const data = this.getUserData();

    const today = new Date().toISOString().split('T')[0];
    const checkedInToday = data.checkins && data.checkins.indexOf(today) >= 0;

    // 对应 loadTizhiRecords：只显示最近5条
    const records = data.tizhiRecords || [];
    const maxShow = Math.min(records.length, 5);
    const tizhiRecords = records.slice(records.length - maxShow);

    this.setData({
      userData: {
        name: data.name,
        tizhi: data.tizhi || '未检测',
        points: data.points || 0
      },
      checkedInToday: checkedInToday,
      tizhiRecords: tizhiRecords,
      stats: {
        chats: (data.chats || []).length,
        checkins: (data.checkins || []).length,
        products: data.productBrowses || 0
      }
    });
  }
});