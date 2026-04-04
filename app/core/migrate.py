import logging
from pathlib import Path
from app.services.neo4j import Neo4jService

logger = logging.getLogger("cloud-companion")
MIGRATIONS_PATH = Path(__file__).parent / "migrations"


async def run_migrations(neo4j_service: Neo4jService):
    driver = neo4j_service.async_driver
    async with driver.session() as session:
        # Ensure migration tracking constraint
        await session.run(
            """
            CREATE CONSTRAINT migration_version IF NOT EXISTS
            FOR (m:Migration)
            REQUIRE m.version IS UNIQUE
            """
        )

        # Get applied migrations
        result = await session.run(
            """
            MATCH (m:Migration)
            RETURN m.version AS version
            """
        )
        applied = {record["version"] async for record in result}

        files = sorted(MIGRATIONS_PATH.glob("*.cypher"))
        for file in files:
            version = file.stem
            if version in applied:
                continue

            logger.info(f"Applying migration: {version}")
            cypher = file.read_text()

            statements = [s.strip() for s in cypher.split(";") if s.strip()]
            for statement in statements:
                await session.run(statement)  # type: ignore

            # Track applied migration — CREATE (never MERGE) since it's a unique event
            await session.run(
                """
                CREATE (:Migration {
                    version: $version,
                    applied_at: datetime()
                })
                """,
                version=version,
            )

        logger.info("Neo4j migrations complete.")


async def get_latest_migration_version(neo4j_service: Neo4jService):
    driver = neo4j_service.async_driver
    async with driver.session() as session:
        result = await session.run(
            """
            MATCH (m:Migration)
            RETURN m.version AS version
            ORDER BY m.applied_at DESC
            LIMIT 1
            
            """
        )
        record = await result.single()
        return record["version"] if record else None
