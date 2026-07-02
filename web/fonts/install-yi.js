/**
 * 滇川黔贵通用彝文字体自动安装器
 * 支持: Windows, macOS, Linux, Android, iOS
 */

class YiFontInstaller {
 constructor() {
 this.fontName = 'YiTongyong';
 this.fontUrl = '/fonts/lingyi.ttf';
 this.installed = false;
 }
 
 // 检测设备类型
 detectDevice() {
 const ua = navigator.userAgent;
 if (/iPhone|iPad|iPod/.test(ua)) return 'ios';
 if (/Android/.test(ua)) return 'android';
 if (/Windows/.test(ua)) return 'windows';
 if (/Mac/.test(ua)) return 'macos';
 if (/Linux/.test(ua)) return 'linux';
 return 'unknown';
 }
 
 // 检测字体是否已安装
 async checkFontInstalled() {
 try {
 await document.fonts.load('48px YiTongyong');
 this.installed = document.fonts.check('48px YiTongyong');
 } catch (e) {
 this.installed = false;
 }
 return this.installed;
 }
 
 // 下载字体文件
 downloadFont() {
 const link = document.createElement('a');
 link.href = this.fontUrl;
 link.download = 'lingyi通用彝文.ttf';
 document.body.appendChild(link);
 link.click();
 document.body.removeChild(link);
 }
 
 // 获取安装指南
 getInstallGuide() {
 const device = this.detectDevice();
 const guides = {
 ios: {
 title: 'iOS设备安装指南',
 steps: [
 '1. 点击下载字体文件',
 '2. 打开"文件"APP，找到下载的字体',
 '3. 点击字体文件，选择"安装"',
 '4. 前往 设置 > 通用 > 描述文件，安装字体描述文件',
 '5. 重启浏览器刷新页面'
 ]
 },
 android: {
 title: 'Android设备安装指南',
 steps: [
 '1. 点击下载字体文件',
 '2. 打开"爱字体"或"字体管家"APP',
 '3. 选择"本地字体"，找到下载的字体',
 '4. 点击应用，重启设备',
 '5. 刷新页面查看效果'
 ]
 },
 windows: {
 title: 'Windows系统安装指南',
 steps: [
 '1. 点击下载字体文件',
 '2. 右键点击字体文件',
 '3. 选择"为所有用户安装"',
 '4. 等待安装完成',
 '5. 刷新浏览器页面'
 ]
 },
 macos: {
 title: 'macOS系统安装指南',
 steps: [
 '1. 点击下载字体文件',
 '2. 双击字体文件打开"字体册"',
 '3. 点击"安装字体"',
 '4. 等待安装完成',
 '5. 刷新浏览器页面'
 ]
 },
 linux: {
 title: 'Linux系统安装指南',
 steps: [
 '1. 点击下载字体文件',
 '2. 将字体复制到 ~/.local/share/fonts/',
 '3. 运行: fc-cache -fv',
 '4. 重启浏览器'
 ]
 }
 };
 return guides[device] || guides.windows;
 }
 
 // 显示安装界面
 showInstallUI(containerId) {
 const container = document.getElementById(containerId);
 if (!container) return;
 
 const device = this.detectDevice();
 const guide = this.getInstallGuide();
 
 container.innerHTML = `
 <div style="font-family:-apple-system,sans-serif;max-width:500px;margin:20px auto;padding:20px;background:#1a1a2e;border-radius:15px;color:#fff;">
 <h2 style="color:#4ecdc4;text-align:center;margin-bottom:20px;">🔤 彝文字体安装</h2>
 
 <div style="text-align:center;padding:20px;background:rgba(255,230,109,0.1);border-radius:10px;margin:15px 0;">
 <div style="font-family:'YiTongyong',sans-serif;font-size:36px;color:#ffe66d;">心 天 火 王 纠缠</div>
 <p style="color:#888;font-size:12px;">↑ 如果显示为方框，说明需要安装字体</p>
 </div>
 
 <div style="background:rgba(78,205,196,0.1);padding:15px;border-radius:10px;margin:15px 0;">
 <h3 style="color:#4ecdc4;margin:0 0 10px 0;">${guide.title}</h3>
 <ol style="margin:0;padding-left:20px;color:#aaa;">
 ${guide.steps.map(s => `<li style="margin:8px 0;">${s}</li>`).join('')}
 </ol>
 </div>
 
 <div style="text-align:center;margin-top:20px;">
 <button onclick="yiInstaller.downloadFont();" style="background:linear-gradient(135deg,#4ecdc4,#44a08d);color:#fff;border:none;padding:15px 40px;border-radius:25px;font-size:16px;cursor:pointer;margin:10px;">📥 下载字体</button>
 <button onclick="location.reload();" style="background:linear-gradient(135deg,#ffe66d,#ff6b6b);color:#1a1a2e;border:none;padding:15px 40px;border-radius:25px;font-size:16px;cursor:pointer;margin:10px;">🔄 刷新页面</button>
 </div>
 
 <p style="text-align:center;color:#666;font-size:12px;margin-top:20px;">
 设备类型: ${device.toUpperCase()} | 字体: lingyi通用彝文（黑）
 </p>
 </div>
 `;
 }
}

// 全局实例
const yiInstaller = new YiFontInstaller();

// 导出
if (typeof window !== 'undefined') {
 window.YiFontInstaller = YiFontInstaller;
 window.yiInstaller = yiInstaller;
}
