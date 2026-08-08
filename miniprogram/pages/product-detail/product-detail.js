// 对应 app.js 中 showProductDetail / closeProductDetail / openProduct / toggleFavorite / saveProductBrowse
const { request } = require('../../utils/api');
const app = getApp();

Page({
  data: {
    product: {},
    allImgs: [],
    currentImgIdx: 0,
    favorited: false,
    autoplay: false
  },

  onLoad() {
    const product = app.globalData.currentProduct;
    if (!product) {
      wx.navigateBack();
      return;
    }

    // 对应 allImgs = [imgSrc, ...(product.images || [])].filter(Boolean)
    const imgSrc = product.image || '';
    const allImgs = [imgSrc, ...(product.images || [])].filter(Boolean);

    this.setData({
      product: product,
      allImgs: allImgs,
      autoplay: allImgs.length > 1
    });

    // 异步检查收藏状态（对应 fetch /api/favorites/check）
    const itemId = product.item_id || '';
    if (itemId) {
      request('/api/favorites/check?user_id=' + encodeURIComponent(app.globalData.userId) + '&item_id=' + encodeURIComponent(itemId))
        .then(data => {
          if (data.favorited) {
            this.setData({ favorited: true });
          }
        })
        .catch(() => {});
    }

    // 记录浏览（对应 saveProductBrowse(product.title || '', 1)）
    this.saveProductBrowse(1);
  },

  // 对应轮播切换（箭头/缩略图/自动轮播 → swiper bindchange）
  onSwiperChange(e) {
    // 防止 source 为空时的反馈循环（切后台恢复时触发）
    if (e.detail.source === 'touch' || e.detail.source === 'autoplay') {
      this.setData({ currentImgIdx: e.detail.current });
    }
  },

  // 切后台暂停轮播，防止恢复时闪烁
  onHide() {
    this.setData({ autoplay: false });
  },

  onShow() {
    if (this.data.allImgs.length > 1) {
      // 延迟恢复，等页面渲染稳定
      setTimeout(() => {
        this.setData({ autoplay: true });
      }, 300);
    }
  },

  // 对应 switchImg（缩略图点击）
  switchImg(e) {
    const idx = e.currentTarget.dataset.idx;
    this.setData({ currentImgIdx: idx });
  },

  // 对应图片点击预览（对应 window.open(imgSrc)）
  previewImage(e) {
    const idx = e.currentTarget.dataset.idx;
    wx.previewImage({
      current: this.data.allImgs[idx],
      urls: this.data.allImgs
    });
  },

  // 对应 openProduct → 生成淘口令并复制（打开淘宝APP自动弹出商品）
  buyProduct() {
    const product = this.data.product;
    const url = product.url || '';
    if (!url) {
      wx.showToast({ title: '暂无购买链接', icon: 'none' });
      return;
    }

    // 淘宝商品：生成淘口令
    if (product.platform === 'taobao' || !product.platform) {
      wx.showLoading({ title: '生成淘口令...' });
      request('/api/products/tpwd?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(product.title || ''))
        .then(data => {
          wx.hideLoading();
          const tpwd = data.model || data.tpwd || '';
          if (tpwd) {
            wx.setClipboardData({
              data: tpwd,
              success() {
                wx.showToast({ title: '淘口令已复制，打开淘宝APP即可查看', icon: 'none', duration: 2500 });
              }
            });
          } else {
            // 淘口令生成失败，降级复制链接
            wx.setClipboardData({
              data: url,
              success() {
                wx.showToast({ title: '链接已复制，打开淘宝APP即可查看', icon: 'none', duration: 2500 });
              }
            });
          }
        })
        .catch(() => {
          wx.hideLoading();
          // 接口异常，降级复制链接
          wx.setClipboardData({
            data: url,
            success() {
              wx.showToast({ title: '链接已复制，打开淘宝APP即可查看', icon: 'none', duration: 2500 });
            }
          });
        });
    } else {
      // 京东等其他平台：直接复制链接
      wx.setClipboardData({
        data: url,
        success() {
          wx.showToast({ title: '链接已复制，打开京东APP即可查看', icon: 'none', duration: 2500 });
        }
      });
    }
  },

  // 对应 toggleFavorite（收藏/取消收藏）
  toggleFavorite() {
    const product = this.data.product;
    const itemId = product.item_id || '';
    if (!itemId) return;

    const userId = app.globalData.userId;
    const isFav = this.data.favorited;

    if (isFav) {
      // 对应 fetch /api/favorites/remove
      request('/api/favorites/remove', {
        method: 'POST',
        data: { user_id: userId, item_id: itemId }
      }).then(() => {
        this.setData({ favorited: false });
      }).catch(() => {});
    } else {
      // 对应 fetch /api/favorites/add
      request('/api/favorites/add', {
        method: 'POST',
        data: {
          user_id: userId,
          item_id: itemId,
          title: product.title || '',
          price: product.price || '',
          image: product.image || '',
          url: product.url || '',
          platform: product.platform || 'taobao',
          shop_name: product.shop_name || ''
        }
      }).then(() => {
        this.setData({ favorited: true });
      }).catch(() => {});
    }
  },

  // 对应 saveProductBrowse
  saveProductBrowse(count) {
    const userId = app.globalData.userId;
    const key = 'som_user_data_' + userId;
    let data = wx.getStorageSync(key) || {};
    if (!data.productBrowses) data.productBrowses = 0;
    data.productBrowses += count;
    wx.setStorageSync(key, data);
  }
});