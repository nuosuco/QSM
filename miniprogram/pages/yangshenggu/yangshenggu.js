// 对应养生谷页面：从后端 /api/knowledge/tizhi 和 /api/knowledge/yaoshi 加载
const { request } = require('../../utils/api');

Page({
  data: {
    tizhiList: [],
    yaoshiList: [],
    loading: true
  },

  onLoad() {
    this.loadKnowledge();
  },

  loadKnowledge() {
    this.setData({ loading: true });

    // 并行加载（对应网页版同时请求两个API）
    Promise.all([
      request('/api/knowledge/tizhi').catch(err => {
        console.error('加载体质失败:', err);
        return { items: [] };
      }),
      request('/api/knowledge/yaoshi').catch(err => {
        console.error('加载药食同源失败:', err);
        return { items: [] };
      })
    ]).then(([tizhiData, yaoshiData]) => {
      this.setData({
        tizhiList: tizhiData.items || tizhiData.list || [],
        yaoshiList: yaoshiData.items || yaoshiData.list || [],
        loading: false
      });
    });
  }
});