from uuid import uuid4
from typing import Optional, Dict, Any, Annotated
from datetime import datetime
from enum import Enum

from app.core.constants import Node, CloudProviderEnum, utc_now


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------


def ensure_datetime(val: str | datetime) -> datetime:
    if isinstance(val, datetime):
        return val
    return datetime.fromisoformat(val)


# ---------------------------------------------------------------------------
# Base Node Model
# ---------------------------------------------------------------------------


class BaseNode:
    label: Node

    _enum_fields: Dict[str, type[Enum]] = {
        "provider": CloudProviderEnum,
    }

    def _coerce(self) -> None:
        for field, enum_cls in self._enum_fields.items():
            value = getattr(self, field, None)
            if value is None:
                continue
            if not isinstance(value, enum_cls):
                try:
                    setattr(self, field, enum_cls(value))
                except ValueError:
                    valid = [e.value for e in enum_cls]
                    raise ValueError(
                        f"Invalid value '{value}' for {field}. Must be one of: {valid}"
                    )

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Organizational Layer
# ---------------------------------------------------------------------------


class Organization(BaseNode):
    label = Node.ORGANIZATION

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        created_at: datetime | str = utc_now(),
        is_active: bool = True,
        id: Optional[str] = None,
    ):
        self.id = id or str(uuid4())
        self.name = name
        self.description = description
        self.created_at = ensure_datetime(created_at)
        self.is_active = is_active

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
        }


class APIKey(BaseNode):
    label = Node.API_KEY

    def __init__(
        self,
        org_id: str,
        name: str,
        hashed_key: str,
        expires_at: datetime | str,
        is_active: bool = True,
        created_at: datetime | str = utc_now(),
        id: Optional[str] = None,
    ):
        self.id = id or str(uuid4())
        self.org_id = org_id
        self.name = name
        self.hashed_key = hashed_key
        self.is_active = is_active
        self.created_at = ensure_datetime(created_at)
        self.expires_at = ensure_datetime(expires_at)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "org_id": self.org_id,
            "name": self.name,
            "hashed_key": self.hashed_key,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }


class Account(BaseNode):
    label = Node.ACCOUNT

    def __init__(
        self,
        org_id: str,
        name: str,
        provider: CloudProviderEnum,
        id: str,
        created_at: datetime | str = utc_now(),
    ):
        self.org_id = org_id
        self.name = name
        self.provider = provider
        self.id = id
        self.created_at = ensure_datetime(created_at)

        self._coerce()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "org_id": self.org_id,
            "name": self.name,
            "provider": self.provider.value,
            "created_at": self.created_at.isoformat(),
        }


# ---------------------------------------------------------------------------
# Location Layer
# ---------------------------------------------------------------------------


class Region(BaseNode):
    label = Node.REGION

    def __init__(
        self,
        provider: CloudProviderEnum,
        id: str,
        name: str,
    ):
        self.provider = provider
        self.code = id
        self.name = name

        self._coerce()

    def to_dict(self):
        return {
            "id": self.code,
            "provider": self.provider.value,
            "name": self.name,
        }


class AvailabilityZone(BaseNode):
    label = Node.AVAILABILITY_ZONE

    def __init__(
        self,
        provider: CloudProviderEnum,
        id: str,
        region_code: str,
    ):
        self.provider = provider
        self.name = id
        self.region_code = region_code

        self._coerce()

    def to_dict(self):
        return {
            "id": self.name,
            "region_code": self.region_code,
            "provider": self.provider.value,
        }


# ---------------------------------------------------------------------------
# Network Layer
# ---------------------------------------------------------------------------


class VirtualNetwork(BaseNode):
    label = Node.NETWORK

    def __init__(
        self,
        account_id: str,
        provider: CloudProviderEnum,
        id: str,
        name: Optional[str],
        region: str,
    ):
        self.account_id = account_id
        self.provider = provider
        self.id = id
        self.name = name
        self.region = region

        self._coerce()

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "provider": self.provider.value,
            "name": self.name,
            "region": self.region,
        }


