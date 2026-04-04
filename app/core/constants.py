from enum import Enum
from datetime import datetime, timezone


class AppMode(str, Enum):
    API = "API"
    CELERY = "CELERY"
    CLI = "CLI"


class Node(str, Enum):

    # Organization / Tenant
    ORGANIZATION = "Organization"
    ACCOUNT = "Account"
    PROJECT = "Project"
    SUBSCRIPTION = "Subscription"
    API_KEY = "APIKey"

    # Geography
    REGION = "Region"
    AVAILABILITY_ZONE = "AvailabilityZone"

    # Networking
    NETWORK = "VirtualNetwork"
    SUBNET = "Subnet"
    ROUTE_TABLE = "RouteTable"
    GATEWAY = "Gateway"
    LOAD_BALANCER = "LoadBalancer"
    FIREWALL = "Firewall"
    NETWORK_POLICY = "NetworkPolicy"
    SECURITY_BOUNDARY = "SecurityBoundary"

    # Compute
    COMPUTE = "Compute"
    SERVERLESS_FUNCTION = "ServerlessFunction"
    CONTAINER_SERVICE = "ContainerService"
    CONTAINER_CLUSTER = "ContainerCluster"

    # Storage
    OBJECT_STORAGE = "ObjectStorage"
    BLOCK_STORAGE = "BlockStorage"
    FILE_STORAGE = "FileStorage"

    # Databases
    DATABASE = "Database"
    CACHE = "Cache"
    DATA_WAREHOUSE = "DataWarehouse"

    # Messaging
    MESSAGE_QUEUE = "MessageQueue"
    EVENT_BUS = "EventBus"
    STREAM = "Stream"

    # Identity & Security
    IDENTITY = "Identity"
    ROLE = "Role"
    SERVICE_ACCOUNT = "ServiceAccount"
    POLICY = "Policy"
    SECRET = "Secret"
    ENCRYPTION_KEY = "EncryptionKey"

    # API / Edge
    API = "API"
    CDN = "CDN"

    # Observability
    LOGGING = "Logging"
    MONITORING = "Monitoring"
    TRACING = "Tracing"

    # DevOps
    BUILD_SERVICE = "BuildService"
    DEPLOYMENT_SERVICE = "DeploymentService"
    INFRASTRUCTURE_AS_CODE = "InfrastructureAsCode"

    # Generic fallback
    RESOURCE = "Resource"

    # Utils
    SERVICE_SYNC_RECORD = "ServiceSyncRecord"
    SYNC_RUN = "SyncRun"


