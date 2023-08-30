import os
from flask import Flask,current_app
from applications.common.script import init_script
from applications.config import BaseConfig
from applications.extensions import init_plugs
from applications.view import init_view
from applications.AIDetector_pytorch import Detector
from flask_cors import CORS

def create_app():
    app = Flask(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

    # with app.app_context():
    #     current_app.model = Detector()

    # 引入数据库配置
    app.config.from_object(BaseConfig)

    # 注册各种插件
    init_plugs(app)

    # 注册路由
    init_view(app)

    # 注册命令
    init_script(app)

    # 配置跨域允许所有来源的请求
    CORS(app)

    return app
