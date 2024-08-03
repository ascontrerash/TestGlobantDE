import pytest
import json
from app import db
from models.hiredEmployee import HiredEmployeeModel

@pytest.fixture
def app():
    from app import app as flask_app
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": 'sqlite:///test.db'
    })
    with flask_app.app_context():
        db.create_all()
    yield flask_app
    with flask_app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_outbounts_insert_batch(client):
    
    data = json.dumps([{
        "name": "Alex Contreas",
        "department_id": 1,
        "job_id": 1
    } for _ in range(1001)])  # 1001 filas para superar el límite

    response = client.post('/insert_batch', data=data, content_type='application/json')
    
    assert response.status_code == 400  # Espera un código de error 400
    assert b"More than 1000 inserted" in response.data  # Mensaje de error esperado