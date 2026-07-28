// 对应 app.js 中 initProductSearch / loadCategories / displayCategories / searchByCategory / searchProducts / loadMoreProducts / displayProducts / setSort
const { request } = require('../../utils/api');
const app = getApp();

Page({
  data: {
    keyword: '',
    currentPlatform: 'taobao',
    currentCategory: '',
    currentSort: 'default',
    currentPage: 1,
    isLoading: false,
    hasMore: true,
    categories: [],
    products: [],
    loading: false
  },

  onLoad() {
    this.loadCategories();
  },

  // 对应 loadCategories()
  loadCategories() {
    request('/api/products/categories').then(data => {
      const categories = data.categories || [];
      this.setData({ categories });
      // 页面加载时自动显示"全部"分类的商品（对应 defaultCategory）
      if (categories.length > 0) {
        const defaultCategory = categories[0];
        this.searchByCategory({
          currentTarget: {
            dataset: { keyword: defaultCategory.keyword, name: defaultCategory.name }
          }
        });
      }
    }).catch(err => {
      console.error('加载分类失败:', err);
      this.setData({ categories: [] });
    });
  },

  // 对应 searchByCategory(keyword, categoryName)
  searchByCategory(e) {
    const keyword = e.currentTarget.dataset.keyword;
    this.setData({
      currentCategory: keyword,
      currentPage: 1,
      hasMore: true
    });
    // 搜索用分类关键词，但不显示在搜索框里
    this.searchProducts(true, keyword);
  },

  // 对应 searchInput 事件
  onSearchInput(e) {
    this.setData({ keyword: e.detail.value });
  },

  // 对应 searchBtn click / Enter
  doSearch() {
    this.setData({
      currentCategory: '',
      currentPage: 1,
      hasMore: true
    });
    this.searchProducts(true);
  },

  // 对应 filterBtn click（平台筛选）
  switchPlatform(e) {
    const platform = e.currentTarget.dataset.platform;
    this.setData({
      currentPlatform: platform,
      currentPage: 1,
      hasMore: true
    });
    if (this.data.currentCategory || this.data.keyword) {
      this.searchProducts(true);
    }
  },

  // 对应 sortBtn click（排序）
  switchSort(e) {
    const sort = e.currentTarget.dataset.sort;
    this.setData({
      currentSort: sort,
      currentPage: 1,
      hasMore: true
    });
    this.searchProducts(true);
  },

  // 对应 searchProducts(clear)
  searchProducts(clear, keywordOverride) {
    if (this.data.isLoading) return;

    this.setData({ isLoading: true, loading: true });

    if (clear) {
      this.setData({ products: [] });
    }

    // 搜索关键词优先级：显式传入 > 当前分类 > 搜索框输入
    const { keyword, currentCategory, currentPlatform, currentPage, currentSort } = this.data;
    const searchKeyword = keywordOverride || currentCategory || keyword;
    const sortParam = currentSort !== 'default' ? '&sort=' + currentSort : '';

    request('/api/products/search?keyword=' + encodeURIComponent(searchKeyword) + '&platform=' + currentPlatform + '&page=' + currentPage + '&page_size=20' + sortParam)
      .then(data => {
        const items = data.items || [];
        if (items.length > 0) {
          const newProducts = clear ? items : [...this.data.products, ...items];
          this.setData({
            products: newProducts,
            hasMore: items.length >= 20,
            currentPage: currentPage + 1
          });
        } else {
          this.setData({ hasMore: false });
        }
      })
      .catch(err => {
        console.error('搜索商品失败:', err);
        if (clear) {
          this.setData({ products: [] });
        }
      })
      .finally(() => {
        this.setData({ isLoading: false, loading: false });
      });
  },

  // 对应 loadMoreProducts()（无限滚动 → 小程序用点击加载）
  loadMore() {
    if (!this.data.hasMore || this.data.isLoading) return;
    this.searchProducts(false);
  },

  // 对应 openProduct → showProductDetail
  openProductDetail(e) {
    const idx = e.currentTarget.dataset.index;
    const product = this.data.products[idx];
    if (!product) return;
    getApp().globalData.currentProduct = product;
    // 记录浏览（对应 saveProductBrowse），出错不阻塞跳转
    try {
      this.saveProductBrowse(1);
    } catch (err) {
      console.error('保存浏览记录失败:', err);
    }
    wx.navigateTo({ url: '/pages/product-detail/product-detail' });
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