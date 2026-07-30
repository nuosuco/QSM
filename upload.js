const ci = require('/root/.nvm/versions/node/v22.22.3/lib/node_modules/miniprogram-ci');

async function upload() {
  const project = new ci.Project({
    appid: 'wx84b342b2152da666',
    type: 'miniProgram',
    projectPath: '/root/SOM/miniprogram',
    privateKeyPath: '/root/SOM/miniprogram/private.key',
    ignores: ['node_modules/**/*', '*.bak*'],
  });

  const uploadResult = await ci.upload({
    project,
    version: '1.0.7',
    desc: '健康测评闭环：AI拍照扫描+体质答题+症状自评+分享图裂变+小麦对话对接+vision会话历史+商品推荐',
    setting: {
      es6: true,
      es7: true,
      minify: true,
      autoPrefixWXSS: true,
    },
    onProgressUpdate: console.log,
  });

  console.log('上传结果:', JSON.stringify(uploadResult, null, 2));
}

upload().catch(err => {
  console.error('上传失败:', err.message);
  process.exit(1);
});
