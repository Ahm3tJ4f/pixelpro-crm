from src.database.core import DbSession
from src.modules.users.model import GetUserResponse


class UserService:
    def __init__(db: DbSession):
        db = self.db

    def get_user(self, user_id: str) -> GetUserResponse:
        