class Relationship(str, Enum):

    # Organizational
    OWNS = "OWNS"
    MANAGES = "MANAGES"
    HAS_API_KEY = "HAS_API_KEY"
    BELONGS_TO = "BELONGS_TO"

    # Location
    LOCATED_IN = "LOCATED_IN"
    DEPLOYED_IN = "DEPLOYED_IN"
    AVAILABLE_IN = "AVAILABLE_IN"

    # Structural
    CONTAINS = "CONTAINS"
    PART_OF = "PART_OF"
    ATTACHED_TO = "ATTACHED_TO"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    HAS_SYNC = "HAS_SYNC"
    HAS_SERVICE_SYNC = "HAS_SERVICE_SYNC"

    # Networking
    HOSTS = "HOSTS"
    ROUTES_TO = "ROUTES_TO"
    CONNECTS_TO = "CONNECTS_TO"
    EXPOSES = "EXPOSES"
    PROTECTS = "PROTECTS"
    ALLOWS_TRAFFIC_TO = "ALLOWS_TRAFFIC_TO"
    DENIES_TRAFFIC_TO = "DENIES_TRAFFIC_TO"

    # IAM / Security
    HAS_POLICY = "HAS_POLICY"
    GRANTS_PERMISSION = "GRANTS_PERMISSION"
    HAS_ACCESS_TO = "HAS_ACCESS_TO"
    ASSUMES_IDENTITY = "ASSUMES_IDENTITY"
    TRUSTS = "TRUSTS"
    IMPERSONATES = "IMPERSONATES"
    AUTHENTICATES_WITH = "AUTHENTICATES_WITH"

    # Compute / Storage
    RUNS_ON = "RUNS_ON"
    USES = "USES"
    MOUNTS = "MOUNTS"
    BACKED_BY = "BACKED_BY"
    ENCRYPTED_BY = "ENCRYPTED_BY"
    BACKED_UP_BY = "BACKED_UP_BY"

    # Data Flow
    READS_FROM = "READS_FROM"
    WRITES_TO = "WRITES_TO"
    STREAMS_TO = "STREAMS_TO"
    FORWARDS_TO = "FORWARDS_TO"

    # Dependency
    DEPENDS_ON = "DEPENDS_ON"
    CALLS = "CALLS"
    TRIGGERS = "TRIGGERS"
    REPLICATES_TO = "REPLICATES_TO"
    FAILS_OVER_TO = "FAILS_OVER_TO"

    HAS_COMPONENT = "HAS_COMPONENT"
    CONFIGURES = "CONFIGURES"
    DEPENDS_ON_COMPONENT = "DEPENDS_ON_COMPONENT"

    # Observability
    EMITS_LOGS_TO = "EMITS_LOGS_TO"
    EMITS_METRICS_TO = "EMITS_METRICS_TO"
    MONITORED_BY = "MONITORED_BY"
    TRACED_BY = "TRACED_BY"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CloudProviderEnum(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class CartographyAccount(str, Enum):
    AWS_ACCOUNT = "AWSAccount"
    AZURE_SUBSCRIPTION = "AzureSubscription"
    GCP_PROJECT = "GCPProject"


PROVIDER_ACCOUNT_MAP = {
    CloudProviderEnum.AWS: CartographyAccount.AWS_ACCOUNT,
    CloudProviderEnum.AZURE: CartographyAccount.AZURE_SUBSCRIPTION,
    CloudProviderEnum.GCP: CartographyAccount.GCP_PROJECT,
}


class Region:

    class AWS(Enum):
        # North America
        US_EAST_1 = ("us-east-1", "US East (N. Virginia)")
        US_EAST_2 = ("us-east-2", "US East (Ohio)")
        US_WEST_1 = ("us-west-1", "US West (N. California)")
        US_WEST_2 = ("us-west-2", "US West (Oregon)")
        CA_CENTRAL_1 = ("ca-central-1", "Canada (Central)")
        MX_CENTRAL_1 = ("mx-central-1", "Mexico (Central)")

        # Europe & Middle East
        EU_WEST_1 = ("eu-west-1", "Europe (Ireland)")
        EU_WEST_2 = ("eu-west-2", "Europe (London)")
        EU_CENTRAL_1 = ("eu-central-1", "Europe (Frankfurt)")
        EU_SOUTH_2 = ("eu-south-2", "Europe (Spain)")
        ME_CENTRAL_1 = ("me-central-1", "Middle East (UAE)")
        IL_CENTRAL_1 = ("il-central-1", "Israel (Tel Aviv)")

        # Asia Pacific
        AP_SOUTH_1 = ("ap-south-1", "Asia Pacific (Mumbai)")
        AP_SOUTHEAST_1 = ("ap-southeast-1", "Asia Pacific (Singapore)")
        AP_SOUTHEAST_2 = ("ap-southeast-2", "Asia Pacific (Sydney)")
        AP_NORTHEAST_1 = ("ap-northeast-1", "Asia Pacific (Tokyo)")

        @property
        def code(self):
            return self.value[0]

        @property
        def name(self):
            return self.value[1]

    class AZURE(Enum):
        # North America
        EAST_US = ("eastus", "East US")
        EAST_US_2 = ("eastus2", "East US 2")
        WEST_US_2 = ("westus2", "West US 2")
        CENTRAL_US = ("centralus", "Central US")
        MEXICO_CENTRAL = ("mexicocentral", "Mexico Central")

        # Europe
        NORTH_EUROPE = ("northeurope", "North Europe (Ireland)")
        WEST_EUROPE = ("westeurope", "West Europe (Netherlands)")
        UK_SOUTH = ("uksouth", "UK South")
        FRANCE_CENTRAL = ("francecentral", "France Central")
        ITALY_NORTH = ("italynorth", "Italy North")

        # Asia
        SOUTHEAST_ASIA = ("southeastasia", "Southeast Asia (Singapore)")
        EAST_ASIA = ("eastasia", "East Asia (Hong Kong)")
        JAPAN_EAST = ("japaneast", "Japan East")
        CENTRAL_INDIA = ("centralindia", "Central India")

        @property
        def code(self):
            return self.value[0]

        @property
        def name(self):
            return self.value[1]

    class GCP(Enum):
        # North America
        US_CENTRAL_1 = ("us-central1", "Iowa, USA")
        US_EAST_1 = ("us-east1", "South Carolina, USA")
        US_EAST_4 = ("us-east4", "N. Virginia, USA")
        US_WEST_1 = ("us-west1", "Oregon, USA")
        NORTHAMERICA_SOUTH_1 = ("northamerica-south1", "Queretaro, Mexico")

        # Europe
        EUROPE_WEST_1 = ("europe-west1", "Belgium")
        EUROPE_WEST_2 = ("europe-west2", "London, UK")
        EUROPE_WEST_3 = ("europe-west3", "Frankfurt, Germany")
        EUROPE_SOUTHWEST_1 = ("europe-southwest1", "Madrid, Spain")

        # Asia
        ASIA_SOUTH_1 = ("asia-south1", "Mumbai, India")
        ASIA_SOUTHEAST_1 = ("asia-southeast1", "Singapore")
        ASIA_NORTHEAST_1 = ("asia-northeast1", "Tokyo, Japan")
        AUSTRALIA_SOUTHEAST_1 = ("australia-southeast1", "Sydney, Australia")

        @property
        def code(self):
            return self.value[0]

        @property
        def name(self):
            return self.value[1]


class BaseResourceType(str, Enum):
    node: Node

    def __new__(cls, value: str, node: Node):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.node = node
        return obj

    @property
    def provider(self) -> CloudProviderEnum:
        return CloudProviderEnum[self.__class__.__name__]


class ResourceType:

    class AWS(BaseResourceType):
        AWS_APIGATEWAY_API_KEY = ("AWS_apigateway_ApiKey", Node.API)
        AWS_APIGATEWAY_AUTHORIZER = ("AWS_apigateway_Authorizer", Node.API)
        AWS_APIGATEWAY_BASE_PATH_MAPPING = ("AWS_apigateway_BasePathMapping", Node.API)
        AWS_APIGATEWAY_DEPLOYMENT = ("AWS_apigateway_Deployment", Node.API)
        AWS_APIGATEWAY_DOCUMENTATION_PART = ("AWS_apigateway_DocumentationPart", Node.API)
        AWS_APIGATEWAY_DOCUMENTATION_VERSION = ("AWS_apigateway_DocumentationVersion", Node.API)
        AWS_APIGATEWAY_DOMAIN_NAME = ("AWS_apigateway_DomainName", Node.API)
        AWS_APIGATEWAY_DOMAIN_NAME_ACCESS_ASSOCIATION = (
            "AWS_apigateway_DomainNameAccessAssociation",
            Node.API,
        )
        AWS_APIGATEWAY_MODEL = ("AWS_apigateway_Model", Node.API)
        AWS_APIGATEWAY_RESOURCE = ("AWS_apigateway_Resource", Node.API)
        AWS_APIGATEWAY_REST_API = ("AWS_apigateway_RestApi", Node.API)
        AWS_APIGATEWAY_STAGE = ("AWS_apigateway_Stage", Node.API)
        AWS_APIGATEWAY_USAGE_PLAN = ("AWS_apigateway_UsagePlan", Node.API)
        AWS_APIGATEWAY_USAGE_PLAN_KEY = ("AWS_apigateway_UsagePlanKey", Node.API)
        AWS_APIGATEWAY_VPC_LINK = ("AWS_apigateway_VpcLink", Node.API)
        AWS_DYNAMODB_BACKUP = ("AWS_dynamodb_Backup", Node.DATABASE)
        AWS_DYNAMODB_TABLE = ("AWS_dynamodb_Table", Node.DATABASE)
        AWS_EC2_CAPACITY_MANAGER_DATA_EXPORT = ("AWS_ec2_CapacityManagerDataExport", Node.COMPUTE)
        AWS_EC2_CARRIER_GATEWAY = ("AWS_ec2_CarrierGateway", Node.COMPUTE)
        AWS_EC2_CLIENT_VPN_ENDPOINT = ("AWS_ec2_ClientVpnEndpoint", Node.COMPUTE)
        AWS_EC2_CLIENT_VPN_ROUTE = ("AWS_ec2_ClientVpnRoute", Node.COMPUTE)
        AWS_EC2_COIP_CIDR = ("AWS_ec2_CoipCidr", Node.COMPUTE)
        AWS_EC2_COIP_POOL = ("AWS_ec2_CoipPool", Node.COMPUTE)
        AWS_EC2_CUSTOMER_GATEWAY = ("AWS_ec2_CustomerGateway", Node.COMPUTE)
        AWS_EC2_DHCP_OPTIONS = ("AWS_ec2_DhcpOptions", Node.COMPUTE)
        AWS_EC2_EGRESS_ONLY_INTERNET_GATEWAY = ("AWS_ec2_EgressOnlyInternetGateway", Node.COMPUTE)
        AWS_EC2_FLOW_LOGS = ("AWS_ec2_FlowLogs", Node.COMPUTE)
        AWS_EC2_FPGA_IMAGE = ("AWS_ec2_FpgaImage", Node.COMPUTE)
        AWS_EC2_IMAGE_USAGE_REPORT = ("AWS_ec2_ImageUsageReport", Node.COMPUTE)
        AWS_EC2_INSTANCE_CONNECT_ENDPOINT = ("AWS_ec2_InstanceConnectEndpoint", Node.COMPUTE)
        AWS_EC2_INSTANCE_EVENT_WINDOW = ("AWS_ec2_InstanceEventWindow", Node.COMPUTE)
        AWS_EC2_INTERNET_GATEWAY = ("AWS_ec2_InternetGateway", Node.COMPUTE)
        AWS_EC2_IPAM = ("AWS_ec2_Ipam", Node.COMPUTE)
        AWS_EC2_IPAM_EXTERNAL_RESOURCE_VERIFICATION_TOKEN = (
            "AWS_ec2_IpamExternalResourceVerificationToken",
            Node.COMPUTE,
        )
        AWS_EC2_IPAM_POLICY = ("AWS_ec2_IpamPolicy", Node.COMPUTE)
        AWS_EC2_IPAM_POOL = ("AWS_ec2_IpamPool", Node.COMPUTE)
        AWS_EC2_IPAM_PREFIX_LIST_RESOLVER = ("AWS_ec2_IpamPrefixListResolver", Node.COMPUTE)
        AWS_EC2_IPAM_PREFIX_LIST_RESOLVER_TARGET = (
            "AWS_ec2_IpamPrefixListResolverTarget",
            Node.COMPUTE,
        )
        AWS_EC2_IPAM_RESOURCE_DISCOVERY = ("AWS_ec2_IpamResourceDiscovery", Node.COMPUTE)
        AWS_EC2_IPAM_SCOPE = ("AWS_ec2_IpamScope", Node.COMPUTE)
        AWS_EC2_KEY_PAIR = ("AWS_ec2_KeyPair", Node.COMPUTE)
        AWS_EC2_LAUNCH_TEMPLATE = ("AWS_ec2_LaunchTemplate", Node.COMPUTE)
        AWS_EC2_LOCAL_GATEWAY_ROUTE = ("AWS_ec2_LocalGatewayRoute", Node.COMPUTE)
        AWS_EC2_LOCAL_GATEWAY_ROUTE_TABLE = ("AWS_ec2_LocalGatewayRouteTable", Node.COMPUTE)
        AWS_EC2_LOCAL_GATEWAY_ROUTE_TABLE_VIRTUAL_INTERFACE_GROUP_ASSOCIATION = (
            "AWS_ec2_LocalGatewayRouteTableVirtualInterfaceGroupAssociation",
            Node.COMPUTE,
        )
        AWS_EC2_LOCAL_GATEWAY_ROUTE_TABLE_VPC_ASSOCIATION = (
            "AWS_ec2_LocalGatewayRouteTableVpcAssociation",
            Node.COMPUTE,
        )
        AWS_EC2_LOCAL_GATEWAY_VIRTUAL_INTERFACE = (
            "AWS_ec2_LocalGatewayVirtualInterface",
            Node.COMPUTE,
        )
        AWS_EC2_LOCAL_GATEWAY_VIRTUAL_INTERFACE_GROUP = (
            "AWS_ec2_LocalGatewayVirtualInterfaceGroup",
            Node.COMPUTE,
        )
        AWS_EC2_MANAGED_PREFIX_LIST = ("AWS_ec2_ManagedPrefixList", Node.COMPUTE)
        AWS_EC2_NAT_GATEWAY = ("AWS_ec2_NatGateway", Node.COMPUTE)
        AWS_EC2_NETWORK_ACL = ("AWS_ec2_NetworkAcl", Node.COMPUTE)
        AWS_EC2_NETWORK_ACL_ENTRY = ("AWS_ec2_NetworkAclEntry", Node.COMPUTE)
        AWS_EC2_NETWORK_INSIGHTS_ACCESS_SCOPE = ("AWS_ec2_NetworkInsightsAccessScope", Node.COMPUTE)
        AWS_EC2_NETWORK_INSIGHTS_PATH = ("AWS_ec2_NetworkInsightsPath", Node.COMPUTE)
        AWS_EC2_NETWORK_INTERFACE = ("AWS_ec2_NetworkInterface", Node.COMPUTE)
        AWS_EC2_NETWORK_INTERFACE_PERMISSION = ("AWS_ec2_NetworkInterfacePermission", Node.COMPUTE)
        AWS_EC2_PLACEMENT_GROUP = ("AWS_ec2_PlacementGroup", Node.COMPUTE)
        AWS_EC2_PUBLIC_IPV4POOL = ("AWS_ec2_PublicIpv4Pool", Node.COMPUTE)
        AWS_EC2_ROUTE = ("AWS_ec2_Route", Node.COMPUTE)
        AWS_EC2_ROUTE_SERVER = ("AWS_ec2_RouteServer", Node.COMPUTE)
        AWS_EC2_ROUTE_SERVER_ENDPOINT = ("AWS_ec2_RouteServerEndpoint", Node.COMPUTE)
        AWS_EC2_ROUTE_SERVER_PEER = ("AWS_ec2_RouteServerPeer", Node.COMPUTE)
        AWS_EC2_ROUTE_TABLE = ("AWS_ec2_RouteTable", Node.COMPUTE)
        AWS_EC2_SECONDARY_NETWORK = ("AWS_ec2_SecondaryNetwork", Node.COMPUTE)
        AWS_EC2_SECONDARY_SUBNET = ("AWS_ec2_SecondarySubnet", Node.COMPUTE)
        AWS_EC2_SECURITY_GROUP = ("AWS_ec2_SecurityGroup", Node.COMPUTE)
        AWS_EC2_SNAPSHOT = ("AWS_ec2_Snapshot", Node.COMPUTE)
        AWS_EC2_SPOT_DATAFEED_SUBSCRIPTION = ("AWS_ec2_SpotDatafeedSubscription", Node.COMPUTE)
        AWS_EC2_SUBNET = ("AWS_ec2_Subnet", Node.COMPUTE)
        AWS_EC2_SUBNET_CIDR_RESERVATION = ("AWS_ec2_SubnetCidrReservation", Node.COMPUTE)
        AWS_EC2_TAGS = ("AWS_ec2_Tags", Node.COMPUTE)
        AWS_EC2_TRAFFIC_MIRROR_FILTER = ("AWS_ec2_TrafficMirrorFilter", Node.COMPUTE)
        AWS_EC2_TRAFFIC_MIRROR_FILTER_RULE = ("AWS_ec2_TrafficMirrorFilterRule", Node.COMPUTE)
        AWS_EC2_TRAFFIC_MIRROR_SESSION = ("AWS_ec2_TrafficMirrorSession", Node.COMPUTE)
        AWS_EC2_TRAFFIC_MIRROR_TARGET = ("AWS_ec2_TrafficMirrorTarget", Node.COMPUTE)
        AWS_EC2_TRANSIT_GATEWAY = ("AWS_ec2_TransitGateway", Node.COMPUTE)
        AWS_EC2_TRANSIT_GATEWAY_CONNECT = ("AWS_ec2_TransitGatewayConnect", Node.COMPUTE)
        AWS_EC2_TRANSIT_GATEWAY_CONNECT_PEER = ("AWS_ec2_TransitGatewayConnectPeer", Node.COMPUTE)
        AWS_EC2_TRANSIT_GATEWAY_METERING_POLICY = (
            "AWS_ec2_TransitGatewayMeteringPolicy",
            Node.COMPUTE,
        )
        AWS_EC2_TRANSIT_GATEWAY_METERING_POLICY_ENTRY = (
            "AWS_ec2_TransitGatewayMeteringPolicyEntry",
            Node.COMPUTE,
        )
        AWS_EC2_TRANSIT_GATEWAY_MULTICAST_DOMAIN = (
            "AWS_ec2_TransitGatewayMulticastDomain",
            Node.COMPUTE,
        )
        AWS_EC2_TRANSIT_GATEWAY_PEERING_ATTACHMENT = (
            "AWS_ec2_TransitGatewayPeeringAttachment",
            Node.COMPUTE,
        )
        AWS_EC2_TRANSIT_GATEWAY_POLICY_TABLE = ("AWS_ec2_TransitGatewayPolicyTable", Node.COMPUTE)
        AWS_EC2_TRANSIT_GATEWAY_PREFIX_LIST_REFERENCE = (
            "AWS_ec2_TransitGatewayPrefixListReference",
            Node.COMPUTE,
        )
        AWS_EC2_TRANSIT_GATEWAY_ROUTE = ("AWS_ec2_TransitGatewayRoute", Node.COMPUTE)
        AWS_EC2_TRANSIT_GATEWAY_ROUTE_TABLE = ("AWS_ec2_TransitGatewayRouteTable", Node.COMPUTE)
        AWS_EC2_TRANSIT_GATEWAY_ROUTE_TABLE_ANNOUNCEMENT = (
            "AWS_ec2_TransitGatewayRouteTableAnnouncement",
            Node.COMPUTE,
        )
        AWS_EC2_TRANSIT_GATEWAY_VPC_ATTACHMENT = (
            "AWS_ec2_TransitGatewayVpcAttachment",
            Node.COMPUTE,
        )
        AWS_EC2_VERIFIED_ACCESS_ENDPOINT = ("AWS_ec2_VerifiedAccessEndpoint", Node.COMPUTE)
        AWS_EC2_VERIFIED_ACCESS_GROUP = ("AWS_ec2_VerifiedAccessGroup", Node.COMPUTE)
        AWS_EC2_VERIFIED_ACCESS_INSTANCE = ("AWS_ec2_VerifiedAccessInstance", Node.COMPUTE)
        AWS_EC2_VERIFIED_ACCESS_TRUST_PROVIDER = (
            "AWS_ec2_VerifiedAccessTrustProvider",
            Node.COMPUTE,
        )
        AWS_EC2_VOLUME = ("AWS_ec2_Volume", Node.COMPUTE)
        AWS_EC2_VPC = ("AWS_ec2_Vpc", Node.COMPUTE)
        AWS_EC2_VPC_BLOCK_PUBLIC_ACCESS_EXCLUSION = (
            "AWS_ec2_VpcBlockPublicAccessExclusion",
            Node.COMPUTE,
        )
        AWS_EC2_VPC_ENCRYPTION_CONTROL = ("AWS_ec2_VpcEncryptionControl", Node.COMPUTE)
        AWS_EC2_VPC_PEERING_CONNECTION = ("AWS_ec2_VpcPeeringConnection", Node.COMPUTE)
        AWS_EC2_VPN_CONCENTRATOR = ("AWS_ec2_VpnConcentrator", Node.COMPUTE)
        AWS_EC2_VPN_CONNECTION = ("AWS_ec2_VpnConnection", Node.COMPUTE)
        AWS_EC2_VPN_CONNECTION_ROUTE = ("AWS_ec2_VpnConnectionRoute", Node.COMPUTE)
        AWS_EC2_VPN_GATEWAY = ("AWS_ec2_VpnGateway", Node.COMPUTE)
        AWS_ECS_CAPACITY_PROVIDER = ("AWS_ecs_CapacityProvider", Node.CONTAINER_SERVICE)
        AWS_ECS_CLUSTER = ("AWS_ecs_Cluster", Node.CONTAINER_SERVICE)
        AWS_ECS_EXPRESS_GATEWAY_SERVICE = ("AWS_ecs_ExpressGatewayService", Node.CONTAINER_SERVICE)
        AWS_ECS_SERVICE = ("AWS_ecs_Service", Node.CONTAINER_SERVICE)
        AWS_ECS_TASK_SET = ("AWS_ecs_TaskSet", Node.CONTAINER_SERVICE)
        AWS_EFS_ACCESS_POINT = ("AWS_efs_AccessPoint", Node.FILE_STORAGE)
        AWS_EFS_FILE_SYSTEM = ("AWS_efs_FileSystem", Node.FILE_STORAGE)
        AWS_EFS_MOUNT_TARGET = ("AWS_efs_MountTarget", Node.FILE_STORAGE)
        AWS_EFS_TAGS = ("AWS_efs_Tags", Node.FILE_STORAGE)
        AWS_EKS_ACCESS_ENTRY = ("AWS_eks_AccessEntry", Node.CONTAINER_CLUSTER)
        AWS_EKS_ADDON = ("AWS_eks_Addon", Node.CONTAINER_CLUSTER)
        AWS_EKS_CAPABILITY = ("AWS_eks_Capability", Node.CONTAINER_CLUSTER)
        AWS_EKS_CLUSTER = ("AWS_eks_Cluster", Node.CONTAINER_CLUSTER)
        AWS_EKS_EKS_ANYWHERE_SUBSCRIPTION = (
            "AWS_eks_EksAnywhereSubscription",
            Node.CONTAINER_CLUSTER,
        )
        AWS_EKS_FARGATE_PROFILE = ("AWS_eks_FargateProfile", Node.CONTAINER_CLUSTER)
        AWS_EKS_NODEGROUP = ("AWS_eks_Nodegroup", Node.CONTAINER_CLUSTER)
        AWS_EKS_POD_IDENTITY_ASSOCIATION = (
            "AWS_eks_PodIdentityAssociation",
            Node.CONTAINER_CLUSTER,
        )
        AWS_IAM_ACCESS_KEY = ("AWS_iam_AccessKey", Node.IDENTITY)
        AWS_IAM_ACCOUNT_ALIAS = ("AWS_iam_AccountAlias", Node.IDENTITY)
        AWS_IAM_GROUP = ("AWS_iam_Group", Node.IDENTITY)
        AWS_IAM_INSTANCE_PROFILE = ("AWS_iam_InstanceProfile", Node.IDENTITY)
        AWS_IAM_LOGIN_PROFILE = ("AWS_iam_LoginProfile", Node.IDENTITY)
        AWS_IAM_OPEN_IDCONNECT_PROVIDER = ("AWS_iam_OpenIDConnectProvider", Node.IDENTITY)
        AWS_IAM_POLICY = ("AWS_iam_Policy", Node.IDENTITY)
        AWS_IAM_POLICY_VERSION = ("AWS_iam_PolicyVersion", Node.IDENTITY)
        AWS_IAM_ROLE = ("AWS_iam_Role", Node.IDENTITY)
        AWS_IAM_SAMLPROVIDER = ("AWS_iam_SAMLProvider", Node.IDENTITY)
        AWS_IAM_SERVICE_LINKED_ROLE = ("AWS_iam_ServiceLinkedRole", Node.IDENTITY)
        AWS_IAM_SERVICE_SPECIFIC_CREDENTIAL = ("AWS_iam_ServiceSpecificCredential", Node.IDENTITY)
        AWS_IAM_USER = ("AWS_iam_User", Node.IDENTITY)
        AWS_IAM_VIRTUAL_MFADEVICE = ("AWS_iam_VirtualMFADevice", Node.IDENTITY)
        AWS_KINESIS_STREAM = ("AWS_kinesis_Stream", Node.STREAM)
        AWS_KMS_ALIAS = ("AWS_kms_Alias", Node.ENCRYPTION_KEY)
        AWS_KMS_CUSTOM_KEY_STORE = ("AWS_kms_CustomKeyStore", Node.ENCRYPTION_KEY)
        AWS_LAMBDA_ALIAS = ("AWS_lambda_Alias", Node.SERVERLESS_FUNCTION)
        AWS_LAMBDA_CAPACITY_PROVIDER = ("AWS_lambda_CapacityProvider", Node.SERVERLESS_FUNCTION)
        AWS_LAMBDA_CODE_SIGNING_CONFIG = ("AWS_lambda_CodeSigningConfig", Node.SERVERLESS_FUNCTION)
        AWS_LAMBDA_EVENT_SOURCE_MAPPING = (
            "AWS_lambda_EventSourceMapping",
            Node.SERVERLESS_FUNCTION,
        )
        AWS_LAMBDA_FUNCTION = ("AWS_lambda_Function", Node.SERVERLESS_FUNCTION)
        AWS_LAMBDA_FUNCTION_URL_CONFIG = ("AWS_lambda_FunctionUrlConfig", Node.SERVERLESS_FUNCTION)
        AWS_RDS_BLUE_GREEN_DEPLOYMENT = ("AWS_rds_BlueGreenDeployment", Node.DATABASE)
        AWS_RDS_CUSTOM_DBENGINE_VERSION = ("AWS_rds_CustomDBEngineVersion", Node.DATABASE)
        AWS_RDS_DBCLUSTER = ("AWS_rds_DBCluster", Node.DATABASE)
        AWS_RDS_DBCLUSTER_ENDPOINT = ("AWS_rds_DBClusterEndpoint", Node.DATABASE)
        AWS_RDS_DBCLUSTER_PARAMETER_GROUP = ("AWS_rds_DBClusterParameterGroup", Node.DATABASE)
        AWS_RDS_DBCLUSTER_SNAPSHOT = ("AWS_rds_DBClusterSnapshot", Node.DATABASE)
        AWS_RDS_DBINSTANCE = ("AWS_rds_DBInstance", Node.DATABASE)
        AWS_RDS_DBPARAMETER_GROUP = ("AWS_rds_DBParameterGroup", Node.DATABASE)
        AWS_RDS_DBPROXY = ("AWS_rds_DBProxy", Node.DATABASE)
        AWS_RDS_DBPROXY_ENDPOINT = ("AWS_rds_DBProxyEndpoint", Node.DATABASE)
        AWS_RDS_DBSECURITY_GROUP = ("AWS_rds_DBSecurityGroup", Node.DATABASE)
        AWS_RDS_DBSHARD_GROUP = ("AWS_rds_DBShardGroup", Node.DATABASE)
        AWS_RDS_DBSNAPSHOT = ("AWS_rds_DBSnapshot", Node.DATABASE)
        AWS_RDS_DBSUBNET_GROUP = ("AWS_rds_DBSubnetGroup", Node.DATABASE)
        AWS_RDS_EVENT_SUBSCRIPTION = ("AWS_rds_EventSubscription", Node.DATABASE)
        AWS_RDS_GLOBAL_CLUSTER = ("AWS_rds_GlobalCluster", Node.DATABASE)
        AWS_RDS_INTEGRATION = ("AWS_rds_Integration", Node.DATABASE)
        AWS_RDS_OPTION_GROUP = ("AWS_rds_OptionGroup", Node.DATABASE)
        AWS_RDS_TENANT_DATABASE = ("AWS_rds_TenantDatabase", Node.DATABASE)
        AWS_ROUTE53_CIDR_COLLECTION = ("AWS_route53_CidrCollection", Node.NETWORK)
        AWS_ROUTE53_HEALTH_CHECK = ("AWS_route53_HealthCheck", Node.NETWORK)
        AWS_ROUTE53_HOSTED_ZONE = ("AWS_route53_HostedZone", Node.NETWORK)
        AWS_ROUTE53_KEY_SIGNING_KEY = ("AWS_route53_KeySigningKey", Node.NETWORK)
        AWS_ROUTE53_QUERY_LOGGING_CONFIG = ("AWS_route53_QueryLoggingConfig", Node.NETWORK)
        AWS_ROUTE53_REUSABLE_DELEGATION_SET = ("AWS_route53_ReusableDelegationSet", Node.NETWORK)
        AWS_ROUTE53_TRAFFIC_POLICY = ("AWS_route53_TrafficPolicy", Node.NETWORK)
        AWS_ROUTE53_TRAFFIC_POLICY_INSTANCE = ("AWS_route53_TrafficPolicyInstance", Node.NETWORK)
        AWS_ROUTE53_VPCASSOCIATION_AUTHORIZATION = (
            "AWS_route53_VPCAssociationAuthorization",
            Node.NETWORK,
        )
        AWS_S3_BUCKET = ("AWS_s3_Bucket", Node.OBJECT_STORAGE)
        AWS_SQS_QUEUE = ("AWS_sqs_Queue", Node.MESSAGE_QUEUE)

    class AZURE(BaseResourceType):

        # Compute
        VIRTUAL_MACHINE = ("AZURE_VM", Node.COMPUTE)
        FUNCTIONS = ("AZURE_FunctionApp", Node.SERVERLESS_FUNCTION)
        APP_SERVICE = ("AZURE_AppService", Node.COMPUTE)
        AKS = ("AZURE_AKS", Node.CONTAINER_CLUSTER)

        # Networking
        VIRTUAL_NETWORK = ("AZURE_VNet", Node.NETWORK)
        SUBNET = ("AZURE_Subnet", Node.SUBNET)
        NETWORK_SECURITY_GROUP = ("AZURE_NSG", Node.FIREWALL)
        LOAD_BALANCER = ("AZURE_LoadBalancer", Node.LOAD_BALANCER)
        APPLICATION_GATEWAY = ("AZURE_AppGateway", Node.LOAD_BALANCER)

        # Storage
        BLOB_STORAGE = ("AZURE_BlobStorage", Node.OBJECT_STORAGE)
        MANAGED_DISK = ("AZURE_ManagedDisk", Node.BLOCK_STORAGE)
        FILE_SHARE = ("AZURE_FileShare", Node.FILE_STORAGE)

        # Databases
        SQL_DATABASE = ("AZURE_SQLDatabase", Node.DATABASE)
        COSMOS_DB = ("AZURE_CosmosDB", Node.DATABASE)
        REDIS_CACHE = ("AZURE_RedisCache", Node.CACHE)

        # Messaging
        SERVICE_BUS = ("AZURE_ServiceBus", Node.MESSAGE_QUEUE)
        EVENT_GRID = ("AZURE_EventGrid", Node.EVENT_BUS)

        # Identity
        ENTRA_ID_USER = ("AZURE_User", Node.IDENTITY)
        ROLE_ASSIGNMENT = ("AZURE_RoleAssignment", Node.ROLE)
        KEY_VAULT = ("AZURE_KeyVault", Node.SECRET)

        # Observability
        MONITOR = ("AZURE_Monitor", Node.MONITORING)
        LOG_ANALYTICS = ("AZURE_LogAnalytics", Node.LOGGING)

    class GCP(BaseResourceType):
        GCP_APPENGINE_APPS = ("GCP_appengine_apps", Node.COMPUTE)
        GCP_APPENGINE_PROJECTS = ("GCP_appengine_projects", Node.COMPUTE)
        GCP_BIGQUERY_DATASETS = ("GCP_bigquery_datasets", Node.DATA_WAREHOUSE)
        GCP_BIGQUERY_JOBS = ("GCP_bigquery_jobs", Node.DATA_WAREHOUSE)
        GCP_BIGQUERY_MODELS = ("GCP_bigquery_models", Node.DATA_WAREHOUSE)
        GCP_BIGQUERY_PROJECTS = ("GCP_bigquery_projects", Node.DATA_WAREHOUSE)
        GCP_BIGQUERY_ROUTINES = ("GCP_bigquery_routines", Node.DATA_WAREHOUSE)
        GCP_BIGQUERY_ROW_ACCESS_POLICIES = ("GCP_bigquery_rowAccessPolicies", Node.DATA_WAREHOUSE)
        GCP_BIGQUERY_TABLEDATA = ("GCP_bigquery_tabledata", Node.DATA_WAREHOUSE)
        GCP_BIGQUERY_TABLES = ("GCP_bigquery_tables", Node.DATA_WAREHOUSE)
        GCP_CLOUDBUILD_PROJECTS = ("GCP_cloudbuild_projects", Node.BUILD_SERVICE)
        GCP_COMPOSER_PROJECTS = ("GCP_composer_projects", Node.RESOURCE)
        GCP_COMPUTE_ACCELERATOR_TYPES = ("GCP_compute_acceleratorTypes", Node.NETWORK)
        GCP_COMPUTE_ADDRESSES = ("GCP_compute_addresses", Node.NETWORK)
        GCP_COMPUTE_ADVICE = ("GCP_compute_advice", Node.NETWORK)
        GCP_COMPUTE_AUTOSCALERS = ("GCP_compute_autoscalers", Node.NETWORK)
        GCP_COMPUTE_BACKEND_BUCKETS = ("GCP_compute_backendBuckets", Node.NETWORK)
        GCP_COMPUTE_BACKEND_SERVICES = ("GCP_compute_backendServices", Node.NETWORK)
        GCP_COMPUTE_CROSS_SITE_NETWORKS = ("GCP_compute_crossSiteNetworks", Node.NETWORK)
        GCP_COMPUTE_DISK_TYPES = ("GCP_compute_diskTypes", Node.NETWORK)
        GCP_COMPUTE_DISKS = ("GCP_compute_disks", Node.NETWORK)
        GCP_COMPUTE_EXTERNAL_VPN_GATEWAYS = ("GCP_compute_externalVpnGateways", Node.NETWORK)
        GCP_COMPUTE_FIREWALL_POLICIES = ("GCP_compute_firewallPolicies", Node.NETWORK)
        GCP_COMPUTE_FIREWALLS = ("GCP_compute_firewalls", Node.NETWORK)
        GCP_COMPUTE_FORWARDING_RULES = ("GCP_compute_forwardingRules", Node.NETWORK)
        GCP_COMPUTE_FUTURE_RESERVATIONS = ("GCP_compute_futureReservations", Node.NETWORK)
        GCP_COMPUTE_GLOBAL_ADDRESSES = ("GCP_compute_globalAddresses", Node.NETWORK)
        GCP_COMPUTE_GLOBAL_FORWARDING_RULES = ("GCP_compute_globalForwardingRules", Node.NETWORK)
        GCP_COMPUTE_GLOBAL_NETWORK_ENDPOINT_GROUPS = (
            "GCP_compute_globalNetworkEndpointGroups",
            Node.NETWORK,
        )
        GCP_COMPUTE_GLOBAL_OPERATIONS = ("GCP_compute_globalOperations", Node.NETWORK)
        GCP_COMPUTE_GLOBAL_ORGANIZATION_OPERATIONS = (
            "GCP_compute_globalOrganizationOperations",
            Node.NETWORK,
        )
        GCP_COMPUTE_GLOBAL_PUBLIC_DELEGATED_PREFIXES = (
            "GCP_compute_globalPublicDelegatedPrefixes",
            Node.NETWORK,
        )
        GCP_COMPUTE_HEALTH_CHECKS = ("GCP_compute_healthChecks", Node.NETWORK)
        GCP_COMPUTE_HTTP_HEALTH_CHECKS = ("GCP_compute_httpHealthChecks", Node.NETWORK)
        GCP_COMPUTE_HTTPS_HEALTH_CHECKS = ("GCP_compute_httpsHealthChecks", Node.NETWORK)
        GCP_COMPUTE_IMAGE_FAMILY_VIEWS = ("GCP_compute_imageFamilyViews", Node.NETWORK)
        GCP_COMPUTE_IMAGES = ("GCP_compute_images", Node.NETWORK)
        GCP_COMPUTE_INSTANCE_GROUP_MANAGERS = ("GCP_compute_instanceGroupManagers", Node.NETWORK)
        GCP_COMPUTE_INSTANCE_GROUPS = ("GCP_compute_instanceGroups", Node.NETWORK)
        GCP_COMPUTE_INSTANCE_TEMPLATES = ("GCP_compute_instanceTemplates", Node.NETWORK)
        GCP_COMPUTE_INSTANCES = ("GCP_compute_instances", Node.NETWORK)
        GCP_COMPUTE_INSTANT_SNAPSHOTS = ("GCP_compute_instantSnapshots", Node.NETWORK)
        GCP_COMPUTE_INTERCONNECT_ATTACHMENT_GROUPS = (
            "GCP_compute_interconnectAttachmentGroups",
            Node.NETWORK,
        )
        GCP_COMPUTE_INTERCONNECT_ATTACHMENTS = ("GCP_compute_interconnectAttachments", Node.NETWORK)
        GCP_COMPUTE_INTERCONNECT_GROUPS = ("GCP_compute_interconnectGroups", Node.NETWORK)
        GCP_COMPUTE_INTERCONNECT_LOCATIONS = ("GCP_compute_interconnectLocations", Node.NETWORK)
        GCP_COMPUTE_INTERCONNECT_REMOTE_LOCATIONS = (
            "GCP_compute_interconnectRemoteLocations",
            Node.NETWORK,
        )
        GCP_COMPUTE_INTERCONNECTS = ("GCP_compute_interconnects", Node.NETWORK)
        GCP_COMPUTE_LICENSE_CODES = ("GCP_compute_licenseCodes", Node.NETWORK)
        GCP_COMPUTE_LICENSES = ("GCP_compute_licenses", Node.NETWORK)
        GCP_COMPUTE_MACHINE_IMAGES = ("GCP_compute_machineImages", Node.NETWORK)
        GCP_COMPUTE_MACHINE_TYPES = ("GCP_compute_machineTypes", Node.NETWORK)
        GCP_COMPUTE_NETWORK_ATTACHMENTS = ("GCP_compute_networkAttachments", Node.NETWORK)
        GCP_COMPUTE_NETWORK_EDGE_SECURITY_SERVICES = (
            "GCP_compute_networkEdgeSecurityServices",
            Node.NETWORK,
        )
        GCP_COMPUTE_NETWORK_ENDPOINT_GROUPS = ("GCP_compute_networkEndpointGroups", Node.NETWORK)
        GCP_COMPUTE_NETWORK_FIREWALL_POLICIES = (
            "GCP_compute_networkFirewallPolicies",
            Node.NETWORK,
        )
        GCP_COMPUTE_NETWORK_PROFILES = ("GCP_compute_networkProfiles", Node.NETWORK)
        GCP_COMPUTE_NETWORKS = ("GCP_compute_networks", Node.NETWORK)
        GCP_COMPUTE_NODE_GROUPS = ("GCP_compute_nodeGroups", Node.NETWORK)
        GCP_COMPUTE_NODE_TEMPLATES = ("GCP_compute_nodeTemplates", Node.NETWORK)
        GCP_COMPUTE_NODE_TYPES = ("GCP_compute_nodeTypes", Node.NETWORK)
        GCP_COMPUTE_ORGANIZATION_SECURITY_POLICIES = (
            "GCP_compute_organizationSecurityPolicies",
            Node.NETWORK,
        )
        GCP_COMPUTE_PACKET_MIRRORINGS = ("GCP_compute_packetMirrorings", Node.NETWORK)
        GCP_COMPUTE_PREVIEW_FEATURES = ("GCP_compute_previewFeatures", Node.NETWORK)
        GCP_COMPUTE_PROJECTS = ("GCP_compute_projects", Node.NETWORK)
        GCP_COMPUTE_PUBLIC_ADVERTISED_PREFIXES = (
            "GCP_compute_publicAdvertisedPrefixes",
            Node.NETWORK,
        )
        GCP_COMPUTE_PUBLIC_DELEGATED_PREFIXES = (
            "GCP_compute_publicDelegatedPrefixes",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_AUTOSCALERS = ("GCP_compute_regionAutoscalers", Node.NETWORK)
        GCP_COMPUTE_REGION_BACKEND_SERVICES = ("GCP_compute_regionBackendServices", Node.NETWORK)
        GCP_COMPUTE_REGION_COMMITMENTS = ("GCP_compute_regionCommitments", Node.NETWORK)
        GCP_COMPUTE_REGION_COMPOSITE_HEALTH_CHECKS = (
            "GCP_compute_regionCompositeHealthChecks",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_DISK_TYPES = ("GCP_compute_regionDiskTypes", Node.NETWORK)
        GCP_COMPUTE_REGION_DISKS = ("GCP_compute_regionDisks", Node.NETWORK)
        GCP_COMPUTE_REGION_HEALTH_AGGREGATION_POLICIES = (
            "GCP_compute_regionHealthAggregationPolicies",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_HEALTH_CHECK_SERVICES = (
            "GCP_compute_regionHealthCheckServices",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_HEALTH_CHECKS = ("GCP_compute_regionHealthChecks", Node.NETWORK)
        GCP_COMPUTE_REGION_HEALTH_SOURCES = ("GCP_compute_regionHealthSources", Node.NETWORK)
        GCP_COMPUTE_REGION_INSTANCE_GROUP_MANAGERS = (
            "GCP_compute_regionInstanceGroupManagers",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_INSTANCE_GROUPS = ("GCP_compute_regionInstanceGroups", Node.NETWORK)
        GCP_COMPUTE_REGION_INSTANCE_TEMPLATES = (
            "GCP_compute_regionInstanceTemplates",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_INSTANCES = ("GCP_compute_regionInstances", Node.NETWORK)
        GCP_COMPUTE_REGION_INSTANT_SNAPSHOTS = ("GCP_compute_regionInstantSnapshots", Node.NETWORK)
        GCP_COMPUTE_REGION_NETWORK_ENDPOINT_GROUPS = (
            "GCP_compute_regionNetworkEndpointGroups",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_NETWORK_FIREWALL_POLICIES = (
            "GCP_compute_regionNetworkFirewallPolicies",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_NOTIFICATION_ENDPOINTS = (
            "GCP_compute_regionNotificationEndpoints",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_OPERATIONS = ("GCP_compute_regionOperations", Node.NETWORK)
        GCP_COMPUTE_REGION_SECURITY_POLICIES = ("GCP_compute_regionSecurityPolicies", Node.NETWORK)
        GCP_COMPUTE_REGION_SSL_CERTIFICATES = ("GCP_compute_regionSslCertificates", Node.NETWORK)
        GCP_COMPUTE_REGION_SSL_POLICIES = ("GCP_compute_regionSslPolicies", Node.NETWORK)
        GCP_COMPUTE_REGION_TARGET_HTTP_PROXIES = (
            "GCP_compute_regionTargetHttpProxies",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_TARGET_HTTPS_PROXIES = (
            "GCP_compute_regionTargetHttpsProxies",
            Node.NETWORK,
        )
        GCP_COMPUTE_REGION_TARGET_TCP_PROXIES = ("GCP_compute_regionTargetTcpProxies", Node.NETWORK)
        GCP_COMPUTE_REGION_URL_MAPS = ("GCP_compute_regionUrlMaps", Node.NETWORK)
        GCP_COMPUTE_REGION_ZONES = ("GCP_compute_regionZones", Node.NETWORK)
        GCP_COMPUTE_REGIONS = ("GCP_compute_regions", Node.NETWORK)
        GCP_COMPUTE_RESERVATION_BLOCKS = ("GCP_compute_reservationBlocks", Node.NETWORK)
        GCP_COMPUTE_RESERVATION_SLOTS = ("GCP_compute_reservationSlots", Node.NETWORK)
        GCP_COMPUTE_RESERVATION_SUB_BLOCKS = ("GCP_compute_reservationSubBlocks", Node.NETWORK)
        GCP_COMPUTE_RESERVATIONS = ("GCP_compute_reservations", Node.NETWORK)
        GCP_COMPUTE_RESOURCE_POLICIES = ("GCP_compute_resourcePolicies", Node.NETWORK)
        GCP_COMPUTE_ROUTERS = ("GCP_compute_routers", Node.NETWORK)
        GCP_COMPUTE_ROUTES = ("GCP_compute_routes", Node.NETWORK)
        GCP_COMPUTE_SECURITY_POLICIES = ("GCP_compute_securityPolicies", Node.NETWORK)
        GCP_COMPUTE_SERVICE_ATTACHMENTS = ("GCP_compute_serviceAttachments", Node.NETWORK)
        GCP_COMPUTE_SNAPSHOTS = ("GCP_compute_snapshots", Node.NETWORK)
        GCP_COMPUTE_SSL_CERTIFICATES = ("GCP_compute_sslCertificates", Node.NETWORK)
        GCP_COMPUTE_SSL_POLICIES = ("GCP_compute_sslPolicies", Node.NETWORK)
        GCP_COMPUTE_STORAGE_POOL_TYPES = ("GCP_compute_storagePoolTypes", Node.NETWORK)
        GCP_COMPUTE_STORAGE_POOLS = ("GCP_compute_storagePools", Node.NETWORK)
        GCP_COMPUTE_SUBNETWORKS = ("GCP_compute_subnetworks", Node.NETWORK)
        GCP_COMPUTE_TARGET_GRPC_PROXIES = ("GCP_compute_targetGrpcProxies", Node.NETWORK)
        GCP_COMPUTE_TARGET_HTTP_PROXIES = ("GCP_compute_targetHttpProxies", Node.NETWORK)
        GCP_COMPUTE_TARGET_HTTPS_PROXIES = ("GCP_compute_targetHttpsProxies", Node.NETWORK)
        GCP_COMPUTE_TARGET_INSTANCES = ("GCP_compute_targetInstances", Node.NETWORK)
        GCP_COMPUTE_TARGET_POOLS = ("GCP_compute_targetPools", Node.NETWORK)
        GCP_COMPUTE_TARGET_SSL_PROXIES = ("GCP_compute_targetSslProxies", Node.NETWORK)
        GCP_COMPUTE_TARGET_TCP_PROXIES = ("GCP_compute_targetTcpProxies", Node.NETWORK)
        GCP_COMPUTE_TARGET_VPN_GATEWAYS = ("GCP_compute_targetVpnGateways", Node.NETWORK)
        GCP_COMPUTE_URL_MAPS = ("GCP_compute_urlMaps", Node.NETWORK)
        GCP_COMPUTE_VPN_GATEWAYS = ("GCP_compute_vpnGateways", Node.NETWORK)
        GCP_COMPUTE_VPN_TUNNELS = ("GCP_compute_vpnTunnels", Node.NETWORK)
        GCP_COMPUTE_WIRE_GROUPS = ("GCP_compute_wireGroups", Node.NETWORK)
        GCP_COMPUTE_ZONE_OPERATIONS = ("GCP_compute_zoneOperations", Node.NETWORK)
        GCP_COMPUTE_ZONE_VM_EXTENSION_POLICIES = (
            "GCP_compute_zoneVmExtensionPolicies",
            Node.NETWORK,
        )
        GCP_COMPUTE_ZONES = ("GCP_compute_zones", Node.NETWORK)
        GCP_DATAFLOW_PROJECTS = ("GCP_dataflow_projects", Node.RESOURCE)
        GCP_DATAPROC_PROJECTS = ("GCP_dataproc_projects", Node.COMPUTE)
        GCP_DEPLOYMENTMANAGER_DEPLOYMENTS = (
            "GCP_deploymentmanager_deployments",
            Node.INFRASTRUCTURE_AS_CODE,
        )
        GCP_DEPLOYMENTMANAGER_MANIFESTS = (
            "GCP_deploymentmanager_manifests",
            Node.INFRASTRUCTURE_AS_CODE,
        )
        GCP_DEPLOYMENTMANAGER_OPERATIONS = (
            "GCP_deploymentmanager_operations",
            Node.INFRASTRUCTURE_AS_CODE,
        )
        GCP_DEPLOYMENTMANAGER_RESOURCES = (
            "GCP_deploymentmanager_resources",
            Node.INFRASTRUCTURE_AS_CODE,
        )
        GCP_DEPLOYMENTMANAGER_TYPES = ("GCP_deploymentmanager_types", Node.INFRASTRUCTURE_AS_CODE)
        GCP_DNS_CHANGES = ("GCP_dns_changes", Node.NETWORK)
        GCP_DNS_DNS_KEYS = ("GCP_dns_dnsKeys", Node.NETWORK)
        GCP_DNS_MANAGED_ZONE_OPERATIONS = ("GCP_dns_managedZoneOperations", Node.NETWORK)
        GCP_DNS_MANAGED_ZONES = ("GCP_dns_managedZones", Node.NETWORK)
        GCP_DNS_POLICIES = ("GCP_dns_policies", Node.NETWORK)
        GCP_DNS_PROJECTS = ("GCP_dns_projects", Node.NETWORK)
        GCP_DNS_RESOURCE_RECORD_SETS = ("GCP_dns_resourceRecordSets", Node.NETWORK)
        GCP_EVENTARC_PROJECTS = ("GCP_eventarc_projects", Node.EVENT_BUS)
        GCP_FIRESTORE_PROJECTS = ("GCP_firestore_projects", Node.DATABASE)
        GCP_IAM_POLICIES = ("GCP_iam_policies", Node.IDENTITY)
        GCP_IAP_PROJECTS = ("GCP_iap_projects", Node.SECURITY_BOUNDARY)
        GCP_IAP_V1 = ("GCP_iap_v1", Node.SECURITY_BOUNDARY)
        GCP_LOGGING_BILLING_ACCOUNTS = ("GCP_logging_billingAccounts", Node.LOGGING)
        GCP_LOGGING_ENTRIES = ("GCP_logging_entries", Node.LOGGING)
        GCP_LOGGING_EXCLUSIONS = ("GCP_logging_exclusions", Node.LOGGING)
        GCP_LOGGING_FOLDERS = ("GCP_logging_folders", Node.LOGGING)
        GCP_LOGGING_LOCATIONS = ("GCP_logging_locations", Node.LOGGING)
        GCP_LOGGING_LOGS = ("GCP_logging_logs", Node.LOGGING)
        GCP_LOGGING_MONITORED_RESOURCE_DESCRIPTORS = (
            "GCP_logging_monitoredResourceDescriptors",
            Node.LOGGING,
        )
        GCP_LOGGING_ORGANIZATIONS = ("GCP_logging_organizations", Node.LOGGING)
        GCP_LOGGING_PROJECTS = ("GCP_logging_projects", Node.LOGGING)
        GCP_LOGGING_SINKS = ("GCP_logging_sinks", Node.LOGGING)
        GCP_LOGGING_V2 = ("GCP_logging_v2", Node.LOGGING)
        GCP_MONITORING_FOLDERS = ("GCP_monitoring_folders", Node.MONITORING)
        GCP_MONITORING_ORGANIZATIONS = ("GCP_monitoring_organizations", Node.MONITORING)
        GCP_MONITORING_PROJECTS = ("GCP_monitoring_projects", Node.MONITORING)
        GCP_MONITORING_SERVICES = ("GCP_monitoring_services", Node.MONITORING)
        GCP_MONITORING_UPTIME_CHECK_IPS = ("GCP_monitoring_uptimeCheckIps", Node.MONITORING)
        GCP_PUBSUB_PROJECTS = ("GCP_pubsub_projects", Node.MESSAGE_QUEUE)
        GCP_RUN_PROJECTS = ("GCP_run_projects", Node.CONTAINER_SERVICE)
        GCP_SECRETMANAGER_PROJECTS = ("GCP_secretmanager_projects", Node.SECRET)
        GCP_SPANNER_PROJECTS = ("GCP_spanner_projects", Node.DATABASE)
        GCP_SPANNER_SCANS = ("GCP_spanner_scans", Node.DATABASE)
        GCP_SQLADMIN_BACKUPS = ("GCP_sqladmin_Backups", Node.DATABASE)
        GCP_SQLADMIN_BACKUP_RUNS = ("GCP_sqladmin_backupRuns", Node.DATABASE)
        GCP_SQLADMIN_CONNECT = ("GCP_sqladmin_connect", Node.DATABASE)
        GCP_SQLADMIN_DATABASES = ("GCP_sqladmin_databases", Node.DATABASE)
        GCP_SQLADMIN_FLAGS = ("GCP_sqladmin_flags", Node.DATABASE)
        GCP_SQLADMIN_INSTANCES = ("GCP_sqladmin_instances", Node.DATABASE)
        GCP_SQLADMIN_OPERATIONS = ("GCP_sqladmin_operations", Node.DATABASE)
        GCP_SQLADMIN_PROJECTS = ("GCP_sqladmin_projects", Node.DATABASE)
        GCP_SQLADMIN_SSL_CERTS = ("GCP_sqladmin_sslCerts", Node.DATABASE)
        GCP_SQLADMIN_TIERS = ("GCP_sqladmin_tiers", Node.DATABASE)
        GCP_SQLADMIN_USERS = ("GCP_sqladmin_users", Node.DATABASE)
        GCP_STORAGE_ANYWHERE_CACHES = ("GCP_storage_anywhereCaches", Node.OBJECT_STORAGE)
        GCP_STORAGE_BUCKET_ACCESS_CONTROLS = (
            "GCP_storage_bucketAccessControls",
            Node.OBJECT_STORAGE,
        )
        GCP_STORAGE_BUCKETS = ("GCP_storage_buckets", Node.OBJECT_STORAGE)
        GCP_STORAGE_CHANNELS = ("GCP_storage_channels", Node.OBJECT_STORAGE)
        GCP_STORAGE_DEFAULT_OBJECT_ACCESS_CONTROLS = (
            "GCP_storage_defaultObjectAccessControls",
            Node.OBJECT_STORAGE,
        )
        GCP_STORAGE_FOLDERS = ("GCP_storage_folders", Node.OBJECT_STORAGE)
        GCP_STORAGE_MANAGED_FOLDERS = ("GCP_storage_managedFolders", Node.OBJECT_STORAGE)
        GCP_STORAGE_NOTIFICATIONS = ("GCP_storage_notifications", Node.OBJECT_STORAGE)
        GCP_STORAGE_OBJECT_ACCESS_CONTROLS = (
            "GCP_storage_objectAccessControls",
            Node.OBJECT_STORAGE,
        )
        GCP_STORAGE_OBJECTS = ("GCP_storage_objects", Node.OBJECT_STORAGE)
        GCP_STORAGE_OPERATIONS = ("GCP_storage_operations", Node.OBJECT_STORAGE)
        GCP_STORAGE_PROJECTS = ("GCP_storage_projects", Node.OBJECT_STORAGE)
        GCP_VPCACCESS_PROJECTS = ("GCP_vpcaccess_projects", Node.NETWORK)
