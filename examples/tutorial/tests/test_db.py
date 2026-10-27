
from flaskr.models import db, User, Post


def test_database_tables_exist(app):
    with app.app_context():
        assert db.session.query(User).count() == 2
        assert db.session.query(Post).count() == 1


def test_post_relationship(app):
    with app.app_context():
        post = db.session.get(Post, 1)

        assert post is not None
        assert post.author is not None
        assert post.author.username == "test"
        assert post in post.author.posts


def test_create_user(app):
    with app.app_context():
        user = User(
            username="novo_usuario",
            password="senha_teste",
        )
        db.session.add(user)
        db.session.commit()

        encontrado = User.query.filter_by(
            username="novo_usuario"
        ).first()

        assert encontrado is not None
