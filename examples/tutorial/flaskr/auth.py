import os
import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from .models import db, User

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

        if not username:
            error = "O nome de usuário é obrigatório."
        elif not password:
            error = "A senha é obrigatória."
        elif User.query.filter_by(username=username).first() is not None:
            error = f"O usuário {username} já está cadastrado."

        avatar_filename = None

        if error is None and avatar_file and avatar_file.filename:
            safe_name = secure_filename(avatar_file.filename)

            if safe_name:
                import uuid
                extension = os.path.splitext(safe_name)[1]
                avatar_filename = f"{uuid.uuid4().hex}{extension}"

                upload_folder = os.path.join(
                    current_app.root_path, "static", "uploads"
                )
                os.makedirs(upload_folder, exist_ok=True)
                avatar_file.save(os.path.join(upload_folder, avatar_filename))

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