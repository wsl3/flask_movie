from app.auth import auth
from flask import render_template


@auth.app_errorhandler(404)
def hander_404(e):
    return render_template("auth/404.html"), 404