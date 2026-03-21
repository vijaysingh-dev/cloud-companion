from uuid import uuid4
from typing import Optional, Dict, Any, Annotated
from datetime import datetime

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
    label: str

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
    ):
        self.org_id = str(uuid4())
        self.name = name
        self.description = description
        self.created_at = ensure_datetime(created_at)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "org_id": self.org_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
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
    ):
        self.key_id = str(uuid4())
        self.org_id = org_id
        self.name = name
        self.hashed_key = hashed_key
        self.is_active = is_active
        self.created_at = ensure_datetime(created_at)
        self.expires_at = ensure_datetime(expires_at)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key_id": self.key_id,
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
        account_id: str,
        created_at: datetime | str = utc_now(),
        last_synced: datetime | str = utc_now(),
    ):
        self.org_id = org_id
        self.name = name
        self.provider = provider
        self.account_id = account_id
        self.created_at = ensure_datetime(created_at)
        self.last_synced = ensure_datetime(last_synced)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "org_id": self.org_id,
            "name": self.name,
            "provider": self.provider.value,
            "account_id": self.account_id,
            "created_at": self.created_at.isoformat(),
            "last_synced": self.last_synced.isoformat(),
        }


# ---------------------------------------------------------------------------
# Location Layer
# ---------------------------------------------------------------------------


class Region(BaseNode):
    label = Node.REGION

    def __init__(
        self,
        provider: CloudProviderEnum,
        code: str,
        name: str,
    ):
        self.provider = provider
        self.code = code
        self.name = name

    def to_dict(self):
        return {
            "provider": self.provider.value,
            "code": self.code,
            "name": self.name,
        }


class AvailabilityZone(BaseNode):
    label = Node.AVAILABILITY_ZONE

    def __init__(
        self,
        provider: CloudProviderEnum,
        name: str,
        region_code: str,
    ):
        self.provider = provider
        self.name = name
        self.region_code = region_code

    def to_dict(self):
        return {
            "provider": self.provider.value,
            "name": self.name,
            "region_code": self.region_code,
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
        network_id: str,
        name: Optional[str],
        region: str,
    ):
        self.account_id = account_id
        self.provider = provider
        self.network_id = network_id
        self.name = name
        self.region = region

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "provider": self.provider.value,
            "network_id": self.network_id,
            "name": self.name,
            "region": self.region,
        }


class Subnet(BaseNode):
    label = Node.SUBNET

    def __init__(
        self,
        subnet_id: str,
        network_id: str,
        region: str,
        cidr: Optional[str],
        account_id: str,
    ):
        self.subnet_id = subnet_id
        self.network_id = network_id
        self.region = region
        self.cidr = cidr
        self.account_id = account_id

    def to_dict(self):
        return {
            "subnet_id": self.subnet_id,
            "network_id": self.network_id,
            "region": self.region,
            "cidr": self.cidr,
            "account_id": self.account_id,
        }


class RouteTable(BaseNode):
    label = Node.ROUTE_TABLE

    def __init__(
        self,
        route_table_id: str,
        account_id: str,
        provider: CloudProviderEnum,
        network_id: str,
        region: str,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.route_table_id = route_table_id
        self.account_id = account_id
        self.provider = provider
        self.network_id = network_id
        self.region = region
        self.name = name
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "route_table_id": self.route_table_id,
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
        boundary_id: str,
        name: Optional[str],
        account_id: str,
        provider: CloudProviderEnum,
    ):
        self.boundary_id = boundary_id
        self.name = name
        self.account_id = account_id
        self.provider = provider

    def to_dict(self):
        return {
            "boundary_id": self.boundary_id,
            "name": self.name,
            "account_id": self.account_id,
            "provider": self.provider.value,
        }


class Gateway(BaseNode):
    label = Node.GATEWAY

    def __init__(
        self,
        gateway_id: str,
        account_id: str,
        provider: CloudProviderEnum,
        gateway_type: str,  # INTERNET, NAT, VPN, TRANSIT, etc.
        region: Optional[str] = None,
        network_id: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.gateway_id = gateway_id
        self.account_id = account_id
        self.provider = provider
        self.gateway_type = gateway_type
        self.region = region
        self.network_id = network_id
        self.name = name
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "gateway_id": self.gateway_id,
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
        identity_id: str,
        name: str,
        provider: CloudProviderEnum,
        account_id: str,
        identity_type: str,
    ):
        self.identity_id = identity_id
        self.name = name
        self.provider = provider
        self.account_id = account_id
        self.identity_type = identity_type

    def to_dict(self):
        return {
            "identity_id": self.identity_id,
            "name": self.name,
            "provider": self.provider.value,
            "account_id": self.account_id,
            "identity_type": self.identity_type,
        }


class Policy(BaseNode):
    label = Node.POLICY

    def __init__(
        self,
        policy_id: str,
        name: str,
        provider: CloudProviderEnum,
        account_id: str,
    ):
        self.policy_id = policy_id
        self.name = name
        self.provider = provider
        self.account_id = account_id

    def to_dict(self):
        return {
            "policy_id": self.policy_id,
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
        resource_id: str,
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
        self.resource_id = resource_id
        self.name = name
        self.resource_type = resource_type
        self.provider = provider
        self.account_id = account_id
        self.region = region
        self.network_id = network_id
        self.subnet_id = subnet_id
        self.metadata = metadata or {}
        self.created_at = ensure_datetime(created_at)

    @property
    def node_type(self):
        from app.core.constants import ResourceType

        return ResourceType[self.provider][self.resource_type].node  # type: ignore

    def to_dict(self):
        return {
            "resource_id": self.resource_id,
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


class SyncMetadata(BaseNode):
    label = Node.SYNC_METADATA

    def __init__(
        self,
        account_id: str,
        regions: list[str],
        services: list[str],
        sync_type: Annotated[str, "baseline", "incremental"],
        trigger: Annotated[str, "setup", "scheduled", "manual"],
        started_at: datetime | str = utc_now(),
        completed_at: Optional[datetime | str] = None,
    ):
        self.sync_id = str(uuid4())
        self.account_id = account_id
        self.regions = regions
        self.services = services
        self.sync_type = sync_type
        self.trigger = trigger
        self.started_at = ensure_datetime(started_at)
        self.completed_at = ensure_datetime(completed_at) if completed_at else None

    def to_dict(self):
        return {
            "sync_id": self.sync_id,
            "account_id": self.account_id,
            "regions": self.regions,
            "services": self.services,
            "sync_type": self.sync_type,
            "trigger": self.trigger,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
