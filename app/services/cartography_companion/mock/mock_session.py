# app/services/cartography_companion/mock/mock_session.py

import logging
from contextlib import contextmanager
from typing import Optional

from moto import mock_aws

from .fixture_loader import load_fixture, FIXTURE_MAP
from .seeders import (
    seed_vpcs,
    seed_subnets,
    seed_security_groups,
    seed_ec2_instances,
    seed_lambdas,
    seed_iam_roles,
    seed_dynamodb_tables,
)

logger = logging.getLogger(__name__)


class MockAWSSession:
    """
    Wraps Moto's mock_aws context.
    Seeds fixture data for the requested services, then returns
    a boto3.Session that cartography can use as-is.
    All boto3 calls inside the context go to Moto, not real AWS.
    """

    def __init__(self, region: str = "us-east-1", account_id: str = "123456789012"):
        self.region = region
        self.account_id = account_id
        self._mock = mock_aws()
        self._session = None

        # Shared state built up as services are seeded
        # downstream seeders (ec2:instance) need IDs from upstream (ec2:vpc)
        self._vpc_map: dict[str, str] = {}
        self._subnet_map: dict[str, str] = {}
        self._sg_map: dict[str, str] = {}
        self._role_map: dict[str, str] = {}

    def start(self) -> "MockAWSSession":
        self._mock.start()
        import boto3

        self._session = boto3.Session(region_name=self.region)
        return self

    def stop(self) -> None:
        self._mock.stop()

    def __enter__(self) -> "MockAWSSession":
        return self.start()

    def __exit__(self, *args) -> None:
        self.stop()

    @property
    def session(self):
        """The boto3.Session to hand to cartography."""
        if not self._session:
            raise RuntimeError("MockAWSSession not started — use as context manager")
        return self._session

    def seed(self, service_keys: list[str]) -> "MockAWSSession":
        """
        Seeds Moto with fixture data for the given service keys.
        Order matters — call this after start() but before handing
        session to cartography.
        """
        # Always seed in dependency order
        seed_order = [
            "iam",
            "ec2:vpc",
            "ec2:subnet",
            "ec2:security_group",
            "ec2:instance",
            "lambda_function",
            "dynamodb",
        ]
        keys_to_seed = [k for k in seed_order if k in service_keys]

        for key in keys_to_seed:
            try:
                self._seed_service(key)
            except FileNotFoundError as e:
                logger.warning(f"No fixture for {key}: {e} — seeding skipped")
            except Exception as e:
                logger.error(f"Failed to seed {key}: {e}")
                raise

        return self

    def _seed_service(self, key: str) -> None:
        import boto3

        if key == "iam":
            data = load_fixture("iam_roles.json")
            client = self._session.client("iam", region_name=self.region)
            self._role_map = seed_iam_roles(client, data)

        elif key == "ec2:vpc":
            data = load_fixture("vpcs.json")
            client = self._session.client("ec2", region_name=self.region)
            self._vpc_map = seed_vpcs(client, data)

        elif key == "ec2:subnet":
            data = load_fixture("subnets.json")
            client = self._session.client("ec2", region_name=self.region)
            self._subnet_map = seed_subnets(client, data, self._vpc_map)

        elif key == "ec2:security_group":
            data = load_fixture("security_groups.json")
            client = self._session.client("ec2", region_name=self.region)
            self._sg_map = seed_security_groups(client, data, self._vpc_map)

        elif key == "ec2:instance":
            data = load_fixture("ec2_instances.json")
            client = self._session.client("ec2", region_name=self.region)
            seed_ec2_instances(client, data, self._sg_map, self._subnet_map)

        elif key == "lambda_function":
            data = load_fixture("lambdas.json")
            client = self._session.client("lambda", region_name=self.region)
            default_role = next(
                iter(self._role_map.values()), "arn:aws:iam::123456789012:role/mock"
            )
            seed_lambdas(client, data, role_arn=default_role)

        elif key == "dynamodb":
            data = load_fixture("dynamodb_tables.json")
            client = self._session.client("dynamodb", region_name=self.region)
            seed_dynamodb_tables(client, data)

        logger.debug(f"Seeded: {key}")
