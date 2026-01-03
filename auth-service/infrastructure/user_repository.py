from motor.motor_asyncio import AsyncIOMotorDatabase
from domain.entities.user import User
from bson import ObjectId

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def get_by_email(self, email: str):
        user_doc = await self.collection.find_one({"email": email})
        if user_doc:
            return User(**user_doc)
        return None

    async def get_by_id(self, user_id: str):
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        user_doc = await self.collection.find_one({"_id": oid})
        if user_doc:
            return User(**user_doc)
        return None

    async def create(self, user: User):
        user_dict = user.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        return user

    async def get_all(self):
        cursor = self.collection.find()
        users = []
        async for doc in cursor:
            users.append(User(**doc))
        return users

    async def delete(self, user_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
