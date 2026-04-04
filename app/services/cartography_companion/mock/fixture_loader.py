# app/services/cartography_companion/mock/fixture_loader.py

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

import os

_SCENARIO = os.getenv("FIXTURES_SCENARIO", "default")
FIXTURES_DIR = Path(__file__).parents[5] / "fixtures" / "aws"

# Override with scenario subfolder if it exists
_SCENARIO_DIR = FIXTURES_DIR / _SCENARIO
if _SCENARIO_DIR.exists():
    FIXTURES_DIR = _SCENARIO_DIR


def load_fixture(filename: str) -> Any:
    path = FIXTURES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {path}")
    with open(path) as f:
        return json.load(f)


# Map service key → fixture files needed to seed that service
# Each entry is a list of (fixture_file, seeder_fn) tuples
FIXTURE_MAP: dict[str, list[tuple[str, str]]] = {
    "ec2:vpc": [("vpcs.json", "seed_vpcs")],
    "ec2:subnet": [("subnets.json", "seed_subnets")],
    "ec2:security_group": [("security_groups.json", "seed_security_groups")],
    "ec2:instance": [("ec2_instances.json", "seed_ec2_instances")],
    "lambda_function": [("lambdas.json", "seed_lambdas")],
    "iam": [("iam_roles.json", "seed_iam_roles")],
    "dynamodb": [("dynamodb_tables.json", "seed_dynamodb_tables")],
}
