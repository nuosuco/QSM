// 对应 app.js 中 initProfile / loadProfile / getUserId / getUserData / loadTizhiRecords
const { request } = require('../../utils/api');
const app = getApp();

Page({
  data: {
    isLoggedIn: false,
    loginChannel: 'sms',
    phone: '',
    smsCode: '',
    email: '',
    emailCode: '',
    loginError: '',
    codeCooldown: 0,
    countryIdx: 0,
    countryList: [
      { label: '🇨🇳 +86', code: '+86' },
      { label: '🇺🇸 +1', code: '+1' },
      { label: '🇬🇧 +44', code: '+44' },
      { label: '🇯🇵 +81', code: '+81' },
      { label: '🇰🇷 +82', code: '+82' },
      { label: '🇸🇬 +65', code: '+65' },
      { label: '🇦🇺 +61', code: '+61' },
      { label: '🇩🇪 +49', code: '+49' },
      { label: '🇫🇷 +33', code: '+33' },
      { label: '🇷🇺 +7', code: '+7' },
      { label: '🇮🇳 +91', code: '+91' },
      { label: '🇧🇷 +55', code: '+55' },
      { label: '🇦🇪 +971', code: '+971' },
      { label: '🇲🇾 +60', code: '+60' },
      { label: '🇹🇭 +66', code: '+66' },
      { label: '🇻🇳 +84', code: '+84' },
      { label: '🇮🇩 +62', code: '+62' },
      { label: '🇵🇭 +63', code: '+63' },
      { label: '🇳🇿 +64', code: '+64' },
      { label: '🇮🇹 +39', code: '+39' },
      { label: '🇪🇸 +34', code: '+34' },
      { label: '🇹🇷 +90', code: '+90' }
    ],
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
    // 每次显示时刷新登录状态和数据
    this.setData({ isLoggedIn: !!wx.getStorageSync('som_auth_token') });
    this.loadProfile();
  },

  // ========== 登录相关 ==========

  switchChannel(e) {
    this.setData({ loginChannel: e.currentTarget.dataset.ch, loginError: '' });
  },

  onPhoneInput(e) { this.setData({ phone: e.detail.value }); },
  onSmsCodeInput(e) { this.setData({ smsCode: e.detail.value }); },
  onEmailInput(e) { this.setData({ email: e.detail.value }); },
  onEmailCodeInput(e) { this.setData({ emailCode: e.detail.value }); },
  onCountryChange(e) { this.setData({ countryIdx: parseInt(e.detail.value) }); },

  async sendCode() {
    const { loginChannel, phone, email, countryList, countryIdx } = this.data;
    let target = loginChannel === 'sms' ? phone.trim() : email.trim();
    if (!target) {
      this.setData({ loginError: loginChannel === 'sms' ? '请输入手机号' : '请输入邮箱' });
      return;
    }

    try {
      const data = await request('/api/auth/send-code', {
        method: 'POST',
        data: {
          target,
          channel: loginChannel,
          country_code: countryList[countryIdx].code
        }
      });
      if (data.success) {
        wx.showToast({ title: '验证码已发送', icon: 'success' });
        // 倒计时
        this.setData({ codeCooldown: 60 });
        this._timer = setInterval(() => {
          const cd = this.data.codeCooldown - 1;
          if (cd <= 0) {
            clearInterval(this._timer);
            this.setData({ codeCooldown: 0 });
          } else {
            this.setData({ codeCooldown: cd });
          }
        }, 1000);
      } else {
        this.setData({ loginError: data.error || '发送失败' });
      }
    } catch (e) {
      this.setData({ loginError: '网络错误，请重试' });
    }
  },

  async doLogin() {
    const { loginChannel, phone, smsCode, email, emailCode, countryList, countryIdx } = this.data;
    let target, code;
    if (loginChannel === 'sms') {
      target = phone.trim();
      code = smsCode.trim();
      if (!target) { this.setData({ loginError: '请输入手机号' }); return; }
      if (!code) { this.setData({ loginError: '请输入验证码' }); return; }
    } else {
      target = email.trim();
      code = emailCode.trim();
      if (!target) { this.setData({ loginError: '请输入邮箱' }); return; }
      if (!code) { this.setData({ loginError: '请输入验证码' }); return; }
    }

    try {
      const data = await request('/api/auth/login', {
        method: 'POST',
        data: {
          target, code,
          channel: loginChannel,
          country_code: countryList[countryIdx].code,
          anonymous_user_id: app.globalData.userId
        }
      });
      if (data.success) {
        wx.setStorageSync('som_auth_token', data.token);
        wx.setStorageSync('som_auth_user', data.user);
        if (data.user && data.user.user_id) {
          app.globalData.userId = data.user.user_id;
        }
        this.setData({ isLoggedIn: true, loginError: '' });
        this.loadProfile();
        wx.showToast({ title: '登录成功', icon: 'success' });
      } else {
        this.setData({ loginError: data.error || '登录失败' });
      }
    } catch (e) {
      this.setData({ loginError: '网络错误，请重试' });
    }
  },

  doLogout() {
    wx.showModal({
      title: '提示',
      content: '确定退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('som_auth_token');
          wx.removeStorageSync('som_auth_user');
          this.setData({ isLoggedIn: false });
          this.loadProfile();
        }
      }
    });
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