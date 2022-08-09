# import pytest
# from fastapi.testclient import TestClient
# from httpx import ASGITransport, AsyncClient
#
# from app.main import app
#
#
# @pytest.fixture
# async def test_app():
#     transport = ASGITransport(
#         app=app, raise_app_exceptions=False, client=("1.2.3.4", 123)
#     )
#     yield AsyncClient(transport=transport, base_url="http://127.0.0.1:8000")
import pytest
import sqlalchemy
from database import TEST_DATABASE_URL, metadata


@pytest.fixture(autouse=True, scope="module")
def create_test_database():
    engine = sqlalchemy.create_engine(TEST_DATABASE_URL)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)
