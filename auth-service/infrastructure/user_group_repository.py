from motor.motor_asyncio import AsyncIOMotorDatabase
from domain.entities.user_group import UserGroup
from bson import ObjectId

class UserGroupRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["user_groups"]

    async def get_by_id(self, group_id: str):
        try:
            oid = ObjectId(group_id)
        except Exception:
            return None
        doc = await self.collection.find_one({"_id": oid})
        if doc:
            return UserGroup(**doc)
        return None

    async def get_by_name(self, name: str):
        doc = await self.collection.find_one({"name": name})
        if doc:
            return UserGroup(**doc)
        return None

    async def get_all(self):
        cursor = self.collection.find()
        groups = []
        async for doc in cursor:
            groups.append(UserGroup(**doc))
        return groups

    async def create(self, group: UserGroup):
        group_dict = group.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(group_dict)
        group.id = str(result.inserted_id)
        return group

    async def update(self, group_id: str, update_data: dict):
        # update_data should match UserGroupUpdate fields
        if not update_data:
            return None
            
        try:
            oid = ObjectId(group_id)
        except Exception:
            return None

        result = await self.collection.update_one(
            {"_id": oid},
            {"$set": update_data}
        )
        if result.modified_count > 0:
            return await self.get_by_id(group_id)
        # If no document matched, return None. If matched but no change, fetch and return.
        if result.matched_count > 0:
             return await self.get_by_id(group_id)
        return None

    async def delete(self, group_id: str):
        try:
            oid = ObjectId(group_id)
        except Exception:
            return False
        result = await self.collection.delete_one({"_id": oid})
        return result.deleted_count > 0
