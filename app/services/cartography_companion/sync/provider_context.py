from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AWSContext:
    boto_session: Any  # boto3.Session


@dataclass
class AzureContext:
    credentials: Any  # cartography Credentials object


@dataclass
class GCPContext:
    google_credentials: Any  # google.oauth2 credentials
    project_id: str


def build_aws_context(service_keys: list[str]) -> AWSContext:
    import boto3

    return AWSContext(boto_session=boto3.Session())


def build_azure_context(account_id: str) -> AzureContext:
    from app.core.config import settings
    from cartography.intel.azure.util.credentials import Authenticator

    auth = Authenticator()
    if settings.AZURE_SP_AUTH:
        creds = auth.authenticate_sp(
            tenant_id=settings.AZURE_TENANT_ID or None,
            client_id=settings.AZURE_CLIENT_ID or None,
            client_secret=settings.AZURE_CLIENT_SECRET or None,
            subscription_id=account_id,
        )
    else:
        creds = auth.authenticate_cli()

    if creds is None:
        raise RuntimeError("Unable to authenticate to Azure.")
    return AzureContext(credentials=creds)


def build_gcp_context(account_id: str) -> GCPContext:
    from app.core.config import settings
    from cartography.intel.gcp.clients import get_gcp_credentials

    creds = get_gcp_credentials(quota_project_id=account_id or settings.GCP_PROJECT_ID or None)
    return GCPContext(google_credentials=creds, project_id=account_id)
