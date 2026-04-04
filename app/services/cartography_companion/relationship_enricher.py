import logging
from pathlib import Path
from typing import Any, Optional
import yaml

logger = logging.getLogger(__name__)


class RelationshipEnricher:
    """
    Loads enrichment_rules.yaml and runs each rule as a Cypher MERGE.
    All rules are idempotent — safe to run after every sync.
    """

    def __init__(self, neo4j: Any, rules_path: Optional[Path] = None):
        self.neo4j = neo4j
        rules_path = rules_path or Path(__file__).parent / "enrichment_rules.yaml"
        self.rules = self._load_rules(rules_path)

    def _load_rules(self, path: Path) -> list[dict]:
        with open(path) as f:
            data = yaml.safe_load(f)
        return data.get("rules", [])

    async def run_all(self, account_id: Optional[str] = None) -> dict[str, int]:
        """
        Runs all enrichment rules. Returns {rule_id: relationships_created}.
        account_id filtering is optional — most rules use node properties to scope.
        """
        results = {}
        for rule in self.rules:
            try:
                count = await self._run_rule(rule, account_id)
                results[rule["id"]] = count
                logger.info(f"Rule '{rule['id']}': {count} relationships merged")
            except Exception as e:
                logger.error(f"Rule '{rule['id']}' failed: {e}")
                results[rule["id"]] = -1
        return results

    async def run_rule(self, rule_id: str) -> int:
        rule = next((r for r in self.rules if r["id"] == rule_id), None)
        if not rule:
            raise ValueError(f"Rule '{rule_id}' not found")
        return await self._run_rule(rule)

    async def _run_rule(self, rule: dict, account_id: Optional[str] = None) -> int:
        cypher = rule["cypher"]
        # We wrap the rule's MERGE in a WITH to count results
        counting_cypher = f"""
        {cypher}
        RETURN count(*) AS merged_count
        """
        params = {}
        if account_id:
            params["account_id"] = account_id

        if hasattr(self.neo4j, "execute_query"):
            results = await self.neo4j.execute_query(counting_cypher, params)
            record = results[0] if results else None
        else:
            result = await self.neo4j.run(counting_cypher, **params)
            record = await result.single()

        return record["merged_count"] if record else 0
