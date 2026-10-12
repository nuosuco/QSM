"""
2026-10-13 小蕊加(中华要求): 商品缓存自动清理
- 目标: product_cache.db 文件大小保持在 ~1GB 附近
- 策略:
  1. 按 updated_at 从旧到新删除, 保留最新数据(新爬的商品自动补进来)
  2. 删除到估算大小 <= 1.05GB 为止
  3. 之后 VACUUM 压缩文件(碎片回收), 实际文件会回到 1GB 左右
- 调用: save_product() 之后(每次爬取入库时顺带检查), 也提供 /api/cache/gc 手动触发
"""
import os, sqlite3, time, threading

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_BASE, 'data', 'product_cache.db')

TARGET_SIZE = int(1.05 * 1024 * 1024 * 1024)  # 1.05GB, 略超 1GB, VACUUM 后会回到 1GB 附近
MIN_ROWS_KEEP = 50000                            # 安全下限: 无论删多少至少留 5 万行

_lock = threading.Lock()

def _file_size():
    try:
        return os.path.getsize(DB_PATH)
    except OSError:
        return 0

def gc_product_cache(verbose=True) -> dict:
    """删除旧记录 + VACUUM, 让数据库文件落在 ~1GB"""
    with _lock:
        before_bytes = _file_size()
        if before_bytes <= TARGET_SIZE:
            return {'status': 'ok', 'skipped': True,
                    'before_mb': before_bytes // 1024 // 1024,
                    'message': '未超 1.05GB, 无需清理(新爬的会自动补进来)'}
        conn = sqlite3.connect(DB_PATH, timeout=30)
        cur = conn.cursor()
        t0 = time.time()
        # 1. 先看总行数
        total = cur.execute('SELECT COUNT(*) FROM product_cache').fetchone()[0]
        # 2. 估算平均行字节, 用 (总大小/总行数) 做保守估算
        avg_bytes = (before_bytes / total) if total > 0 else 0
        # 3. 想保留多少行: 保留行 × 平均字节 ≈ 0.95GB(VACUUM 前), VACUUM 后文件会再缩
        keep_rows = max(MIN_ROWS_KEEP, int(0.95 * 1024 * 1024 * 1024 / avg_bytes)) if avg_bytes > 0 else total
        delete_rows = total - keep_rows
        if delete_rows > 0:
            cur.execute(
                'DELETE FROM product_cache WHERE item_id IN ('
                '  SELECT item_id FROM product_cache ORDER BY updated_at ASC LIMIT ?'
                ')', (delete_rows,))
            conn.commit()
            print(f'[cache-gc] 删除 {delete_rows} 条旧记录(按 updated_at 升序), 保留 {keep_rows} 条')
        else:
            keep_rows = total
            print('[cache-gc] 无需删除(数据行足够新)')
        # 4. VACUUM 回收碎片
        t1 = time.time()
        cur.execute('VACUUM')
        conn.close()
        after_bytes = _file_size()
        dur = time.time() - t0
        if verbose:
            print(f'[cache-gc] VACUUM 完成, 文件 {before_bytes//1024//1024}MB -> {after_bytes//1024//1024}MB, 耗时 {time.time()-t1:.1f}s')
        return {
            'status': 'ok',
            'skipped': False,
            'deleted_rows': delete_rows,
            'kept_rows': keep_rows,
            'before_mb': before_bytes // 1024 // 1024,
            'after_mb': after_bytes // 1024 // 1024,
            'duration_s': round(dur, 1),
            'vacuum_s': round(time.time() - t1, 1),
        }

# 供 save_product() 之后调用: 自动触发(超 1.05GB 才动刀)
def auto_gc_if_needed() -> dict:
    return gc_product_cache(verbose=False)
