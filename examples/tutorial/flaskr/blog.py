
from flask import (
    Blueprint, flash, g, redirect, render_template,
    request, url_for
)
from werkzeug.exceptions import abort

from .uploads import save_image
from .auth import login_required
from .models import db, Post

bp = Blueprint("blog", __name__)


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
            try:
                image_filename = save_image(image_file)
            except ValueError as e:
                flash(str(e))
                return render_template("blog/create.html"), 400

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
            if image_file and image_file.filename:
                try:
                    new_image = save_image(image_file)
                except ValueError as e:
                    flash(str(e))
                    return render_template(
                        "blog/update.html", post=post
                    ), 400

                if new_image:
                    post.imagem_post = new_image

            post.title = title
            post.body = body

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
