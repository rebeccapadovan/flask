
import pytest
from flask import g, session

from flaskr.models import db, User


def test_register(client, app):
    assert client.get("/auth/register").status_code == 200

    response = client.post(
        "/auth/register",
        data={"username": "a", "password": "a"},
    )
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        user = db.session.query(User).filter_by(username="a").first()
        assert user is not None


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", "O nome de usuário é obrigatório."),
        ("a", "", "A senha é obrigatória."),
        ("test", "test", "já está cadastrado"),
    ),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register",
        data={"username": username, "password": password},
    )
    assert message.encode("utf-8") in response.data


def test_login(client, auth):
    assert client.get("/auth/login").status_code == 200

    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user.username == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("a", "test", "Nome de usuário incorreto."),
        ("test", "a", "Senha incorreta."),
    ),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message.encode("utf-8") in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
