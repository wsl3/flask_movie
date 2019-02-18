"""
    这是auth蓝本 views, 对应flask_movie 的前端页面
"""

from app.auth import auth
from app.extensions import db

@auth.route("/")
def index():

    return "Hello Flask!"