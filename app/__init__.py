from flask import Flask, render_template
from app.extensions import db, migrate
from app.models import Movie, User, Category, Comment  # it is must that make models and db together
from app import config
from app.auth import auth  # blueprint: auth
from app.crawl import begin_crawl
from faker import Faker
import click


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app=app, db=db)

    app.register_blueprint(auth)  # register auth

    register_commands(app=app)
    return app


def register_commands(app):

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
        movies = begin_crawl(pages=pages) # type(movies) -> []
        click.echo("\n开始数据库存入操作！\n")

        for movie_info in movies:
            movie_msg = movie_info.get('movie_msg') # -> {}
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

            # 创建Category
            for type in movie_msg.get('tags'):
                if Category.query.filter_by(type=type).first():
                    continue

                category = Category(
                    type=type.strip()
                )
                category.movies.append(Movie.query.filter_by(title=movie_msg.get('title')).first())
                db.session.add(category)

            db.session.commit()

            # 创建User
            for u in user_msg:
                if User.query.filter_by(username=u.get('username')).first():
                    continue

                user = User(
                    username=u.get('username'),
                    password=u.get('password'),
                    email=f.email(),
                    head_picture=u.get('head_picture')
                )
                db.session.add(user)
            db.session.commit()

            # 创建Comment
            for u in user_msg:
                comment = Comment(
                    body=u.get('comment'),
                    timestamp=u.get('timestamp'),
                    movie=Movie.query.filter(Movie.title==movie_msg.get('title')).first(),
                    user=User.query.filter(User.username==u.get('username')).first()
                )
                db.session.add(comment)
            db.session.commit()

        click.echo("Run!Run!Run!\n信息全部存储完毕,转战前线！\n你指尖跳动的电光,是我不变的信仰！\n")



