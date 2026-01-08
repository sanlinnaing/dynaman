from motor.motor_asyncio import AsyncIOMotorDatabase
from metadata_context.domain.entities.form_layout import FormLayout
from bson import ObjectId

class FormLayoutRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["form_layouts"]

    async def get_by_id(self, layout_id: str):
        try:
            oid = ObjectId(layout_id)
        except Exception:
            return None
        doc = await self.collection.find_one({"_id": oid})
        if doc:
            return FormLayout(**doc)
        return None

    async def get_by_schema(self, schema_name: str):
        cursor = self.collection.find({"schema_name": schema_name})
        layouts = []
        async for doc in cursor:
            layouts.append(FormLayout(**doc))
        return layouts

    async def create(self, layout: FormLayout):
        layout_dict = layout.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(layout_dict)
        layout.id = str(result.inserted_id)
        return layout

    async def update(self, layout_id: str, update_data: dict):
        if not update_data:
            return None
        try:
            oid = ObjectId(layout_id)
        except Exception:
            return None
        
        result = await self.collection.update_one(
            {"_id": oid},
            {"$set": update_data}
        )
        if result.modified_count > 0 or result.matched_count > 0:
            return await self.get_by_id(layout_id)
        return None

    async def delete(self, layout_id: str):
        try:
            oid = ObjectId(layout_id)
        except Exception:
            return False
        result = await self.collection.delete_one({"_id": oid})
        return result.deleted_count > 0
