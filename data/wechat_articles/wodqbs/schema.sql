-- 记忆承载公众号文章数据库
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT UNIQUE NOT NULL,  -- 微信文章ID
    title TEXT NOT NULL,
    author TEXT DEFAULT '碧树西风',
    publish_date TEXT,
    update_date TEXT,
    content TEXT,
    summary TEXT,
    read_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    original BOOLEAN DEFAULT FALSE,
    ip_location TEXT,
    cover_image TEXT,
    source TEXT DEFAULT 'wechat',
    url TEXT,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending'
);

-- 交易信号表
CREATE TABLE IF NOT EXISTS trading_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT,
    signal_type TEXT,  -- bullish/bearish/neutral
    confidence REAL,
    keywords TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id)
);

-- 交易日志表
CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id INTEGER,
    entry_price REAL,
    exit_price REAL,
    quantity REAL,
    pnl REAL,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (signal_id) REFERENCES trading_signals(id)
);

-- 采集进度表
CREATE TABLE IF NOT EXISTS collection_progress (
    page INTEGER PRIMARY KEY,
    last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'running'
);
