const ci = require('/root/.nvm/versions/node/v22.22.3/lib/node_modules/miniprogram-ci');
const path = require('path');

(async () => {
  const project = new ci.Project({
    appid: 'wx84b342b2152da666',
    type: 'miniProgram',
    projectPath: path.resolve(__dirname),
    privateKeyPath: path.resolve(__dirname, 'private.key'),
    ignores: ['node_modules/**/*'],
  });

  const uploadResult = await ci.upload({
    project,
    version: '1.0.11',
    desc: '小程序三引导提问样式+正则修复+后端推荐引导语优化',
    setting: {
      es6: true,
      minify: true,
      minifyWXSS: true,
      minifyWXML: true,
    },
    onProgressUpdate: console.log,
  });

  console.log('上传完成！', uploadResult);
})();
