// 健康测评：体质测评 + 症状自评 → 分享图裂变 → 对接小麦
const { request } = require('../../utils/api');

// 九种体质测评题目
const TIZHI_QUESTIONS = [
  { q: '你容易感到疲乏、气短吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { qixu: [0, 1, 2, 3] } },
  { q: '你手脚容易发凉、怕冷吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { yangxu: [0, 1, 2, 3] } },
  { q: '你手心脚心容易发热、口干吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { yinxu: [0, 1, 2, 3] } },
  { q: '你体型偏胖、腹部松软、痰多吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { tanshi: [0, 1, 2, 3] } },
  { q: '你面部容易出油、口苦、大便黏滞吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { shire: [0, 1, 2, 3] } },
  { q: '你皮肤容易出现瘀斑、面色晦暗吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { xueyu: [0, 1, 2, 3] } },
  { q: '你容易情绪低落、多愁善感、胸闷叹气吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { qiyu: [0, 1, 2, 3] } },
  { q: '你容易过敏（食物、药物、花粉等）吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { tebing: [0, 1, 2, 3] } },
  { q: '你精力充沛、睡眠好、适应力强吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { pinghe: [0, 1, 2, 3] } },
  { q: '你容易头晕、站起时眼前发黑吗？', options: ['从不', '偶尔', '经常', '总是'], scores: { qixu: [0, 1, 2, 3], yangxu: [0, 0, 1, 2] } }
];

// 症状自评题目（三高/痛风/风湿/失眠/疲劳/脾胃）
const SYMPTOM_QUESTIONS = [
  { q: '你经常头晕、头痛、耳鸣吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaoya: [0, 1, 2, 3] } },
  { q: '你容易面红耳赤、急躁易怒吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaoya: [0, 1, 2, 3] } },
  { q: '你经常口渴、多饮、多尿吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaotang: [0, 1, 2, 3] } },
  { q: '你容易饿、吃得多但体重下降吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaotang: [0, 1, 2, 3] } },
  { q: '你视力模糊、伤口愈合慢、手脚发麻吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { tangniao: [0, 1, 2, 3] } },
  { q: '你体检发现血脂偏高、容易胸闷吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { gaozhi: [0, 1, 2, 3] } },
  { q: '你关节（尤其大脚趾）红肿热痛、夜间发作过吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { tongfeng: [0, 1, 2, 3] } },
  { q: '你爱吃海鲜、喝啤酒、吃动物内脏吗？', options: ['很少', '偶尔', '经常', '天天'], scores: { tongfeng: [0, 1, 2, 3] } },
  { q: '你关节晨僵、遇冷疼痛加重、游走性疼痛吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { fengshi: [0, 1, 2, 3] } },
  { q: '你入睡困难、易醒、多梦、睡眠质量差吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { shimian: [0, 1, 2, 3] } },
  { q: '你持续疲倦、注意力下降、怎么睡都不够吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { pilao: [0, 1, 2, 3] } },
  { q: '你容易腹胀、大便稀溏、食欲差吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { piwei: [0, 1, 2, 3] } },
  { q: '你肢体麻木、沉重、像裹了湿布吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { fengshi: [0, 1, 2, 3], piwei: [0, 0, 1, 2] } },
  { q: '你体检发现尿酸偏高吗？', options: ['正常', '临界', '偏高', '很高'], scores: { tongfeng: [0, 1, 2, 3] } },
  { q: '你血压测量经常超过 140/90 吗？', options: ['正常', '临界', '偏高', '很高'], scores: { gaoya: [0, 1, 2, 3] } },
  { q: '你空腹血糖经常超过 6.1 吗？', options: ['正常', '临界', '偏高', '很高'], scores: { gaotang: [0, 1, 2, 3] } },
  { q: '你已被诊断为糖尿病或糖耐量异常吗？', options: ['没有', '临界', '已确诊', '多年'], scores: { tangniao: [0, 1, 2, 3] } },
  { q: '你尿频、尿急、夜尿多、排尿无力吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { qianlie: [0, 1, 2, 3] } },
  { q: '你会阴部坠胀、腰骶酸痛、久坐加重吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { qianlie: [0, 1, 2, 3] } },
  { q: '你皮肤瘙痒、起疹、反复发作吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { pifu: [0, 1, 2, 3] } },
  { q: '你皮肤干燥脱屑、遇热或出汗加重吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { pifu: [0, 1, 2, 3] } },
  { q: '你手脚冰凉、麻木、青筋凸起、静脉曲张吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { xueye: [0, 1, 2, 3] } },
  { q: '你蹲下站起头晕、面色苍白、心悸气短吗？', options: ['没有', '偶尔', '经常', '很严重'], scores: { xueye: [0, 1, 2, 3] } }
];

// 体质结果模板
const TIZHI_RESULTS = {
  qixu: { name: '气虚质', emoji: '😮‍💨', symptoms: ['容易累', '气短懒言', '爱感冒', '面色偏黄'], desc: '元气不足，脏腑功能偏弱。', diet: '黄芪炖鸡、山药薏米粥、红枣桂圆茶', avoid: '生冷寒凉、过度劳累、大汗运动', life: '早睡早起，适度散步，避免过劳' },
  yangxu: { name: '阳虚质', emoji: '🥶', symptoms: ['怕冷', '手脚冰凉', '喜热饮', '大便稀溏'], desc: '阳气不足，畏寒怕冷。', diet: '当归生姜羊肉汤、桂圆红枣茶、韭菜炒核桃', avoid: '冰饮、寒凉水果、空调直吹', life: '多晒太阳，温水泡脚，冬季进补' },
  yinxu: { name: '阴虚质', emoji: '🔥', symptoms: ['手心发热', '口干', '盗汗', '失眠多梦'], desc: '阴液亏少，虚火内生。', diet: '银耳百合羹、枸杞菊花茶、桑葚粥', avoid: '辛辣煎炸、熬夜、过度出汗', life: '早睡养阴，静养为主，避免燥热' },
  tanshi: { name: '痰湿质', emoji: '🫧', symptoms: ['体型偏胖', '痰多', '身体沉重', '面部油腻'], desc: '痰湿凝聚，脾运不健。', diet: '薏米赤小豆汤、陈皮茯苓茶、冬瓜荷叶汤', avoid: '甜腻油炸、酒、久坐不动', life: '多运动出汗，饮食清淡，控制体重' },
  shire: { name: '湿热质', emoji: '🌡️', symptoms: ['面油口苦', '大便黏滞', '小便黄', '易长痘'], desc: '湿热内蕴，缠绵难解。', diet: '绿豆薏米汤、苦瓜凉拌、茵陈茶', avoid: '辛辣油腻、酒、熬夜', life: '清淡饮食，多运动，避免潮湿环境' },
  xueyu: { name: '血瘀质', emoji: '🩸', symptoms: ['面色晦暗', '皮肤瘀斑', '痛经', '唇色暗'], desc: '血行不畅，瘀血内阻。', diet: '山楂红糖水、玫瑰花茶、黑木耳炒山药', avoid: '久坐不动、寒凉收引、情绪压抑', life: '多运动促循环，保持心情舒畅' },
  qiyu: { name: '气郁质', emoji: '😔', symptoms: ['情绪低落', '胸闷叹气', '多愁善感', '咽中异物感'], desc: '气机郁滞，情志不畅。', diet: '玫瑰花茶、佛手柑粥、合欢花饮', avoid: '压抑情绪、独处过久、咖啡因过量', life: '多社交，培养爱好，适当运动释放' },
  tebing: { name: '特禀质', emoji: '🤧', symptoms: ['易过敏', '打喷嚏', '皮肤起疹', '适应力差'], desc: '先天禀赋异常，易过敏。', diet: '黄芪红枣粥、蜂蜜水、山药莲子汤', avoid: '已知过敏原、辛辣刺激、环境突变', life: '远离过敏原，增强体质，规律作息' },
  pinghe: { name: '平和质', emoji: '😊', symptoms: ['精力充沛', '睡眠好', '适应力强', '面色红润'], desc: '阴阳气血调和，最健康的体质。', diet: '均衡饮食即可，无需特殊调理', avoid: '暴饮暴食、熬夜、过度劳累', life: '保持现有好习惯，顺应节气养生' }
};

// 症状结果模板
const SYMPTOM_RESULTS = {
  gaoya: { name: '高血压倾向', emoji: '🔴', symptoms: ['头晕头痛', '耳鸣', '面红易怒', '血压偏高'], desc: '肝阳上亢或痰湿阻络，血压调节失衡。', diet: '芹菜汁、山楂决明子茶、天麻炖鱼头', avoid: '高盐饮食、烟酒、情绪激动、熬夜', life: '低盐低脂，每日散步30分钟，监测血压' },
  gaotang: { name: '高血糖倾向', emoji: '🟠', symptoms: ['多饮多尿', '容易饿', '体重下降', '血糖偏高'], desc: '阴虚燥热，脾失运化，糖代谢异常。', diet: '苦瓜炒蛋、山药薏米粥、玉米须茶', avoid: '甜食精米面、含糖饮料、油炸食品', life: '控制碳水，餐后散步，定期测血糖' },
  tangniao: { name: '糖尿病倾向', emoji: '🔶', symptoms: ['三多一少', '视力模糊', '伤口愈合慢', '手脚发麻'], desc: '消渴证，阴虚燥热日久，累及肝肾，并发症风险高。', diet: '苦瓜排骨汤、黄精枸杞茶、荞麦面、山药薏米粥', avoid: '白糖红糖、精白米面、高糖水果、油炸食品', life: '严格控糖，餐后步行20分钟，定期查糖化血红蛋白' },
  gaozhi: { name: '高血脂倾向', emoji: '🟡', symptoms: ['头晕胸闷', '肢体麻木', '血脂偏高', '体型偏胖'], desc: '痰浊瘀阻，脂代谢紊乱。', diet: '山楂荷叶茶、黑木耳炒洋葱、燕麦粥', avoid: '动物内脏、油炸食品、奶油甜点', life: '有氧运动，控制体重，少油少盐' },
  tongfeng: { name: '高尿酸/痛风倾向', emoji: '🟣', symptoms: ['关节红肿热痛', '夜间发作', '尿酸偏高', '爱吃海鲜啤酒'], desc: '湿热瘀阻，尿酸代谢异常，浊毒留滞关节。', diet: '薏米赤小豆汤、芹菜汁、玉米须茶、冬瓜汤', avoid: '海鲜、啤酒、动物内脏、浓肉汤、火锅', life: '多喝水（每日2000ml+），低嘌呤饮食，控制体重' },
  fengshi: { name: '风湿/类风湿倾向', emoji: '🔵', symptoms: ['关节晨僵', '遇冷加重', '游走性疼痛', '肢体沉重'], desc: '风寒湿邪痹阻经络，气血运行不畅。', diet: '当归生姜羊肉汤、薏米粥、桂枝茶', avoid: '寒凉食物、冷水、潮湿环境', life: '保暖避寒，适度关节活动，热敷缓解' },
  shimian: { name: '失眠倾向', emoji: '⚪', symptoms: ['入睡困难', '易醒多梦', '白天疲倦', '心烦焦虑'], desc: '心脾两虚或肝火扰心，神不安舍。', diet: '酸枣仁百合汤、桂圆莲子粥、小米红枣粥', avoid: '咖啡浓茶（下午后）、睡前刷手机、过饱', life: '固定作息时间，睡前泡脚，避免睡前兴奋' },
  pilao: { name: '慢性疲劳倾向', emoji: '🟤', symptoms: ['持续疲倦', '注意力下降', '怎么睡都不够', '动力不足'], desc: '气血亏虚，脾肾不足，精力化生无源。', diet: '黄芪党参炖鸡、红枣枸杞茶、山药薏米粥', avoid: '过度劳累、熬夜、久坐不动', life: '劳逸结合，适度运动，午间小憩' },
  piwei: { name: '脾胃虚弱倾向', emoji: '🟢', symptoms: ['腹胀', '大便稀溏', '食欲差', '面色萎黄'], desc: '脾失健运，胃纳不佳，气血生化不足。', diet: '山药莲子粥、四神汤、小米南瓜粥', avoid: '生冷寒凉、油腻难消化、暴饮暴食', life: '少食多餐，细嚼慢咽，饭后散步' },
  qianlie: { name: '前列腺问题倾向', emoji: '🔷', symptoms: ['尿频尿急', '夜尿多', '排尿无力', '会阴坠胀'], desc: '肾气不固，湿热下注，膀胱气化不利。', diet: '南瓜子粥、枸杞山药汤、冬瓜薏米汤、番茄炒蛋', avoid: '久坐、憋尿、辛辣酒、冷饮', life: '避免久坐（每小时起身），温水坐浴，适度运动' },
  pifu: { name: '皮肤问题倾向', emoji: '🩹', symptoms: ['皮肤瘙痒', '起疹反复', '干燥脱屑', '遇热加重'], desc: '血虚风燥或湿热蕴肤，肌肤失养。', diet: '银耳百合羹、绿豆薏米汤、黑芝麻核桃粥、土茯苓煲汤', avoid: '辛辣海鲜、酒、热水烫洗、化纤衣物', life: '保湿润肤，避免搔抓，穿纯棉宽松衣物' },
  xueye: { name: '血液循环问题倾向', emoji: '🫀', symptoms: ['手脚冰凉', '肢体麻木', '青筋凸起', '蹲起头晕'], desc: '气虚血瘀，寒凝经脉，血行不畅。', diet: '当归生姜羊肉汤、山楂红糖水、黑木耳炒洋葱、桂圆红枣茶', avoid: '久坐不动、寒凉收引、紧身衣物、吸烟', life: '每日有氧运动30分钟，睡前泡脚，避免久站久坐' }
};

Page({
  data: {
    phase: 'start',       // start | quiz | result
    mode: '',             // tizhi | symptom
    questions: [],
    currentIndex: 0,
    selectedAnswer: -1,
    answers: [],
    result: null,
    testCount: 0
  },

  onLoad(options) {
    // 支持从分享图扫码进入：scene=tizhi 或 scene=symptom
    if (options.mode) {
      this.setData({ mode: options.mode });
    }
    // 加载测评人数
    request('/api/tizhi-test/count').then(res => {
      if (res && res.count) this.setData({ testCount: res.count });
    }).catch(() => {});
  },

  startTest() {
    wx.showActionSheet({
      itemList: ['🌿 体质测评（九种体质）', '⚠️ 症状自评（三高/痛风/风湿等）'],
      success: (res) => {
        const mode = res.tapIndex === 0 ? 'tizhi' : 'symptom';
        const questions = mode === 'tizhi' ? TIZHI_QUESTIONS : SYMPTOM_QUESTIONS;
        this.setData({
          mode,
          phase: 'quiz',
          questions,
          currentIndex: 0,
          selectedAnswer: -1,
          answers: []
        });
      }
    });
  },

  selectAnswer(e) {
    const idx = e.currentTarget.dataset.idx;
    const { currentIndex, questions, answers } = this.data;
    const newAnswers = [...answers];
    newAnswers[currentIndex] = idx;

    if (currentIndex < questions.length - 1) {
      // 下一题
      this.setData({
        answers: newAnswers,
        selectedAnswer: idx,
        currentIndex: currentIndex + 1
      });
      // 短暂高亮后切题
      setTimeout(() => this.setData({ selectedAnswer: -1 }), 200);
    } else {
      // 答完，计算结果
      this.setData({ answers: newAnswers, selectedAnswer: idx });
      setTimeout(() => this.calcResult(newAnswers), 300);
    }
  },

  calcResult(answers) {
    const { mode, questions } = this.data;
    const templates = mode === 'tizhi' ? TIZHI_RESULTS : SYMPTOM_RESULTS;
    const scores = {};

    questions.forEach((q, i) => {
      const ansIdx = answers[i] || 0;
      const qScores = q.scores;
      for (const [key, vals] of Object.entries(qScores)) {
        if (!scores[key]) scores[key] = 0;
        scores[key] += vals[ansIdx] || 0;
      }
    });

    // 找最高分
    let maxKey = '';
    let maxScore = -1;
    for (const [key, score] of Object.entries(scores)) {
      if (score > maxScore) {
        maxScore = score;
        maxKey = key;
      }
    }

    // 如果最高分为0（全部选"从不/没有"），判定为平和质/健康
    if (maxScore <= 1) {
      maxKey = mode === 'tizhi' ? 'pinghe' : 'piwei';
    }

    const result = templates[maxKey] || templates[Object.keys(templates)[0]];
    result.key = maxKey;
    result.score = maxScore;

    // 收集次高分（可能有兼夹）
    const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);
    if (sorted.length > 1 && sorted[1][1] >= maxScore * 0.6) {
      const secondary = templates[sorted[1][0]];
      if (secondary) result.secondary = secondary.name;
    }

    this.setData({ phase: 'result', result });

    // 保存测评结果到后端
    const app = getApp();
    request('/api/tizhi-test/save', {
      method: 'POST',
      data: {
        user_id: app.globalData.userId || '',
        mode: mode,
        result_key: maxKey,
        result_name: result.name,
        score: maxScore,
        answers: answers
      }
    }).catch(() => {});

    // 生成分享图
    setTimeout(() => this.drawShareImage(result), 500);
  },

  drawShareImage(result) {
    const query = wx.createSelectorQuery();
    query.select('#shareCanvas').fields({ node: true, size: true }).exec((res) => {
      if (!res || !res[0] || !res[0].node) return;
      const canvas = res[0].node;
      const ctx = canvas.getContext('2d');
      const dpr = wx.getWindowInfo().pixelRatio || 2;
      const W = 375, H = 520;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.scale(dpr, dpr);

      // 背景
      ctx.fillStyle = '#f0f7f0';
      ctx.fillRect(0, 0, W, H);

      // 顶部绿色条
      ctx.fillStyle = '#4a9d6e';
      ctx.fillRect(0, 0, W, 8);

      // 标题
      ctx.fillStyle = '#2c3e50';
      ctx.font = 'bold 22px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('🌿 我的健康自测报告', W / 2, 50);

      // 体质/症状名
      ctx.fillStyle = '#4a9d6e';
      ctx.font = 'bold 28px sans-serif';
      ctx.fillText(`${result.emoji} ${result.name}`, W / 2, 100);

      // 症状标签
      ctx.font = '14px sans-serif';
      ctx.fillStyle = '#666';
      const sympText = result.symptoms.join(' · ');
      ctx.fillText(sympText, W / 2, 135);

      // 描述
      ctx.fillStyle = '#555';
      ctx.font = '13px sans-serif';
      this.wrapText(ctx, result.desc, W / 2, 170, W - 60, 20);

      // 小麦建议框
      const boxY = 210;
      ctx.fillStyle = '#ffffff';
      this.roundRect(ctx, 25, boxY, W - 50, 180, 12);
      ctx.fill();
      ctx.strokeStyle = '#4a9d6e';
      ctx.lineWidth = 1;
      this.roundRect(ctx, 25, boxY, W - 50, 180, 12);
      ctx.stroke();

      ctx.fillStyle = '#4a9d6e';
      ctx.font = 'bold 15px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText('🌾 小麦建议', 45, boxY + 30);

      ctx.fillStyle = '#333';
      ctx.font = '13px sans-serif';
      ctx.fillText(`✅ 食疗：${result.diet}`, 45, boxY + 60);
      ctx.fillText(`❌ 忌口：${result.avoid}`, 45, boxY + 90);
      ctx.fillText(`🏠 起居：${result.life}`, 45, boxY + 120);

      if (result.secondary) {
        ctx.fillStyle = '#999';
        ctx.font = '12px sans-serif';
        ctx.fillText(`兼夹倾向：${result.secondary}`, 45, boxY + 155);
      }

      // 底部引导
      ctx.textAlign = 'center';
      ctx.fillStyle = '#4a9d6e';
      ctx.font = 'bold 14px sans-serif';
      ctx.fillText('扫码问小麦，对症食疗 →', W / 2, 440);

      ctx.fillStyle = '#999';
      ctx.font = '11px sans-serif';
      ctx.fillText('松麦SOM · 中医养生 · 有机生活', W / 2, 470);

      // 小程序码占位（需要后端 wxacode API 生成后替换）
      ctx.fillStyle = '#ddd';
      ctx.fillRect(W / 2 - 35, 480, 70, 30);
      ctx.fillStyle = '#999';
      ctx.font = '10px sans-serif';
      ctx.fillText('[小程序码]', W / 2, 500);

      this._canvas = canvas;
    });
  },

  wrapText(ctx, text, x, y, maxWidth, lineHeight) {
    let line = '';
    for (let i = 0; i < text.length; i++) {
      const testLine = line + text[i];
      if (ctx.measureText(testLine).width > maxWidth && line) {
        ctx.fillText(line, x, y);
        line = text[i];
        y += lineHeight;
      } else {
        line = testLine;
      }
    }
    ctx.fillText(line, x, y);
  },

  roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  },

  saveShareImage() {
    if (!this._canvas) {
      wx.showToast({ title: '图片生成中...', icon: 'none' });
      return;
    }
    wx.canvasToTempFilePath({
      canvas: this._canvas,
      success: (res) => {
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: () => wx.showToast({ title: '已保存到相册', icon: 'success' }),
          fail: () => wx.showToast({ title: '保存失败，请检查相册权限', icon: 'none' })
        });
      },
      fail: () => wx.showToast({ title: '生成失败', icon: 'none' })
    });
  },

  goAskXiaomai() {
    const { result, mode } = this.data;
    // 跳到小麦对话页，带上体质/症状信息
    const hint = mode === 'tizhi'
      ? `我刚做了体质测评，结果是【${result.name}】，请给我食疗调理方案`
      : `我刚做了症状自评，倾向【${result.name}】，请给我食疗调理方案`;
    wx.setStorageSync('som_tizhi_hint', hint);
    wx.switchTab({ url: '/pages/chat/chat' });
  }
});
