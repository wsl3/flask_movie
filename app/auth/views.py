"""
    这是auth蓝本 views, 对应flask_movie 的前端页面
"""

from app.auth import auth
from flask import current_app, render_template
from app.extensions import db

@auth.route("/")
def index():

    return render_template("auth/index.html")