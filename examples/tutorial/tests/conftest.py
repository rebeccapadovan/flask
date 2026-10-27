import pytest

from flaskr import create_app
from flaskr.models import db, User, Post
from werkzeug.security import generate_password_hash


@pytest.fixture
def app(tmp_path):
    """Cria um aplicativo e um banco isolado para cada teste."""
    database_path = tmp_path / "test.sqlite"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path.as_posix()}",
        "SECRET_KEY": "test",
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            username="test",
            password=generate_password_hash("test"),
        )
        other = User(
            username="other",
            password=generate_password_hash("test"),
        )

        db.session.add_all([user, other])
        db.session.flush()

        post = Post(
            title="test title",
            body="test\nbody",
            author_id=user.id,
        )
        db.session.add(post)
        db.session.commit()

    yield app

    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login",
            data={"username": username, "password": password},
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
