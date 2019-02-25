from flask import Flask, render_template
from app.extensions import db, migrate
from app.models import Movie, User, Category, Comment  # it is must that make models and db together
from app import config
from app.auth import auth  # blueprint: auth
from app.crawl import begin_crawl
from faker import Faker
import click
from sqlalchemy import text


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app=app, db=db)

    app.register_blueprint(auth)  # register auth

    register_commands(app=app)
    register_template_filter(app=app)
    register_shell_context(app=app)
    return app


def register_template_filter(app):
    # 处理模板中的 演员字段数据
    @app.template_filter("get_string")
    def get_string(arg):
        temp = arg.split("/")
        if len(temp) > 3:
            temp = temp[:3]
        return "/".join(temp)

    # 处理模板中的 电影简介字段数据(简介过长)
    @app.template_filter("be_smaller")
    def be_smaller(arg):
        if len(arg) > 74:
            arg = arg[:74] + " ..."
        else:
            arg += " ..."
        return arg


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, Category=Category, Movie=Movie, Comment=Comment, User=User, text=text)


def register_commands(app):
    @app.cli.command()
    @click.option("--username", default="root", help="create a username of admin")
    @click.option("--password", default="666", help="create a password of admin")
    @click.option("--email", default="admin@mail", help="create a email of admin")
    @click.option("--head_picture", default="http://img.hao661.com/qq.hao661.com/uploads/allimg/180922/1S9294412-0.jpg",
                  help="create a head_picture of admin")
    def admin(username, password, email, head_picture):

        click.echo("Admin username:\t%s" % username)
        click.echo("Admin password:\t%s" % password)
        click.echo("Admin    email:\t%s" % email)
        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            admin.username = username
            admin.password = password
            admin.email = email,
            admin.head_picture = head_picture

        else:
            admin = User(
                username=username,
                password=password,
                email=email,
                head_picture=head_picture,
                is_admin=True
            )
        db.session.add(admin)
        db.session.commit()

        click.echo("...Done!\n")

    @app.cli.command()
    def rebuild():
        db.drop_all()
        db.create_all()

    @app.cli.command()
    @click.option("--pages", default=3, help="需要爬取的page,每个page有20部电影！")
    def crawl(pages):
        f = Faker("zh_CN")

        click.echo("即将开始爬取工作, 共有%d页, %d部电影！\n" % (pages, pages * 20))

        dex = 0
        movies = begin_crawl(pages=pages)  # type(movies) -> []
        click.echo("\n开始数据库存入操作！\n")

        for movie_info in movies:
            movie_msg = movie_info.get('movie_msg')  # -> {}
            user_msg = movie_info.get('user_msg')  # -> [{},{}]

            dex += 1
            click.echo("%d...正在存储 <%s> 相应信息\n" % (dex, movie_msg.get('title')))

            # 创建Movie
            movie = Movie(
                title=movie_msg.get('title'),
                year="/".join(movie_msg.get('year')),
                country=movie_msg.get('country'),
                language=movie_msg.get('language'),
                movie_picture=movie_msg.get('movie_picture'),
                movie_url=movie_msg.get('movie_url'),
                score=movie_msg.get('score'),
                time=movie_msg.get('time'),
                director="/".join(movie_msg.get('director')),
                actors="/".join(movie_msg.get('actors')),
                summary=movie_msg.get('summary')
            )
            db.session.add(movie)
            db.session.commit()

            current_movie = Movie.query.filter_by(title=movie_msg.get('title')).first()

            # 创建Category
            for type in movie_msg.get('tags'):
                # 有这个电影tag, 直接把电影添加到该tag中
                cate = Category.query.filter_by(type=type).first()
                if cate:
                    cate.movies.append(current_movie)
                    continue
                # 没有该tag, 创建该tag, 再把该电影添加到该tag中
                category = Category(
                    type=type
                )
                category.movies.append(current_movie)
                db.session.add(category)

            db.session.commit()

            # 创建User and Comment
            for u in user_msg:
                comment = Comment(
                    body=u.get('comment'),
                    timestamp=u.get('timestamp'),
                    movie=current_movie
                    # user=User.query.filter(User.username == u.get('username')).first()
                )
                us = User.query.filter_by(username=u.get('username')).first()
                if us:
                    comment.user = us
                    continue

                user = User(
                    username=u.get('username'),
                    password=u.get('password'),
                    email=f.email(),
                    head_picture=u.get('head_picture')
                )
                comment.user = user
                db.session.add(user)
            db.session.commit()

            # # 创建Comment
            # for u in user_msg:
            #
            #     db.session.add(comment)
            # db.session.commit()

        click.echo("Run!Run!Run!\n信息全部存储完毕,转战前线！\n你指尖跳动的电光,是我不变的信仰！\n")