class Subnet(BaseNode):
    label = Node.SUBNET

    def __init__(
        self,
        id: str,
        network_id: str,
        region: str,
        cidr: Optional[str],
        account_id: str,
    ):
        self.id = id
        self.network_id = network_id
        self.region = region
        self.cidr = cidr
        self.account_id = account_id

    def to_dict(self):
        return {
            "id": self.id,
            "network_id": self.network_id,
            "region": self.region,
            "cidr": self.cidr,
            "account_id": self.account_id,
        }


class RouteTable(BaseNode):
    label = Node.ROUTE_TABLE

    def __init__(
        self,
        id: str,
        account_id: str,
        provider: CloudProviderEnum,
        network_id: str,
        region: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.account_id = account_id
        self.provider = provider
        self.network_id = network_id
        self.region = region
        self.name = name
        self.metadata = metadata or {}

        self._coerce()

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "provider": self.provider.value,
            "network_id": self.network_id,
            "region": self.region,
            "name": self.name,
            "metadata": self.metadata,
        }


class SecurityBoundary(BaseNode):
    label = Node.SECURITY_BOUNDARY

    def __init__(
        self,
        id: str,
        name: Optional[str],
        account_id: str,
        provider: CloudProviderEnum,
    ):
        self.id = id
        self.name = name
        self.account_id = account_id
        self.provider = provider

        self._coerce()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "account_id": self.account_id,
            "provider": self.provider.value,
        }


class Gateway(BaseNode):
    label = Node.GATEWAY

    def __init__(
        self,
        id: str,
        account_id: str,
        provider: CloudProviderEnum,
        gateway_type: str,  # INTERNET, NAT, VPN, TRANSIT, etc.
        region: Optional[str] = None,
        network_id: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.account_id = account_id
        self.provider = provider
        self.gateway_type = gateway_type
        self.region = region
        self.network_id = network_id
        self.name = name
        self.metadata = metadata or {}

        self._coerce()

    def to_dict(self):
        return {
            "id": self.id,
            "account_id": self.account_id,
            "provider": self.provider.value,
            "gateway_type": self.gateway_type,
            "region": self.region,
            "network_id": self.network_id,
            "name": self.name,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Identity & Policy
# ---------------------------------------------------------------------------


class Identity(BaseNode):
    label = Node.IDENTITY

    def __init__(
        self,
        id: str,
        name: str,
        provider: CloudProviderEnum,
        account_id: str,
        identity_type: str,
    ):
        self.id = id
        self.name = name
        self.provider = provider
        self.account_id = account_id
        self.identity_type = identity_type

        self._coerce()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider.value,
            "account_id": self.account_id,
            "identity_type": self.identity_type,
        }


class Policy(BaseNode):
    label = Node.POLICY

    def __init__(
        self,
        id: str,
        name: str,
        provider: CloudProviderEnum,
        account_id: str,
    ):
        self.id = id
        self.name = name
        self.provider = provider
        self.account_id = account_id

        self._coerce()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider.value,
            "account_id": self.account_id,
        }


# ---------------------------------------------------------------------------
# Generic Cloud Resource Node
# ---------------------------------------------------------------------------


