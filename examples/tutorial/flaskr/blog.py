import os
import uuid

from flask import (
    Blueprint, flash, g, redirect, render_template,
    request, url_for, current_app
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from .auth import login_required
from .models import db, Post

bp = Blueprint("blog", __name__)


def save_image(file):
    if not file or not file.filename:
        return None

    safe_name = secure_filename(file.filename)
    if not safe_name:
        return None

    extension = os.path.splitext(safe_name)[1].lower()
    filename = f"{uuid.uuid4().hex}{extension}"

    upload_folder = os.path.join(
        current_app.root_path, "static", "uploads"
    )
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, filename))

    return filename


def get_post(id, check_author=True):
    post = db.session.get(Post, id)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@bp.route("/")
def index():
    posts = Post.query.order_by(Post.created.desc()).all()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"].strip()
        body = request.form["body"]
        image_file = request.files.get("imagem_post")
        error = None

        if not title:
            error = "O título é obrigatório."

        if error:
            flash(error)
        else:
            image_filename = save_image(image_file)

            post = Post(
                title=title,
                body=body,
                author_id=g.user.id,
                imagem_post=image_filename,
            )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"].strip()
        body = request.form["body"]
        image_file = request.files.get("imagem_post")
        error = None

        if not title:
            error = "O título é obrigatório."

        if error:
            flash(error)
        else:
            post.title = title
            post.body = body

            if image_file and image_file.filename:
                new_image = save_image(image_file)
                if new_image:
                    post.imagem_post = new_image

            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("blog.index"))