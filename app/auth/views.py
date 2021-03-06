"""
    这是auth蓝本 views, 对应flask_movie 的前端页面
"""

from app.auth import auth
from app.extensions import db
from flask import current_app, render_template, request, redirect, url_for, session
from sqlalchemy import text, or_
from app.models import Movie, User, Category, Comment
from app.utils import login_required, skip_back




@auth.route("/")
def index():
    movies = Movie.query.filter(text("id<:id")).params(id=9).all()
    country = ["中国大陆", "韩国", "日本", "台湾", "美国", "所有国家"]
    time = ["2019", "2018", "2017", "2016", "所有时间"]
    categories = Category.query.all()
    return render_template("auth/index.html", movies=movies, categories=categories,
                           country=country, time=time)


@auth.route("/search/<int:id>/")
@auth.route("/search")
def search(id=0):
    args = request.args.get('search')
    if id:
        t = Category.query.get(id)
        args = t.type
        find = t.movies
        return render_template("auth/search.html", find=find, args=args)
    elif args:
        find = Movie.query.filter(Movie.title.like("%{}%".format(args))).all()
        return render_template("auth/search.html", find=find, args=args)
    else:
        redirect(url_for('auth.index'))

# search movie by country
@auth.route("/search2/<tag>")
def search2(tag):
    args = tag
    if args == "所有国家":
        find = Movie.query.all()
    else:
        find = Movie.query.filter(Movie.country.like("%{}%".format(args))).all()
    return render_template("auth/search.html", find=find, args=args)

# search movie by year
@auth.route("/search3/<tag>")
def search3(tag):
    args = tag
    if args == "所有时间":
        # 按照 id 逆向排序 find = Movie.query.order_by("-id").all()
        #                find = Movie.query.order_by(Movie.id.desc()).all()
        find = Movie.query.order_by(Movie.id).all()
    else:
        find = Movie.query.filter(Movie.year.like("%{}%".format(args))).all()
    return render_template("auth/search.html", find=find, args=args)

# please pardon me for the shit code of login()
@auth.route("/login/", methods=["GET", "POST"])
def login():
    # note!!! redirect()必须被return才能完成url跳转
    if request.method == "POST":
        username = request.form.get('username')
        pwd = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        # login sucess
        if user and user.confirm_pwd(pwd):
            session["username"] = username
            session["id"] = user.id
            if (session.get("URL") == url_for("auth.login", _external=True)) or \
                (session.get("URL") == url_for("auth.register", _external=True)):
                return redirect(url_for("auth.index"))
            else:
                return skip_back()
        # login fail
        else:
            return redirect(url_for('auth.login'))
    else:
        # GET请求 login, 同时在session中记录Referer
        session["URL"] = request.headers.get("Referer")
        return render_template("auth/login.html")


@auth.route("/post_comment/<int:movie_id>", methods=["POST"])
@login_required
def post_comment(movie_id):
    body = request.form.get("comment")

    comment = Comment(body=body)
    comment.user_id = session.get("id")
    comment.movie_id = movie_id

    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("auth.display", id=movie_id))


@auth.route("/display/<int:id>")
def display(id):

    movie = Movie.query.get(id)
    categories = movie.categories
    comments = Comment.query.filter(Comment.movie_id==id).order_by(Comment.timestamp.desc()).all()
    return render_template("auth/display.html", movie=movie, categories=categories,comments=comments)


@auth.route("/logout/")
def logout():
    session.pop("username", None)
    return redirect(url_for('auth.index'))


@auth.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        email = request.form.get('email')

        if User.query.filter_by(username=username).first():
            return redirect(url_for('auth.register'))
        if username and password and password == repassword:
            user = User(
                username=username,
                password=password,
                email=email
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html')


@auth.route("/vip/", methods=["GET", "POST"])
@login_required
def self_center():
    user = User.query.get(session.get("id"))
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        repeat_name = User.query.filter_by(username=username).first()
        if username and email and not repeat_name:
            user.username = username
            user.email = email
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.index"))
        else:
            return redirect(url_for("auth.self_center"))
    return render_template('auth/self_center.html', user=user)

# change the password
@auth.route("/vip/change_psw/", methods=["GET", "POST"])
@login_required
def change_pwd():
    if request.method == "POST":
        user = User.query.get(session.get("id"))
        oldpwd = request.form.get("oldpwd")
        newpwd = request.form.get("newpwd")

        if user.password == oldpwd:
            user.password = newpwd
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.index"))
        else:
            return redirect(url_for("auth.change_pwd"))
    return render_template("auth/pwd.html")

# comment list
@auth.route("/vip/comments/")
@login_required
def comments_records():
    user = User.query.get(session.get("id"))
    comments = Comment.query.filter(Comment.user_id==user.id).order_by(Comment.timestamp.desc()).all()
    return render_template("auth/comments.html", comments=comments, user=user)