// SOM 松麦 - API工具（对应网页版 fetch 调用）
const app = getApp();

function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: app.globalData.baseUrl + url,
      method: options.method || 'GET',
      data: options.data || {},
      header: options.header || { 'Content-Type': 'application/json' },
      timeout: options.timeout || 45000,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(new Error('HTTP ' + res.statusCode));
        }
      },
      fail(err) {
        reject(err);
      }
    });
  });
}

module.exports = { request };