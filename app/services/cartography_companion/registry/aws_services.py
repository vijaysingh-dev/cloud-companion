from .service_definition import ServiceDefinition

AWS_SERVICES: list[ServiceDefinition] = [

    # ── Identity & Access ─────────────────────────────────────────────────

    ServiceDefinition(
        key="iam",
        provider="aws",
        display_name="IAM",
        module_path="cartography.intel.aws.iam",
        function_name="sync",
        requires_region=False,
        description="Users, roles, groups, policies and their permission relationships.",
    ),
    ServiceDefinition(
        key="iaminstanceprofiles",
        provider="aws",
        display_name="IAM Instance Profiles",
        module_path="cartography.intel.aws.iam",
        function_name="sync_iam_instance_profiles",
        requires_region=False,
        depends_on=["iam"],
        description="EC2 instance profiles and their attached IAM roles.",
    ),

    # ── Networking (must come before compute) ────────────────────────────

    ServiceDefinition(
        key="ec2:vpc",
        provider="aws",
        display_name="EC2 VPCs",
        module_path="cartography.intel.aws.ec2.vpcs",
        function_name="sync_vpc",
        description="Virtual Private Clouds — network isolation boundaries.",
    ),
    ServiceDefinition(
        key="ec2:subnet",
        provider="aws",
        display_name="EC2 Subnets",
        module_path="cartography.intel.aws.ec2.subnets",
        function_name="sync_subnets",
        depends_on=["ec2:vpc"],
        description="Subnets within VPCs and their availability zone placement.",
    ),
    ServiceDefinition(
        key="ec2:security_group",
        provider="aws",
        display_name="EC2 Security Groups",
        module_path="cartography.intel.aws.ec2.security_groups",
        function_name="sync_ec2_security_groups",
        depends_on=["ec2:vpc"],
        description="Security groups — inbound/outbound traffic rules.",
    ),
    ServiceDefinition(
        key="ec2:route_table",
        provider="aws",
        display_name="Route Tables",
        module_path="cartography.intel.aws.ec2.route_tables",
        function_name="sync_route_tables",
        depends_on=["ec2:vpc", "ec2:subnet"],
        description="VPC route tables and their subnet associations.",
    ),
    ServiceDefinition(
        key="ec2:internet_gateway",
        provider="aws",
        display_name="Internet Gateways",
        module_path="cartography.intel.aws.ec2.internet_gateways",
        function_name="sync_internet_gateways",
        depends_on=["ec2:vpc"],
        description="Internet gateways attached to VPCs.",
    ),

    # ── Compute ───────────────────────────────────────────────────────────

    ServiceDefinition(
        key="ec2:instance",
        provider="aws",
        display_name="EC2 Instances",
        module_path="cartography.intel.aws.ec2.instances",
        function_name="sync_ec2_instances",
        depends_on=["ec2:vpc", "ec2:subnet", "ec2:security_group"],
        description="EC2 compute instances, state, type, and network placement.",
    ),
    ServiceDefinition(
        key="ec2:network_interface",
        provider="aws",
        display_name="EC2 Network Interfaces",
        module_path="cartography.intel.aws.ec2.network_interfaces",
        function_name="sync_network_interfaces",
        depends_on=["ec2:instance", "ec2:security_group"],
        description="ENIs — the bridge between EC2 instances and security groups.",
    ),
    ServiceDefinition(
        key="ec2:volumes",
        provider="aws",
        display_name="EBS Volumes",
        module_path="cartography.intel.aws.ec2.volumes",
        function_name="sync_ebs_volumes",
        depends_on=["ec2:instance"],
        description="EBS block storage volumes and instance attachments.",
    ),
    ServiceDefinition(
        key="ec2:load_balancer_v2",
        provider="aws",
        display_name="ALB/NLB",
        module_path="cartography.intel.aws.ec2.load_balancers_v2",
        function_name="sync_load_balancers_v2",
        depends_on=["ec2:instance", "ec2:security_group"],
        description="Application and Network Load Balancers and target groups.",
    ),

    # ── Containers ────────────────────────────────────────────────────────

    ServiceDefinition(
        key="ecs",
        provider="aws",
        display_name="ECS",
        module_path="cartography.intel.aws.ecs",
        function_name="sync_ecs_clusters",
        depends_on=["iam", "ec2:security_group"],
        description="ECS clusters, services, tasks and container definitions.",
    ),
    ServiceDefinition(
        key="eks",
        provider="aws",
        display_name="EKS",
        module_path="cartography.intel.aws.eks",
        function_name="sync_eks_clusters",
        depends_on=["iam", "ec2:security_group", "ec2:subnet"],
        description="EKS Kubernetes clusters and node groups.",
    ),
    ServiceDefinition(
        key="ecr",
        provider="aws",
        display_name="ECR",
        module_path="cartography.intel.aws.ecr",
        function_name="sync_ecr_repositories",
        description="ECR container registries and image repositories.",
    ),

    # ── Serverless ────────────────────────────────────────────────────────

    ServiceDefinition(
        key="lambda_function",
        provider="aws",
        display_name="Lambda",
        module_path="cartography.intel.aws.lambda_function",
        function_name="sync_lambda_functions",
        depends_on=["iam"],
        description="Lambda functions, runtimes, VPC config and IAM roles.",
    ),
    ServiceDefinition(
        key="apigateway",
        provider="aws",
        display_name="API Gateway v1",
        module_path="cartography.intel.aws.apigateway",
        function_name="sync_apigateway_rest_apis",
        depends_on=["lambda_function"],
        description="REST APIs, stages, resources and Lambda integrations.",
    ),
    ServiceDefinition(
        key="apigatewayv2",
        provider="aws",
        display_name="API Gateway v2",
        module_path="cartography.intel.aws.apigatewayv2",
        function_name="sync_apigatewayv2",
        depends_on=["lambda_function"],
        description="HTTP and WebSocket APIs.",
    ),

    # ── Storage ───────────────────────────────────────────────────────────

    ServiceDefinition(
        key="s3",
        provider="aws",
        display_name="S3",
        module_path="cartography.intel.aws.s3",
        function_name="sync_s3_buckets",
        requires_region=False,
        description="S3 buckets, policies, ACLs and encryption settings.",
    ),
    ServiceDefinition(
        key="efs",
        provider="aws",
        display_name="EFS",
        module_path="cartography.intel.aws.efs",
        function_name="sync_efs_file_systems",
        depends_on=["ec2:security_group", "ec2:subnet"],
        description="EFS file systems and mount targets.",
    ),

    # ── Databases ─────────────────────────────────────────────────────────

    ServiceDefinition(
        key="rds",
        provider="aws",
        display_name="RDS",
        module_path="cartography.intel.aws.rds",
        function_name="sync_rds_instances",
        depends_on=["ec2:security_group", "ec2:subnet"],
        description="RDS database instances, clusters and subnet groups.",
    ),
    ServiceDefinition(
        key="dynamodb",
        provider="aws",
        display_name="DynamoDB",
        module_path="cartography.intel.aws.dynamodb",
        function_name="sync_dynamodb_tables",
        description="DynamoDB tables, indices and stream configurations.",
    ),
    ServiceDefinition(
        key="elasticache",
        provider="aws",
        display_name="ElastiCache",
        module_path="cartography.intel.aws.elasticache",
        function_name="sync_elasticache",
        depends_on=["ec2:security_group", "ec2:subnet"],
        description="ElastiCache Redis and Memcached clusters.",
    ),

    # ── Messaging ─────────────────────────────────────────────────────────

    ServiceDefinition(
        key="sqs",
        provider="aws",
        display_name="SQS",
        module_path="cartography.intel.aws.sqs",
        function_name="sync_sqs_queues",
        description="SQS queues and their access policies.",
    ),
    ServiceDefinition(
        key="sns",
        provider="aws",
        display_name="SNS",
        module_path="cartography.intel.aws.sns",
        function_name="sync_sns_topics",
        description="SNS topics and their subscriptions.",
    ),

    # ── Security & Compliance ─────────────────────────────────────────────

    ServiceDefinition(
        key="kms",
        provider="aws",
        display_name="KMS",
        module_path="cartography.intel.aws.kms",
        function_name="sync_kms_keys",
        requires_region=False,
        description="KMS encryption keys and their aliases.",
    ),
    ServiceDefinition(
        key="secretsmanager",
        provider="aws",
        display_name="Secrets Manager",
        module_path="cartography.intel.aws.secretsmanager",
        function_name="sync_secretsmanager_secrets",
        description="Secrets and their rotation configuration.",
    ),
    ServiceDefinition(
        key="cloudtrail",
        provider="aws",
        display_name="CloudTrail",
        module_path="cartography.intel.aws.cloudtrail",
        function_name="sync_cloudtrail",
        requires_region=False,
        description="CloudTrail trails and their S3/CloudWatch destinations.",
    ),

    # ── Observability ─────────────────────────────────────────────────────

    ServiceDefinition(
        key="cloudwatch",
        provider="aws",
        display_name="CloudWatch",
        module_path="cartography.intel.aws.cloudwatch",
        function_name="sync_cloudwatch_log_groups",
        description="CloudWatch log groups and alarms.",
    ),

    # ── DNS & Networking (global) ─────────────────────────────────────────

    ServiceDefinition(
        key="route53",
        provider="aws",
        display_name="Route53",
        module_path="cartography.intel.aws.route53",
        function_name="sync_route53",
        requires_region=False,
        description="Hosted zones and DNS record sets.",
    ),
]