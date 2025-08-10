import pytest
from fastapi.testclient import TestClient
from redis import ConnectionPool, Redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.core import Base, get_db
from src.main import app
from src.core.constants import TEST_DATABASE_URL, TEST_REDIS_URL
from src.core.redis import get_redis

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

test_redis_pool = ConnectionPool.from_url(
    TEST_REDIS_URL, decode_responses=True, max_connections=10
)


def test_get_db():
    test_db = TestSessionLocal()
    try:
        yield test_db
    finally:
        test_db.close()


def test_get_redis():
    try:
        redis_client = Redis(connection_pool=test_redis_pool)
        redis_client.ping()
        return redis_client
    except Exception as e:
        raise pytest.fail(f"Failed to connect to test Redis: {e}")


@pytest.fixture
def redis_client():
    """Get Redis client for testing"""
    try:
        redis_client = Redis(connection_pool=test_redis_pool)
        redis_client.ping()
        yield redis_client
        redis_client.flushdb()
    except Exception as e:
        raise pytest.fail(f"Failed to connect to test Redis: {e}")


@pytest.fixture(scope="session")
def testing_client():
    Base.metadata.create_all(bind=test_engine)

    app.dependency_overrides[get_db] = test_get_db
    app.dependency_overrides[get_redis] = test_get_redis

    with TestClient(app) as client:
        yield client

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def operator_user_payload():
    return {
        "username": "operator",
        "password": "operator",
        "firstName": "Operator",
        "lastName": "Operator",
        "userRole": "OPERATOR",
    }


@pytest.fixture
def login_response(testing_client, operator_user_payload):
    # Register the operator user first
    testing_client.post("/auth/register", json=operator_user_payload)

    payload = {
        "username": operator_user_payload["username"],
        "password": operator_user_payload["password"],
    }

    response = testing_client.post("/auth/login", json=payload)
    return response.json()
