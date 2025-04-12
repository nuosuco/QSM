"""
松麦生态商城API服务

启动Flask服务器提供松麦生态商城API接口
"""

import os
import logging
from flask import Flask, jsonify, render_template, send_from_directory, send_file, redirect, url_for
from quantum_economy.WeQ.marketplace.api import marketplace_api
from quantum_economy.WeQ.marketplace.marketplace_core import SomMarketplace

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("marketplace_app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MarketplaceApp")

def create_app(test_config=None):
    """创建并配置Flask应用"""
    # 创建应用实例
    app = Flask(__name__, 
                instance_relative_config=True,
                static_folder=None)  # 禁用默认静态文件夹
    
    # 基本配置
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'marketplace.sqlite'),
    )

    if test_config is None:
        # 加载配置
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 加载测试配置
        app.config.from_mapping(test_config)

    # 确保instance文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # 初始化商城
    marketplace = SomMarketplace()
    app.marketplace = marketplace
    
    # 注册蓝图
    app.register_blueprint(marketplace_api, url_prefix='/api/marketplace')
    
    # 配置模板和静态文件目录
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates', 'static'))
    
    # 确保静态文件目录存在
    os.makedirs(static_dir, exist_ok=True)
    
    # 设置静态文件路由
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(static_dir, filename)
    
    # 首页路由 - 使用templates文件夹中的index.html
    @app.route('/')
    def index():
        return send_file(os.path.join(template_dir, 'index.html'))
    
    # 有机食品列表页面的HTML路由
    @app.route('/weq/marketplace/organic-products.html')
    def organic_products_page():
        return send_file(os.path.join(template_dir, 'static', 'organic-products.html'))
    
    # 有机食品列表页面的API路由
    @app.route('/weq/marketplace/organic-products')
    def organic_products():
        # 获取所有有机食品产品
        organic_products = marketplace.get_products_by_filter(category="有机食品")
        # 如果没有有机食品类别的产品，返回所有产品
        if not organic_products:
            organic_products = marketplace.get_all_products()
            organic_products = [p.to_dict() for p in organic_products.values()]
            
        return jsonify({
            "status": "success",
            "message": "有机食品产品列表获取成功",
            "data": {
                "products": organic_products
            }
        })
    
    # 产品详情页面
    @app.route('/weq/marketplace/product/<product_id>')
    def product_detail(product_id):
        product_detail = marketplace.get_product_detail(product_id)
        if not product_detail.get('success'):
            return jsonify({
                "status": "error",
                "message": f"未找到产品: {product_id}"
            }), 404
            
        return jsonify({
            "status": "success",
            "data": {
                "product": product_detail['product']
            }
        })
    
    # 添加商品到购物车API
    @app.route('/api/marketplace/cart/add')
    def add_to_cart():
        from flask import request
        product_id = request.args.get('product_id')
        quantity = request.args.get('quantity', 1, type=int)
        
        # 这里需要实现添加到购物车的逻辑
        # 简单返回成功信息
        return jsonify({
            "status": "success",
            "message": f"已成功将商品 {product_id} 添加到购物车，数量：{quantity}",
            "cart_count": quantity
        })
    
    # 健康检查端点
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "ok",
            "service": "松麦生态商城API服务",
            "version": "1.0.0"
        })
    
    logger.info("松麦生态商城API服务初始化完成")
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True) 

"""
"""
量子基因编码: QE-APP-0E67C0CC1F2A
纠缠状态: 活跃
纠缠对象: ['WeQ/weq_core.py']
纠缠强度: 0.98
""""""

// 开发团队：中华 ZhoHo ，Claude 