class Resource(BaseNode):
    """
    All cloud services (EC2, RDS, Lambda, AKS, GKE, etc.) fall into this generic node.
    """

    label = Node.RESOURCE

    def __init__(
        self,
        id: str,
        name: Optional[str],
        resource_type: str,
        provider: CloudProviderEnum,
        account_id: str,
        region: Optional[str] = None,
        network_id: Optional[str] = None,
        subnet_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: datetime | str = utc_now(),
    ):
        self.id = id
        self.name = name
        self.resource_type = resource_type
        self.provider = provider
        self.account_id = account_id
        self.region = region
        self.network_id = network_id
        self.subnet_id = subnet_id
        self.metadata = metadata or {}
        self.created_at = ensure_datetime(created_at)

        self._coerce()

    @property
    def node_type(self):
        from app.core.constants import ResourceType

        return ResourceType[self.provider][self.resource_type].node  # type: ignore

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "resource_type": self.resource_type,
            "provider": self.provider.value,
            "account_id": self.account_id,
            "region": self.region,
            "network_id": self.network_id,
            "subnet_id": self.subnet_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class ServiceSyncRecord(BaseNode):
    """
    Permanent per-service sync record in Neo4j.
    One node per (account_id, service_key) — always reflects the latest run.
    Written/upserted at completion of each service sync, never mid-run.

    Graph pattern:
        (Account)-[:HAS_SERVICE_SYNC]->(ServiceSyncRecord)
    """

    label = Node.SERVICE_SYNC_RECORD

    def __init__(
        self,
        account_id: str,
        service_key: str,
        provider: CloudProviderEnum | str,
        last_status: Annotated[str, "completed", "failed"],
        last_update_tag: int,
        last_regions: Optional[list[str]] = None,
        last_completed_at: Optional[datetime | str] = None,
        last_error: Optional[str] = None,
        id: Optional[str] = None,
        **kwargs,
    ):
        # Stable id — keyed on (account_id, service_key) so MERGE is idempotent
        self.id = id or f"{account_id}:{service_key}"
        self.account_id = account_id
        self.service_key = service_key
        self.provider = provider.value if isinstance(provider, CloudProviderEnum) else provider
        self.last_status = last_status
        self.last_update_tag = last_update_tag
        self.last_regions = last_regions or []
        self.last_completed_at = ensure_datetime(last_completed_at) if last_completed_at else None
        self.last_error = last_error
        self.meta: Dict[str, Any] = kwargs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "account_id": self.account_id,
            "service_key": self.service_key,
            "provider": self.provider,
            "last_status": self.last_status,
            "last_update_tag": self.last_update_tag,
            "last_regions": self.last_regions,
            "last_completed_at": (
                self.last_completed_at.isoformat() if self.last_completed_at else None
            ),
            "last_error": self.last_error,
        }


class SyncRun(BaseNode):
    """
    Represents one completed pipeline.run() call.
    Written to Neo4j ONCE at completion — never updated after that.
    Runtime state lives in Redis.
    """

    label = Node.SYNC_RUN

    def __init__(
        self,
        provider: CloudProviderEnum | str,
        account_id: str,
        started_at: datetime | str,
        update_tag: int,
        services: Optional[list[str]] = None,
        regions: Optional[list[str]] = None,
        trigger: Optional[Annotated[str, "setup", "scheduled", "manual"]] = None,
        status: Annotated[str, "completed", "failed", "partial"] = "completed",
        completed_at: Optional[datetime | str] = None,
        succeeded: Optional[list[str]] = None,
        failed: Optional[list[str]] = None,
        skipped: Optional[list[str]] = None,
        id: Optional[str] = None,
        **kwargs,
    ):
        self.id = id or str(uuid4())
        self.provider = provider.value if isinstance(provider, CloudProviderEnum) else provider
        self.account_id = account_id
        self.update_tag = update_tag
        self.services = services or []  # all requested keys
        self.regions = regions or []
        self.trigger = trigger
        self.status = status
        self.started_at = ensure_datetime(started_at)
        self.completed_at = ensure_datetime(completed_at) if completed_at else None
        self.succeeded = succeeded or []  # keys that completed ok
        self.failed = failed or []  # keys that errored at runtime
        self.skipped = skipped or []  # keys that were locked/skipped
        self.meta: Dict[str, Any] = kwargs

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "provider": self.provider,
            "account_id": self.account_id,
            "update_tag": self.update_tag,
            "services": self.services,
            "regions": self.regions,
            "trigger": self.trigger,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "skipped": self.skipped,
        }
