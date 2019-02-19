"""
    这是auth蓝本 views, 对应flask_movie 的前端页面
"""

from app.auth import auth
from flask import current_app, render_template
from sqlalchemy import text
from app.models import Movie, User, Category, Comment

@auth.route("/")
def index():
    movies = Movie.query.filter(text("id<:id")).params(id=9).all()

    return render_template("auth/index.html", movies=movies)