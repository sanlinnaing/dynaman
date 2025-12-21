from motor.motor_asyncio import AsyncIOMotorDatabase
from building_blocks.config import settings
from bson import ObjectId
from typing import Any

class RecordRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["user_records"]

    async def init_indices(self):
        # The Secret for No-Code: Wildcard Index
        await self.collection.create_index([("content.$**", 1)])
        # Full-text search index
        await self.collection.create_index([("$**", "text")])

    async def create(self, entity_name: str, content: dict, metadata: dict):
        doc = {"entity": entity_name, "content": content, "_metadata": metadata}
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def update(self, entity_name: str, record_id: str, content: dict, metadata_update: dict):
        query = {"_id": ObjectId(record_id), "entity": entity_name}
        update_op = {
            "$set": {
                "content": content,
            }
        }
        for k, v in metadata_update.items():
            update_op["$set"][f"_metadata.{k}"] = v
            
        result = await self.collection.update_one(query, update_op)
        return result.modified_count > 0

    async def soft_delete(self, entity_name: str, record_id: str, deleted_at):
        query = {"_id": ObjectId(record_id), "entity": entity_name}
        update_op = {"$set": {"_metadata.deleted_at": deleted_at}}
        result = await self.collection.update_one(query, update_op)
        return result.modified_count > 0

    async def find_all(self, entity_name: str, skip: int = 0, limit: int = 50):
        query = {
            "entity": entity_name,
            "$or": [
                {"_metadata.deleted_at": None},
                {"_metadata.deleted_at": {"$exists": False}}
            ]
        }
        cursor = self.collection.find(query).skip(skip).limit(limit)
        records = await cursor.to_list(length=limit)
        for record in records:
            record["id"] = str(record["_id"])
            del record["_id"]
        return records

    async def find(self, entity_name: str, query: dict, skip: int = 0, limit: int = 50):
        # Merge the user query with the soft delete filter
        # Remap query fields to match embedded "content" structure
        content_query = {}
        for k, v in query.items():
             if k == "_id": 
                 content_query[k] = v 
             else:
                 content_query[f"content.{k}"] = v

        full_query = {
            "entity": entity_name, 
            **content_query,
            "$or": [
                {"_metadata.deleted_at": None},
                {"_metadata.deleted_at": {"$exists": False}}
            ]
        }
        cursor = self.collection.find(full_query).skip(skip).limit(limit)
        records = await cursor.to_list(length=limit)
        for record in records:
            record["id"] = str(record["_id"])
            del record["_id"]
        return records

    async def search(self, entity_name: str, search_text: str, skip: int = 0, limit: int = 50):
        query = {
            "entity": entity_name,
            "$text": {"$search": search_text},
            "$or": [
                {"_metadata.deleted_at": None},
                {"_metadata.deleted_at": {"$exists": False}}
            ]
        }
        cursor = self.collection.find(query).skip(skip).limit(limit)
        records = await cursor.to_list(length=limit)
        for record in records:
            record["id"] = str(record["_id"])
            del record["_id"]
        return records

    async def get_by_id(self, entity_name: str, record_id: str):
        query = {
            "_id": ObjectId(record_id),
            "entity": entity_name,
            "$or": [
                {"_metadata.deleted_at": None},
                {"_metadata.deleted_at": {"$exists": False}}
            ]
        }
        record = await self.collection.find_one(query)
        if record:
            record["id"] = str(record["_id"])
            del record["_id"]
        return record

    async def check_uniqueness(self, entity_name: str, field_name: str, value: Any, exclude_record_id: str = None) -> bool:
        query = {
            "entity": entity_name,
            f"content.{field_name}": value,
            "$or": [
                {"_metadata.deleted_at": None},
                {"_metadata.deleted_at": {"$exists": False}}
            ]
        }
        if exclude_record_id:
            query["_id"] = {"$ne": ObjectId(exclude_record_id)}
            
        count = await self.collection.count_documents(query)
        return count == 0