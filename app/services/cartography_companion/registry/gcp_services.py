from .service_definition import ServiceDefinition

GCP_SERVICES: list[ServiceDefinition] = [
    # ── Compute ───────────────────────────────────────────────────────────
    # sync(neo4j_session, compute, project_id, zones, gcp_update_tag, common_job_parameters)
    ServiceDefinition(
        key="compute",
        provider="gcp",
        display_name="Compute",
        module_path="cartography.intel.gcp.compute",
        function_name="sync",
        requires_region=False,
        gcp_client_service="compute",
        gcp_client_version="v1",
        gcp_prefetch="fetch_compute_zones",  # injects `zones`
        description="Sync GCP Compute instances, VPCs, subnets, firewalls, forwarding rules.",
    ),
    # ── Storage ───────────────────────────────────────────────────────────
    # sync(neo4j_session, storage, project_id, gcp_update_tag, common_job_parameters)
    ServiceDefinition(
        key="storage",
        provider="gcp",
        display_name="Storage",
        module_path="cartography.intel.gcp.storage",
        function_name="sync",
        requires_region=False,
        gcp_client_service="storage",
        gcp_client_version="v1",
        description="Sync GCP Cloud Storage buckets and labels.",
    ),
    # ── GKE ──────────────────────────────────────────────────────────────
    # sync(neo4j_session, container, project_id, clusters, gcp_update_tag, common_job_parameters)
    ServiceDefinition(
        key="gke",
        provider="gcp",
        display_name="GKE",
        module_path="cartography.intel.gcp.gke",
        function_name="sync",
        requires_region=False,
        depends_on=["compute"],
        gcp_client_service="container",
        gcp_client_version="v1",
        gcp_prefetch="fetch_gke_clusters",  # injects `clusters`
        description="Sync GKE clusters and node pools.",
    ),
    # ── DNS ───────────────────────────────────────────────────────────────
    # sync(neo4j_session, dns, project_id, gcp_update_tag, common_job_parameters)
    ServiceDefinition(
        key="dns",
        provider="gcp",
        display_name="DNS",
        module_path="cartography.intel.gcp.dns",
        function_name="sync",
        requires_region=False,
        gcp_client_service="dns",
        gcp_client_version="v1",
        description="Sync GCP Cloud DNS zones and record sets.",
    ),
    # ── IAM ───────────────────────────────────────────────────────────────
    # sync(neo4j_session, iam, project_id, gcp_update_tag, common_job_parameters)
    ServiceDefinition(
        key="iam",
        provider="gcp",
        display_name="IAM",
        module_path="cartography.intel.gcp.iam",
        function_name="sync",
        requires_region=False,
        gcp_client_service="iam",
        gcp_client_version="v1",
        description="Sync GCP IAM service accounts, roles and bindings.",
    ),
    # ── KMS ───────────────────────────────────────────────────────────────
    # sync(neo4j_session, kms, project_id, gcp_update_tag, common_job_parameters)
    ServiceDefinition(
        key="kms",
        provider="gcp",
        display_name="KMS",
        module_path="cartography.intel.gcp.kms",
        function_name="sync",
        requires_region=False,
        gcp_client_service="cloudkms",
        gcp_client_version="v1",
        description="Sync GCP Cloud KMS key rings and keys.",
    ),
    # ── Bigtable ──────────────────────────────────────────────────────────
    # sync(neo4j_session, bigtableadmin, project_id, instances, gcp_update_tag, common_job_parameters)
    ServiceDefinition(
        key="bigtable",
        provider="gcp",
        display_name="Bigtable",
        module_path="cartography.intel.gcp.bigtable",
        function_name="sync",
        requires_region=False,
        gcp_client_service="bigtableadmin",
        gcp_client_version="v2",
        gcp_prefetch="fetch_bigtable_instances",  # injects `instances`
        description="Sync GCP Bigtable instances, clusters and app profiles.",
    ),
    # ── BigQuery ──────────────────────────────────────────────────────────
    # sync(neo4j_session, bigquery, project_id, gcp_update_tag, common_job_parameters)
    ServiceDefinition(
        key="bigquery",
        provider="gcp",
        display_name="BigQuery",
        module_path="cartography.intel.gcp.bigquery",
        function_name="sync",
        requires_region=False,
        gcp_client_service="bigquery",
        gcp_client_version="v2",
        description="Sync GCP BigQuery datasets and tables.",
    ),
    # ── BigQuery Connection ───────────────────────────────────────────────
    # sync(neo4j_session, bigqueryconnection, project_id, gcp_update_tag, common_job_parameters)
    ServiceDefinition(
        key="bigquery_connection",
        provider="gcp",
        display_name="BigQuery Connection",
        module_path="cartography.intel.gcp.bigquery_connection",
        function_name="sync",
        requires_region=False,
        depends_on=["bigquery"],
        gcp_client_service="bigqueryconnection",
        gcp_client_version="v1",
        description="Sync GCP BigQuery external connection resources.",
    ),
    # ── Cloud Functions ───────────────────────────────────────────────────
    # sync(neo4j_session, cloudfunctions, project_id, gcp_update_tag, common_job_parameters)
    # NOTE: verify module path against your installed cartography version
    ServiceDefinition(
        key="gcf",
        provider="gcp",
        display_name="Cloud Functions",
        module_path="cartography.intel.gcp.cloudfunctions",
        function_name="sync",
        requires_region=False,
        gcp_client_service="cloudfunctions",
        gcp_client_version="v1",
        description="Sync GCP Cloud Functions.",
    ),
    # ── Cloud Run ─────────────────────────────────────────────────────────
    # NOTE: verify module path against your installed cartography version
    ServiceDefinition(
        key="cloud_run",
        provider="gcp",
        display_name="Cloud Run",
        module_path="cartography.intel.gcp.cloudrun",
        function_name="sync",
        requires_region=False,
        gcp_client_service="run",
        gcp_client_version="v1",
        description="Sync GCP Cloud Run services and revisions.",
    ),
    # ── Cloud SQL ─────────────────────────────────────────────────────────
    # sync(neo4j_session, sqladmin, project_id, gcp_update_tag, common_job_parameters)
    # NOTE: verify module path against your installed cartography version
    ServiceDefinition(
        key="cloud_sql",
        provider="gcp",
        display_name="Cloud SQL",
        module_path="cartography.intel.gcp.cloudsql",
        function_name="sync",
        requires_region=False,
        gcp_client_service="sqladmin",
        gcp_client_version="v1",
        description="Sync GCP Cloud SQL instances and databases.",
    ),
    # ── Secrets Manager ───────────────────────────────────────────────────
    # NOTE: verify module path against your installed cartography version
    ServiceDefinition(
        key="secretsmanager",
        provider="gcp",
        display_name="Secrets Manager",
        module_path="cartography.intel.gcp.secretmanager",
        function_name="sync",
        requires_region=False,
        gcp_client_service="secretmanager",
        gcp_client_version="v1",
        description="Sync GCP Secret Manager secrets.",
    ),
    # ── Artifact Registry ─────────────────────────────────────────────────
    # NOTE: verify module path against your installed cartography version
    ServiceDefinition(
        key="artifact_registry",
        provider="gcp",
        display_name="Artifact Registry",
        module_path="cartography.intel.gcp.artifactregistry",
        function_name="sync",
        requires_region=False,
        gcp_client_service="artifactregistry",
        gcp_client_version="v1",
        description="Sync GCP Artifact Registry repositories.",
    ),
    # ── AI Platform / Vertex AI ───────────────────────────────────────────
    # NOTE: verify module path against your installed cartography version
    ServiceDefinition(
        key="aiplatform",
        provider="gcp",
        display_name="AI Platform",
        module_path="cartography.intel.gcp.aiplatform",
        function_name="sync",
        requires_region=False,
        gcp_client_service="aiplatform",
        gcp_client_version="v1",
        description="Sync GCP Vertex AI / AI Platform resources.",
    ),
    # ── Policy Bindings ───────────────────────────────────────────────────
    ServiceDefinition(
        key="policy_bindings",
        provider="gcp",
        display_name="Policy Bindings",
        module_path="cartography.intel.gcp.iam",
        function_name="sync_policy_bindings",
        requires_region=False,
        depends_on=["iam"],
        gcp_client_service="cloudresourcemanager",
        gcp_client_version="v1",
        description="Sync GCP IAM policy bindings.",
    ),
    # ── Permission Relationships ──────────────────────────────────────────
    ServiceDefinition(
        key="permission_relationships",
        provider="gcp",
        display_name="Permission Relationships",
        module_path="cartography.intel.gcp.iam",
        function_name="sync_permission_relationships",
        requires_region=False,
        depends_on=["iam", "policy_bindings"],
        gcp_client_service="cloudresourcemanager",
        gcp_client_version="v1",
        description="Sync GCP IAM permission relationships between principals and resources.",
    ),
]
