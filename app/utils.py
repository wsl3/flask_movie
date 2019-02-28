# 程序的辅助功能, 比如登陆保护
from functools import wraps
from flask import session, redirect, url_for, session



def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("username"):
            # 这里必须有return, 否则会报错(视图函数没有返回值)
            # wrapper相当于视图函数, 必须有返回值
            # 找这个错找了一晚上, Fuck!
            # 吃饭去！
            return func(*args, **kwargs)
        else:
            return redirect(url_for("auth.login"))
    return wrapper

def skip_back():
    url = session.get("URL", url_for("auth.index"))
    return redirect(url)

