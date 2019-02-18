"""
    这是auth蓝本, 对应flask_movie 的前端页面
"""
from flask import Blueprint

auth = Blueprint("auth", __name__)

# 避免循环导入
# 注册前端页面
from app.auth import views