import pytest

from flaskr.models import db, User, Post


def test_index(client, auth):
    response = client.get("/")
    assert response.status_code == 200

    auth.login()
    response = client.get("/")
    assert b"test title" in response.data
    assert b"test\nbody" in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize("path", ("/create", "/1/update", "/1/delete"))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    with app.app_context():
        post = db.session.get(Post, 1)
        post.author_id = 2
        db.session.commit()

    auth.login()
    assert client.post("/1/update").status_code == 403
    assert client.post("/1/delete").status_code == 403
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize("path", ("/2/update", "/2/delete"))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_create(client, auth, app):
    auth.login()
    assert client.get("/create").status_code == 200

    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        count = db.session.query(Post).count()
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get("/1/update").status_code == 200

    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        post = db.session.get(Post, 1)
        assert post.title == "updated"


@pytest.mark.parametrize("path", ("/create", "/1/update"))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert "O título é obrigatório.".encode("utf-8") in response.data


def test_delete(client, auth, app):
    auth.login()
    response = client.post("/1/delete")
    assert response.headers["Location"] == "/"

    with app.app_context():
        post = db.session.get(Post, 1)
        assert post is None
