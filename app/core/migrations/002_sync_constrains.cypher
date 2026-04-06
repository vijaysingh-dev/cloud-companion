CREATE CONSTRAINT service_sync_record_id IF NOT EXISTS
FOR (r:ServiceSyncRecord) REQUIRE r.id IS UNIQUE;

