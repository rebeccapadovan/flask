
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template,
    request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .models import db, User
from .uploads import save_image

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view


@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        avatar_file = request.files.get("avatar")
        error = None
        avatar_filename = None

        if not username:
            error = "O nome de usuário é obrigatório."
        elif not password:
            error = "A senha é obrigatória."
        elif User.query.filter_by(username=username).first() is not None:
            error = f"O usuário {username} já está cadastrado."

        if error is None and avatar_file and avatar_file.filename:
            try:
                avatar_filename = save_image(avatar_file)
            except ValueError as e:
                error = str(e)

        if error is None:
            user = User(
                username=username,
                password=generate_password_hash(password),
                avatar=avatar_filename,
            )
            db.session.add(user)

            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                error = "Não foi possível concluir o cadastro."

            if error is None:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        error = None

        if user is None:
            error = "Nome de usuário incorreto."
        elif not check_password_hash(user.password, password):
            error = "Senha incorreta."

        if error is None:
            session.clear()
            session["user_id"] = user.id
            return redirect(url_for("blog.index"))

        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("blog.index"))
