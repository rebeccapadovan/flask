from flaskr import create_app

def test_config():
    """Testa a configuração do aplicativo."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing


def test_hello(client):
    """Testa se a página inicial do Flaskr abre."""
    response = client.get("/")
    assert response.status_code == 200
