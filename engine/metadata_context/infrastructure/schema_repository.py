from motor.motor_asyncio import AsyncIOMotorDatabase
import pymongo

class SchemaRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["schemas"]

    async def create_indexes(self):
        """Creates necessary indexes for the schema collection."""
        await self.collection.create_index(
            [("entity_name", 1), ("version", 1)],
            unique=True,
            name="schema_entity_name_version_unique_idx"
        )

    async def get_by_name(self, entity_name: str):
        """Gets the latest version of a schema by its name."""
        cursor = self.collection.find({"entity_name": entity_name}).sort("version", pymongo.DESCENDING).limit(1)
        documents = await cursor.to_list(length=1)
        return documents[0] if documents else None

    async def get_by_name_and_version(self, entity_name: str, version: int):
        """Gets a specific version of a schema."""
        return await self.collection.find_one({"entity_name": entity_name, "version": version})

    async def save(self, schema_dict: dict):
        """
        Saves a new version of a schema.
        The use case is responsible for setting the correct version number.
        A unique index on (name, version) in MongoDB will prevent duplicates.
        """
        await self.collection.insert_one(schema_dict)

    async def list_all(self):
        """Returns a list of all schema names."""
        return await self.collection.distinct("entity_name")

    async def delete(self, entity_name: str):
        """Deletes all versions of a schema by its name."""
        result = await self.collection.delete_many({"entity_name": entity_name})
        return result.deleted_count > 0