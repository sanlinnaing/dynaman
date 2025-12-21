# Addressing Concerns About Existing Data on Schema Updates

This document addresses the concern of how to handle existing data when a schema is updated in Dynaman.

## The Challenge

When a schema is updated, existing records in the database that were created with the old schema might become "invalid" under the new schema rules. For example:

*   A field's type is changed (e.g., `string` to `number`).
*   A new required field is added.
*   A field is removed.
*   Validation constraints are made stricter (e.g., `min_length` is increased).

This can lead to two main problems:
1.  **Data Inconsistency:** Your database will contain a mix of records following different versions of the schema.
2.  **Application Errors:** When your application reads data that doesn't conform to the current schema, it might lead to unexpected behavior or crashes.

## Proposed Strategy: On-Read Validation and Explicit Updates

To manage this, we propose a strategy that prioritizes data integrity for new and updated records, while providing a clear path for handling older records.

1.  **Immediate Enforcement for New/Updated Data:** All new records and any updates to existing records will be strictly validated against the **latest** version of the schema. If validation fails, the operation will be rejected. This is the behavior you've seen with the validation error responses.

2.  **No Automatic Background Migration:** We will **not** implement an automatic, system-wide migration of all existing data every time a schema is changed. Such migrations are complex, can be resource-intensive (especially with large datasets), and carry risks of data loss if not perfectly executed.

3.  **Validation on Read (Future consideration):** While not in the immediate scope of the current request, a future enhancement could be to validate data when it is read. If an entity is read from the database and does not conform to the current schema, the API could return a specific error or a warning, indicating that the record is outdated.

## What This Means for You

*   **Updating Schemas is a Conscious Decision:** You should be aware that changing a schema can affect your existing data.
*   **Old Data Remains As-Is:** Old records will not be automatically updated. They will only be validated against the new schema if you attempt to **update** them.
*   **Updating a Record Requires Conformance:** If you `PUT` or `PATCH` an existing record, the entire record must be valid under the new schema. For example, if you added a new required field to the schema, you must include that new field in your update request for an old record, even if you are only changing another field.

This approach provides a good balance between flexibility and data integrity, without the high overhead of full data migrations.

## Next Steps

With this understanding, I will proceed with implementing the schema update endpoints.
