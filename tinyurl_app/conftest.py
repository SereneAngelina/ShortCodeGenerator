import pytest
from app import app, db


@pytest.fixture(scope='module')
def test_client():
    test_app = app

    test_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test_db.app"
    test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with test_app.test_client() as testing_client:
        with test_app.app_context():
            db.create_all()
            yield testing_client
            db.session.remove()
            db.drop_all()
