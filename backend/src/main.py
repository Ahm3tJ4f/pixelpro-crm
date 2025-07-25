from fastapi import FastAPI
from src.database.core import DbSession
from src.database.entities.user import User

app = FastAPI()


@app.get("/test-user")
def test_user(db: DbSession):
    # Try to query users
    users = db.query(User).all()
    return {"message": "DB connection works!", "users": len(users)}
