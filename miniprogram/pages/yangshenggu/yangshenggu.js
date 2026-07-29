// 养生谷：节气养生 + 护眼训练 + 九种体质 + 药食同源
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
