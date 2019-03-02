'''
    数据库模型
'''

from app.extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# 创建关联表,设置 movie 和 category 的双向关系
association_table = db.Table("association", db.Column("category_id", db.Integer, db.ForeignKey("category.id")),
                             db.Column("movie_id", db.Integer, db.ForeignKey("movie.id")))


# 管理员和普通用户
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(600), nullable=False)
    email = db.Column(db.String(30), nullable=False, index=True)
    head_picture = db.Column(db.String(600),
                             default="http://img.hao661.com/qq.hao661.com/uploads/allimg/180922/1S9294412-0.jpg")
    is_admin = db.Column(db.Boolean, default=False)

    # 用户和评论的一对多关系
    # 和Comment设置关系, 反向引用为user
    comments = db.relationship("Comment", backref="user")

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def confirm_pwd(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    def __repr__(self):
        return "User:<{}>".format(self.username)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    title = db.Column(db.String(120), nullable=False, index=True)
    year = db.Column(db.String(100), index=True, default=2019)
    country = db.Column(db.String(80), default="我也不知道呀！", index=True)
    language = db.Column(db.String(60), default="你来看啊(滑稽)")
    movie_picture = db.Column(db.String(600))
    movie_url = db.Column(db.String(600), default="../static/video/htpy.mp4")
    score = db.Column(db.String(40))  # 评分
    time = db.Column(db.String(60))  # 时间
    director = db.Column(db.String(40))  # 导演
    actors = db.Column(db.String(600))  # 演员
    summary = db.Column(db.Text)  # 简介
    # kind = db.Column(db.Integer, default="1")  # 影视种类--> 电影,电视剧,
    # episodes = db.Column(db.Integer)  # 集数

    # 电影和评论的一对多关系
    # 和Comment设置关系, 反向引用为movie
    comments = db.relationship("Comment", backref="movie")

    # 电影和分类的多对多关系
    categories = db.relationship("Category", secondary=association_table, back_populates="movies")

    def __repr__(self):
        return "Movie:<{}>".format(self.title)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 电影和评论的一对多关系
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"))

    # 用户和评论的一对多关系
    # 和User设置关系,反向引用为user
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return "Comment:<{}>".format(self.body)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    type = db.Column(db.String(30), nullable=False, index=True, unique=True)

    # 电影和分类的多对多关系
    movies = db.relationship("Movie", secondary=association_table, back_populates="categories")

    def __repr__(self):
        return "Category:<{}>".format(self.type)
